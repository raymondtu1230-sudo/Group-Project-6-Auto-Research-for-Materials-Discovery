"""Missing-only direct Chemeleon preparation; infrastructure is never science."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO = Path(__file__).resolve().parents[1]
METHOD = "chemeleon_generative_baseline"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def fingerprint(root: Path = REPO) -> dict:
    """Pin the driver, official scientific code/config, protocol and data."""
    paths = [root / "M1/run_experiment.py", root / "M1/cost_tracking.py"]
    for sub in [
        "M1/protocol",
        "M1/MADE/configs",
        "M1/MADE/src",
        "M1/MADE/scripts",
        "M1/MADE/data",
    ]:
        paths.extend(
            p
            for p in (root / sub).rglob("*")
            if p.suffix in {".py", ".yaml", ".json", ".csv"}
        )
    paths.extend([root / "M1/MADE/uv.lock", root / "M1/MADE/pyproject.toml"])
    return {str(p.relative_to(root)): digest(p) for p in sorted(set(paths))}


def make_plan(published: Path, output: Path) -> dict:
    # This import requires the actual locked MADE environment, not a stand-in.
    sys.path.insert(0, str(REPO))
    from M2.prepare_missing import import_verified_archives, prepare

    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads(
        (published / "M2/configs/verified_baselines.json").read_text()
    )
    # Successful new attempts are reused only after actual offline validation.
    for receipt in sorted((published / "M2/execution_ledger").glob("*/receipt_*.json")):
        record = json.loads(receipt.read_text())
        if record["status"] == "verified_completed":
            manifest["archives"].append(
                {
                    "path": str((published / record["archive"]).resolve()),
                    "sha256": record["sha256"],
                }
            )
    for item in manifest["archives"]:
        item["path"] = str((published / item["path"]).resolve())
    manifest_path = output / "input-manifest.json"
    write(manifest_path, manifest)
    import_verified_archives(
        manifest_path, output / "reused", published / "M2/verification"
    )
    protocol = REPO / "M1/protocol/protocol_v1.yaml"
    systems = REPO / "M1/protocol/dev_systems.json"
    if digest(protocol) != digest(published / protocol.relative_to(REPO)) or digest(
        systems
    ) != digest(published / systems.relative_to(REPO)):
        raise ValueError(
            "Current published protocol/systems changed; prepare a new pinned source"
        )
    plan = prepare(output / "reused", protocol, systems)
    missing = [u for u in plan["missing_units"] if u["method"] == METHOD]
    if any(u["method"] != METHOD for u in plan["missing_units"]):
        raise ValueError(
            "Unexpected missing Random units; review rather than rescheduling"
        )
    result = {
        "expected": plan["expected_baseline_units"],
        "completed": plan["completed_baseline_units"],
        "missing_count": len(missing),
        "matrix": {"include": missing},
        "mode": "direct_from_scratch",
        "initial_pool_resume": False,
        "capacity_policy": "Bounded full run permitted; timeout risk explicitly accepted, no six-hour completion guarantee.",
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
        "published_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=published, text=True
        ).strip(),
        "science_sha256": fingerprint(),
        "manifest_sha256": digest(published / "M2/configs/verified_baselines.json"),
        "units": plan["units"],
    }
    write(output / "plan.json", result)
    certificate = published / "M2/configs/chemeleon_direct_validation.json"
    result["validated_direct_source"] = False
    if certificate.is_file():
        proof = json.loads(certificate.read_text())
        result["validated_direct_source"] = (
            proof.get("passed") is True
            and proof.get("source_sha") == result["source_sha"]
            and all(
                digest(REPO / name) == expected
                for name, expected in proof["code_sha256"].items()
            )
        )
    write(output / "plan.json", result)
    return result


def validate_request(request: dict, plan: dict, formal: bool = False) -> list:
    if (
        not re.fullmatch(r"[0-9a-f]{40}", request.get("source_sha", ""))
        or request["source_sha"] != plan["source_sha"]
    ):
        raise ValueError("Request must pin the exact checked-out source commit")
    parallel = request.get("max_parallel")
    if (
        isinstance(parallel, bool)
        or not isinstance(parallel, int)
        or not 1 <= parallel <= 17
    ):
        raise ValueError("max_parallel must be 1..17")
    if formal and (
        request.get("mode") != "formal_direct"
        or request.get("acknowledgement")
        != "RUN_ONLY_MISSING_DEV_CHEMELEON_B20_NO_RESUME"
    ):
        raise ValueError("Explicit formal request acknowledgement required")
    if formal and not plan.get("validated_direct_source"):
        raise ValueError(
            "This exact direct source has no successful published preflight certificate"
        )
    if not formal and request.get("mode") != "infrastructure_only":
        raise ValueError("Infrastructure workflow cannot run formal science")
    all_units = plan["matrix"]["include"]
    selected = request.get("units", "all_missing")
    if selected == "all_missing":
        return all_units
    if not isinstance(selected, list) or not selected:
        raise ValueError("Select all_missing or a nonempty list of system/seed objects")
    keys = [(u.get("system"), u.get("seed")) for u in selected]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate requested unit")
    units = {(u["system"], u["seed"]): u for u in all_units}
    if any(k not in units for k in keys):
        raise ValueError(
            "Requested unit is already completed or outside missing dev protocol"
        )
    return [units[k] for k in keys]


def budget(job_epoch: int, now: int | None = None) -> dict:
    elapsed = max(0, (int(time.time()) if now is None else now) - job_epoch)
    # One minute below the Actions step limit covers TERM/KILL and final capture.
    seconds = min(340 * 60 - 60, 360 * 60 - elapsed - 20 * 60 - 60)
    if seconds < 60:
        raise ValueError("No safe compute budget remains after setup")
    return {
        "job_limit_minutes": 360,
        "compute_step_limit_minutes": 340,
        "compute_seconds": seconds,
        "setup_elapsed_seconds": elapsed,
        "save_reserve_seconds": 20 * 60,
        "termination_reserve_seconds": 60,
        "initial_pool_resume": False,
    }


def api_check(output: Path) -> None:
    """One bounded authenticated public summary query; never serialize the key."""
    from mp_api.client import MPRester

    key = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip()
    if not key:
        raise ValueError("Repository API secret is unavailable")
    started = time.monotonic()
    try:
        with MPRester(api_key=key, timeout=30, mute_progress_bars=True) as client:
            docs = client.materials.summary.search(
                material_ids=["mp-149"],
                fields=["material_id"],
                num_chunks=1,
                chunk_size=1,
            )
        ok = len(docs) == 1 and str(docs[0].material_id) == "mp-149"
    except Exception as error:
        # Exception strings can contain request headers/URLs: retain type only.
        write(
            output,
            {
                "authenticated": False,
                "error_type": type(error).__name__,
                "elapsed_seconds": time.monotonic() - started,
            },
        )
        raise RuntimeError("Real API query failed; see redacted result") from None
    write(
        output,
        {
            "authenticated": ok,
            "material_id": "mp-149",
            "query": "public summary, identity field only",
            "elapsed_seconds": time.monotonic() - started,
        },
    )
    if not ok:
        raise RuntimeError("Unexpected real API response")


def probe(output: Path, system: str, seed: int, attempt: int, fail: bool) -> None:
    target = output / f"{system}/seed_{seed}/attempt_{attempt}"
    target.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC).isoformat()
    # Fixed 45 seconds, no models, oracle or scientific trajectories.
    time.sleep(45)
    write(
        target / "probe.json",
        {
            "scope": "infrastructure_only_not_science",
            "system": system,
            "seed": seed,
            "attempt": attempt,
            "runner_name": os.environ.get("RUNNER_NAME"),
            "hostname": platform.node(),
            "job_id": os.environ.get("GITHUB_JOB"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "started_at": started,
            "completed_at": datetime.now(UTC).isoformat(),
            "intentional_failure": fail,
        },
    )
    if fail:
        raise SystemExit(23)


def package(output: Path, unit: str, attempt: int, exit_code: int) -> dict:
    """Preserve successes, failures and timeouts without rewriting official records."""
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{unit}-attempt-{attempt}.zip"
    if archive.exists():
        raise ValueError("Refusing to overwrite an earlier attempt archive")
    candidates = [
        REPO / "M1/MADE/results/protocol_v1",
        REPO / "M1/MADE/checkpoints",
        REPO / "M2/runtime",
    ]
    secret = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip().encode()
    with ZipFile(archive, "w", ZIP_DEFLATED) as target:
        for root in candidates:
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                data = path.read_bytes()
                if secret and secret in data:
                    data = data.replace(secret, b"[REDACTED]")
                target.writestr(str(path.relative_to(REPO)), data)
    status = "timeout" if exit_code == 124 else "failed"
    validation_error = None
    if exit_code == 0:
        sys.path.insert(0, str(REPO))
        from M2.evaluate import collect

        try:
            runs, issues = collect(REPO / "M1/MADE/results/protocol_v1", "dev")
            if len(runs) == 1 and not issues:
                status = "verified_completed"
            else:
                validation_error = {"validated_runs": len(runs), "issues": issues}
        except Exception as error:
            validation_error = {"error_type": type(error).__name__}
    record = {
        "status": status,
        "exit_code": exit_code,
        "unit": unit,
        "attempt": attempt,
        "archive": archive.name,
        "sha256": digest(archive),
        "validation_error": validation_error,
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
    }
    write(output / "receipt.json", record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "budget", "api", "probe", "package"])
    parser.add_argument("--published", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--system")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--fail", action="store_true")
    parser.add_argument("--exit-code", type=int, default=1)
    args = parser.parse_args()
    if args.action == "plan":
        result = make_plan(args.published, args.output)
        if args.request:
            request = json.loads(args.request.read_text())
            selected = validate_request(request, result, args.formal)
            with Path(os.environ["GITHUB_OUTPUT"]).open("a") as stream:
                print("matrix=" + json.dumps({"include": selected}), file=stream)
                print("parallel=" + str(request["max_parallel"]), file=stream)
                print("source=" + request["source_sha"], file=stream)
                print(
                    "retry_of=" + json.dumps(request.get("retry_of", {})), file=stream
                )
        print(
            json.dumps(
                {k: result[k] for k in ["expected", "completed", "missing_count"]}
            )
        )
    elif args.action == "budget":
        result = budget(int(os.environ["M2_JOB_EPOCH"]))
        write(args.output, result)
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as stream:
            print("seconds=" + str(result["compute_seconds"]), file=stream)
    elif args.action == "api":
        api_check(args.output)
    elif args.action == "probe":
        probe(args.output, args.system, args.seed, args.attempt, args.fail)
    elif args.action == "package":
        print(
            json.dumps(
                package(
                    args.output,
                    f"{args.system}-{args.seed}",
                    args.attempt,
                    args.exit_code,
                )
            )
        )


if __name__ == "__main__":
    main()
