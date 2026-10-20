"""Read-only archive integrity/completeness audit; no models or oracle calls."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent / "audit.json"
SOURCE = "63077ea3ea612197a5ad0e71fbe015d80149ca37"
MANIFEST_HASH = "11c6e0dfd27c7c57d1b51d31cdd588be6475e0c804d4069e5e88d8522f4f2fee"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def only(names: list[str], suffix: str) -> str:
    matches = [n for n in names if n.endswith(suffix)]
    assert len(matches) == 1, (suffix, matches)
    return matches[0]


def inspect(path: str, expected: str, completed: bool) -> dict:
    archive = ROOT / path
    data = archive.read_bytes()
    actual = sha(data)
    assert actual == expected, path
    with ZipFile(archive) as zipped:
        assert zipped.testzip() is None, path
        names = zipped.namelist()
        metadata = json.loads(zipped.read(only(names, "/run_metadata.json")))
        history = json.loads(zipped.read(only(names, "/m2_metrics_history.json")))
        result = {
            "archive": path,
            "sha256": actual,
            "bytes": len(data),
            "sha256_matches": True,
            "zip_crc_passed": True,
            "method": metadata["method"],
            "system": "-".join(metadata["system"])
            if isinstance(metadata["system"], list)
            else metadata["system"],
            "seed": metadata["seed"],
            "query_budget": metadata["query_budget"],
            "metadata_status": metadata.get("status"),
            "query_counts": history["query_counts"],
            "complete_curve": history["complete_curve"],
        }
        assert metadata["split"] == "dev" and metadata["query_budget"] == 20
        if completed:
            assert metadata["status"] == "completed"
            assert history["complete_curve"]
            assert history["query_counts"] == list(range(1, 21))
            assert only(names, "/trajectories/episode_000.json")
        else:
            exit_record = json.loads(zipped.read(only(names, "/m2_exit.json")))
            assert exit_record["termination"] == "compute_time_limit"
            checkpoints = [n for n in names if n.endswith("/checkpoint.json")]
            result["termination"] = exit_record["termination"]
            result["checkpoint_files"] = checkpoints
            result["cif_files"] = sum(n.endswith(".cif") for n in names)
            if checkpoints:
                assert len(checkpoints) == 1
                raw_checkpoint = zipped.read(checkpoints[0])
                checkpoint = json.loads(raw_checkpoint)
                cache = checkpoint["agent_state"]["generator"]["cached_candidates"]
                candidates = [item for entries in cache.values() for item in entries]
                assert all(
                    isinstance(item, list)
                    and len(item) == 2
                    and item[0].get("@class") == "Structure"
                    and item[0].get("sites")
                    and item[0].get("lattice")
                    and isinstance(item[1], str)
                    for item in candidates
                )
                result["saved_checkpoint"] = {
                    "sha256": sha(raw_checkpoint),
                    "bytes": len(raw_checkpoint),
                    "query_count": checkpoint["query_count"],
                    "metrics_history_length": len(checkpoint["metrics_history"]),
                    "trajectory_length": len(checkpoint["trajectory"]),
                    "cached_candidate_count": len(candidates),
                    "cache_keys": list(cache),
                    "candidate_payloads_structurally_present": True,
                    "agent_state_present": True,
                    "environment_state_present": bool(checkpoint["env_state"]),
                    "config_present": bool(checkpoint["config"]),
                    "recovery_execution_verified": False,
                }
            progress = zipped.read(only(names, "/m2_progress.jsonl")).decode().splitlines()
            result["last_progress_diagnostics"] = json.loads(progress[-1])
        return result


def main() -> None:
    manifest_file = ROOT / "M2/configs/verified_baselines.json"
    manifest_bytes = manifest_file.read_bytes()
    assert sha(manifest_bytes) == MANIFEST_HASH, "Original manifest changed"
    original = json.loads(manifest_bytes)["archives"]
    assert len(original) == 19
    prior = [inspect(r["path"], r["sha256"], True) for r in original]
    receipts = []
    for path in sorted((ROOT / "M2/execution_ledger").rglob("receipt_*.json")):
        record = json.loads(path.read_text())
        if record["attempt"] in {3938658932401, 3938733161401}:
            receipts.append(record)
    assert len(receipts) == 17
    assert len({r["unit"] for r in receipts}) == 17
    assert Counter(r["status"] for r in receipts) == {
        "verified_completed": 15,
        "timeout": 2,
    }
    new = []
    for receipt in receipts:
        assert receipt["source_sha"] == SOURCE
        assert receipt["validation_error"] is None
        row = inspect(
            receipt["archive"], receipt["sha256"], receipt["status"] == "verified_completed"
        )
        row["receipt_status"] = receipt["status"]
        row["attempt"] = receipt["attempt"]
        new.append(row)
    complete = prior + [r for r in new if r["receipt_status"] == "verified_completed"]
    keys = {(r["method"], r["system"], r["seed"]) for r in complete}
    assert len(keys) == len(complete) == 34
    methods = Counter(r["method"] for r in complete)
    assert methods["random_generator_baseline"] == 18
    assert methods["chemeleon_generative_baseline"] == 16
    au = next(r for r in new if r["system"] == "Au-K-Tb" and r["seed"] == 17)
    co = next(r for r in new if r["system"] == "Co-Dy-W" and r["seed"] == 43)
    assert not au["checkpoint_files"] and au["query_counts"] == []
    assert au["cif_files"] == 0
    assert co["saved_checkpoint"]["cached_candidate_count"] == 1024
    assert co["saved_checkpoint"]["query_count"] == 1
    assert co["query_counts"] == [1]
    report = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "published_snapshot": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "scientific_source": SOURCE,
        "scope": "offline archive bytes, CRC, complete B20 curves and timeout checkpoint inspection",
        "new_scientific_experiments": 0,
        "models_loaded": False,
        "api_calls": 0,
        "metric_validation": "existing automatic verified_completed receipts retained; no new full metrics recomputation",
        "original_manifest_sha256": MANIFEST_HASH,
        "original_archives_unchanged": 19,
        "new_successful_archives": 15,
        "timeout_archives_preserved": 2,
        "all_archive_sha256_and_crc_passed": 36,
        "complete_distinct_B20_units": 34,
        "complete_by_method": dict(methods),
        "missing_units": ["Au-K-Tb-17", "Co-Dy-W-43"],
        "resume_admission": {
            "Au-K-Tb-17": "No checkpoint or CIF pool in preserved archive; current evidence cannot resume initial generation",
            "Co-Dy-W-43": "1024 cached structures and query-1 checkpoint preserved; restore is a candidate for validation, not a verified continuation",
        },
        "original_archives": prior,
        "new_archives": new,
        "passed": True,
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"original_archives", "new_archives"}}, indent=2))


if __name__ == "__main__":
    main()
