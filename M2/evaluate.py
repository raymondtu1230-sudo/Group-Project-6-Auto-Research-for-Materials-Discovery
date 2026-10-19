"""Offline validation and reporting of completed, real MADE protocol runs.

Official evaluation history is never passed back to the agent. Missing runs,
missing costs and missing paired baselines remain explicit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from made.evaluation.metrics import DiscoveryCurveMetrics

M1_DIR = Path(__file__).resolve().parents[1] / "M1"
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
BASELINES = ("random_generator_baseline", "chemeleon_generative_baseline")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def snapshot_hash(entries: list[dict[str, Any]]) -> str:
    values = sorted(
        json.dumps(e, sort_keys=True, separators=(",", ":")) for e in entries
    )
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def finite(value: Any, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


@dataclass
class Run:
    path: Path
    metadata: dict[str, Any]
    history: list[dict[str, Any]]
    row: dict[str, Any]
    reference_hash: str


def load_run(path: Path) -> Run:
    metadata = read_json(path / "run_metadata.json")
    if metadata.get("status") != "completed":
        raise ValueError("Run is not marked completed")
    if (
        metadata.get("protocol_settings", {}).get("oracle", {}).get("name")
        != "ORBOracle"
    ):
        raise ValueError("Only real ORB protocol results belong in this scoreboard")
    budget = metadata["query_budget"]
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError("Invalid query budget")
    if (
        metadata["protocol_settings"].get("environment", {}).get("query_budget")
        != budget
    ):
        raise ValueError("Query budget differs from the recorded protocol")
    payload = read_json(path / "trajectories/episode_000.json")
    if read_json(path / "summary/summary.json").get("episodes") != 1:
        raise ValueError("Exactly one episode per system and seed is required")
    metrics = payload["metrics"]
    if (
        len(payload.get("trajectory", [])) != budget
        or metrics.get("final/queries_used") != budget
    ):
        raise ValueError("Trajectory and official query count must both equal B")
    record = read_json(path / "m2_metrics_history.json")
    history = record.get("metrics_history", [])
    if not record.get("complete_curve") or [
        x.get("queries_used") for x in history
    ] != list(range(1, budget + 1)):
        raise ValueError("Complete official per-query history is required")
    for point in history:
        for key in (MSUN, CURVE):
            if not 0 <= finite(point.get(key), key) <= point["queries_used"]:
                raise ValueError(f"Out-of-range {key}")
    msun = finite(metrics.get(f"final/{MSUN}"), "mSUN")
    audc = finite(
        metrics.get("final/discovery_curve_area_under_discovery_curve"), "AUDC"
    )
    if history[-1][MSUN] != msun:
        raise ValueError("Final mSUN differs from the official history")
    calculated = DiscoveryCurveMetrics.area_under_discovery_curve(
        history, metric_key=CURVE
    )
    if not math.isclose(audc, calculated, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("Official AUDC and recorded history disagree")
    reference = payload.get("phase_diagram_gt")
    if not isinstance(reference, list) or not reference:
        raise ValueError("Reference snapshot is required for data-revision consistency")
    cost = metadata.get("cost", {})
    if cost.get("oracle", {}).get("queries", budget) != budget:
        raise ValueError("Cost query count disagrees with trajectory")
    row = {
        "method": metadata["method"],
        "split": metadata["split"],
        "system": "-".join(metadata["system"]),
        "seed": metadata["seed"],
        "attempt": metadata.get("attempt", 1),
        "B": budget,
        "mSUN_at_B": msun,
        "AUDC": audc,
        "oracle_queries": budget,
        "wall_time_seconds": metadata.get("wall_time_seconds"),
        "known_cost_usd": cost.get("total_known_cost_usd"),
        "cost_status": cost.get("total_cost_status", "not_reported"),
        "llm_input_tokens": cost.get("llm", {}).get("input_tokens"),
        "llm_output_tokens": cost.get("llm", {}).get("output_tokens"),
        "machine": metadata.get("machine"),
        "processor": metadata.get("processor"),
        "source": str(path),
    }
    return Run(path, metadata, history, row, snapshot_hash(reference))


def unit_key(metadata: dict[str, Any]) -> tuple[str, str, str, int]:
    return (
        metadata["method"],
        metadata["split"],
        "-".join(metadata["system"]),
        int(metadata["seed"]),
    )


def collect(root: Path, split: str) -> tuple[list[Run], list[dict[str, Any]]]:
    latest: dict[tuple[str, str, str, int], tuple[int, Path]] = {}
    issues: list[dict[str, Any]] = []
    for path in sorted(root.rglob("run_metadata.json")):
        try:
            metadata = read_json(path)
            if metadata.get("split") != split:
                continue
            key, attempt = unit_key(metadata), int(metadata.get("attempt", 1))
            if key in latest:
                if latest[key][0] == attempt:
                    raise ValueError(
                        "Duplicate unit/attempt; deduplicate input explicitly"
                    )
                old = latest[key]
                issues.append(
                    {
                        "kind": "superseded_attempt",
                        "source": str(path.parent if attempt < old[0] else old[1]),
                    }
                )
            if key not in latest or attempt > latest[key][0]:
                latest[key] = (attempt, path.parent)
        except (ValueError, KeyError, TypeError) as error:
            issues.append(
                {"kind": "invalid_metadata", "source": str(path), "error": str(error)}
            )
    runs = []
    for _, path in latest.values():
        try:
            runs.append(load_run(path))
        except (ValueError, KeyError, TypeError, OSError) as error:
            issues.append(
                {
                    "kind": "incomplete_or_invalid_run",
                    "source": str(path),
                    "error": str(error),
                }
            )
    return runs, issues


def compare(runs: list[Run]) -> None:
    index = {unit_key(run.metadata): run for run in runs}
    references: dict[tuple[str, str], set[str]] = defaultdict(set)
    protocols = set()
    for run in runs:
        references[(run.row["split"], run.row["system"])].add(run.reference_hash)
        protocols.add(json.dumps(run.metadata["protocol_settings"], sort_keys=True))
    if len(protocols) > 1 or any(len(values) > 1 for values in references.values()):
        raise ValueError(
            "Protocol or material reference revision differs; stop aggregation"
        )
    for run in runs:
        for baseline_name, short in zip(
            BASELINES, ("random", "chemeleon"), strict=True
        ):
            baseline = index.get(
                (baseline_name, run.row["split"], run.row["system"], run.row["seed"])
            )
            run.row[f"AF_vs_{short}"] = None
            run.row[f"EF_vs_{short}"] = None
            run.row[f"comparison_{short}"] = "missing_paired_baseline"
            if baseline is not None:
                run.row[f"AF_vs_{short}"] = DiscoveryCurveMetrics.acceleration_factor(
                    run.history, baseline.history, metric_key=CURVE
                )
                run.row[f"EF_vs_{short}"] = DiscoveryCurveMetrics.enhancement_factor(
                    run.history, baseline.history, metric_key=CURVE
                )
                run.row[f"comparison_{short}"] = (
                    "official_zero_baseline_convention"
                    if baseline.history[-1][CURVE] == 0
                    else "paired_system_seed_budget"
                )


def summarize(runs: list[Run]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[Run]] = defaultdict(list)
    for run in runs:
        groups[(run.row["method"], run.row["split"], run.row["system"])].append(run)
    result = []
    for (method, split, system), group in sorted(groups.items()):
        row: dict[str, Any] = {
            "method": method,
            "split": split,
            "system": system,
            "n": len(group),
        }
        for field in (
            "mSUN_at_B",
            "AUDC",
            "wall_time_seconds",
            "known_cost_usd",
            "AF_vs_random",
            "EF_vs_random",
            "AF_vs_chemeleon",
            "EF_vs_chemeleon",
        ):
            values = [
                run.row[field]
                for run in group
                if isinstance(run.row.get(field), (int, float))
                and math.isfinite(run.row[field])
            ]
            row[f"{field}_n"] = len(values)
            row[f"{field}_mean"] = statistics.mean(values) if values else None
            row[f"{field}_std"] = statistics.stdev(values) if len(values) > 1 else None
        result.append(row)
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


def plot_curves(runs: list[Run], output: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    systems = sorted({run.row["system"] for run in runs})
    fig, axes = plt.subplots(
        len(systems), 2, figsize=(11, 3.5 * len(systems)), squeeze=False
    )
    for i, system in enumerate(systems):
        methods = sorted(
            {run.row["method"] for run in runs if run.row["system"] == system}
        )
        for method in methods:
            group = [
                run
                for run in runs
                if run.row["system"] == system and run.row["method"] == method
            ]
            for j, metric in enumerate((MSUN, CURVE)):
                values = np.array(
                    [[0, *[point[metric] for point in run.history]] for run in group],
                    dtype=float,
                )
                x, mean = np.arange(values.shape[1]), values.mean(axis=0)
                axes[i, j].plot(x, mean, label=f"{method} (n={len(group)})")
                if len(group) > 1:
                    sd = values.std(axis=0, ddof=1)
                    axes[i, j].fill_between(x, mean - sd, mean + sd, alpha=0.15)
                axes[i, j].set(
                    xlabel="Oracle queries",
                    ylabel="Official discovery count",
                    title=f"{system}: {'mSUN' if j == 0 else 'AUDC source curve'}",
                )
                axes[i, j].grid(alpha=0.2)
                axes[i, j].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(output / "discovery_curves.png", dpi=180)
    fig.savefig(output / "discovery_curves.svg")
    plt.close(fig)


def main() -> None:
    import yaml

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "check"), default="dev")
    parser.add_argument(
        "--allow-partial", action="store_true", help="Development review only"
    )
    args = parser.parse_args()
    runs, issues = collect(args.results_root, args.split)
    protocol = yaml.safe_load((M1_DIR / "protocol/protocol_v1.yaml").read_text())
    accepted = []
    for run in runs:
        if run.metadata["protocol_settings"] == protocol:
            accepted.append(run)
        else:
            issues.append(
                {
                    "kind": "protocol_mismatch",
                    "source": str(run.path),
                    "error": "Recorded settings differ from the current frozen protocol",
                }
            )
    runs = accepted
    systems = read_json(M1_DIR / f"protocol/{args.split}_systems.json")
    expected = {
        (method, args.split, "-".join(system), seed)
        for method in protocol["methods"]["required"]
        for system in systems
        for seed in protocol["repeats"]["seeds"]
    }
    missing = sorted(expected - {unit_key(run.metadata) for run in runs})
    args.output.mkdir(parents=True, exist_ok=True)
    audit = {
        "split": args.split,
        "validated_runs": len(runs),
        "missing_units": missing,
        "issues": issues,
        "final_comparison_complete": not missing
        and not any(x["kind"] != "superseded_attempt" for x in issues),
    }
    (args.output / "validation.json").write_text(json.dumps(audit, indent=2))
    if not runs:
        raise SystemExit("No complete real-material runs to score; see validation.json")
    compare(runs)
    write_csv(args.output / "per_run.csv", [run.row for run in runs])
    write_csv(args.output / "per_system_summary.csv", summarize(runs))
    plot_curves(runs, args.output)
    print(
        json.dumps(
            {
                "validated_runs": len(runs),
                "missing_units": len(missing),
                "output": str(args.output),
            }
        )
    )
    if not audit["final_comparison_complete"] and not args.allow_partial:
        raise SystemExit(
            "Final comparison is incomplete; partial outputs are for development only"
        )


if __name__ == "__main__":
    main()
