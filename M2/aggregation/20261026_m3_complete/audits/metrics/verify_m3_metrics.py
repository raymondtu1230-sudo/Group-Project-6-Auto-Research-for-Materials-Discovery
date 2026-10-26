"""Read-only verification of real M3 component-study records and curves."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import sys
import types
from typing import Any

import numpy as np
import yaml


BASE = Path(__file__).resolve().parents[1]
SNAPSHOT = BASE / "snapshot"
OUTPUT = Path(__file__).resolve().parent
METHODS = ("m3_full", "m3_planning_off", "m3_self_correction_off")
FLAGS = ("enable_planning", "enable_memory", "enable_reflection", "enable_exploration", "enable_tool_routing")
EXPECTED_FLAGS = {
    "m3_full": (True, True, True, False, False),
    "m3_planning_off": (False, True, True, False, False),
    "m3_self_correction_off": (True, True, False, False, False),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def exact_functions():
    metrics = SNAPSHOT / "M1/MADE/src/made/evaluation/metrics.py"
    node = next(n for n in ast.parse(metrics.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "DiscoveryCurveMetrics")
    namespace = {"np": np, "Any": Any}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(metrics), "exec"), namespace)
    module = types.ModuleType("made.evaluation.metrics")
    module.DiscoveryCurveMetrics = namespace["DiscoveryCurveMetrics"]
    sys.modules["made.evaluation.metrics"] = module
    evaluator = SNAPSHOT / "M2/evaluate.py"
    spec = importlib.util.spec_from_file_location("m3_readonly_actual_evaluator", evaluator)
    ev = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ev
    spec.loader.exec_module(ev)
    packaging = SNAPSHOT / "M1/package_reference_evidence.py"
    function = next(n for n in ast.parse(packaging.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "curve_from_trajectory")
    curve_namespace = {"Path": Path, "json": json, "math": math}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(packaging), "exec"), curve_namespace)
    return ev, curve_namespace[function.name], {
        "M2_evaluator_sha256": sha(evaluator),
        "official_metric_module_sha256": sha(metrics),
        "official_metric_class_AST_sha256": hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(),
        "M1_trajectory_packaging_sha256": sha(packaging),
        "M1_curve_function_AST_sha256": hashlib.sha256(ast.dump(function, include_attributes=False).encode()).hexdigest(),
        "loader": "exact unchanged official class and trajectory-function AST; real NumPy; no scientific dependency mocks or formula edits",
        "numpy_version": np.__version__,
    }


def differences(a: Any, b: Any, path: str = "") -> list[dict[str, Any]]:
    if isinstance(a, dict) and isinstance(b, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            result.extend(differences(a.get(key), b.get(key), path + "." + key if path else key))
        return result
    return [] if a == b else [{"path": path, "off": a, "m3_full": b}]


def main() -> None:
    ev, reconstruct, provenance = exact_functions()
    root = SNAPSHOT / "M3/results/frozen_20261025/protocol_v1"
    runs, configs, rows, errors = {}, {}, [], []
    for method in METHODS:
        paths = sorted((root / method / "dev").rglob("run_metadata.json"))
        if len(paths) != 18:
            errors.append(f"{method}: expected18 actual units; found{len(paths)}")
        for metadata in paths:
            path = metadata.parent
            run = ev.load_run(path)
            key = (method, run.row["system"], run.row["seed"])
            if key in runs:
                errors.append(f"Duplicate actual unit:{key}")
            runs[key] = run
            config = yaml.safe_load((path / "resolved_config.yaml").read_text())
            configs[key] = config
            if tuple(config["agent"].get(k) for k in FLAGS) != EXPECTED_FLAGS[method]:
                errors.append(f"Wrong M3 component-study switch profile:{key}")
            reconstructed = reconstruct(path)
            saved = read(path / "m2_metrics_history.json")
            mismatches = []
            for actual, derived in zip(saved["metrics_history"], reconstructed["metrics_history"], strict=True):
                for field in ("queries_used", ev.MSUN, ev.CURVE, "discovery_curve_area_under_discovery_curve", "discovery_curve_area_under_discovery_curve_normalized"):
                    if actual.get(field) != derived[field]:
                        mismatches.append({"query": derived["queries_used"], "metric": field, "saved": actual.get(field), "from_actual_trajectory": derived[field]})
            actual_curve_AUDC = ev.DiscoveryCurveMetrics.area_under_discovery_curve(saved["metrics_history"], metric_key=ev.CURVE)
            payload = read(path / "trajectories/episode_000.json")
            endpoint_AUDC = payload["metrics"]["final/discovery_curve_area_under_discovery_curve"]
            endpoint_mSUN = payload["metrics"]["final/" + ev.MSUN]
            passed = not mismatches and math.isclose(actual_curve_AUDC, endpoint_AUDC, rel_tol=1e-9, abs_tol=1e-9) and saved["metrics_history"][-1][ev.MSUN] == endpoint_mSUN
            if not passed:
                errors.append(f"Actual trajectory/history/endpoint disagreement:{key}")
            rows.append({
                "method": method, "system": run.row["system"], "seed": run.row["seed"],
                "path": str(path.relative_to(SNAPSHOT)), "saved_history_source": saved.get("source"),
                "actual_trajectory_sha256": sha(path / "trajectories/episode_000.json"),
                "saved_history_sha256": sha(path / "m2_metrics_history.json"),
                "trajectory_function_prefixes_checked": len(saved["metrics_history"]),
                "mismatches": mismatches, "actual_official_AUDC": actual_curve_AUDC,
                "original_official_AUDC": endpoint_AUDC, "original_mSUN": endpoint_mSUN,
                "canonical_material_reference_sha256": run.reference_hash, "accepted": passed,
            })
    ev.compare(list(runs.values()))
    log_fields = {"experiment.output_dir", "agent.capture_path", "agent.capture_run_id", "agent.memory_manager.log_path", "agent.memory_manager.run_id", "agent.exploration_policy.log_path"}
    pairs = []
    for method, switch in (("m3_planning_off", "agent.enable_planning"), ("m3_self_correction_off", "agent.enable_reflection")):
        for system, seed in sorted({(r.row["system"], r.row["seed"]) for r in runs.values()}):
            off, full = runs[(method, system, seed)], runs[("m3_full", system, seed)]
            ds = differences(configs[(method, system, seed)], configs[("m3_full", system, seed)])
            unexpected = [d for d in ds if d["path"] not in log_fields | {switch}]
            matched = off.reference_hash == full.reference_hash and off.metadata["protocol_settings"] == full.metadata["protocol_settings"] and not unexpected
            if not matched:
                errors.append(f"M3 component comparator/config/reference mismatch:{method}/{system}/{seed}")
            pairs.append({"method": method, "comparator": "m3_full", "system": system, "seed": seed,
                          "configuration_differences": ds, "unexpected_configuration_differences": unexpected,
                          "protocol_and_material_reference_match": matched,
                          "delta_mSUN_off_minus_m3_full": off.row["mSUN_at_B"] - full.row["mSUN_at_B"],
                          "delta_AUDC_off_minus_m3_full": off.row["AUDC"] - full.row["AUDC"],
                          "AF_off_vs_m3_full": ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE),
                          "EF_off_vs_m3_full": ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE)})
    summaries = ev.summarize_methods(list(runs.values()), read(SNAPSHOT / "M1/protocol/dev_systems.json"), [17, 29, 43])
    result = {"snapshot_commit": "dcd3481a44f5bd9e0f9d7e58778a7f59a5a81210", "accepted": not errors,
              "actual_run_count": len(runs), "new_m3_full_units": sum(r["method"] == "m3_full" for r in rows),
              "new_m3_full_trajectory_prefixes_checked": sum(r["trajectory_function_prefixes_checked"] for r in rows if r["method"] == "m3_full"),
              "all_M3_trajectory_prefixes_checked": sum(r["trajectory_function_prefixes_checked"] for r in rows),
              "official_endpoint_AUDCs_checked": len(rows), "paired_M3_component_comparisons": len(pairs),
              "new_scientific_runs": 0, "agent_calls": 0, "oracle_calls": 0,
              "history_provenance": "All M3 histories are explicitly reconstructed from actual saved trajectory observations, not recovered original checkpoints.",
              "scope": "M3 component study against m3_full, not Full-system single-switch ablations. Decisions on any additional Full-system planning/self-correction experiments belong to M1/M6, not this audit or an assumed M3 assignment.",
              "source_provenance": provenance, "errors": errors, "per_run": rows,
              "paired_comparisons": pairs, "method_summaries": summaries}
    (OUTPUT / "m3_metrics_independent_audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("accepted", "actual_run_count", "new_m3_full_units", "new_m3_full_trajectory_prefixes_checked", "all_M3_trajectory_prefixes_checked", "official_endpoint_AUDCs_checked", "paired_M3_component_comparisons", "errors")}))
    print(json.dumps([{"method": r["method"], "mSUN": r["mSUN_at_B_mean"], "mSUN_seed_SD": r["mSUN_at_B_std"], "AUDC": r["AUDC_mean"], "AUDC_seed_SD": r["AUDC_std"]} for r in summaries]))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
