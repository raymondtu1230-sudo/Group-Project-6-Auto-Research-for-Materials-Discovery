"""Prepare a protocol-derived baseline matrix without starting experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "check", "hidden"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = REPO / "M1/protocol/protocol_v1.yaml"
    protocol = yaml.safe_load(protocol_path.read_text())
    systems_path = REPO / "M1/protocol" / f"{args.split}_systems.json"
    systems = json.loads(systems_path.read_text()) if systems_path.exists() else []
    seeds = protocol["repeats"]["seeds"]
    matrix = [
        {
            "method": "chemeleon_generative_baseline",
            "split": args.split,
            "system": "-".join(system),
            "seed": seed,
        }
        for system in systems
        for seed in seeds
    ]
    result = {
        "kind": "preparation_only_no_experiments_started",
        "split": args.split,
        "dispatch_enabled": False,
        "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "systems_sha256": (
            hashlib.sha256(systems_path.read_bytes()).hexdigest()
            if systems_path.exists()
            else None
        ),
        "query_budget": protocol["environment"]["query_budget"],
        "seeds": seeds,
        "unit_count": len(matrix),
        "matrix": {"include": matrix},
        "gates_before_check_dispatch": [
            "Confirm the arrangement with the colleague after their reply",
            "Verify safe Chemeleon recovery or an adequately long CPU host",
            "Verify one check unit before authorizing the remaining units",
            "Use distinct attempt IDs and retain raw outputs and stage costs",
        ],
        "hidden_status": (
            "Await M1 official hidden-split support and evaluation coordination"
            if args.split == "hidden"
            else "Not requested"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Prepared {len(matrix)} {args.split} units; dispatch remains disabled")


if __name__ == "__main__":
    main()
