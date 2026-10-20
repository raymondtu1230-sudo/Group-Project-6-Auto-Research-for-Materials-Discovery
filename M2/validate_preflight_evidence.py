"""Validate 17 real infrastructure jobs and compute observed interval overlap."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def audit(folder: Path, jobs_path: Path) -> dict:
    probes = [json.loads(p.read_text()) for p in folder.rglob("probe.json")]
    jobs = json.loads(jobs_path.read_text())["jobs"]
    matrix = [j for j in jobs if j["name"].startswith("probe (")]
    events = []
    for p in probes:
        events.extend(
            [
                (datetime.fromisoformat(p["started_at"]), 1),
                (datetime.fromisoformat(p["completed_at"]), -1),
            ]
        )
    peak = active = 0
    for _, change in sorted(events, key=lambda e: (e[0], e[1])):
        active += change
        peak = max(peak, active)
    result = {
        "scope": "infrastructure_only_not_science",
        "probe_records": len(probes),
        "unique_unit_directories": len(
            {(p["system"], p["seed"], p["attempt"]) for p in probes}
        ),
        "matrix_jobs": len(matrix),
        "unique_runner_names": len({j["runner_name"] for j in matrix}),
        "observed_probe_peak_concurrency": peak,
        "matrix_successes": sum(j["conclusion"] == "success" for j in matrix),
        "matrix_expected_failures": sum(j["conclusion"] == "failure" for j in matrix),
        "job_durations_seconds": {
            j["name"]: (
                datetime.fromisoformat(j["completed_at"].replace("Z", "+00:00"))
                - datetime.fromisoformat(j["started_at"].replace("Z", "+00:00"))
            ).total_seconds()
            for j in matrix
        },
        "account_plan": "unknown; connector does not expose billing or global slots",
        "future_free_slots": "unknown; observed overlap is a point-in-time measurement",
    }
    result["passed"] = (
        len(probes)
        == len(matrix)
        == result["unique_unit_directories"]
        == result["unique_runner_names"]
        == 17
        and result["matrix_successes"] == 16
        and result["matrix_expected_failures"] == 1
        and sum(bool(p["intentional_failure"]) for p in probes) == 1
    )
    (folder / "scheduling-validation.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--downloads", type=Path, required=True)
    p.add_argument("--jobs", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.downloads, args.jobs)
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)
