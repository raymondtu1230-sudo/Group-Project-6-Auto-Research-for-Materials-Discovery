"""Read-only intake audit of recorded M5 data; no scientific runtime imports."""
from __future__ import annotations

import ast
import collections
import copy
import csv
import hashlib
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parent / "snapshot"
ORIGINAL = HERE.parents[1] / "runtime/frozen_reference"
RESULTS = SNAPSHOT / "M1/MADE/results/protocol_v1"
SYSTEMS = {"Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm"}
SEEDS = {17, 29, 43}
MSUN = "final/novelty_stable_unique_novel_count"
AUDC = "final/discovery_curve_area_under_discovery_curve"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


# Execute only the existing standard-library canonicalization function.
tree = ast.parse((SNAPSHOT / "M2/evaluate.py").read_text())
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "snapshot_hash")
namespace = {"copy": copy, "hashlib": hashlib, "json": json}
exec(compile(ast.Module(body=[node], type_ignores=[]), "M2/evaluate.py:snapshot_hash", "exec"), namespace)
reference_hash = namespace["snapshot_hash"]


def command_values(metadata):
    return dict(x.split("=", 1) for x in metadata["command"][1:])


def select_full(system, seed):
    candidates = []
    for path in (RESULTS / "m1_full/dev" / system / f"seed_{seed}").glob("attempt_*/run_metadata.json"):
        meta = read(path)
        if meta.get("status") == "completed":
            candidates.append((meta["attempt"], path.parent))
    return max(candidates)[1]


units = []
input_checks = []
inventory = []
for attempt in sorted((RESULTS / "exploration_off").rglob("attempt_*")):
    if not attempt.is_dir():
        continue
    metadata = read(attempt / "run_metadata.json")
    system = "-".join(metadata["system"])
    seed = metadata["seed"]
    payload = read(attempt / "trajectories/episode_000.json")
    summary = read(attempt / "summary/summary.json")
    episodes = read(attempt / "summary/episodes.json")
    full_path = select_full(system, seed)
    full_meta = read(full_path / "run_metadata.json")
    full_payload = read(full_path / "trajectories/episode_000.json")
    values, full_values = command_values(metadata), command_values(full_meta)
    differences = {
        key: {"full": full_values.get(key), "off": values.get(key)}
        for key in sorted(set(values) | set(full_values))
        if values.get(key) != full_values.get(key)
        and key != "experiment.output_dir"
    }
    hashes = []
    for key, expected in metadata["m1_input_sha256"].items():
        path = ORIGINAL / "M1" / key.replace("\\", "/")
        raw = path.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        variants = {"raw": raw, "LF": lf, "CRLF": lf.replace(b"\n", b"\r\n")}
        matches = [name for name, content in variants.items() if sha(content) == expected]
        check = {"unit": f"{system}/{seed}", "path": key.replace("\\", "/"),
                 "recorded_sha256": expected, "matching_representation": matches}
        input_checks.append(check)
        hashes.append(bool(matches))
    canonical = reference_hash(payload["phase_diagram_gt"])
    cumulative, counts = 0, []
    for point in payload["trajectory"]:
        cumulative += int(bool(point.get("is_stable") and point.get("is_newly_discovered")))
        counts.append(cumulative)
    # Endpoint arithmetic only; this is not scientific prefix re-evaluation.
    # Official _extract_discovery_curve prepends the (0,0) origin.
    origin_counts = [0] + counts
    trapezoid = sum((left + right) / 2 for left, right in zip(origin_counts, origin_counts[1:]))
    missing = [name for name in (
        "resolved_config.yaml", "hydra/config.yaml", "hydra/hydra.yaml", "hydra/overrides.yaml",
        "m4_evidence.jsonl", "m4_proposal_events.jsonl", "m5_decisions.jsonl", "run_benchmark.log",
    ) if not (attempt / name).is_file()]
    own_files = sorted(p for p in attempt.rglob("*") if p.is_file())
    console = attempt.parent / f"console_attempt_{metadata['attempt']:02d}.log"
    if console.is_file():
        own_files.append(console)
    for path in own_files:
        content = path.read_bytes()
        inventory.append({"path": str(path.relative_to(SNAPSHOT)), "bytes": len(content), "sha256": sha(content)})
    endpoints_equal = all(
        payload["metrics"][key] == summary["summary"][key]["mean"] == episodes[0][key]
        for key in (MSUN, AUDC)
    )
    units.append({
        "system": system, "seed": seed, "attempt": metadata["attempt"],
        "path": str(attempt.relative_to(SNAPSHOT)), "selected_full_path": str(full_path.relative_to(SNAPSHOT)),
        "status": metadata["status"], "split": metadata["split"], "query_budget": metadata["query_budget"],
        "trajectory_queries": len(payload["trajectory"]), "official_queries": payload["metrics"]["final/queries_used"],
        "episodes": metadata["episodes"], "summary_episodes": summary["episodes"],
        "protocol_equal_to_selected_full": metadata["protocol_settings"] == full_meta["protocol_settings"],
        "canonical_reference_sha256": canonical,
        "reference_equal_to_selected_full": canonical == reference_hash(full_payload["phase_diagram_gt"]),
        "source_hash_count": len(hashes), "all_recorded_source_hashes_match_original_freeze": all(hashes),
        "recorded_command_scientific_differences": differences,
        "recorded_command_only_exploration_switch_differs": differences == {"agent.enable_exploration": {"full": "true", "off": "false"}},
        "actual_resolved_configuration_available": (attempt / "resolved_config.yaml").is_file(),
        "actual_realized_configuration_one_switch_certified": False,
        "missing_package_items": missing,
        "attempt_file_count": len(own_files) - int(console.is_file()), "console_available_at_seed_parent": console.is_file(),
        "mSUN": payload["metrics"][MSUN], "AUDC": payload["metrics"][AUDC],
        "summary_trajectory_episode_endpoints_equal": endpoints_equal,
        "recorded_hit_flag_arithmetic_matches_mSUN": cumulative == payload["metrics"][MSUN],
        "recorded_hit_flag_trapezoid_AUDC": trapezoid,
        "recorded_hit_flag_trapezoid_matches_AUDC": trapezoid == payload["metrics"][AUDC],
        "M5_analysis_helper_step_sum_AUDC": sum(counts),
        "m1_full_mSUN": full_payload["metrics"][MSUN], "m1_full_AUDC": full_payload["metrics"][AUDC],
        "made_upstream_commit_field": metadata["made_upstream_commit"],
        "protocol_expected_upstream_commit": metadata["protocol_settings"]["made_upstream_commit"],
        "dependency_versions": metadata["dependency_versions"],
        "full_dependency_versions": full_meta["dependency_versions"],
        "machine": metadata["machine"], "platform": metadata["platform"], "processor": metadata["processor"],
        "python": metadata["python"], "full_machine": full_meta["machine"], "full_platform": full_meta["platform"],
        "full_processor": full_meta["processor"], "full_python": full_meta["python"],
        "wall_time_seconds": metadata["wall_time_seconds"],
    })

prior = read(HERE.parents[1] / "stage_m3full_intake_20261026/audit_m3/m3_full_intake_audit.json")
broader = []
for original in prior["broader_source_equivalence"]:
    path = original["path"]
    old = (ORIGINAL / path).read_bytes().replace(b"\r\n", b"\n")
    now = (SNAPSHOT / path).read_bytes().replace(b"\r\n", b"\n")
    broader.append({"path": path, "original02_lf_sha256": sha(old), "snapshot_lf_sha256": sha(now), "LF_equal": old == now})

def aggregate(field):
    seeds = [statistics.mean(unit[field] for unit in units if unit["seed"] == seed) for seed in sorted(SEEDS)]
    return {"mean": statistics.mean(seeds), "sample_sd_of_three_seed_means": statistics.stdev(seeds), "seed_means": seeds}

def paired(field):
    deltas = [unit["m1_full_" + field] - unit[field] for unit in units]
    seeds = [statistics.mean(unit["m1_full_" + field] - unit[field] for unit in units if unit["seed"] == seed) for seed in sorted(SEEDS)]
    return {"direction": "m1_full minus exploration_off", "mean": statistics.mean(deltas),
            "sample_sd_of_three_seed_means": statistics.stdev(seeds), "seed_mean_differences": seeds,
            "wins_ties_losses": [sum(v > 0 for v in deltas), sum(v == 0 for v in deltas), sum(v < 0 for v in deltas)]}

coverage = {(unit["system"], unit["seed"]) for unit in units}
audit = {
    "snapshot_commit": "a27634d9edbf231d0c034273fa9f977f9d5e799e",
    "original_frozen_commit": "02e0026bf450f71f4f7862228d295f5b02b49e12",
    "acceptance": {"completed_recorded_endpoints_validated": len(units) == 18 and all(
        unit["status"] == "completed" and unit["trajectory_queries"] == unit["official_queries"] == unit["query_budget"] == 20
        and unit["summary_trajectory_episode_endpoints_equal"] and unit["reference_equal_to_selected_full"]
        and unit["protocol_equal_to_selected_full"] and unit["all_recorded_source_hashes_match_original_freeze"]
        for unit in units), "complete_required_original_packages": False,
        "actual_resolved_one_switch_configurations_certified": False,
        "description": "Accept original endpoints for provisional evidence; hold full-package acceptance until original configs and component logs are supplied."},
    "units_count": len(units), "queries": sum(unit["trajectory_queries"] for unit in units),
    "coverage_exact_dev_6_systems_3_seeds": coverage == {(system, seed) for system in SYSTEMS for seed in SEEDS} and len(units) == 18,
    "attempt_counts": dict(collections.Counter(str(unit["attempt"]) for unit in units)),
    "recorded_source_fingerprints": input_checks, "source_fingerprint_comparison_count": len(input_checks),
    "source_fingerprint_all_match": all(check["matching_representation"] for check in input_checks),
    "broader_source_file_count": len(broader), "broader_source_all_LF_equal": all(check["LF_equal"] for check in broader),
    "broader_source_equivalence": broader,
    "units": units, "file_inventory": inventory, "received_result_files": len(inventory),
    "aggregate_exploration_off": {field: aggregate(field) for field in ("mSUN", "AUDC")},
    "paired_full_minus_off": {field: paired(field) for field in ("mSUN", "AUDC")},
    "no_scientific_runtime_imports": True, "no_oracle_model_agent_calls": True, "no_remote_mutations": True,
    "history_note": "No original per-query history/checkpoint received. Hit-flag endpoint arithmetic is not scientific prefix re-evaluation or recovered original history.",
    "source_note": "All74 recorded hashes match frozen Windows CRLF checkouts. This verifies recorded scientific inputs, not a clean detached Git HEAD, the binary checkpoint bytes, installed packages, or absent runtime logs.",
    "configuration_note": "Metadata command has exactly intended exploration-only switch difference after excluding run paths. Source/config defaults also match freeze. Missing resolved configs prevent direct certification of realized runtime configuration.",
    "machine_note": "Official Full is macOS ARM torch2.9.1; M5 is Windows AMD torch2.14.1+cu126, despite recorded CPU execution. Report same-machine-family and controlled timing claims are unsupported.",
}
dry_path = SNAPSHOT / "M5/evidence/dry-run-alpha0.8"
dry_meta = read(dry_path / "run_metadata.json")
dry_payload = read(dry_path / "episode_000.json")
replaced = next(unit for unit in units if unit["system"] == "Mg-Sn-Sr" and unit["seed"] == 17)
counterfactual = {}
for label, field in (("mSUN", MSUN), ("AUDC", AUDC)):
    values = [unit["m1_full_" + label] for unit in units]
    values[units.index(replaced)] = dry_payload["metrics"][field]
    counterfactual[label] = {"mean": statistics.mean(values), "pooled_population_sd": statistics.pstdev(values),
                             "Mg_Sn_Sr_mean": statistics.mean(dry_payload["metrics"][field] if unit is replaced else unit["m1_full_" + label] for unit in units if unit["system"] == "Mg-Sn-Sr")}
audit["M5_report_reference_selection_audit"] = {
    "actual_selection_script_or_manifest_received": False,
    "correct_selected_full_mean": {label: statistics.mean(unit["m1_full_" + label] for unit in units) for label in ("mSUN", "AUDC")},
    "stale_substitution_exact_numeric_signature": counterfactual,
    "replaced_official_unit": {"path": replaced["selected_full_path"], "mSUN": replaced["m1_full_mSUN"], "AUDC": replaced["m1_full_AUDC"]},
    "stale_dry_run": {"path": str(dry_path.relative_to(SNAPSHOT)), "seed": dry_meta["seed"], "attempt": dry_meta["attempt"],
                      "started_at_utc": dry_meta["started_at_utc"], "made_upstream_commit": dry_meta["made_upstream_commit"],
                      "mSUN": dry_payload["metrics"][MSUN], "AUDC": dry_payload["metrics"][AUDC],
                      "trajectory_sha256": sha((dry_path / "episode_000.json").read_bytes())},
    "interpretation": "Replacing only the completed frozen Mg-Sn-Sr seed17 attempt02 with this21Oct dry run exactly reproduces the published M5 ON means and rounded population SDs. This is strong numeric evidence of a stale comparator; without a selection manifest it is not proof of how the author selected records or failed-attempt aggregation.",
}
audit["curve_arithmetic_note"] = {
    "zero_origin_included_per_official_extract_discovery_curve": True,
    "naive_hit_flag_trapezoid_matches_units": sum(unit["recorded_hit_flag_trapezoid_matches_AUDC"] for unit in units),
    "exceptions": [{key: unit[key] for key in ("system", "seed", "mSUN", "AUDC", "recorded_hit_flag_trapezoid_AUDC")} for unit in units if not unit["recorded_hit_flag_trapezoid_matches_AUDC"]],
    "M5_analysis_helper_mean_step_sum_AUDC": statistics.mean(unit["M5_analysis_helper_step_sum_AUDC"] for unit in units),
    "official_mean_AUDC": statistics.mean(unit["AUDC"] for unit in units),
    "helper_wrong_for_official_AUDC_units": sum(unit["M5_analysis_helper_step_sum_AUDC"] != unit["AUDC"] for unit in units),
    "requirement": "All18 zero-origin cumulative-hit curves agree with recorded final mSUN/AUDC. This is endpoint arithmetic validation; any saved curves remain labelled recorded-trajectory reconstruction, not recovered original checkpoints. Use unchanged official metric functions for paired AF/EF.",
}
(HERE / "m5_input_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
flat = [{key: unit[key] for key in ("system", "seed", "attempt", "status", "mSUN", "AUDC", "m1_full_mSUN", "m1_full_AUDC", "reference_equal_to_selected_full", "recorded_command_only_exploration_switch_differs", "actual_resolved_configuration_available", "path")} for unit in units]
with (HERE / "m5_per_unit_endpoints.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(flat[0]))
    writer.writeheader()
    writer.writerows(flat)
print(json.dumps({key: audit[key] for key in ("acceptance", "units_count", "queries", "coverage_exact_dev_6_systems_3_seeds", "attempt_counts", "source_fingerprint_comparison_count", "source_fingerprint_all_match", "broader_source_file_count", "broader_source_all_LF_equal", "received_result_files", "aggregate_exploration_off", "paired_full_minus_off")}, indent=2))
