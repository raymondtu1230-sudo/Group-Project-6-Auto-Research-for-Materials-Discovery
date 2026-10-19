"""Experimental execution wrapper for the unchanged M1 Chemeleon driver.

Not admitted to baseline reporting until batch-scale/cross-runner proof passes.
Each planned pause remains a failed/incomplete M1 attempt, never a score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from M2.generation_cache import BatchCache, GenerationPausedError  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--max-new-batches", type=int, default=1)
    parser.add_argument("driver_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    driver_args = list(args.driver_args)
    if driver_args and driver_args[0] == "--":
        driver_args.pop(0)
    unit = argparse.ArgumentParser(add_help=False)
    unit.add_argument(
        "--method", required=True, choices=["chemeleon_generative_baseline"]
    )
    unit.add_argument("--split", required=True, choices=["dev"])
    unit.add_argument("--system", required=True)
    unit.add_argument("--seed", required=True, type=int)
    unit.add_argument("--attempt", required=True, type=int)
    values = unit.parse_args(driver_args)
    if args.max_new_batches < 1:
        parser.error("max-new-batches must be positive")
    identity = {k: v for k, v in vars(values).items() if k != "attempt"}
    files = [
        "M1/run_experiment.py",
        "M1/protocol/protocol_v1.yaml",
        "M1/MADE/uv.lock",
        "M1/MADE/src/made/agents/generators/chemeleon.py",
        "M1/MADE/src/made/agents/generators/cached.py",
        "M2/generation_cache.py",
        "M2/cache_protocol.py",
    ]
    identity["source_hashes"] = {
        name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in files
    }
    from chemeleon_dng.diffusion.diffusion_module import DiffusionModule

    cache = BatchCache(args.cache_dir, identity, args.max_new_batches)
    old_args = sys.argv
    old_error_mode = os.environ.get("HYDRA_FULL_ERROR")
    os.environ["HYDRA_FULL_ERROR"] = "1"
    started = time.monotonic()
    outcome = "failed"
    try:
        sys.argv = [str(REPO / "M1/run_experiment.py"), *driver_args]
        with cache.patch(DiffusionModule):
            runpy.run_path(str(REPO / "M1/run_experiment.py"), run_name="__main__")
        outcome = "completed"
    except GenerationPausedError:
        outcome = "planned_generation_pause"
    finally:
        sys.argv = old_args
        if old_error_mode is None:
            os.environ.pop("HYDRA_FULL_ERROR", None)
        else:
            os.environ["HYDRA_FULL_ERROR"] = old_error_mode
        record = {
            "outcome": outcome,
            "new_batches": cache.sampled,
            "replayed_batches": cache.replayed,
            "elapsed_seconds": time.monotonic() - started,
            "attempt": values.attempt,
            "benchmark_score": outcome == "completed",
            "identity": identity,
        }
        target = args.cache_dir / f"stage_attempt_{values.attempt}.json"
        if target.exists():
            raise ValueError("Preserve existing stage evidence; choose a new attempt")
        target.write_text(json.dumps(record, indent=2) + "\n")
    if outcome == "planned_generation_pause":
        raise SystemExit(75)


if __name__ == "__main__":
    main()
