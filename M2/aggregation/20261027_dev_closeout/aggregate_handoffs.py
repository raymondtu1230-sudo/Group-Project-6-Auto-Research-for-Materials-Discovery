"""Validate real handoffs with the unchanged M2 evaluator and aggregate them.

No agent, oracle, checkpoint restoration, or new scientific run is invoked.
The lean loader compiles the exact official DiscoveryCurveMetrics class AST,
with real NumPy, so unrelated model dependencies are not imported. The complete
class and evaluator source hashes are recorded. Metric formulas are not edited.
All writes, including derivative evaluation views, are under M2.
"""

from __future__ import annotations

import argparse
import ast
import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import sys
import types
from typing import Any
import zipfile

import numpy as np
import yaml

BASE = "b36e2a50d9d3e31fc941d827addab94db2c5d3cc"
FREEZE = "02e0026bf450f71f4f7862228d295f5b02b49e12"
METHODS = {
    "random_generator_baseline", "chemeleon_generative_baseline", "m1_full",
    "tool_routing_off", "memory_off", "exploration_off", "m3_full", "m3_planning_off", "m3_self_correction_off",
}
COMPONENT = {"m3_full", "m3_planning_off", "m3_self_correction_off"}
FLAGS = ["enable_planning", "enable_memory", "enable_reflection",
         "enable_exploration", "enable_tool_routing"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def exact_evaluator(snapshot: Path):
    metrics = snapshot / "M1/MADE/src/made/evaluation/metrics.py"
    assert digest(metrics) == "f24d68a2b0a854cf7d880a97079c47e1d8160da11f7f31fa8900274067c7e3a1"
    source = metrics.read_text()
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, ast.ClassDef)
             and n.name == "DiscoveryCurveMetrics"]
    assert len(nodes) == 1
    module_ast = ast.Module(body=nodes, type_ignores=[])
    namespace = {"np": np, "Any": Any, "__name__": "made.evaluation.metrics"}
    exec(compile(module_ast, str(metrics), "exec"), namespace)
    metric_module = types.ModuleType("made.evaluation.metrics")
    metric_module.DiscoveryCurveMetrics = namespace["DiscoveryCurveMetrics"]
    metric_module.__file__ = str(metrics)
    sys.modules["made.evaluation.metrics"] = metric_module
    evaluator_path = snapshot / "M2/evaluate.py"
    assert digest(evaluator_path) == "2eacad27246a8669657c6551807cbfeb1274cf94b691840f2f196d55e3e93a89"
    spec = importlib.util.spec_from_file_location("m2_exact_handoff_evaluator", evaluator_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    provenance = {
        "evaluator_path": "M2/evaluate.py", "evaluator_sha256": digest(evaluator_path),
        "official_metric_module_path": "M1/MADE/src/made/evaluation/metrics.py",
        "official_metric_module_sha256": digest(metrics),
        "official_class_ast_sha256": hashlib.sha256(ast.dump(nodes[0], include_attributes=False).encode()).hexdigest(),
        "load_mode": "exact_unchanged_class_AST_with_real_numpy_no_unrelated_model_imports",
        "numpy_version": np.__version__, "metric_formula_modifications": 0,
        "evaluator_modifications": 0, "agent_calls": 0, "oracle_calls": 0,
    }
    return module, provenance


def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, archive
        for name in z.namelist():
            p = Path(name)
            assert not p.is_absolute() and ".." not in p.parts, name
        z.extractall(destination)


def profile(method: str) -> tuple[str, str]:
    if method in COMPONENT:
        return "M3_component_study_exploration_and_routing_off", ("not_applicable" if method == "m3_full" else "m3_full")
    if method in {"memory_off", "tool_routing_off", "exploration_off"}:
        return "frozen_full_single_switch_ablation", "m1_full"
    if method == "m1_full":
        return "frozen_full_reference", "not_applicable"
    return "generator_baseline", "not_applicable"


def configuration_differences(left: Any, right: Any, prefix: str = "") -> set[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        return set().union(*(configuration_differences(left.get(k), right.get(k), prefix + "/" + k)
                             for k in left.keys() | right.keys()))
    return {prefix} if left != right else set()


def interpolation_fields(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        return [field for key, item in value.items()
                for field in interpolation_fields(item, prefix + "/" + str(key))]
    if isinstance(value, list):
        return [field for index, item in enumerate(value)
                for field in interpolation_fields(item, prefix + "/" + str(index))]
    return [prefix] if isinstance(value, str) and "${" in value else []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--prior-results", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for p in (args.work, args.output):
        assert "M2" in p.resolve().parts
        if p.exists() and any(p.iterdir()):
            raise SystemExit(f"Refusing to overwrite existing output: {p}")
        p.mkdir(parents=True, exist_ok=True)
    snapshot, prior = args.snapshot.resolve(), args.prior_results.resolve()
    os.environ["MPLCONFIGDIR"] = str(args.work.resolve() / "matplotlib_cache")
    ev, loader = exact_evaluator(snapshot)
    protocol = yaml.safe_load((snapshot / "M1/protocol/protocol_v1.yaml").read_text())
    systems = read(snapshot / "M1/protocol/dev_systems.json")
    seeds = protocol["repeats"]["seeds"]
    expected_pairs = {( "-".join(s), seed) for s in systems for seed in seeds}
    views = args.work / "evaluation_views"
    sources = []
    curves = {}
    for p in (prior / "report/recorded_curve_analysis").rglob("reevaluated_curve.json"):
        d = read(p)
        if d["method"] in {"random_generator_baseline", "chemeleon_generative_baseline", "tool_routing_off"}:
            assert d["accepted"] and d["original_endpoint_matches"]
            curves[(d["method"], d["system"], d["seed"])] = (p, d)
    assert len(curves) == 54
    # Original baseline ZIP members are copied byte-for-byte; no metadata edits.
    extracted = {}
    for key, (curve_path, d) in sorted(curves.items()):
        source = d["source"]
        if "::" in source:
            archive_s, member = source.split("::", 1)
            candidates = list(prior.rglob(Path(archive_s).name)) + list(snapshot.rglob(Path(archive_s).name))
            matches = [p for p in candidates if digest(p) == d["archive_sha256"]]
            assert matches, (archive_s, d["archive_sha256"])
            archive = matches[0]
            archive_key = d["archive_sha256"]
            if archive_key not in extracted:
                target = args.work / "baseline_originals" / (archive.stem + "-" + archive_key[:12])
                safe_extract(archive, target)
                extracted[archive_key] = target
            origin = extracted[archive_key] / member
        else:
            rel = source.split("/M2/results/preserved/raw/", 1)[1]
            origin = prior / "raw" / rel
            if not origin.is_dir():
                artifact_id, member = rel.split("/", 1)
                receipt = next(x for x in read(prior / "provenance.json")["artifacts"]
                               if str(x["artifact_id"]) == artifact_id)
                archive = prior / receipt["archive"]
                assert digest(archive) == receipt["sha256"]
                archive_key = receipt["sha256"]
                if archive_key not in extracted:
                    target = args.work / "routing_originals" / artifact_id
                    safe_extract(archive, target)
                    extracted[archive_key] = target
                origin = extracted[archive_key] / member
        for rel, sha in d["input_sha256"].items():
            assert digest(origin / rel) == sha, (origin, rel)
        sources.append((origin, curve_path, d))
    m4 = snapshot / "M4/evidence/frozen-memory-ablation-20261026"
    archive = m4 / "memory_off_raw_results.zip"
    assert digest(archive) == read(m4 / "checksums.json")[archive.name]["sha256"]
    safe_extract(archive, args.work / "m4_originals")
    for root in [snapshot / "M3/results/frozen_20261025/protocol_v1",
                 snapshot / "M1/MADE/results/protocol_v1/exploration_off/dev",
                 args.work / "m4_originals/M1/MADE/results/protocol_v1/memory_off/dev"]:
        for p in sorted(root.rglob("run_metadata.json")):
            if read(p).get("status") == "completed":
                sources.append((p.parent, None, None))
    accepted_full = {
        (r["system"], r["seed"]): r
        for r in read(snapshot / "M2/aggregation/20261026_m3_complete/results/input_receipts.json")
        if r["method"] == "m1_full"
    }
    assert len(accepted_full) == 18
    selected_full, excluded_full = set(), []
    for p in sorted((snapshot / "M1/MADE/results/protocol_v1/m1_full/dev").rglob("run_metadata.json")):
        meta = read(p)
        key = ("-".join(meta["system"]), meta["seed"])
        receipt = accepted_full.get(key)
        if receipt and digest(p) == receipt["original_metadata_sha256"]:
            assert meta["status"] == "completed" and key not in selected_full
            assert digest(p.parent / "trajectories/episode_000.json") == receipt["original_trajectory_sha256"]
            assert digest(p.parent / "resolved_config.yaml") == receipt["original_resolved_config_sha256"]
            approved_attempt = 2 if key[0] == "Mg-Sn-Sr" and key[1] in {17, 29} else 1
            assert meta["attempt"] == approved_attempt
            sources.append((p.parent, None, None))
            selected_full.add(key)
        else:
            excluded_full.append({"source": str(p.parent), "method": meta.get("method"),
                "system": key[0], "seed": key[1], "attempt": meta.get("attempt"),
                "status": meta.get("status"), "reason": "not_the_hash_pinned_accepted_frozen_reference"})
    assert selected_full == expected_pairs
    write(args.output / "excluded_nonreference_full_attempts.json", excluded_full)
    assert len(sources) == 162
    previous_m5 = {
        (r["system"], r["seed"]): r
        for r in read(snapshot / "M2/aggregation/20261026_m5_intake/results/m5_endpoint_evidence_receipts.json")
    }
    receipts = []
    m5_auxiliary_corrections = []
    m5_manifest_checks = []
    for origin, curve_path, d in sources:
        meta = read(origin / "run_metadata.json")
        method, system, seed = meta["method"], "-".join(meta["system"]), meta["seed"]
        target = views / method / "dev" / system / f"seed_{seed}" / f"attempt_{meta.get('attempt', 1):02d}"
        shutil.copytree(origin, target)
        derived = False
        captured_path = target / "m2_metrics_history.json"
        captured = read(captured_path) if captured_path.exists() else None
        if captured is None or not captured.get("complete_curve"):
            assert d is not None and method == "tool_routing_off"
            if captured_path.exists():
                shutil.copy2(captured_path, target / "original_incomplete_metrics_history.json")
            write(target / "m2_metrics_history.json", {
                "source": "separately_validated_offline_recorded_trajectory_re_evaluation_not_original_checkpoint",
                "provenance_note": "Derivative evaluation view only; original result files and failed collection audit remain unchanged.",
                "complete_curve": True, "metrics_history": d["reevaluated_metrics_history"],
                "source_analysis_sha256": digest(curve_path), "historical_checkpoint_recovered": False,
            })
            derived = True
        loaded = ev.load_run(target)
        assert loaded.metadata["protocol_settings"] == protocol
        history = read(target / "m2_metrics_history.json")
        if d:
            assert loaded.reference_hash == d["canonical_material_reference_sha256"]
            for old, checked in zip(loaded.history, d["reevaluated_metrics_history"], strict=True):
                assert old[ev.MSUN] == checked[ev.MSUN] and old[ev.CURVE] == checked[ev.CURVE]
        # Crosscheck M1's newly added reconstructed histories with prior official
        # structure-and-energy re-evaluation; these are not original captures.
        if method == "m1_full":
            p = prior / "report/recorded_curve_analysis/m1_full" / system / f"seed_{seed}" / f"attempt_{meta.get('attempt', 1):02d}/reevaluated_curve.json"
            prior_curve = read(p)
            assert prior_curve["accepted"]
            assert digest(origin / "trajectories/episode_000.json") == prior_curve["original_trajectory_sha256"]
            for x, y in zip(loaded.history, prior_curve["reevaluated_metrics_history"], strict=True):
                assert x[ev.MSUN] == y[ev.MSUN] and x[ev.CURVE] == y[ev.CURVE]
        config = yaml.safe_load((origin / "resolved_config.yaml").read_text())
        agent = config.get("agent", {})
        flags = {k: agent.get(k) for k in FLAGS}
        expected_flags = {
            "m1_full": [True, True, True, True, True],
            "tool_routing_off": [True, True, True, True, False],
            "memory_off": [True, False, True, True, True],
            "exploration_off": [True, True, True, False, True],
            "m3_full": [True, True, True, False, False],
            "m3_planning_off": [False, True, True, False, False],
            "m3_self_correction_off": [True, True, False, False, False],
        }
        if method in expected_flags:
            assert list(flags.values()) == expected_flags[method], (method, flags)
        evidence_files_verified = 0
        if method == "exploration_off":
            old = previous_m5[(system, seed)]
            for relative in ("run_metadata.json", "trajectories/episode_000.json"):
                assert digest(origin / relative) == old["original_files"][relative]["sha256"]
            manifest = read(origin / "evidence_manifest.json")
            assert manifest["recorded_revision"] == meta["made_upstream_commit"]
            for relative, record in manifest["files"].items():
                assert not Path(relative).is_absolute() and ".." not in Path(relative).parts
                published = (origin / relative).read_bytes()
                published_sha = hashlib.sha256(published).hexdigest()
                if len(published) == record["bytes"] and published_sha == record["sha256"]:
                    verification_mode = "exact_published_bytes"
                else:
                    windows_bytes = published.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                    assert len(windows_bytes) == record["bytes"]
                    assert hashlib.sha256(windows_bytes).hexdigest() == record["sha256"]
                    verification_mode = "only_deterministic_LF_to_CRLF_matches_recorded_Windows_bytes"
                m5_manifest_checks.append({"method": method, "system": system, "seed": seed,
                    "file": relative, "verification_mode": verification_mode,
                    "published_bytes": len(published), "published_sha256": published_sha,
                    "recorded_manifest_bytes": record["bytes"], "recorded_manifest_sha256": record["sha256"],
                    "published_source_modified": False})
                evidence_files_verified += 1
            assert evidence_files_verified == 8
            assert len(meta["m1_input_sha256"]) == 74
            for relative, expected in meta["m1_input_sha256"].items():
                source_file = snapshot / "M1" / relative.replace("\\", "/")
                content = source_file.read_bytes().replace(b"\r\n", b"\n")
                assert expected in {hashlib.sha256(content).hexdigest(), hashlib.sha256(content.replace(b"\n", b"\r\n")).hexdigest()}
            old_curve = read(snapshot / "M2/aggregation/20261026_m5_intake/results/derived_endpoint_analysis" / system / f"seed_{seed}" / "reconstructed_curve.json")
            for now, earlier in zip(loaded.history, old_curve["metrics_history"], strict=True):
                assert now[ev.MSUN] == earlier[ev.MSUN] and now[ev.CURVE] == earlier[ev.CURVE]
            original_history = copy.deepcopy(history)
            shutil.copy2(origin / "m2_metrics_history.json", target / "as_submitted_metrics_history.json")
            for query, point in enumerate(history["metrics_history"], start=1):
                prefix = history["metrics_history"][:query]
                expected_raw = ev.DiscoveryCurveMetrics.area_under_discovery_curve(prefix, metric_key=ev.CURVE)
                assert math.isclose(point["discovery_curve_area_under_discovery_curve"], expected_raw, rel_tol=1e-12, abs_tol=1e-12)
                expected_normalized = ev.DiscoveryCurveMetrics.area_under_discovery_curve(prefix, metric_key=ev.CURVE, normalize=True)
                field = "discovery_curve_area_under_discovery_curve_normalized"
                supplied = point[field]
                if not math.isclose(supplied, expected_normalized, rel_tol=1e-12, abs_tol=1e-12):
                    m5_auxiliary_corrections.append({"method": method, "system": system, "seed": seed,
                        "queries_used": query, "field": field, "as_submitted": supplied,
                        "corrected_analysis_view_value": expected_normalized,
                        "official_function": "DiscoveryCurveMetrics.area_under_discovery_curve(normalize=True)",
                        "as_submitted_history_sha256": digest(origin / "m2_metrics_history.json"),
                        "source_original_modified": False, "core_mSUN_and_raw_AUDC_modified": False})
                    point[field] = expected_normalized
            # Only the auxiliary normalization field changes in this separate
            # analysis view. The as-submitted source and bytes remain intact.
            stripped_before, stripped_after = copy.deepcopy(original_history), copy.deepcopy(history)
            for document in (stripped_before, stripped_after):
                for point in document["metrics_history"]:
                    point.pop("discovery_curve_area_under_discovery_curve_normalized", None)
            assert stripped_before == stripped_after
            write(target / "m2_metrics_history.json", history)
            derived = True
            retained_view = args.output / "m5_history_analysis_views" / system / f"seed_{seed}"
            retained_view.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target / "as_submitted_metrics_history.json", retained_view / "as_submitted_metrics_history.json")
            shutil.copy2(target / "m2_metrics_history.json", retained_view / "corrected_analysis_metrics_history.json")
        receipts.append({
            "method": method, "system": system, "seed": seed,
            "original_source": str(origin), "view": str(target),
            "original_metadata_sha256": digest(origin / "run_metadata.json"),
            "original_trajectory_sha256": digest(origin / "trajectories/episode_000.json"),
            "original_resolved_config_sha256": digest(origin / "resolved_config.yaml"),
            "history_source": history.get("source"), "history_is_derived_view": derived,
            "actual_recorded_revision": loaded.row["repository_revision"],
            "canonical_material_reference_sha256": loaded.reference_hash,
            "scientific_profile": profile(method)[0], "causal_comparator": profile(method)[1],
            "strict_canonical_accepted": True,
            "supplied_configuration_interpolation_fields": interpolation_fields(config),
            "m5_evidence_manifest_files_verified": evidence_files_verified,
            "as_submitted_history_sha256": digest(origin / "m2_metrics_history.json"),
            "evaluation_view_history_sha256": digest(target / "m2_metrics_history.json"),
            "auxiliary_normalized_AUDC_corrected_in_separate_view": method == "exploration_off",
            "flags": flags,
        })
    # Invoke the actual unmodified evaluator CLI function, including its own
    # protocol/reference comparison and baseline AF/EF calculations.
    evaluator_output = args.output / "m2_evaluator"
    sys.argv = [str(snapshot / "M2/evaluate.py"), "--results-root", str(views),
                "--output", str(evaluator_output), "--split", "dev"]
    ev.main()
    validation = read(evaluator_output / "validation.json")
    assert validation["validated_runs"] == 162 and validation["issues"] == []
    runs, issues = ev.collect(views, "dev")
    assert issues == [] and len(runs) == 162
    m3_runs = [r for r in runs if r.row["method"] in COMPONENT]
    assert len(m3_runs) == 54
    ev.compare(m3_runs)
    write(args.output / "m3_only_validation.json", {
        "validator": "unchanged_M2_evaluate_load_run_collect_compare",
        "validated_runs": 54, "methods": {m: 18 for m in sorted(COMPONENT)},
        "issues": [], "protocol_and_canonical_reference_comparison": "passed",
        "paired_comparator": "m3_full", "original_result_files_modified": 0,
    })
    m5_runs = [r for r in runs if r.row["method"] == "exploration_off"]
    assert len(m5_runs) == 18
    ev.compare(m5_runs)
    write(args.output / "m5_only_validation.json", {
        "validator": "unchanged_M2_evaluate_load_run_collect_compare",
        "validated_runs": 18, "method": "exploration_off", "issues": [],
        "protocol_and_canonical_reference_comparison": "passed",
        "prior_provisional_metadata_and_trajectory_hashes_unchanged": 18,
        "prior_provisional_discovery_count_prefixes_matched": 360,
        "actual_packaged_evidence_manifest_file_checks": 144,
        "as_submitted_originals_passed_core_load_run": 18,
        "as_submitted_auxiliary_normalized_AUDC_correct": False,
        "auxiliary_normalized_AUDC_mismatched_prefixes": len(m5_auxiliary_corrections),
        "separate_analysis_view_auxiliary_normalization_corrected": True,
        "configuration_artifact_note": "saved_run_composed_configuration; any retained interpolation fields are listed per unit",
        "strict_acceptance_scope": "actual unchanged M2 evaluator checks; does not assert every Hydra runtime interpolation was expanded in the supplied artifact",
        "original_result_files_modified": 0,
    })
    ev.compare(runs)
    ev.write_csv(args.output / "m5_normalized_AUDC_corrections.csv", m5_auxiliary_corrections)
    ev.write_csv(args.output / "m5_evidence_manifest_verification.csv", m5_manifest_checks)
    write(args.output / "m5_evidence_manifest_verification.json", {
        "manifest_members_verified": len(m5_manifest_checks),
        "exact_published_bytes": sum(r["verification_mode"] == "exact_published_bytes" for r in m5_manifest_checks),
        "recorded_Windows_bytes_reproduced_by_only_LF_to_CRLF": sum(r["verification_mode"] != "exact_published_bytes" for r in m5_manifest_checks),
        "unexplained_mismatches": 0,
        "published_source_files_modified": 0,
        "scope": "recorded manifest is from Windows checkout; actual published LF bytes and hashes are recorded separately",
    })
    write(args.output / "m5_auxiliary_normalization_audit.json", {
        "submitted_core_query_count_and_raw_AUDC_prefixes_checked": 360,
        "submitted_core_prefixes_passed": 360,
        "submitted_auxiliary_normalized_AUDC_mismatches": len(m5_auxiliary_corrections),
        "as_submitted_history_copies_preserved": 18,
        "auxiliary_normalized_AUDC_analysis_views_corrected": 18,
        "correction_scope": "only discovery_curve_area_under_discovery_curve_normalized; all other history fields unchanged",
        "official_function": "unchanged DiscoveryCurveMetrics.area_under_discovery_curve(normalize=True)",
        "shared_primary_metrics_use": "mSUN_raw_AUDC_AF_EF; auxiliary normalization is not used",
        "source_originals_modified": 0,
    })
    assert {r.row["method"] for r in runs} == METHODS
    for method in METHODS:
        assert {(r.row["system"], r.row["seed"]) for r in runs if r.row["method"] == method} == expected_pairs
    receipt_index = {(r["method"], r["system"], r["seed"]): r for r in receipts}
    for r in runs:
        receipt = receipt_index[(r.row["method"], r.row["system"], r.row["seed"])]
        r.row.update({k: receipt[k] for k in ("scientific_profile", "causal_comparator", "history_source", "actual_recorded_revision", "strict_canonical_accepted")})
        r.row["original_source"] = receipt["original_source"]
    ev.write_csv(args.output / "per_run_with_baseline_comparisons.csv", [r.row for r in runs])
    summary = ev.summarize_methods(runs, systems, seeds)
    for row in summary:
        row["scientific_profile"], row["causal_comparator"] = profile(row["method"])
        row["strict_canonical_accepted"] = True
    ev.write_csv(args.output / "per_method_summary.csv", summary)
    previous_summaries = {
        r["method"]: r
        for r in csv.DictReader((snapshot / "M2/aggregation/20261026_m5_intake/results/nine_method_summary_with_acceptance.csv").open())
    }
    checked_fields = 0
    for row in summary:
        old = previous_summaries[row["method"]]
        for key, value in row.items():
            if key.endswith(("_mean", "_std", "_seed_n")) and value is not None:
                assert math.isclose(value, float(old[key]), rel_tol=1e-12, abs_tol=1e-12), (row["method"], key)
                checked_fields += 1
    write(args.output / "prior_numeric_continuity.json", {
        "all_nine_methods_unchanged_from_previous_endpoint_table": True,
        "previous_eight_canonical_methods_unchanged": True,
        "matched_numeric_aggregate_fields": checked_fields,
        "change_is_M5_package_acceptance_not_new_scientific_runs": True,
    })
    ev.write_csv(args.output / "per_system_summary.csv", ev.summarize(runs))
    index = {(r.row["method"], r.row["system"], r.row["seed"]): r for r in runs}
    pairs = []
    for method in ("memory_off", "tool_routing_off", "exploration_off"):
        for system, seed in sorted(expected_pairs):
            off, full = index[(method, system, seed)], index[("m1_full", system, seed)]
            pairs.append({"method": method, "system": system, "seed": seed,
                "comparator": "m1_full", "delta_mSUN_off_minus_full": off.row["mSUN_at_B"]-full.row["mSUN_at_B"],
                "delta_AUDC_off_minus_full": off.row["AUDC"]-full.row["AUDC"],
                "AF_off_vs_full": ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE),
                "EF_off_vs_full": ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE)})
    ev.write_csv(args.output / "paired_full_system_ablations.csv", pairs)
    m3_pairs = []
    allowed_log_differences = {
        "/agent/memory_manager/log_path", "/agent/exploration_policy/log_path",
        "/agent/capture_path", "/experiment/output_dir",
    }
    for method, flag in (("m3_planning_off", "enable_planning"),
                         ("m3_self_correction_off", "enable_reflection")):
        for system, seed in sorted(expected_pairs):
            off, full = index[(method, system, seed)], index[("m3_full", system, seed)]
            assert full.metadata["m1_input_sha256"] == off.metadata["m1_input_sha256"]
            assert len(full.metadata["m1_input_sha256"]) == 74
            full_config = yaml.safe_load((full.path / "resolved_config.yaml").read_text())
            off_config = yaml.safe_load((off.path / "resolved_config.yaml").read_text())
            differences = configuration_differences(full_config, off_config)
            assert "/agent/" + flag in differences
            assert differences <= allowed_log_differences | {"/agent/" + flag}, (method, system, seed, differences)
            m3_pairs.append({
                "method": method, "system": system, "seed": seed, "comparator": "m3_full",
                "full_mSUN_at_20": full.row["mSUN_at_B"], "off_mSUN_at_20": off.row["mSUN_at_B"],
                "full_AUDC": full.row["AUDC"], "off_AUDC": off.row["AUDC"],
                "delta_mSUN_full_minus_off": full.row["mSUN_at_B"] - off.row["mSUN_at_B"],
                "delta_AUDC_full_minus_off": full.row["AUDC"] - off.row["AUDC"],
                "AF_off_vs_m3_full": ev.DiscoveryCurveMetrics.acceleration_factor(off.history, full.history, metric_key=ev.CURVE),
                "EF_off_vs_m3_full": ev.DiscoveryCurveMetrics.enhancement_factor(off.history, full.history, metric_key=ev.CURVE),
                "pair_source_hashes_compared": 74, "pair_source_hashes_identical": True,
                "config_differences": ";".join(sorted(differences)),
                "full_actual_recorded_revision": full.row["repository_revision"],
                "off_actual_recorded_revision": off.row["repository_revision"],
                "scientific_profile": "M3_component_study_exploration_and_routing_off",
            })
    ev.write_csv(args.output / "paired_m3_component_ablations.csv", m3_pairs)
    m3_effect_summary = []
    for method in ("m3_planning_off", "m3_self_correction_off"):
        group = [r for r in m3_pairs if r["method"] == method]
        row = {"method": method, "comparator": "m3_full", "matched_pairs": 18,
               "aggregation": "equal_weight_system_mean_per_seed_then_seed_mean_and_sample_sd"}
        for key in ("delta_mSUN_full_minus_off", "delta_AUDC_full_minus_off", "AF_off_vs_m3_full", "EF_off_vs_m3_full"):
            values = [statistics.mean(r[key] for r in group if r["seed"] == seed) for seed in seeds]
            row[key + "_mean"] = statistics.mean(values)
            row[key + "_std"] = statistics.stdev(values)
        row["full_mSUN_better_pairs"] = sum(r["delta_mSUN_full_minus_off"] > 0 for r in group)
        row["full_mSUN_equal_pairs"] = sum(r["delta_mSUN_full_minus_off"] == 0 for r in group)
        row["full_mSUN_worse_pairs"] = sum(r["delta_mSUN_full_minus_off"] < 0 for r in group)
        m3_effect_summary.append(row)
    ev.write_csv(args.output / "m3_component_effect_summary.csv", m3_effect_summary)
    costs = [{k: r.row.get(k) for k in ("method", "system", "seed", "wall_time_seconds", "known_cost_usd", "cost_status", "llm_input_tokens", "llm_output_tokens", "machine", "processor", "original_source")} for r in runs]
    ev.write_csv(args.output / "per_run_costs.csv", costs)
    # Historical endpoint reports can now be independently checked against the
    # newly supplied actual 18-run comparator, not substituted for raw results.
    historical = [r for r in csv.DictReader((snapshot / "M3/results/m3_ablation_runs.csv").open()) if r["method"] == "m3_full"]
    assert len(historical) == 18
    assert {(r["system"], int(r["seed"])) for r in historical} == expected_pairs
    for old in historical:
        actual = index[("m3_full", old["system"], int(old["seed"]))]
        assert actual.row["mSUN_at_B"] == float(old["msun"])
        assert actual.row["AUDC"] == float(old["audc"])
    write(args.output / "m3_comparator_validation.json", {
        "method": "m3_full", "status": "actual_18_raw_runs_validated",
        "raw_runs_validated": 18, "historical_reported_endpoints_matched": 18,
        "matched_component_pairs": 36, "source_hash_checks_per_pair": 74,
        "all_paired_scientific_config_differences_are_only_assigned_switch": True,
        "config_logging_output_path_differences_preserved_and_listed": True,
        "historical_comparator_missing": False,
    })
    # Equal system weights inside each seed, SD across three seed means.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    chart_data = []
    for method in sorted(METHODS):
        group = [r for r in runs if r.row["method"] == method]
        values = np.array([[0, *[p[ev.CURVE] for p in r.history]] for r in group])
        seed_values = np.array([values[[r.row["seed"] == seed for r in group]].mean(axis=0) for seed in seeds])
        mean, sd = seed_values.mean(axis=0), seed_values.std(axis=0, ddof=1)
        ax = axes[1 if method in COMPONENT else 0]
        ax.plot(range(21), mean, label=method)
        ax.fill_between(range(21), mean-sd, mean+sd, alpha=.12)
        chart_data.extend({"method": method, "queries": q, "mean": float(mean[q]), "sample_sd_across_seed_means": float(sd[q])} for q in range(21))
    axes[0].set_title("Frozen Full and one-switch ablations / baselines")
    axes[1].set_title("M3 component study: exploration and routing OFF")
    for ax in axes:
        ax.set(xlabel="Oracle queries", ylabel="Stable discovery count (official AUDC source)")
        ax.grid(alpha=.2)
        ax.legend(fontsize=8, loc="upper left" if ax is axes[0] else "lower right")
    fig.tight_layout()
    fig.savefig(args.output / "discovery_curves_by_study.png", dpi=180)
    fig.savefig(args.output / "discovery_curves_by_study.svg")
    plt.close(fig)
    ev.write_csv(args.output / "aggregate_discovery_curve_data.csv", chart_data)
    write(args.output / "input_receipts.json", receipts)
    write(args.output / "evaluation_provenance.json", {
        "source_snapshot_commit": BASE, "original_scientific_freeze_commit": FREEZE,
        "m3_full_actual_recorded_revision": "ae7fe81991c56dd2d77685220b74ddbef11039c7",
        "m5_exploration_off_actual_recorded_revision": "aedf8ca238d2ef56948c0eadf2c897aef67f5104",
        "source_revision_policy": "preserve_each_original_metadata_revision; no historical run is relabelled",
        "full_reference_selection": "prior_accepted_metadata_trajectory_and_configuration_hashes; never_latest_attempt",
        "aggregation_script_sha256": digest(Path(__file__)), **loader})
    write(args.output / "aggregation_validation.json", {
        "accepted_runs": 162, "methods": {m: 18 for m in sorted(METHODS)},
        "unique_system_seed_units_per_method": 18, "protocol_and_material_reference_comparison": "passed",
        "m2_evaluator_issues": [], "baseline_paired_comparisons": 324,
        "all_new_peer_runs_accepted": True, "full_system_ablations_available": ["memory_off", "tool_routing_off", "exploration_off"],
        "full_system_matched_pairs_validated": 54,
        "full_system_additional_planning_self_correction_scope": "M1_M6_design_decision_not_M3_component_delivery_debt",
        "full_system_exploration_off_delivery": "18_raw_runs_canonical_evaluator_accepted",
        "m3_component_study_runs_validated": 54, "m3_component_off_runs_validated": 36,
        "m3_full_raw_comparator_independently_validated": True, "m3_full_raw_missing": False,
        "m3_assigned_component_study_complete": True, "m3_matched_component_pairs_validated": 36,
        "m3_component_causal_deltas_status": "matched_actual_raw_full_and_off_validated",
        "m5_original_configuration_artifacts_present_and_manifest_checked": 18,
        "m5_submitted_auxiliary_normalization_mismatches": len(m5_auxiliary_corrections),
        "m5_auxiliary_normalization_corrected_only_in_analysis_views": True,
        "m5_previous_strict_rejections_preserved": True,
        "all_received_declared_development_packages_canonical_accepted": True,
        "additional_full_system_planning_self_correction_requires_scope_decision": True,
        "all_group_work_complete": False, "new_scientific_runs": 0, "new_oracle_queries": 0,
        "original_files_modified": 0, "derived_view_histories": sum(r["history_is_derived_view"] for r in receipts),
        "routing_record_only_reevaluation_history_views": 18,
        "m5_auxiliary_only_corrected_history_views": 18,
        "m1_reconstructed_curves_crosschecked_against_prior_structure_energy_reevaluation": 18,
    })
    manifest = {str(p.relative_to(args.output)): {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(args.output.rglob("*")) if p.is_file()}
    write(args.output / "output_manifest.json", manifest)
    print(json.dumps({"accepted": 162, "issues": 0, "output": str(args.output), "m3_full_raw_missing": False}))


if __name__ == "__main__":
    main()
