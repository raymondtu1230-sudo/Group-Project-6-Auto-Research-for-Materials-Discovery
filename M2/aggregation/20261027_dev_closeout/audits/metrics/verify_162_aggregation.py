"""Independently audit final aggregation arithmetic, receipts and derivative views."""

from __future__ import annotations

import copy
import csv
import json
import math
from pathlib import Path
import statistics

import verify_m5_complete as source


OUTPUT = Path(__file__).resolve().parent
AGGREGATION = source.PROJECT / "M2/aggregation/20261027_dev_closeout"
RESULTS = AGGREGATION / "results"
SEEDS = (17, 29, 43)
NORMALIZED = "discovery_curve_area_under_discovery_curve_normalized"


def csvread(name):
    with (RESULTS / name).open() as stream:
        return list(csv.DictReader(stream))


def main():
    ev, reconstruct, provenance = source.exact_evaluator()
    errors = []

    def check(value, expected, label):
        if not math.isclose(float(value), float(expected), rel_tol=1e-12, abs_tol=1e-12):
            errors.append({"item": label, "aggregate": value, "independent": expected})

    receipts = source.read(RESULTS / "input_receipts.json")
    runs = {}
    for receipt in receipts:
        run = ev.load_run(Path(receipt["view"]))
        key = (run.row["method"], run.row["system"], run.row["seed"])
        if key in runs:
            errors.append({"duplicate_unit": key})
        runs[key] = run
        for folder_key in ("original_source", "view"):
            for name, receipt_key in (("run_metadata.json", "original_metadata_sha256"), ("trajectories/episode_000.json", "original_trajectory_sha256"), ("resolved_config.yaml", "original_resolved_config_sha256")):
                if source.sha(Path(receipt[folder_key]) / name) != receipt[receipt_key]:
                    errors.append({"receipt_hash_mismatch": key, "folder": folder_key, "file": name})
    if len(runs) != 162:
        errors.append({"expected_runs": 162, "actual": len(runs)})
    expected_methods = {"random_generator_baseline", "chemeleon_generative_baseline", "m1_full", "tool_routing_off", "memory_off", "exploration_off", "m3_full", "m3_planning_off", "m3_self_correction_off"}
    expected_keys = {(method, system, seed) for method in expected_methods for system in source.SYSTEMS for seed in SEEDS}
    if set(runs) != expected_keys or len(receipts) != 162:
        errors.append({"unit_grid_wrong": sorted(set(runs) ^ expected_keys), "receipt_count": len(receipts)})
    old_receipts = source.read(source.SNAPSHOT / "M2/aggregation/20261026_m3_complete/results/input_receipts.json")
    previous = {(r["method"], r["system"], r["seed"]): r for r in old_receipts}
    current = {(r["method"], r["system"], r["seed"]): r for r in receipts}
    for key, prior in previous.items():
        for field in ("original_metadata_sha256", "original_trajectory_sha256", "original_resolved_config_sha256"):
            if current[key][field] != prior[field]:
                errors.append({"previous_144_original_changed": key, "field": field})
    old_m5 = source.read(source.OLD / "audit_metrics/m5_metrics_independent_audit.json")
    for row in old_m5["per_run"]:
        key = (row["method"], row["system"], row["seed"])
        if row["method"] == "exploration_off":
            run = runs[key]
            check(run.row["mSUN_at_B"], row["mSUN"], f"old_M5_endpoint/{key}/mSUN")
            check(run.row["AUDC"], row["AUDC"], f"old_M5_endpoint/{key}/AUDC")
            if current[key]["original_metadata_sha256"] != row["run_metadata_sha256"] or current[key]["original_trajectory_sha256"] != row["trajectory_sha256"]:
                errors.append({"previous_M5_original_changed": key})
    # Recompute each direction from actual matched histories, not from old AF/EF CSVs.
    baseline_pairs = 0
    per_run_rows = csvread("per_run_with_baseline_comparisons.csv")
    if len(per_run_rows) != 162 or {(r["method"], r["system"], int(r["seed"])) for r in per_run_rows} != expected_keys:
        errors.append({"per_run_table_grid_wrong": len(per_run_rows)})
    for row in per_run_rows:
        key = (row["method"], row["system"], int(row["seed"]))
        run = runs[key]
        for field in ("mSUN_at_B", "AUDC", "wall_time_seconds", "known_cost_usd"):
            check(row[field], run.row[field], f"unit/{key}/{field}")
        for baseline, suffix in (("random_generator_baseline", "random"), ("chemeleon_generative_baseline", "chemeleon")):
            comparator = runs[(baseline, key[1], key[2])]
            for prefix, function in (("AF", ev.DiscoveryCurveMetrics.acceleration_factor), ("EF", ev.DiscoveryCurveMetrics.enhancement_factor)):
                value = float(function(run.history, comparator.history, metric_key=ev.CURVE))
                check(row[f"{prefix}_vs_{suffix}"], value, f"baseline/{key}/{prefix}/{baseline}")
                run.row[f"{prefix}_vs_{suffix}"] = value
            baseline_pairs += 1
    summary_fields = ("mSUN_at_B", "AUDC", "wall_time_seconds", "known_cost_usd", "AF_vs_random", "EF_vs_random", "AF_vs_chemeleon", "EF_vs_chemeleon")
    summary_checks = 0
    summaries = csvread("per_method_summary.csv")
    if len(summaries) != 9 or {s["method"] for s in summaries} != expected_methods:
        errors.append({"summary_method_grid_wrong": len(summaries)})
    for summary in summaries:
        method = summary["method"]
        for field in summary_fields:
            seed_means = [statistics.mean(run.row[field] for key, run in runs.items() if key[0] == method and key[2] == seed) for seed in SEEDS]
            check(summary[field + "_mean"], statistics.mean(seed_means), f"method/{method}/{field}/mean")
            check(summary[field + "_std"], statistics.stdev(seed_means), f"method/{method}/{field}/sample_SD")
            summary_checks += 2
    full_pairs = csvread("paired_full_system_ablations.csv")
    expected_full_keys = {(method, system, seed) for method in ("memory_off", "tool_routing_off", "exploration_off") for system in source.SYSTEMS for seed in SEEDS}
    if len(full_pairs) != 54 or {(p["method"], p["system"], int(p["seed"])) for p in full_pairs} != expected_full_keys:
        errors.append({"Full_pair_grid_wrong": len(full_pairs)})
    for row in full_pairs:
        key = (row["method"], row["system"], int(row["seed"]))
        off, full = runs[key], runs[("m1_full", key[1], key[2])]
        for label, expected in (("delta_mSUN_off_minus_full", off.row["mSUN_at_B"]-full.row["mSUN_at_B"]), ("delta_AUDC_off_minus_full", off.row["AUDC"]-full.row["AUDC"]), ("AF_off_vs_full", ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE)), ("EF_off_vs_full", ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE))):
            check(row[label], expected, f"Full_pair/{key}/{label}")
    m3_pairs = csvread("paired_m3_component_ablations.csv")
    expected_m3_keys = {(method, system, seed) for method in ("m3_planning_off", "m3_self_correction_off") for system in source.SYSTEMS for seed in SEEDS}
    if len(m3_pairs) != 36 or {(p["method"], p["system"], int(p["seed"])) for p in m3_pairs} != expected_m3_keys:
        errors.append({"M3_pair_grid_wrong": len(m3_pairs)})
    for row in m3_pairs:
        key = (row["method"], row["system"], int(row["seed"]))
        off, full = runs[key], runs[("m3_full", key[1], key[2])]
        for label, expected in (("delta_mSUN_full_minus_off", full.row["mSUN_at_B"]-off.row["mSUN_at_B"]), ("delta_AUDC_full_minus_off", full.row["AUDC"]-off.row["AUDC"]), ("AF_off_vs_m3_full", ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE)), ("EF_off_vs_m3_full", ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE))):
            check(row[label], expected, f"M3_pair/{key}/{label}")
    for row in csvread("m3_component_effect_summary.csv"):
        group = [p for p in m3_pairs if p["method"] == row["method"]]
        for field in ("delta_mSUN_full_minus_off", "delta_AUDC_full_minus_off", "AF_off_vs_m3_full", "EF_off_vs_m3_full"):
            values = [statistics.mean(float(p[field]) for p in group if int(p["seed"]) == seed) for seed in SEEDS]
            check(row[field+"_mean"], statistics.mean(values), f"M3_effect/{row['method']}/{field}/mean")
            check(row[field+"_std"], statistics.stdev(values), f"M3_effect/{row['method']}/{field}/sample_SD")
        for label, condition in (("full_mSUN_better_pairs", lambda x:x>0), ("full_mSUN_equal_pairs", lambda x:x==0), ("full_mSUN_worse_pairs", lambda x:x<0)):
            check(row[label], sum(condition(float(p["delta_mSUN_full_minus_off"])) for p in group), f"M3_effect/{row['method']}/{label}")
    # Verify all preserved original M5 histories and only auxiliary-field corrections.
    supplied_differences, correction_points = {}, 0
    strict_source_audit = source.read(OUTPUT / "m5_complete_strict_independent_audit.json")
    original_history_hashes = {(r["method"], r["system"], r["seed"]): r["saved_history_sha256"] for r in strict_source_audit["per_run"]}
    for key, run in runs.items():
        if key[0] != "exploration_off":
            continue
        receipt = current[key]
        original = Path(receipt["original_source"]) / "m2_metrics_history.json"
        submitted_copy = run.path / "as_submitted_metrics_history.json"
        if source.sha(original) != source.sha(submitted_copy) or source.sha(original) != receipt["as_submitted_history_sha256"]:
            errors.append({"as_submitted_history_preservation_failed": key})
        if source.sha(original) != original_history_hashes[key]:
            errors.append({"original_history_modified_since_strict_source_audit": key})
        durable = RESULTS / "m5_history_analysis_views" / key[1] / f"seed_{key[2]}"
        if source.sha(durable / "as_submitted_metrics_history.json") != source.sha(original):
            errors.append({"published_submitted_history_bytes_wrong": key})
        if source.sha(durable / "corrected_analysis_metrics_history.json") != source.sha(run.path / "m2_metrics_history.json"):
            errors.append({"published_corrected_history_bytes_wrong": key})
        before, after = source.read(original), source.read(run.path / "m2_metrics_history.json")
        reconstructed = reconstruct(Path(receipt["original_source"]))["metrics_history"]
        for query, (old, new, expected) in enumerate(zip(before["metrics_history"], after["metrics_history"], reconstructed, strict=True), start=1):
            prefix = after["metrics_history"][:query]
            official = float(ev.DiscoveryCurveMetrics.area_under_discovery_curve(prefix, metric_key=ev.CURVE, normalize=True))
            check(new[NORMALIZED], official, f"normalized_view/{key}/{query}")
            check(new[NORMALIZED], expected[NORMALIZED], f"normalized_M1_helper/{key}/{query}")
            if not math.isclose(old[NORMALIZED], official, rel_tol=1e-12, abs_tol=1e-12):
                supplied_differences[(key[1], key[2], query)] = (old[NORMALIZED], official, source.sha(original))
            old_core, new_core = copy.deepcopy(old), copy.deepcopy(new)
            old_core.pop(NORMALIZED, None)
            new_core.pop(NORMALIZED, None)
            if old_core != new_core:
                errors.append({"core_history_changed_in_view": key, "query": query})
            correction_points += 1
        for document in (before, after):
            for point in document["metrics_history"]:
                point.pop(NORMALIZED, None)
        if before != after:
            errors.append({"nonauxiliary_document_changed": key})
    differences = csvread("m5_normalized_AUDC_corrections.csv")
    found = set()
    for row in differences:
        key = (row["system"], int(row["seed"]), int(row["queries_used"]))
        found.add(key)
        expected = supplied_differences[key]
        check(row["as_submitted"], expected[0], f"difference_receipt/{key}/original")
        check(row["corrected_analysis_view_value"], expected[1], f"difference_receipt/{key}/corrected")
        if row["as_submitted_history_sha256"] != expected[2]:
            errors.append({"difference_receipt_original_hash_wrong": key})
    if found != set(supplied_differences) or len(differences) != 305:
        errors.append({"auxiliary_difference_receipt_count_wrong": len(differences), "independent_expected": len(supplied_differences)})
    curves = csvread("aggregate_discovery_curve_data.csv")
    if len(curves) != 189 or {(r["method"], int(r["queries"])) for r in curves} != {(m,q) for m in expected_methods for q in range(21)}:
        errors.append({"aggregate_curve_grid_wrong": len(curves)})
    for row in curves:
        method, query = row["method"], int(row["queries"])
        means = [statistics.mean(0 if query == 0 else run.history[query-1][ev.CURVE] for key, run in runs.items() if key[0] == method and key[2] == seed) for seed in SEEDS]
        check(row["mean"], statistics.mean(means), f"chart/{method}/{query}/mean")
        check(row["sample_sd_across_seed_means"], statistics.stdev(means), f"chart/{method}/{query}/sample_SD")
    costs = csvread("per_run_costs.csv")
    if len(costs) != 162 or {(r["method"], r["system"], int(r["seed"])) for r in costs} != expected_keys:
        errors.append({"cost_table_grid_wrong": len(costs)})
    for row in costs:
        key = (row["method"], row["system"], int(row["seed"]))
        actual = runs[key].row
        for field in ("wall_time_seconds", "known_cost_usd"):
            check(row[field], actual[field], f"cost/{key}/{field}")
        for field in ("cost_status", "llm_input_tokens", "llm_output_tokens", "machine", "processor"):
            expected = "" if actual.get(field) is None else str(actual[field])
            if row[field] != expected:
                errors.append({"cost_or_machine_label_wrong": key, "field": field, "actual": row[field], "expected": expected})
    manifest = source.read(RESULTS / "output_manifest.json")
    for relative, record in manifest.items():
        path = RESULTS / relative
        if path.stat().st_size != record["bytes"] or source.sha(path) != record["sha256"]:
            errors.append({"output_manifest_failed": relative})
    recorded = source.read(RESULTS / "evaluation_provenance.json")
    for field, expected in (("evaluator_sha256", provenance["M2_evaluator_sha256"]), ("official_metric_module_sha256", provenance["official_metrics_module_sha256"]), ("official_class_ast_sha256", provenance["official_metric_class_AST_sha256"]), ("aggregation_script_sha256", source.sha(AGGREGATION / "aggregate_handoffs.py"))):
        if recorded[field] != expected:
            errors.append({"evaluator_provenance_mismatch": field})
    validation = source.read(RESULTS / "aggregation_validation.json")
    if validation["accepted_runs"] != 162 or validation["m2_evaluator_issues"]:
        errors.append({"canonical_validation_failed": validation})
    result = {
        "accepted": not errors, "actual_strict_run_count": len(runs), "methods": 9,
        "baseline_comparison_pairs_recomputed": baseline_pairs, "baseline_AF_and_EF_scalar_values_checked": baseline_pairs*2,
        "seed_first_method_mean_SD_scalar_checks": summary_checks, "paired_Full_system_comparisons": len(full_pairs), "paired_M3_component_comparisons": len(m3_pairs),
        "previous_canonical_original_units_hash_matched": len(previous), "previous_M5_endpoint_units_unchanged": 18,
        "M5_original_and_as_submitted_histories_preserved": 18, "M5_corrected_normalized_prefixes_officially_verified": correction_points,
        "published_as_submitted_and_corrected_history_copy_pairs_checked": 18,
        "auxiliary_normalized_difference_receipts_verified": len(differences), "aggregate_curve_mean_SD_points_checked": len(curves),
        "output_manifest_files_checked": len(manifest), "source_provenance": provenance,
        "audit_script_sha256": source.sha(Path(__file__)),
        "actual_cost_and_machine_rows_checked": len(costs),
        "source_originals_modified": 0, "new_scientific_runs": 0, "oracle_calls": 0,
        "limitations": "Configuration artifacts retain documented static/runtime interpolations; original supplied supplementary normalized-AUDC errors are corrected only in separate M2 views. No claim of independent new hull/novelty reevaluation.",
        "errors": errors,
    }
    (OUTPUT / "aggregation_162_independent_review.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
