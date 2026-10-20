"""Use the hosted six-hour job while bounding termination, package and upload."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


def budget(job_epoch: int, now: int | None = None) -> dict:
    elapsed = max(0, (int(time.time()) if now is None else now) - job_epoch)
    # Observed successful package/upload took tens of seconds. Keep explicit
    # bounded allowances: TERM/KILL 60s, package 60s, upload 180s, cleanup 30s.
    reserve = 60 + 60 + 180 + 30
    seconds = 360 * 60 - elapsed - reserve
    if seconds < 60:
        raise ValueError("Insufficient safe compute time after setup")
    return {
        "job_limit_minutes": 360,
        "compute_step_limit_minutes": 360,
        "compute_seconds": seconds,
        "setup_elapsed_seconds": elapsed,
        "termination_reserve_seconds": 60,
        "package_limit_seconds": 60,
        "upload_limit_seconds": 180,
        "cleanup_reserve_seconds": 30,
        "total_reserve_seconds": reserve,
        "scientific_budget": 20,
        "scientific_settings_changed": False,
    }


if __name__ == "__main__":
    value = budget(int(os.environ["M2_JOB_EPOCH"]))
    path = Path("../../M2/runtime/time-budget.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        print(f"seconds={value['compute_seconds']}", file=output)
    print(json.dumps(value))
