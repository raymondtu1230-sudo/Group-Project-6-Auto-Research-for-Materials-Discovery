"""Test real Chemeleon generation before admitting experimental batch replay.

Run in separate processes: continuous, deliberately interrupted, then resumed.
Small integration fixtures are not protocol scores or full-pool performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
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
    args = parser.parse_args()
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
        }
        report = {
            "kind": "real_cross_process_chemeleon_batch_recovery",
            "benchmark_score": False,
            "fixture": "Li2O, two candidates, batch size 1, original 256 diffusion steps",
            "checks": checks,
            "passed": all(checks.values()),
            "scope": "Small actual-model integration check. Full protocol pool/batch-scale validation still required.",
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
    generator = ChemeleonGenerator(task="csp", batch_size=1, device="cpu")
    plan = Plan(compositions=[Composition("Li2O")], num_candidates=2)
    cache = BatchCache(
        args.output / "cache",
        {"fixture": "Li2O-two-candidates-seed17"},
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
        "structures": [s.as_dict() for s in result] if result else None,
        "rng": rng_state(),
        "new_batches": cache.sampled,
        "replayed_batches": cache.replayed,
        "cache_source_sha256": hashlib.sha256(
            (REPO / "M2/generation_cache.py").read_bytes()
        ).hexdigest(),
    }
    target = args.output / f"{args.mode}.json"
    if target.exists():
        raise ValueError("Keep previous evidence; use a fresh output directory")
    target.write_text(json.dumps(record, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
