"""Offline audit of a completed paired development pilot; never agent input."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MADE = ROOT / "M1/MADE"


def differences(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            result.extend(
                differences(a.get(key), b.get(key), f"{path}.{key}".strip("."))
            )
        return result
    return [] if a == b else [path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import yaml

    sys.path.insert(0, str(ROOT / "M2"))
    from evaluate import load_run

    report = {
        "development_only": True,
        "scope": "one dev pair, M3/M4, not frozen-full ablation",
        "system": "Mg-Sn-Sr",
        "seed": 17,
        "budget": 20,
        "arms": {},
    }
    configs, runs = {}, {}
    for arm in ["on", "off"]:
        path = (
            MADE
            / f"results/protocol_v1/m4_dev_pilot_{arm}/dev/Mg-Sn-Sr/seed_17/attempt_{args.attempt:02d}"
        )
        run = load_run(path)
        runs[arm] = run
        configs[arm] = yaml.safe_load((path / "resolved_config.yaml").read_text())
        trace = json.loads((path / "m3_decision_trace.json").read_text())
        assert trace, (
            "No decision trace captured; do not claim consumption verification"
        )
        assert any(row.get("memory_used") for row in trace) == (arm == "on")
        if arm == "off":
            assert all(not row.get("memory_ids") for row in trace)
        export = path / "m4_evidence_complete.jsonl"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "M4/export_evidence.py"),
                str(path / "trajectories/episode_000.json"),
                str(export),
                "--run-id",
                f"m4_dev_pilot_{arm}-dev-Mg-Sn-Sr-seed17-attempt{args.attempt:02d}",
                "--episode-id",
                "0",
                "--elements",
                "Mg",
                "Sn",
                "Sr",
            ],
            check=True,
        )
        records = [json.loads(line) for line in export.read_text().splitlines()]
        assert len(records) == 20
        online = path / "m4_evidence.jsonl"
        events = path / "m4_proposal_events.jsonl"
        report["arms"][arm] = {
            "official_metrics": {**run.row, "source": str(path.relative_to(ROOT))},
            "trace_reviews": len(trace),
            "reviews_using_memory": sum(bool(x.get("memory_used")) for x in trace),
            "complete_evidence_records": len(records),
            "online_memory_records": len(online.read_text().splitlines())
            if online.exists()
            else 0,
            "proposal_events": len(events.read_text().splitlines())
            if events.exists()
            else 0,
            "raw_files_sha256": {
                str(file.relative_to(path)): hashlib.sha256(
                    file.read_bytes()
                ).hexdigest()
                for file in path.rglob("*")
                if file.is_file()
            },
        }
    changed = differences(configs["on"], configs["off"])
    allowed = {
        "agent.enable_memory",
        "agent.memory_manager.log_path",
        "agent.memory_manager.run_id",
        "agent.capture_path",
        "agent.capture_run_id",
        "experiment.output_dir",
    }
    assert set(changed) <= allowed, f"Unexpected configuration differences: {changed}"
    assert configs["on"]["agent"]["enable_memory"] is True
    assert configs["off"]["agent"]["enable_memory"] is False
    assert runs["on"].reference_hash == runs["off"].reference_hash
    report.update(
        configuration_differences=changed,
        same_reference_snapshot=True,
        official_run_validation="both accepted by M2 load_run",
        interpretation="Single-seed development evidence only; no aggregate improvement claim",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise SystemExit("Preserve previous audit; choose a new output path")
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"audit": "passed", "output": str(args.output)}))


if __name__ == "__main__":
    main()
