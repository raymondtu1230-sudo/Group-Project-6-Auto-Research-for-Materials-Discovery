"""Validate completeness, query counts, and data consistency for protocol v1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

M1_DIR = Path(__file__).resolve().parent
MADE_DIR = M1_DIR / "MADE"
PROTOCOL = yaml.safe_load((M1_DIR / "protocol/protocol_v1.yaml").read_text())


def canonical_hash(entries: list[dict[str, Any]]) -> str:
    serialized = [
        json.dumps(entry, sort_keys=True, separators=(",", ":")) for entry in entries
    ]
    canonical = "\n".join(sorted(serialized)).encode()
    return hashlib.sha256(canonical).hexdigest()


def expected_methods(split: str) -> list[str]:
    required = PROTOCOL["methods"]["required"]
    ablations = PROTOCOL["methods"]["ablations"]
    return required + ablations if split == "dev" else required


def validate(split: str) -> list[str]:
    errors: list[str] = []
    systems = json.loads((M1_DIR / f"protocol/{split}_systems.json").read_text())
    seeds = PROTOCOL["repeats"]["seeds"]
    budget = int(PROTOCOL["environment"]["query_budget"])
    data_hashes: dict[str, set[str]] = {}

    for system_elements in systems:
        system = "-".join(system_elements)
        for method in expected_methods(split):
            for seed in seeds:
                seed_dir = (
                    MADE_DIR
                    / "results/protocol_v1"
                    / method
                    / split
                    / system
                    / f"seed_{seed}"
                )
                attempts = (
                    sorted(
                        seed_dir.glob("attempt_*"),
                        key=lambda path: int(path.name.removeprefix("attempt_")),
                    )
                    if seed_dir.is_dir()
                    else []
                )
                run_dir = attempts[-1] if attempts else seed_dir / "attempt_01"
                metadata_path = run_dir / "run_metadata.json"
                trajectory_path = run_dir / "trajectories/episode_000.json"
                summary_path = run_dir / "summary/summary.json"
                if not all(
                    path.is_file()
                    for path in (metadata_path, trajectory_path, summary_path)
                ):
                    errors.append(
                        f"missing or incomplete latest attempt: {method}/{split}/{system}/seed_{seed}"
                    )
                    continue

                metadata = json.loads(metadata_path.read_text())
                if metadata.get("status") != "completed":
                    errors.append(
                        f"run not marked complete: {method}/{split}/{system}/seed_{seed}"
                    )

                trajectory = json.loads(trajectory_path.read_text())
                queries = trajectory.get("metrics", {}).get("final/queries_used")
                if queries != budget:
                    errors.append(
                        f"wrong query count ({queries}) for {method}/{split}/{system}/seed_{seed}; expected {budget}"
                    )
                ground_truth = trajectory.get("phase_diagram_gt")
                if not isinstance(ground_truth, list):
                    errors.append(
                        f"ground-truth snapshot missing: {method}/{split}/{system}/seed_{seed}"
                    )
                else:
                    data_hashes.setdefault(system, set()).add(
                        canonical_hash(ground_truth)
                    )

                summary = json.loads(summary_path.read_text())
                if summary.get("episodes") != 1:
                    errors.append(
                        f"expected exactly one episode: {method}/{split}/{system}/seed_{seed}"
                    )

    for system, hashes in data_hashes.items():
        if len(hashes) != 1:
            errors.append(f"ground-truth snapshot differs across runs for {system}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "check"), required=True)
    args = parser.parse_args()
    errors = validate(args.split)
    if errors:
        raise SystemExit("Protocol validation failed:\n- " + "\n- ".join(errors))
    print(
        f"Protocol v1 {args.split} results passed completeness and consistency checks."
    )


if __name__ == "__main__":
    main()
