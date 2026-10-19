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
    digest,
    rng_state,
)
from made.agents.base import Plan  # noqa: E402
from made.agents.generators.chemeleon import ChemeleonGenerator  # noqa: E402


def runner_checks(interrupted: dict, resumed: dict, jobs: list[dict]) -> dict:
    """Use recorded GitHub runner IDs; hostnames are not unique runner IDs."""
    before = [j for j in jobs if j.get("runner_name") == interrupted.get("name")]
    after = [j for j in jobs if j.get("runner_name") == resumed.get("name")]
    found = len(before) == len(after) == 1
    return {
        "runner_records_match_jobs": found,
        "different_runner_ids": bool(
            found
            and before[0].get("runner_id")
            and after[0].get("runner_id")
            and before[0]["runner_id"] != after[0]["runner_id"]
        ),
        "different_job_ids": bool(
            found
            and before[0].get("id")
            and after[0].get("id")
            and before[0]["id"] != after[0]["id"]
        ),
    }


def sample_fingerprints(directory: Path) -> list[dict]:
    result = []
    for path in sorted(directory.glob("batch_*.json")):
        envelope = json.loads(path.read_text())
        payload = envelope["payload"]
        if digest(payload) != envelope["sha256"]:
            raise ValueError("Evidence batch checksum differs")
        result.append({
            "batch": path.name,
            "atoms_sha256": hashlib.sha256(
                payload["ase_atoms_json"].encode()
            ).hexdigest(),
            "identity_sha256": payload["identity_sha256"],
            "rng_before_sha256": digest(payload["rng_before"]),
            "rng_after_sha256": digest(payload["rng_after"]),
        })
    return result


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
    parser.add_argument("--runner-jobs", type=Path)
    args = parser.parse_args()
    if args.batch_size < 1 or args.num_candidates != 2 * args.batch_size:
        parser.error("Recovery check requires exactly two equal positive batches")
    args.output.mkdir(parents=True, exist_ok=True)
    if args.mode == "compare":
        expected = json.loads((args.output / "continuous.json").read_text())
        actual = json.loads((args.output / "resume.json").read_text())
        interrupted = json.loads((args.output / "interrupt.json").read_text())
        checks = {
            "diffusion_steps_equal": expected["diffusion_steps"]
            == actual["diffusion_steps"]
            == 256,
            "exact_generated_atoms_and_batch_rng": expected["sample_fingerprints"]
            == actual["sample_fingerprints"]
            and len(actual["sample_fingerprints"]) == 2,
            "exact_ordered_cif_files": expected["cif_manifest"]
            == actual["cif_manifest"]
            and len(actual["cif_manifest"]) == args.num_candidates,
            "rng_equal": expected["rng"] == actual["rng"],
            "first_batch_preserved": interrupted["new_batches"] == 1,
            "completed_batch_not_sampled_twice": actual["replayed_batches"] == 1
            and actual["new_batches"] == 1,
            "candidate_count": len(actual["structures"]) == args.num_candidates,
            "reference_candidate_count": len(expected["structures"] or [])
            == args.num_candidates,
            "reference_generated_all_batches": expected["new_batches"] == 2
            and expected["replayed_batches"] == 0,
            "interrupted_before_completion": interrupted["structures"] is None,
            "fixture_equal": expected["fixture"]
            == actual["fixture"]
            == interrupted["fixture"],
            "cache_source_equal": expected["cache_source_sha256"]
            == actual["cache_source_sha256"]
            == interrupted["cache_source_sha256"],
            "saved_batch_bytes_preserved": interrupted["first_batch_sha256"]
            == actual["first_batch_sha256"],
        }
        if args.require_cross_runner:
            if not args.runner_jobs:
                parser.error("Cross-runner evidence requires GitHub job metadata")
            jobs = json.loads(args.runner_jobs.read_text())["jobs"]
            checks.update(runner_checks(interrupted["runner"], actual["runner"], jobs))
        report = {
            "kind": "real_cross_process_chemeleon_batch_recovery",
            "benchmark_score": False,
            "fixture": actual["fixture"],
            "checks": checks,
            "passed": all(checks.values()),
            "diagnostics": {
                "structure_dicts_bitwise_equal": expected["structures"]
                == actual["structures"],
                "hostnames_differ": interrupted["runner"]["hostname"]
                != actual["runner"]["hostname"],
            },
            "comparison_basis": "Exact serialized generated ASE atoms, exact ordered CIF bytes, and exact batch/final RNG; no numeric rounding or tolerance. Redundant pymatgen float fields and hostnames remain diagnostics.",
            "scope": "Actual-model recovery fixture only; not a protocol score or complete protocol-pool validation.",
        }
        (args.output / "verification.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(json.dumps(report, indent=2))
        if not report["passed"]:
            raise SystemExit(1)
        return
    target = args.output / f"{args.mode}.json"
    if target.exists():
        raise ValueError("Keep previous evidence; use a fresh output directory")
    from chemeleon_dng.diffusion.diffusion_module import DiffusionModule

    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    fixture = {
        "formula": "Li2O",
        "batch_size": args.batch_size,
        "num_candidates": args.num_candidates,
        "seed": 17,
        "diffusion_steps": "unchanged model default (256)",
    }
    cif_directory = args.output / f"cifs-{args.mode}"
    generator = ChemeleonGenerator(
        task="csp", batch_size=args.batch_size, device="cpu",
        output_dir=str(cif_directory),
    )
    plan = Plan(compositions=[Composition("Li2O")], num_candidates=args.num_candidates)
    cache = BatchCache(
        args.output / ("continuous-cache" if args.mode == "continuous" else "cache"),
        {"fixture": fixture},
        1 if args.mode == "interrupt" else None,
    )
    result = None
    # Continuous mode records each original sample call without replay or pause.
    # The same exact sample data is retained for comparison with the resumed run.
    with cache.patch(DiffusionModule):
        try:
            result = generator.generate(plan, {})
        except GenerationPausedError:
            if args.mode != "interrupt":
                raise
    record = {
        "fixture": fixture,
        "diffusion_steps": generator.dm.num_timesteps,
        "runner": {"hostname": socket.gethostname(), "name": os.getenv("RUNNER_NAME")},
        "structures": [s.as_dict() for s in result] if result else None,
        "rng": rng_state(),
        "new_batches": cache.sampled,
        "replayed_batches": cache.replayed,
        "cache_source_sha256": hashlib.sha256(
            (REPO / "M2/generation_cache.py").read_bytes()
        ).hexdigest(),
        "sample_fingerprints": sample_fingerprints(cache.directory),
        "cif_manifest": [
            {
                "path": str(path.relative_to(cif_directory)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in sorted(cif_directory.rglob("*.cif"))
        ],
        "first_batch_sha256": hashlib.sha256(
            (args.output / "cache/batch_0000.json").read_bytes()
        ).hexdigest()
        if args.mode != "continuous"
        else None,
    }
    target.write_text(json.dumps(record, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
