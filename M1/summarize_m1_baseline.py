"""Summarize completed M1 baseline development runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "MADE/results/protocol_v1/m1_baseline/dev"
OUTPUT = ROOT / "m1_baseline_dev_summary.csv"
SYSTEMS = ["Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm"]
SEEDS = [17, 29, 43]


def latest_completed(system: str, seed: int) -> Path:
    attempts = sorted((RESULTS / system / f"seed_{seed}").glob("attempt_*"))
    for path in reversed(attempts):
        metadata = path / "run_metadata.json"
        if metadata.is_file() and json.loads(metadata.read_text()).get("status") == "completed":
            return path
    raise FileNotFoundError(f"No completed run for {system} seed {seed}")


def main() -> None:
    fields = ["system", "seed", "queries", "msun_at_20", "msun_fraction", "audc", "wall_time_seconds", "known_cost_usd", "result_dir"]
    rows = []
    for system in SYSTEMS:
        for seed in SEEDS:
            path = latest_completed(system, seed)
            metadata = json.loads((path / "run_metadata.json").read_text())
            summary = json.loads((path / "summary/summary.json").read_text())["summary"]
            rows.append({
                "system": system,
                "seed": seed,
                "queries": metadata["cost"]["oracle"]["queries"],
                "msun_at_20": summary["final/novelty_stable_unique_novel_count"]["mean"],
                "msun_fraction": summary["final/novelty_stable_unique_novel_fraction"]["mean"],
                "audc": summary["final/discovery_curve_area_under_discovery_curve"]["mean"],
                "wall_time_seconds": metadata["wall_time_seconds"],
                "known_cost_usd": metadata["cost"]["total_known_cost_usd"],
                "result_dir": str(path.relative_to(ROOT)),
            })
    with OUTPUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
