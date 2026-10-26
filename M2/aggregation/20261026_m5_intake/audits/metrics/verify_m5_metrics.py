"""Read-only M5 endpoint and comparator audit using actual recorded trajectories."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any

import numpy as np


BASE = Path(__file__).resolve().parents[1]
SNAPSHOT = BASE / "snapshot"
OUTPUT = Path(__file__).resolve().parent
ROOT = SNAPSHOT / "M1/MADE/results/protocol_v1"
SEEDS = (17, 29, 43)
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
METHODS = ("m1_full", "exploration_off")
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
AUDC = "discovery_curve_area_under_discovery_curve"


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_exact_functions():
    metrics = SNAPSHOT / "M1/MADE/src/made/evaluation/metrics.py"
    metric_node = next(n for n in ast.parse(metrics.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "DiscoveryCurveMetrics")
    namespace = {"np": np, "Any": Any}
    exec(compile(ast.Module(body=[metric_node], type_ignores=[]), str(metrics), "exec"), namespace)
    packaging = SNAPSHOT / "M1/package_reference_evidence.py"
    curve_node = next(n for n in ast.parse(packaging.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "curve_from_trajectory")
    curve_namespace = {"Path": Path, "json": json, "math": math}
    exec(compile(ast.Module(body=[curve_node], type_ignores=[]), str(packaging), "exec"), curve_namespace)
    evaluator = SNAPSHOT / "M2/evaluate.py"
    hash_node = next(n for n in ast.parse(evaluator.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "snapshot_hash")
    hash_namespace = {"Any": Any, "copy": copy, "json": json, "hashlib": hashlib}
    exec(compile(ast.Module(body=[hash_node], type_ignores=[]), str(evaluator), "exec"), hash_namespace)
    provenance = {
        "official_metric_module_sha256": sha(metrics),
        "official_metric_class_AST_sha256": hashlib.sha256(ast.dump(metric_node, include_attributes=False).encode()).hexdigest(),
        "M1_packaging_module_sha256": sha(packaging),
        "M1_trajectory_curve_function_AST_sha256": hashlib.sha256(ast.dump(curve_node, include_attributes=False).encode()).hexdigest(),
        "M2_evaluator_sha256": sha(evaluator),
        "canonical_reference_hash_function_AST_sha256": hashlib.sha256(ast.dump(hash_node, include_attributes=False).encode()).hexdigest(),
        "numpy_version": np.__version__,
        "execution": "Unchanged official class/helper/function AST, real NumPy; no formula edits or dependency mocks.",
    }
    return namespace["DiscoveryCurveMetrics"], curve_namespace["curve_from_trajectory"], hash_namespace["snapshot_hash"], provenance


def values_summary(values: list[float]) -> dict[str, Any]:
    return {"n": len(values), "mean": statistics.mean(values), "sample_SD": statistics.stdev(values), "population_SD": statistics.pstdev(values)}


def main() -> None:
    official, reconstruct, reference_hash, provenance = load_exact_functions()
    errors: list[str] = []
    rows, ignored, by_key = [], [], {}
    expected = {(s, seed) for s in SYSTEMS for seed in SEEDS}
    for method in METHODS:
        for meta_file in sorted((ROOT / method / "dev").rglob("run_metadata.json")):
            path = meta_file.parent
            metadata = read(meta_file)
            tpath = path / "trajectories/episode_000.json"
            payload = read(tpath) if tpath.exists() else {}
            metrics = payload.get("metrics", {})
            system = "-".join(metadata["system"])
            seed = metadata["seed"]
            eligible = metadata.get("status") == "completed" and metrics.get("final/queries_used") == 20 and len(payload.get("trajectory", [])) == 20
            if not eligible:
                ignored.append({"path": str(path.relative_to(SNAPSHOT)), "method": method, "system": system, "seed": seed, "status": metadata.get("status"), "completed_queries": metrics.get("final/queries_used"), "run_metadata_sha256": sha(meta_file), "reason": "Original failed/incomplete attempt preserved and excluded from successful frozen comparator."})
                continue
            key = (method, system, seed)
            if key in by_key:
                errors.append(f"Duplicate eligible actual unit: {key}")
            history = reconstruct(path)["metrics_history"]
            calculated_audc = float(official.area_under_discovery_curve(history, metric_key=CURVE))
            final_msun = float(metrics[f"final/{MSUN}"])
            final_audc = float(metrics[f"final/{AUDC}"])
            checks = {
                "recorded_stable_new_observation_count_matches_final_mSUN": history[-1][MSUN] == final_msun,
                "official_AUDC_from_recorded_observation_curve_matches_final_AUDC": math.isclose(calculated_audc, final_audc, rel_tol=1e-12, abs_tol=1e-12),
                "query_counts_1_to_20": [h["queries_used"] for h in history] == list(range(1, 21)),
                "metadata_budget_episode_split": metadata["query_budget"] == 20 and metadata["episodes"] == 1 and metadata["split"] == "dev",
            }
            summary = read(path / "summary/summary.json")
            episodes = read(path / "summary/episodes.json")
            for metric, value in ((MSUN, final_msun), (AUDC, final_audc), ("queries_used", 20)):
                checks[f"summary_matches_{metric}"] = summary["summary"][f"final/{metric}"]["mean"] == value and len(episodes) == 1 and episodes[0][f"final/{metric}"] == value
            command = metadata["command"]
            expected_flags = {"enable_planning": True, "enable_memory": True, "enable_reflection": True, "enable_exploration": method == "m1_full", "enable_tool_routing": True}
            command_flags = {k: next((x.rsplit("=", 1)[1] for x in command if x.startswith(f"agent.{k}=")), None) for k in expected_flags}
            checks["recorded_command_switches_correct"] = all(command_flags[k] == str(v).lower() for k, v in expected_flags.items())
            if not all(checks.values()):
                errors.append(f"Actual endpoint/record audit failed: {key}")
            row = {
                "method": method, "system": system, "seed": seed, "attempt": metadata["attempt"],
                "path": str(path.relative_to(SNAPSHOT)), "mSUN": final_msun, "AUDC": final_audc,
                "recomputed_recorded_stable_new_endpoint": history[-1][MSUN], "official_recomputed_AUDC": calculated_audc,
                "trajectory_sha256": sha(tpath), "run_metadata_sha256": sha(meta_file),
                "canonical_material_reference_sha256": reference_hash(payload["phase_diagram_gt"]),
                "recorded_upstream_commit": metadata.get("made_upstream_commit"), "machine": metadata.get("machine"),
                "protocol_settings": metadata["protocol_settings"], "checks": checks, "accepted": all(checks.values()),
                "original_history_present": (path / "m2_metrics_history.json").exists(),
                "history_audit_kind": "Read-only reconstruction from actual saved is_stable/is_newly_discovered observations; not recovered original checkpoint and not an independent hull/novelty reevaluation.",
            }
            rows.append(row)
            by_key[key] = row
        actual = {(r["system"], r["seed"]) for r in rows if r["method"] == method}
        if actual != expected:
            errors.append(f"Incomplete or unexpected successful {method} sweep: {actual ^ expected}")

    method_summaries = []
    for method in METHODS:
        selected = [r for r in rows if r["method"] == method]
        result = {"method": method, "runs": len(selected), "primary_statistic": "Six equally weighted systems mean within seed, then mean and sample SD across 3 seeds.", "supplement_statistic": "Pooled 18-episode population SD describes system/seed dispersion, not the primary seed-level uncertainty."}
        for metric in ("mSUN", "AUDC"):
            seed_means = [{"seed": seed, "six_system_mean": statistics.mean(by_key[(method, system, seed)][metric] for system in SYSTEMS)} for seed in SEEDS]
            result[metric] = {"primary": {**values_summary([x["six_system_mean"] for x in seed_means]), "seed_means": seed_means}, "pooled_episode_supplement": values_summary([r[metric] for r in selected])}
        method_summaries.append(result)

    pairs, system_summaries = [], []
    for system in SYSTEMS:
        result = {"system": system}
        for metric in ("mSUN", "AUDC"):
            on = [by_key[("m1_full", system, seed)][metric] for seed in SEEDS]
            off = [by_key[("exploration_off", system, seed)][metric] for seed in SEEDS]
            result[metric] = {"ON": values_summary(on), "OFF": values_summary(off), "paired_ON_minus_OFF": values_summary([a-b for a,b in zip(on, off, strict=True)])}
        system_summaries.append(result)
        for seed in SEEDS:
            on, off = by_key[("m1_full", system, seed)], by_key[("exploration_off", system, seed)]
            match = on["canonical_material_reference_sha256"] == off["canonical_material_reference_sha256"] and on["protocol_settings"] == off["protocol_settings"]
            if not match:
                errors.append(f"Material reference/protocol differs: {system}/{seed}")
            pairs.append({"system": system, "seed": seed, "ON_attempt": on["attempt"], "OFF_attempt": off["attempt"], "canonical_reference_and_protocol_match": match, "delta_mSUN_ON_minus_OFF": on["mSUN"]-off["mSUN"], "delta_AUDC_ON_minus_OFF": on["AUDC"]-off["AUDC"]})
    effect_summary = {}
    for metric in ("mSUN", "AUDC"):
        per_seed = [statistics.mean(p[f"delta_{metric}_ON_minus_OFF"] for p in pairs if p["seed"] == seed) for seed in SEEDS]
        d = [p[f"delta_{metric}_ON_minus_OFF"] for p in pairs]
        effect_summary[metric] = {"ON_minus_OFF_primary_seed_aggregate": values_summary(per_seed), "seed_order": list(SEEDS), "seed_mean_deltas": per_seed, "paired_episode_ON_wins": sum(x > 0 for x in d), "paired_episode_ties": sum(x == 0 for x in d), "paired_episode_ON_losses": sum(x < 0 for x in d)}
    findings = [
        {"severity": "report_correction", "item": "Mg-Sn-Sr Full comparator", "reported": "ON mSUN10.0; AUDC96.0", "actual": "Successful frozen attempts 02/02/01 for seeds17/29/43 give mSUN12/9/12 and AUDC105/98.5/105: mean11.0 and102.83333333333333. The two unsuccessful attempt01 directories remain preserved."},
        {"severity": "report_correction", "item": "Overall mean and effect", "reported": "ON9.8 versusOFF9.7; delta+0.2; AUDCON87.0 versusOFF88.2; delta-1.2", "actual": "ON10.0 versusOFF9.666666666666666; delta+0.3333333333333333. AUDCON88.11111111111111 versusOFF88.22222222222223; delta-0.1111111111111111."},
        {"severity": "statistic_label", "item": "Overall std4.8 to2.7", "actual": "Correct rounded pooled18-episode population SDs ofmSUN, but not primary equal-system seed-first sample SD. Descriptive cross-system dispersion only; no statistically established stabilisation or causal rescue claim."},
        {"severity": "report_correction", "item": "Full pooled AUDC population SD", "reported": 28.5, "actual": 28.81770075046255, "rounded_to_one_decimal": 28.8},
        {"severity": "report_correction", "item": "Same machine family", "reported": "Same machine family", "actual": "The frozen Full metadata records a macOS arm MacBook; exploration_off records Windows AMD64/AuthenticAMD. Budgets and oracle execution device match; machine family does not. Do not infer runtime speedup from this comparison."},
        {"severity": "interpretation_limit", "item": "Mechanism claims", "actual": "Per-system direction is observed. UCB causality, easy/hard system labels, opportunity cost, mode collapse and future gains are interpretations requiring actual decision evidence and cannot be established from endpoints alone."},
    ]
    result = {
        "snapshot_commit": "a27634d9edbf231d0c034273fa9f977f9d5e799e", "raw_endpoint_audit_accepted": not errors,
        "M5_report_requires_corrections": True, "successful_actual_run_count": len(rows), "new_exploration_off_units": sum(r["method"] == "exploration_off" for r in rows),
        "official_AUDC_endpoint_recomputations": len(rows), "actual_observation_prefixes_reconstructed": len(rows)*20,
        "successful_frozen_Full_comparator_policy": "Exactly one completedB20 episode for each expecteddevsystem/seed. Mg-Sn-Sr17/29 useattempt02, other16useattempt01. Failed/incomplete originalattempts preserved and excluded.",
        "new_scientific_runs": 0, "agent_calls": 0, "oracle_calls": 0,
        "provenance_limitation": "This audit validates saved actual stability/new-discovery observations and official area arithmetic/endpoints. It does not recalculate hull energies, structure matching or novelty from physics, and does not claim recovered original histories.",
        "source_provenance": provenance, "errors": errors, "ignored_preserved_attempts": ignored,
        "audited_M5_report_sha256": sha(SNAPSHOT / "M5/report/M5_RESULTS.md"),
        "audit_script_sha256": sha(Path(__file__)),
        "per_run": rows, "method_summaries": method_summaries, "per_system_statistics": system_summaries,
        "paired_effects": pairs, "effect_summary": effect_summary, "report_findings": findings,
    }
    (OUTPUT / "m5_metrics_independent_audit.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"accepted": not errors, "runs": len(rows), "errors": errors, "summaries": method_summaries, "effects": effect_summary}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
