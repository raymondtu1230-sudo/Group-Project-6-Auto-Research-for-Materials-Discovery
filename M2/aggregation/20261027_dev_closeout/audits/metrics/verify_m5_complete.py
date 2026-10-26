"""Strict read-only acceptance of the original M5 package and approved Full units."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import types
from typing import Any

import numpy as np
import yaml


OUTPUT = Path(__file__).resolve().parent
BASE = OUTPUT.parent
SNAPSHOT = BASE / "snapshot"
PROJECT = BASE.parents[1]
ROOT = SNAPSHOT / "M1/MADE/results/protocol_v1"
OLD = PROJECT / "M2/stage_m5_intake_20261026"
SEEDS = (17, 29, 43)
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
FLAGS = ("enable_planning", "enable_memory", "enable_reflection", "enable_exploration", "enable_tool_routing")


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_evaluator():
    metrics = SNAPSHOT / "M1/MADE/src/made/evaluation/metrics.py"
    metric_node = next(n for n in ast.parse(metrics.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "DiscoveryCurveMetrics")
    namespace = {"np": np, "Any": Any}
    exec(compile(ast.Module(body=[metric_node], type_ignores=[]), str(metrics), "exec"), namespace)
    module = types.ModuleType("made.evaluation.metrics")
    module.DiscoveryCurveMetrics = namespace["DiscoveryCurveMetrics"]
    sys.modules["made.evaluation.metrics"] = module
    evaluator_path = SNAPSHOT / "M2/evaluate.py"
    spec = importlib.util.spec_from_file_location("complete_m5_actual_evaluator", evaluator_path)
    evaluator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = evaluator
    spec.loader.exec_module(evaluator)
    package_path = SNAPSHOT / "M1/package_reference_evidence.py"
    curve_node = next(n for n in ast.parse(package_path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "curve_from_trajectory")
    curve_namespace = {"Path": Path, "json": json, "math": math}
    exec(compile(ast.Module(body=[curve_node], type_ignores=[]), str(package_path), "exec"), curve_namespace)
    provenance = {
        "M2_evaluator_sha256": sha(evaluator_path),
        "official_metrics_module_sha256": sha(metrics),
        "official_metric_class_AST_sha256": hashlib.sha256(ast.dump(metric_node, include_attributes=False).encode()).hexdigest(),
        "M1_curve_helper_module_sha256": sha(package_path),
        "M1_curve_helper_AST_sha256": hashlib.sha256(ast.dump(curve_node, include_attributes=False).encode()).hexdigest(),
        "loader": "Unchanged actual M2.evaluate.load_run; unchanged official metric class and M1 trajectory helper AST; real NumPy; no scientific dependency mocks or formula edits.",
        "numpy_version": np.__version__,
    }
    return evaluator, curve_namespace["curve_from_trajectory"], provenance


def interpolations(value: Any, path: str = "") -> list[dict[str, str]]:
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in interpolations(child, f"{path}.{key}" if path else key)]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in interpolations(child, f"{path}[{index}]" )]
    if isinstance(value, str) and "${" in value:
        return [{"path": path, "saved_value": value, "kind": "runtime_resolver" if any(t in value for t in ("${hydra:", "${oc.env:")) else "static_reference_or_selector"}]
    return []


def main() -> None:
    ev, reconstruct, provenance = exact_evaluator()
    errors, rows, runs = [], [], {}
    old_result = read(OLD / "audit_metrics/m5_metrics_independent_audit.json")
    old_index = {(r["method"], r["system"], r["seed"]): r for r in old_result["per_run"]}
    expected_paths = []
    for method in ("m1_full", "exploration_off"):
        for system in SYSTEMS:
            for seed in SEEDS:
                attempt = 2 if method == "m1_full" and system == "Mg-Sn-Sr" and seed in (17, 29) else 1
                expected_paths.append(ROOT / method / "dev" / system / f"seed_{seed}" / f"attempt_{attempt:02d}")
    for path in expected_paths:
        label = str(path.relative_to(SNAPSHOT))
        try:
            run = ev.load_run(path)
            key = (run.row["method"], run.row["system"], run.row["seed"])
            runs[key] = run
            reconstructed = reconstruct(path)
            saved = read(path / "m2_metrics_history.json")
            mismatch = []
            auxiliary_mismatch = []
            for actual, derived in zip(saved["metrics_history"], reconstructed["metrics_history"], strict=True):
                for field in ("queries_used", ev.MSUN, ev.CURVE, "discovery_curve_area_under_discovery_curve", "discovery_curve_area_under_discovery_curve_normalized"):
                    if actual.get(field) != derived[field]:
                        difference = {"query": derived["queries_used"], "field": field, "saved": actual.get(field), "actual_observation_reconstruction": derived[field]}
                        (auxiliary_mismatch if field.endswith("_normalized") else mismatch).append(difference)
            config = yaml.safe_load((path / "resolved_config.yaml").read_text())
            hydro = yaml.safe_load((path / "hydra/config.yaml").read_text())
            old = old_index[key]
            old_path = OLD / "snapshot" / old["path"]
            original_files = []
            if key[0] == "exploration_off":
                for original in sorted(p for p in old_path.rglob("*") if p.is_file()):
                    relative = original.relative_to(old_path)
                    target = path / relative
                    matched = target.is_file() and sha(original) == sha(target)
                    original_files.append({"path": str(relative), "old_sha256": sha(original), "new_sha256": sha(target) if target.is_file() else None, "unchanged": matched})
            settings_checks = {
                "required_curve_fields_match_unchanged_M1_helper_all20_prefixes": not mismatch,
                "dataset_matches_actual_metadata": config["dataset"]["elements"] == run.metadata["system"],
                "seed_matches_actual_metadata": config["experiment"]["seed"] == run.metadata["seed"],
                "B20_episode1": config["environment"]["budget"] == 20 and config["experiment"]["num_episodes"] == 1,
                "CPU_ORBv3_conservative": config["oracle"]["device"] == "cpu" and config["oracle"]["model_name"] == "orb-v3-conservative-inf-omat",
                "correct_single_switch_profile": tuple(config["agent"][k] for k in FLAGS) == (True, True, True, key[0] == "m1_full", True),
                "new_endpoint_matches_previous_verified_endpoint": run.row["mSUN_at_B"] == old["mSUN"] and run.row["AUDC"] == old["AUDC"],
                "actual_trajectory_unchanged": sha(path / "trajectories/episode_000.json") == old["trajectory_sha256"],
                "actual_metadata_unchanged": sha(path / "run_metadata.json") == old["run_metadata_sha256"],
                "all_previously_published_original_M5_files_unchanged": all(x["unchanged"] for x in original_files),
            }
            if key[0] == "exploration_off":
                settings_checks["composed_config_matches_original_saved_Hydra_config"] = config == hydro
                settings_checks["composed_and_original_config_bytes_identical"] = sha(path / "resolved_config.yaml") == sha(path / "hydra/config.yaml")
            if not all(settings_checks.values()):
                errors.append({"path": label, "error": "Independent settings/history/preservation checks failed", "failed": [k for k,v in settings_checks.items() if not v]})
            rows.append({"path": label, "method": key[0], "system": key[1], "seed": key[2], "attempt": run.metadata["attempt"], "strict_M2_load_run_accepted": True, "checks": settings_checks, "saved_history_source": saved.get("source"), "history_prefixes_checked": len(saved["metrics_history"]), "core_metric_mismatches": mismatch, "auxiliary_normalized_AUDC_mismatches": auxiliary_mismatch, "mSUN": run.row["mSUN_at_B"], "AUDC": run.row["AUDC"], "canonical_material_reference_sha256": run.reference_hash, "resolved_configuration_interpolations": interpolations(config), "original_M5_files_preserved": original_files, "trajectory_sha256": sha(path / "trajectories/episode_000.json"), "metadata_sha256": sha(path / "run_metadata.json"), "saved_history_sha256": sha(path / "m2_metrics_history.json"), "resolved_config_sha256": sha(path / "resolved_config.yaml")})
        except Exception as exc:
            errors.append({"path": label, "error": f"{type(exc).__name__}: {exc}"})
    pairs = []
    for system in SYSTEMS:
        for seed in SEEDS:
            full, off = runs.get(("m1_full", system, seed)), runs.get(("exploration_off", system, seed))
            if not (full and off):
                continue
            matched = full.reference_hash == off.reference_hash and full.metadata["protocol_settings"] == off.metadata["protocol_settings"]
            if not matched:
                errors.append({"system": system, "seed": seed, "error": "Canonical material reference/protocol mismatch"})
            pairs.append({"system": system, "seed": seed, "full_attempt": full.metadata["attempt"], "off_attempt": off.metadata["attempt"], "canonical_reference_and_protocol_match": matched, "delta_mSUN_full_minus_off": full.row["mSUN_at_B"]-off.row["mSUN_at_B"], "delta_AUDC_full_minus_off": full.row["AUDC"]-off.row["AUDC"], "AF_off_vs_full": float(ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE)), "EF_off_vs_full": float(ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE))})
    selected = {str(path) for path in expected_paths if "/m1_full/" in str(path)}
    excluded = [{"path": str(p.parent.relative_to(SNAPSHOT)), "status": read(p).get("status"), "reason": "Not one of the18 M1-approved frozen reference attempt paths; preserved, never silently selected by completion/latest-attempt rules."} for p in sorted((ROOT / "m1_full/dev").rglob("run_metadata.json")) if str(p.parent) not in selected]
    summaries = ev.summarize_methods(list(runs.values()), [s.split("-") for s in SYSTEMS], list(SEEDS))
    result = {
        "snapshot_commit": "b36e2a50d9d3e31fc941d827addab94db2c5d3cc", "accepted": not errors,
        "strict_M2_load_run_new_M5_accepted": sum(r["method"] == "exploration_off" for r in rows),
        "strict_M2_load_run_approved_frozen_Full_accepted": sum(r["method"] == "m1_full" for r in rows),
        "new_M5_saved_history_prefixes_checked": sum(r["history_prefixes_checked"] for r in rows if r["method"] == "exploration_off"),
        "all_saved_history_prefixes_checked": sum(r["history_prefixes_checked"] for r in rows),
        "all_original_endpoints_unchanged": all(r["checks"]["new_endpoint_matches_previous_verified_endpoint"] for r in rows),
        "acceptance_scope": "Unchanged strict M2 evaluator and required mSUN/raw AUDC/AF/EF curves, with explicit configuration and auxiliary-field qualifications below. Not a claim that all submitted history fields agree with official definitions.",
        "all_submitted_history_fields_match_official": not any(r["auxiliary_normalized_AUDC_mismatches"] for r in rows),
        "auxiliary_normalized_AUDC_mismatch_count": sum(len(r["auxiliary_normalized_AUDC_mismatches"]) for r in rows),
        "auxiliary_normalized_AUDC_qualification": "305 new M5 prefix normalized-AUDC values differ from unchanged official helper (official area/(queries_used**2/2)). This unused supplementary field is not read by strict M2.evaluate for required mSUN, raw AUDC, AF or EF. Original source history remains unchanged and all discrepancies are preserved. Do not use this submitted normalized field or describe every metric-history field as verified/lossless.",
        "new_scientific_runs": 0, "agent_calls": 0, "oracle_calls": 0,
        "history_provenance": "M5 histories are explicitly labelled actual saved-observation reconstructions using the unchanged M1 helper; original checkpoints are not claimed recovered, no independent hull/novelty reevaluation is claimed.",
        "configuration_qualification": "M5 resolved_config.yaml is a byte-identical copy of original saved composed Hydra config in all18 units. Critical dataset/seed/B/oracle/switch fields are concrete and match metadata. Both static references and runtime resolvers remain verbatim, including seeds, agent budget, selector device and output/env references. This is accepted by unchanged strict M2.load_run, but is not a claim that every YAML interpolation was fully evaluated at packaging time.",
        "source_provenance": provenance, "audit_script_sha256": sha(Path(__file__)), "errors": errors,
        "per_run": rows, "paired_Full_comparisons": pairs, "excluded_preserved_Full_attempts": excluded, "method_summaries": summaries,
    }
    (OUTPUT / "m5_complete_strict_independent_audit.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k:result[k] for k in ("accepted", "strict_M2_load_run_new_M5_accepted", "strict_M2_load_run_approved_frozen_Full_accepted", "new_M5_saved_history_prefixes_checked", "all_original_endpoints_unchanged", "errors")}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
