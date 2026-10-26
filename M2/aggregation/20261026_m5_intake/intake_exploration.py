"""Incremental intake of real M5 records without inventing missing evidence.

Strict M2 evaluation is preserved separately from endpoint-only analysis.
The prior 144-run accepted report is reused unchanged. No model or oracle runs.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import statistics
import sys

import numpy as np
import yaml

SNAPSHOT = "a27634d9edbf231d0c034273fa9f977f9d5e799e"
ACCEPTED = "canonical_accepted_prior_144"
PENDING = "endpoint_verified_resolved_configuration_and_package_pending"
METHOD = "exploration_off"
BASELINES = ("random_generator_baseline", "chemeleon_generative_baseline")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def rows(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def exact_modules(snapshot: Path):
    helper = snapshot / "M2/aggregation/20261026_m3_complete/aggregate_handoffs.py"
    spec = importlib.util.spec_from_file_location("accepted_m2_helper", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    evaluator, provenance = module.exact_evaluator(snapshot)
    curve_source = snapshot / "M1/package_reference_evidence.py"
    node = next(n for n in ast.parse(curve_source.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == "curve_from_trajectory")
    scope = {"Path": Path, "json": json, "math": math}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(curve_source), "exec"), scope)
    provenance.update({
        "prior_helper_sha256": sha(helper),
        "official_curve_source": "M1/package_reference_evidence.py",
        "official_curve_source_sha256": sha(curve_source),
        "official_curve_function_ast_sha256": hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(),
        "curve_function_formula_modifications": 0,
    })
    return evaluator, scope["curve_from_trajectory"], provenance


def method_summary(records: list[dict], systems: list[str], seeds: list[int]) -> dict:
    index = {(r["system"], r["seed"]): r for r in records}
    assert set(index) == {(s, seed) for s in systems for seed in seeds}
    result = {"method": METHOD, "split": "dev", "runs_available": 18,
              "runs_expected": 18, "systems_expected": 6, "seeds_expected": 3,
              "complete_method_sweep": True, "canonical_acceptance_complete": False,
              "acceptance_class": PENDING,
              "aggregation": "equal_weight_system_mean_per_seed_then_seed_mean_and_sample_sd"}
    for key in ("mSUN_at_B", "AUDC", "wall_time_seconds", "known_cost_usd",
                "AF_vs_random", "EF_vs_random", "AF_vs_chemeleon", "EF_vs_chemeleon"):
        per_seed = []
        for seed in seeds:
            values = [index[(s, seed)].get(key) for s in systems]
            if all(isinstance(x, (int, float)) and math.isfinite(x) for x in values):
                per_seed.append(statistics.mean(values))
        result[key + "_seed_n"] = len(per_seed)
        result[key + "_mean"] = statistics.mean(per_seed) if len(per_seed) == len(seeds) else None
        result[key + "_std"] = statistics.stdev(per_seed) if len(per_seed) == len(seeds) else None
    result.update({"scientific_profile": "intended_frozen_full_single_switch_exploration_ablation_configuration_unverified",
                   "causal_comparator": "m1_full_package_pending"})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for p in (args.work, args.output):
        assert "M2" in p.resolve().parts
        if p.exists() and any(p.iterdir()):
            raise SystemExit(f"Refusing to overwrite populated directory: {p}")
        p.mkdir(parents=True, exist_ok=True)
    snapshot = args.snapshot.resolve()
    os.environ["MPLCONFIGDIR"] = str(args.work.resolve() / "matplotlib_cache")
    ev, official_curve, provenance = exact_modules(snapshot)
    prior = snapshot / "M2/aggregation/20261026_m3_complete/results"
    prior_manifest = read(prior / "output_manifest.json")
    for name, entry in prior_manifest.items():
        assert (prior / name).stat().st_size == entry["bytes"] and sha(prior / name) == entry["sha256"]
    prior_validation = read(prior / "aggregation_validation.json")
    assert prior_validation["accepted_runs"] == 144 and prior_validation["m2_evaluator_issues"] == []
    prior_records = rows(prior / "per_run_with_baseline_comparisons.csv")
    prior_index = {(r["method"], r["system"], int(r["seed"])): r for r in prior_records}
    prior_receipts = {(r["method"], r["system"], r["seed"]): r for r in read(prior / "input_receipts.json")}
    assert len(prior_index) == 144
    protocol = yaml.safe_load((snapshot / "M1/protocol/protocol_v1.yaml").read_text())
    systems = ["-".join(s) for s in read(snapshot / "M1/protocol/dev_systems.json")]
    seeds = protocol["repeats"]["seeds"]
    root = snapshot / "M1/MADE/results/protocol_v1/exploration_off/dev"
    metadata_paths = sorted(root.rglob("run_metadata.json"))
    assert len(metadata_paths) == 18
    strict_output = args.output / "strict_m2_evaluator_m5_only"
    sys.argv = [str(snapshot / "M2/evaluate.py"), "--results-root", str(root),
                "--output", str(strict_output), "--split", "dev"]
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
        try:
            ev.main()
        except SystemExit as error:
            strict_exit = str(error)
        else:
            strict_exit = "0"
    (args.output / "strict_m2_evaluator_stdout.log").write_text(stdout.getvalue() + strict_exit + "\n")
    strict = read(strict_output / "validation.json")
    assert strict["validated_runs"] == 0 and len(strict["issues"]) == 18
    assert all(x["kind"] == "incomplete_or_invalid_run" and "resolved_config.yaml" in x["error"] for x in strict["issues"])
    baseline_curves = {}
    curve_root = snapshot / "M2/verification/preserved-40204426478/report/recorded_curve_analysis"
    for baseline in BASELINES:
        for p in (curve_root / baseline).rglob("reevaluated_curve.json"):
            d = read(p)
            key = (baseline, d["system"], d["seed"])
            assert d["accepted"] and d["original_endpoint_matches"]
            assert d["original_trajectory_sha256"] == prior_receipts[key]["original_trajectory_sha256"]
            assert d["canonical_material_reference_sha256"] == prior_receipts[key]["canonical_material_reference_sha256"]
            history = d["reevaluated_metrics_history"]
            assert history[-1][ev.MSUN] == float(prior_index[key]["mSUN_at_B"])
            assert ev.DiscoveryCurveMetrics.area_under_discovery_curve(history, metric_key=ev.CURVE) == float(prior_index[key]["AUDC"])
            baseline_curves[key] = history
    assert len(baseline_curves) == 36
    records, receipts, paired, curve_points, cost_rows = [], [], [], [], []
    seen = set()
    for metadata_path in metadata_paths:
        origin, meta = metadata_path.parent, read(metadata_path)
        system, seed = "-".join(meta["system"]), meta["seed"]
        assert (system, seed) not in seen
        seen.add((system, seed))
        assert meta["method"] == METHOD and meta["split"] == "dev" and meta["status"] == "completed"
        assert meta["query_budget"] == 20 and meta["episodes"] == 1 and meta["protocol_settings"] == protocol
        command_flags = [x for x in meta["command"] if x.startswith("agent.enable_")]
        assert set(command_flags) == {"agent.enable_planning=true", "agent.enable_memory=true",
            "agent.enable_reflection=true", "agent.enable_exploration=false", "agent.enable_tool_routing=true"}
        hash_checks = []
        assert len(meta["m1_input_sha256"]) == 74
        for relative, expected in meta["m1_input_sha256"].items():
            source = snapshot / "M1" / relative.replace("\\", "/")
            data = source.read_bytes().replace(b"\r\n", b"\n")
            matches = expected in {hashlib.sha256(data).hexdigest(), hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()}
            assert matches, (system, seed, relative)
            hash_checks.append(relative)
        payload = read(origin / "trajectories/episode_000.json")
        summary = read(origin / "summary/summary.json")
        assert summary["episodes"] == 1 and len(payload["trajectory"]) == 20
        assert payload["metrics"]["final/queries_used"] == 20
        history_record = official_curve(origin)
        history = history_record["metrics_history"]
        derived = args.output / "derived_endpoint_analysis" / system / f"seed_{seed}" / "reconstructed_curve.json"
        history_record.update({"acceptance_class": PENDING, "strict_canonical_accepted": False,
            "source_trajectory_sha256": sha(origin / "trajectories/episode_000.json"),
            "actual_resolved_configuration_available": False,
            "note": "Separate trajectory reconstruction; no original checkpoint or actual resolved configuration recovered."})
        save(derived, history_record)
        reference_hash = ev.snapshot_hash(payload["phase_diagram_gt"])
        full_candidates = [p.parent for p in (snapshot / "M1/MADE/results/protocol_v1/m1_full/dev" / system / f"seed_{seed}").rglob("run_metadata.json") if read(p).get("status") == "completed"]
        full_path = max(full_candidates, key=lambda p: read(p / "run_metadata.json")["attempt"])
        full = ev.load_run(full_path)
        key = ("m1_full", system, seed)
        assert sha(full_path / "run_metadata.json") == prior_receipts[key]["original_metadata_sha256"]
        assert sha(full_path / "trajectories/episode_000.json") == prior_receipts[key]["original_trajectory_sha256"]
        assert full.reference_hash == reference_hash
        msun = ev.finite(payload["metrics"][f"final/{ev.MSUN}"], "mSUN")
        audc = ev.finite(payload["metrics"]["final/discovery_curve_area_under_discovery_curve"], "AUDC")
        assert history[-1][ev.MSUN] == msun and ev.DiscoveryCurveMetrics.area_under_discovery_curve(history, metric_key=ev.CURVE) == audc
        cost = meta.get("cost", {})
        row = {"method": METHOD, "split": "dev", "system": system, "seed": seed,
            "attempt": meta["attempt"], "B": 20, "mSUN_at_B": msun, "AUDC": audc,
            "oracle_queries": 20, "wall_time_seconds": meta.get("wall_time_seconds"),
            "known_cost_usd": cost.get("total_known_cost_usd"), "cost_status": cost.get("total_cost_status"),
            "llm_input_tokens": cost.get("llm", {}).get("input_tokens"),
            "llm_output_tokens": cost.get("llm", {}).get("output_tokens"),
            "machine": meta.get("machine"), "processor": meta.get("processor"),
            "actual_recorded_revision": meta.get("made_upstream_commit"),
            "acceptance_class": PENDING, "canonical_accepted": False,
            "scientific_profile": "intended_full_single_switch_exploration_configuration_unverified",
            "causal_comparator": "m1_full_package_pending", "original_source": str(origin),
            "history_source": "M1_curve_from_trajectory_reconstruction_endpoint_checked"}
        for baseline, short in zip(BASELINES, ("random", "chemeleon"), strict=True):
            baseline_history = baseline_curves[(baseline, system, seed)]
            row[f"AF_vs_{short}"] = ev.DiscoveryCurveMetrics.acceleration_factor(history, baseline_history, metric_key=ev.CURVE)
            row[f"EF_vs_{short}"] = ev.DiscoveryCurveMetrics.enhancement_factor(history, baseline_history, metric_key=ev.CURVE)
            row[f"comparison_{short}"] = "provisional_trajectory_derived_curve_package_pending"
        records.append(row)
        paired.append({"method": METHOD, "system": system, "seed": seed, "acceptance_class": PENDING,
            "full_attempt": full.metadata["attempt"], "off_attempt": meta["attempt"],
            "full_mSUN_at_20": full.row["mSUN_at_B"], "off_mSUN_at_20": msun,
            "full_AUDC": full.row["AUDC"], "off_AUDC": audc,
            "delta_mSUN_full_minus_off": full.row["mSUN_at_B"] - msun,
            "delta_AUDC_full_minus_off": full.row["AUDC"] - audc,
            "AF_off_vs_full": ev.DiscoveryCurveMetrics.acceleration_factor(history, full.history, metric_key=ev.CURVE),
            "EF_off_vs_full": ev.DiscoveryCurveMetrics.enhancement_factor(history, full.history, metric_key=ev.CURVE)})
        curve_points.extend({"method": METHOD, "system": system, "seed": seed,
            "queries_used": point["queries_used"], "mSUN": point[ev.MSUN], "stable_discoveries": point[ev.CURVE],
            "AUDC_to_query": point["discovery_curve_area_under_discovery_curve"], "acceptance_class": PENDING} for point in history)
        cost_rows.append({key: row.get(key) for key in ("method", "system", "seed", "wall_time_seconds", "known_cost_usd", "cost_status", "llm_input_tokens", "llm_output_tokens", "machine", "processor", "acceptance_class", "original_source")})
        files = [str(p.relative_to(origin)) for p in origin.rglob("*") if p.is_file()]
        assert "resolved_config.yaml" not in files and "m2_metrics_history.json" not in files
        receipts.append({"method": METHOD, "system": system, "seed": seed, "source": str(origin),
            "original_files": {f: {"bytes": (origin / f).stat().st_size, "sha256": sha(origin / f)} for f in files},
            "recorded_revision": meta.get("made_upstream_commit"), "recorded_command_flags": command_flags,
            "source_file_hash_checks": len(hash_checks), "canonical_material_reference_sha256": reference_hash,
            "endpoint_audit_passed": True, "strict_canonical_accepted": False,
            "missing_evidence": ["resolved_config.yaml", "raw_Hydra_configuration", "original_per_query_metrics_history", "component_logs"],
            "derived_history_path": str(derived), "derived_history_sha256": sha(derived)})
    assert seen == {(s, seed) for s in systems for seed in seeds}
    method = method_summary(records, systems, seeds)
    existing_summaries = rows(prior / "per_method_summary.csv")
    for row in existing_summaries:
        row.update({"acceptance_class": ACCEPTED, "canonical_acceptance_complete": True})
    ev.write_csv(args.output / "nine_method_summary_with_acceptance.csv", [*existing_summaries, method])
    existing_records = [{**r, "acceptance_class": ACCEPTED, "canonical_accepted": True} for r in prior_records]
    ev.write_csv(args.output / "combined_162_endpoint_rows_with_acceptance.csv", [*existing_records, *records])
    ev.write_csv(args.output / "m5_endpoint_only_per_run.csv", records)
    ev.write_csv(args.output / "m5_provisional_full_pairs.csv", paired)
    ev.write_csv(args.output / "m5_derived_per_query_curves.csv", curve_points)
    ev.write_csv(args.output / "m5_per_run_costs.csv", cost_rows)
    effect = {"method": METHOD, "comparator": "m1_full", "acceptance_class": PENDING, "matched_endpoint_pairs": 18}
    for key in ("delta_mSUN_full_minus_off", "delta_AUDC_full_minus_off", "AF_off_vs_full", "EF_off_vs_full"):
        means = [statistics.mean(r[key] for r in paired if r["seed"] == seed) for seed in seeds]
        effect[key + "_mean"], effect[key + "_std"] = statistics.mean(means), statistics.stdev(means)
    for metric in ("mSUN", "AUDC"):
        key = f"delta_{metric}_full_minus_off"
        effect[f"full_{metric}_better_pairs"] = sum(r[key] > 0 for r in paired)
        effect[f"full_{metric}_equal_pairs"] = sum(r[key] == 0 for r in paired)
        effect[f"full_{metric}_worse_pairs"] = sum(r[key] < 0 for r in paired)
    save(args.output / "m5_provisional_effect_summary.json", effect)
    save(args.output / "m5_endpoint_evidence_receipts.json", receipts)
    save(args.output / "canonical_144_carryover.json", {
        "source_report": "M2/aggregation/20261026_m3_complete/results",
        "source_manifest_sha256": sha(prior / "output_manifest.json"), "source_manifest_entries_verified": len(prior_manifest),
        "canonical_accepted_runs": 144, "source_validation_sha256": sha(prior / "aggregation_validation.json"),
        "recomputed_old_scientific_runs": 0, "old_report_modified": False})
    save(args.output / "acceptance_validation.json", {
        "canonical_accepted_runs": 144, "new_m5_strict_accepted_runs": 0,
        "new_m5_strict_rejections": 18, "new_m5_endpoint_only_verified_runs": 18,
        "new_m5_derived_curve_points": 360, "new_m5_provisional_baseline_comparisons": 36,
        "new_m5_provisional_full_comparisons": 18, "total_rows_with_acceptance_labels": 162,
        "all_162_canonical_accepted": False, "all_group_packages_complete": False,
        "pending_item": "M5_original_resolved_configuration_and_complete_evidence_package",
        "actual_resolved_configurations_fabricated": 0, "original_files_modified": 0,
        "new_scientific_runs": 0, "new_oracle_queries": 0})
    save(args.output / "evaluation_provenance.json", {"source_snapshot_commit": SNAPSHOT,
        "script_sha256": sha(Path(__file__)), "analysis_scope": "strict_rejection_plus_separate_endpoint_only_provisional_analysis",
        "canonical_144_reused_unchanged": True, **provenance})
    # Incrementally plot accepted aggregate curves plus the explicitly pending arm.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    chart = rows(prior / "aggregate_discovery_curve_data.csv")
    new_values = np.array([[0, *[r["stable_discoveries"] for r in curve_points if r["system"] == system and r["seed"] == seed]] for seed in seeds for system in systems])
    seed_values = new_values.reshape(3, 6, 21).mean(axis=1)
    mean, sd = seed_values.mean(axis=0), seed_values.std(axis=0, ddof=1)
    chart.extend({"method": METHOD, "queries": q, "mean": float(mean[q]), "sample_sd_across_seed_means": float(sd[q]), "acceptance_class": PENDING} for q in range(21))
    for r in chart:
        r.setdefault("acceptance_class", ACCEPTED)
    ev.write_csv(args.output / "nine_method_aggregate_curve_data.csv", chart)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for name in sorted({r["method"] for r in chart}):
        group = sorted([r for r in chart if r["method"] == name], key=lambda r: int(r["queries"]))
        x, y, errors = [int(r["queries"]) for r in group], np.array([float(r["mean"]) for r in group]), np.array([float(r["sample_sd_across_seed_means"]) for r in group])
        ax = axes[1 if name.startswith("m3_") else 0]
        ax.plot(x, y, linestyle="--" if name == METHOD else "-", label=name + (" [package pending]" if name == METHOD else ""))
        ax.fill_between(x, y-errors, y+errors, alpha=.1)
    axes[0].set_title("Full study: exploration OFF endpoint audit only")
    axes[1].set_title("Validated M3 component study: exploration/routing OFF")
    for ax in axes:
        ax.set(xlabel="Oracle queries", ylabel="Stable discovery count (official AUDC source)")
        ax.grid(alpha=.2)
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(args.output / "discovery_curves_with_pending_m5.png", dpi=180)
    fig.savefig(args.output / "discovery_curves_with_pending_m5.svg")
    plt.close(fig)
    manifest = {str(p.relative_to(args.output)): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(args.output.rglob("*")) if p.is_file()}
    save(args.output / "output_manifest.json", manifest)
    print(json.dumps({"canonical_accepted": 144, "new_m5_strict_accepted": 0,
        "new_m5_endpoint_only_verified": 18, "m5_mSUN": method["mSUN_at_B_mean"],
        "m5_AUDC": method["AUDC_mean"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
