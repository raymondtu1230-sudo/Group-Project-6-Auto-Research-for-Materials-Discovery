"""Test real Chemeleon generation before admitting experimental batch replay.

Run in separate processes: continuous, deliberately interrupted, then resumed.
Small integration fixtures are not protocol scores or full-pool performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import socket
import sys
from pathlib import Path

import numpy as np
import torch
from pymatgen.core import Composition

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from M2.generation_cache import (  # noqa: E402
    BatchCache,
    GenerationPausedError,
    rng_state,
)

from made.agents.base import Plan  # noqa: E402
from made.agents.generators.chemeleon import ChemeleonGenerator  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("continuous", "interrupt", "resume", "compare"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--num-candidates", type=int, default=2)
    parser.add_argument("--require-cross-runner", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1 or args.num_candidates != 2 * args.batch_size:
        parser.error("Recovery check requires exactly two equal positive batches")
    args.output.mkdir(parents=True, exist_ok=True)
    if args.mode == "compare":
        expected = json.loads((args.output / "continuous.json").read_text())
        actual = json.loads((args.output / "resume.json").read_text())
        interrupted = json.loads((args.output / "interrupt.json").read_text())
        checks = {
            "structures_equal": expected["structures"] == actual["structures"],
            "rng_equal": expected["rng"] == actual["rng"],
            "first_batch_preserved": interrupted["new_batches"] == 1,
            "completed_batch_not_sampled_twice": actual["replayed_batches"] == 1
            and actual["new_batches"] == 1,
            "candidate_count": len(actual["structures"]) == args.num_candidates,
            "fixture_equal": expected["fixture"] == actual["fixture"]
            == interrupted["fixture"],
            "cache_source_equal": expected["cache_source_sha256"]
            == actual["cache_source_sha256"] == interrupted["cache_source_sha256"],
            "saved_batch_bytes_preserved": interrupted["first_batch_sha256"]
            == actual["first_batch_sha256"],
        }
        if args.require_cross_runner:
            checks["different_runner_hosts"] = (
                interrupted["runner"]["hostname"] != actual["runner"]["hostname"]
            )
        report = {
            "kind": "real_cross_process_chemeleon_batch_recovery",
            "benchmark_score": False,
            "fixture": actual["fixture"],
            "checks": checks,
            "passed": all(checks.values()),
            "scope": "Actual-model recovery fixture only; not a protocol score or complete protocol-pool validation.",
        }
        (args.output / "verification.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(json.dumps(report, indent=2))
        if not report["passed"]:
            raise SystemExit(1)
        return
    from chemeleon_dng.diffusion.diffusion_module import DiffusionModule

    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    fixture = {
        "formula": "Li2O", "batch_size": args.batch_size,
        "num_candidates": args.num_candidates, "seed": 17,
        "diffusion_steps": "unchanged model default (256)",
    }
    generator = ChemeleonGenerator(task="csp", batch_size=args.batch_size, device="cpu")
    plan = Plan(compositions=[Composition("Li2O")], num_candidates=args.num_candidates)
    cache = BatchCache(
        args.output / "cache",
        {"fixture": fixture},
        1 if args.mode == "interrupt" else None,
    )
    result = None
    if args.mode == "continuous":
        result = generator.generate(plan, {})
    else:
        with cache.patch(DiffusionModule):
            try:
                result = generator.generate(plan, {})
            except GenerationPausedError:
                if args.mode != "interrupt":
                    raise
    record = {
        "fixture": fixture,
        "runner": {"hostname": socket.gethostname(), "name": os.getenv("RUNNER_NAME")},
        "structures": [s.as_dict() for s in result] if result else None,
        "rng": rng_state(),
        "new_batches": cache.sampled,
        "replayed_batches": cache.replayed,
        "cache_source_sha256": hashlib.sha256(
            (REPO / "M2/generation_cache.py").read_bytes()
        ).hexdigest(),
        "first_batch_sha256": hashlib.sha256(
            (args.output / "cache/batch_0000.json").read_bytes()
        ).hexdigest() if args.mode != "continuous" else None,
    }
    target = args.output / f"{args.mode}.json"
    if target.exists():
        raise ValueError("Keep previous evidence; use a fresh output directory")
    target.write_text(json.dumps(record, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()

