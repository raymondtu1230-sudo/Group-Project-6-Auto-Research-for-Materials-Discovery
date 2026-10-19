"""Verify checkpoint continuation using the actual Chemeleon diffusion model.

This is a generation integration check, not an oracle benchmark or mSUN score.
It downloads the upstream model weights and performs three real sampling calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from pymatgen.core import Composition

from made.agents.base import Plan
from made.agents.m2_tool_routing import CheckpointedChemeleonGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output already contains evidence; choose a new directory")
    args.output.mkdir(parents=True, exist_ok=True)
    plan = Plan(compositions=[Composition("Li2O")], num_candidates=1)
    context = {"elements": ["Li", "O"], "m1_queries_remaining": 20}
    first = CheckpointedChemeleonGenerator(
        seed=args.seed, task="csp", batch_size=1, device="cpu"
    )
    random.seed(123)
    np.random.seed(123)
    torch.manual_seed(123)
    python_rng = random.getstate()
    numpy_rng = np.random.get_state()
    torch_rng = torch.get_rng_state().clone()
    started = time.monotonic()
    initial = first.generate(plan, context)
    saved = json.loads(json.dumps(first.get_state(), allow_nan=False))
    (args.output / "generator_checkpoint.json").write_text(json.dumps(saved, indent=2))
    expected = first.generate(plan, context)
    resumed = CheckpointedChemeleonGenerator(
        seed=args.seed, task="csp", batch_size=1, device="cpu"
    )
    resumed.load_state(saved)
    actual = resumed.generate(plan, context)
    structures = {
        name: [structure.as_dict() for structure in values]
        for name, values in (
            ("initial", initial),
            ("expected", expected),
            ("resumed", actual),
        )
    }
    structures_match = structures["expected"] == structures["resumed"]
    state_matches = first.get_state() == resumed.get_state()
    current_numpy_rng = np.random.get_state()
    streams_preserved = (
        python_rng == random.getstate()
        and numpy_rng[0] == current_numpy_rng[0]
        and np.array_equal(numpy_rng[1], current_numpy_rng[1])
        and numpy_rng[2:] == current_numpy_rng[2:]
        and torch.equal(torch_rng, torch.get_rng_state())
    )
    report = {
        "kind": "real_chemeleon_checkpoint_integration",
        "benchmark_score": False,
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "seed": args.seed,
        "device": "cpu",
        "torch_version": torch.__version__,
        "platform": platform.platform(),
        "model_class": type(first.dm).__name__,
        "actual_sampling_calls": 3,
        "samples_per_call": [len(initial), len(expected), len(actual)],
        "structure_continuation_equal": structures_match,
        "checkpoint_state_equal": state_matches,
        "external_random_streams_preserved": streams_preserved,
        "wall_time_seconds": round(time.monotonic() - started, 3),
        "passed": structures_match
        and state_matches
        and streams_preserved
        and len(initial) == len(expected) == len(actual) == 1,
    }
    for name, values in structures.items():
        encoded = json.dumps(values, sort_keys=True, allow_nan=False)
        (args.output / f"{name}_structures.json").write_text(encoded)
        report[f"{name}_sha256"] = hashlib.sha256(encoded.encode()).hexdigest()
    (args.output / "verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit("Actual Chemeleon checkpoint continuation failed")


if __name__ == "__main__":
    main()
