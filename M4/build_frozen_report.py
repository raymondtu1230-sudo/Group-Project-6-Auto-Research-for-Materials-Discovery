"""Offline reporting from preserved trajectories. Never used by the agent."""

from __future__ import annotations
import argparse
import csv
import json
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "M2"))
from evaluate import CURVE, MSUN, load_run  # noqa: E402
from made.evaluation.metrics import DiscoveryCurveMetrics  # noqa: E402


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pairs = list(
        csv.DictReader(
            (
                ROOT / "M4/evidence/frozen-memory-ablation-20261026/paired_results.csv"
            ).open()
        )
    )
    all_runs, curves, costs, comparisons = {}, [], [], []
    for pair in pairs:
        key = (pair["system"], int(pair["seed"]))
        runs = {}
        for arm, column in [("ON", "reference"), ("OFF", "result")]:
            relative = Path(pair[column]).relative_to("M1/MADE/results/protocol_v1")
            path = args.results_root / relative
            run = load_run(path)
            runs[arm] = run
            m = run.metadata
            cost = m.get("cost", {})
            llm = cost.get("llm", {})
            costs.append(
                {
                    "system": key[0],
                    "seed": key[1],
                    "arm": arm,
                    "campaign_queries": m["query_budget"],
                    "wall_time_seconds": m.get("wall_time_seconds"),
                    "machine": m.get("machine"),
                    "platform": m.get("platform"),
                    "llm_calls": llm.get("calls"),
                    "input_tokens": llm.get("input_tokens"),
                    "output_tokens": llm.get("output_tokens"),
                    "llm_cost_usd": llm.get("cost_usd"),
                    "llm_cost_status": llm.get("cost_status"),
                    "known_cost_usd": cost.get("total_known_cost_usd"),
                    "total_cost_status": cost.get("total_cost_status"),
                    "initialization_oracle_calls": "not_instrumented",
                    "source": pair[column],
                }
            )
            for h in run.history:
                curves.append(
                    {
                        "system": key[0],
                        "seed": key[1],
                        "arm": arm,
                        "query": h["queries_used"],
                        "mSUN": h[MSUN],
                        "new_stable": h[CURVE],
                        "history_source": "M1 trajectory reconstruction"
                        if arm == "ON"
                        else "official checkpoint capture",
                    }
                )
        assert runs["ON"].reference_hash == runs["OFF"].reference_hash
        all_runs[key] = runs
        comparisons.append(
            {
                "system": key[0],
                "seed": key[1],
                "AF_OFF_vs_ON": DiscoveryCurveMetrics.acceleration_factor(
                    runs["OFF"].history, runs["ON"].history, metric_key=CURVE
                ),
                "EF_OFF_vs_ON": DiscoveryCurveMetrics.enhancement_factor(
                    runs["OFF"].history, runs["ON"].history, metric_key=CURVE
                ),
                "metric_key": CURVE,
                "reference_method": "m1_full",
                "proposal_method": "memory_off",
            }
        )
    write_csv(args.output / "per_query_curves.csv", curves)
    write_csv(args.output / "per_run_cost.csv", costs)
    write_csv(args.output / "paired_AF_EF_OFF_vs_ON.csv", comparisons)
    aggregate = []
    for arm in ["ON", "OFF"]:
        for query in range(1, 21):
            record = {"arm": arm, "query": query}
            for metric in ["mSUN", "new_stable"]:
                seed_means = [
                    statistics.mean(
                        r[metric]
                        for r in curves
                        if r["arm"] == arm and r["query"] == query and r["seed"] == seed
                    )
                    for seed in [17, 29, 43]
                ]
                record[metric + "_mean"] = statistics.mean(seed_means)
                record[metric + "_seed_sd"] = statistics.stdev(seed_means)
            aggregate.append(record)
    write_csv(args.output / "aggregate_curves.csv", aggregate)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.3), layout="constrained")
    for ax, metric, title in zip(
        axs,
        ["mSUN", "new_stable"],
        ["mSUN over the query budget", "Discovery curve used for AUDC"],
        strict=True,
    ):
        for arm, color in [("ON", "#164A72"), ("OFF", "#BA6434")]:
            rows = [r for r in aggregate if r["arm"] == arm]
            x = [r["query"] for r in rows]
            y = [r[metric + "_mean"] for r in rows]
            sd = [r[metric + "_seed_sd"] for r in rows]
            ax.plot(x, y, label="Memory " + arm, color=color, linewidth=2)
            ax.fill_between(
                x,
                [a - b for a, b in zip(y, sd)],
                [a + b for a, b in zip(y, sd)],
                color=color,
                alpha=0.12,
            )
        ax.set(
            title=title,
            xlabel="Completed campaign queries",
            ylabel="Mean count",
            xlim=(1, 20),
            ylim=(0, None),
        )
        ax.set_xticks([1, 5, 10, 15, 20])
        ax.grid(axis="y", alpha=0.2)
        ax.legend(frameon=False)
    fig.savefig(args.output / "discovery_curves.png", dpi=200)
    fig.savefig(args.output / "discovery_curves.svg")
    plt.close(fig)
    # Cases selected to show a gain, an adverse outcome and wasteful allocation.
    specs = [
        ("Co-Mg-Na", 29, "Positive endpoint difference"),
        ("Mg-Sn-Sr", 17, "Concentrated search with an adverse outcome"),
        ("Co-Mg-Na", 17, "Wasteful allocation and equal final mSUN"),
    ]
    case_rows = []
    for system, seed, title in specs:
        for arm, run in all_runs[(system, seed)].items():
            payload = json.loads(
                (run.path / "trajectories/episode_000.json").read_text()
            )
            decisions = [
                json.loads(s)
                for s in (run.path / "m5_decisions.jsonl").read_text().splitlines()
            ]
            memory_path = run.path / "m4_evidence.jsonl"
            online = (
                [json.loads(s) for s in memory_path.read_text().splitlines()]
                if memory_path.exists()
                else []
            )
            for index, t in enumerate(payload["trajectory"]):
                query = index + 1
                decision = decisions[index]
                assert decision["query_count"] == index
                case_rows.append(
                    {
                        "case": title,
                        "system": system,
                        "seed": seed,
                        "arm": arm,
                        "query": query,
                        "formula": t.get("reduced_formula"),
                        "stable": t.get("is_stable"),
                        "new": t.get("is_newly_discovered"),
                        "e_above_hull": t.get("e_above_hull"),
                        "mSUN": run.history[index][MSUN],
                        "stable_discoveries": run.history[index][CURVE],
                        "m5_mode": decision.get("mode"),
                        "m5_rationale": decision.get("rationale"),
                        "policy_incoming_compositions": json.dumps(
                            decision.get("incoming_compositions")
                        ),
                        "policy_outgoing_compositions": json.dumps(
                            decision.get("outgoing_compositions")
                        ),
                        "online_records_before_decision": sum(
                            r["query_count"] <= index for r in online
                        ),
                        "exact_ON_review_memory_ids": "not_retained"
                        if arm == "ON"
                        else "none_memory_disabled",
                    }
                )
    write_csv(args.output / "traced_cases.csv", case_rows)
    summary = {
        arm: {
            "runs": 18,
            "campaign_queries": sum(
                r["campaign_queries"] for r in costs if r["arm"] == arm
            ),
            "wall_time_total_seconds": sum(
                r["wall_time_seconds"] for r in costs if r["arm"] == arm
            ),
            "wall_time_mean_seconds": statistics.mean(
                r["wall_time_seconds"] for r in costs if r["arm"] == arm
            ),
            "machines": sorted({r["machine"] for r in costs if r["arm"] == arm}),
            "llm_usage": "not_reported",
            "all_oracle_evaluations": "not_instrumented_including_initialization",
        }
        for arm in ["ON", "OFF"]
    }
    (args.output / "cost_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
