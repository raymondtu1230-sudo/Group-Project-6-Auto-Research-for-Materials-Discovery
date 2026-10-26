"""Offline M5 supplemental-package intake: standard library plus Ruby YAML."""
from __future__ import annotations

import ast
import collections
import copy
import csv
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
M2 = HERE.parents[1]
ROOT = HERE.parent / "snapshot"
OLD = M2 / "stage_m5_intake_20261026/snapshot"
FREEZE = M2 / "runtime/frozen_reference"
RESULTS = ROOT / "M1/MADE/results/protocol_v1"
MSUN = "final/novelty_stable_unique_novel_count"
AUDC = "final/discovery_curve_area_under_discovery_curve"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(content):
    return hashlib.sha256(content).hexdigest()


def flatten(value, prefix=""):
    result = {}
    for key, child in value.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(child, dict):
            result.update(flatten(child, name))
        else:
            result[name] = child
    return result


tree = ast.parse((ROOT / "M2/evaluate.py").read_text())
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "snapshot_hash")
namespace = {"copy": copy, "hashlib": hashlib, "json": json}
exec(compile(ast.Module(body=[node], type_ignores=[]), "M2/evaluate.py:snapshot_hash", "exec"), namespace)
reference_hash = namespace["snapshot_hash"]

attempts = sorted(path.parent for path in (RESULTS / "exploration_off/dev").rglob("run_metadata.json"))
full_paths = {}
for attempt in attempts:
    metadata = read(attempt / "run_metadata.json")
    system, seed = "-".join(metadata["system"]), metadata["seed"]
    candidates = []
    for path in (RESULTS / "m1_full/dev" / system / f"seed_{seed}").glob("attempt_*/run_metadata.json"):
        full_meta = read(path)
        if full_meta.get("status") == "completed":
            candidates.append((full_meta["attempt"], path.parent))
    full_paths[attempt] = max(candidates)[1]

yaml_paths = sorted({str(path) for attempt in attempts for path in (
    attempt / "hydra/config.yaml", attempt / "hydra/overrides.yaml", attempt / "resolved_config.yaml",
    full_paths[attempt] / "hydra/config.yaml",
)})
parsed = subprocess.run(
    ["/usr/bin/ruby", "-ryaml", "-rjson", "-e", "paths=JSON.parse(STDIN.read); puts JSON.generate(paths.to_h { |p| [p,YAML.load_file(p)] })"],
    input=json.dumps(yaml_paths), text=True, capture_output=True, check=True,
)
configs = json.loads(parsed.stdout)

prior_inventory = []
for old in sorted((OLD / "M1/MADE/results/protocol_v1/exploration_off").rglob("*")):
    if old.is_file():
        rel = old.relative_to(OLD)
        now = ROOT / rel
        prior_inventory.append({"path": str(rel), "old_sha256": sha(old.read_bytes()),
                                "new_sha256": sha(now.read_bytes()) if now.exists() else None,
                                "byte_equal": now.is_file() and old.read_bytes() == now.read_bytes()})

units, manifest_checks, input_checks, normalized_errors = [], [], [], []
for attempt in attempts:
    metadata = read(attempt / "run_metadata.json")
    system, seed = "-".join(metadata["system"]), metadata["seed"]
    label = f"{system}/seed_{seed}/attempt_{metadata['attempt']:02d}"
    full = full_paths[attempt]
    full_meta = read(full / "run_metadata.json")
    payload = read(attempt / "trajectories/episode_000.json")
    full_payload = read(full / "trajectories/episode_000.json")
    summary = read(attempt / "summary/summary.json")
    episodes = read(attempt / "summary/episodes.json")
    config = configs[str(attempt / "hydra/config.yaml")]
    flat = flatten(config)
    full_flat = flatten(configs[str(full / "hydra/config.yaml")])
    diff = {key: {"full": full_flat.get(key), "off": flat.get(key)} for key in set(flat) | set(full_flat)
            if flat.get(key) != full_flat.get(key) and key != "experiment.output_dir"}
    interpolation_values = {key: value for key, value in flat.items() if isinstance(value, str) and "${" in value}
    flags = {key: config["agent"][key] for key in ("enable_planning", "enable_memory", "enable_reflection", "enable_exploration", "enable_tool_routing")}
    for key, recorded in metadata["m1_input_sha256"].items():
        data = (FREEZE / "M1" / key.replace("\\", "/")).read_bytes()
        lf = data.replace(b"\r\n", b"\n")
        matches = [name for name, data in (("raw", data), ("LF", lf), ("CRLF", lf.replace(b"\n", b"\r\n"))) if sha(data) == recorded]
        input_checks.append({"unit": label, "path": key.replace("\\", "/"), "recorded_sha256": recorded, "matching_representation": matches})
    manifest = read(attempt / "evidence_manifest.json")
    for relative, recorded in manifest["files"].items():
        path = attempt / relative
        content = path.read_bytes()
        crlf = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        matches = [name for name, data in (("received_bytes", content), ("Windows_CRLF_checkout", crlf))
                   if sha(data) == recorded["sha256"] and len(data) == recorded["bytes"]]
        manifest_checks.append({"unit": label, "path": relative, "matching_representation": matches,
                                "recorded_sha256": recorded["sha256"], "recorded_bytes": recorded["bytes"]})
    record = read(attempt / "m2_metrics_history.json")
    history = record["metrics_history"]
    cumulative, area, previous = 0, 0.0, 0
    prefix_errors = []
    for query, (step, point) in enumerate(zip(payload["trajectory"], history), start=1):
        cumulative += int(bool(step.get("is_stable") and step.get("is_newly_discovered")))
        area += (previous + cumulative) / 2
        previous = cumulative
        if not (point["queries_used"] == query and point["num_newly_discovered_stable"] == cumulative
                and point["novelty_stable_unique_novel_count"] == cumulative
                and point["discovery_curve_area_under_discovery_curve"] == area):
            prefix_errors.append(query)
        expected = area / (query**2 / 2)
        if point["discovery_curve_area_under_discovery_curve_normalized"] != expected:
            normalized_errors.append({"unit": label, "query": query, "recorded": point["discovery_curve_area_under_discovery_curve_normalized"],
                                      "official_normalization_formula": "AUDC / (queries_used**2 / 2)", "expected": expected})
    m4 = [json.loads(line) for line in (attempt / "m4_evidence.jsonl").read_text().splitlines()]
    expected_id = f"exploration_off-{system}-seed{seed}-attempt01"
    overrides = configs[str(attempt / "hydra/overrides.yaml")]
    expected_files = ("run_metadata.json", "trajectories/episode_000.json", "summary/summary.json", "summary/episodes.json", "summary/episodes.csv",
                      "hydra/config.yaml", "hydra/hydra.yaml", "hydra/overrides.yaml", "resolved_config.yaml", "m4_evidence.jsonl", "run_benchmark.log",
                      "console_attempt_01.log", "m2_metrics_history.json", "evidence_manifest.json")
    units.append({
        "unit": label, "system": system, "seed": seed, "attempt": metadata["attempt"], "status": metadata["status"],
        "attempt_path": str(attempt.relative_to(ROOT)), "selected_full_path": str(full.relative_to(ROOT)),
        "queries": len(payload["trajectory"]), "official_queries": payload["metrics"]["final/queries_used"],
        "metadata_budget": metadata["query_budget"], "episodes": summary["episodes"], "split": metadata["split"],
        "saved_Hydra_flags": flags, "saved_Hydra_scientific_differences_vs_full_excluding_output_dir": diff,
        "only_exploration_switch_differs": diff == {"agent.enable_exploration": {"full": True, "off": False}},
        "saved_config_seed_system_budget_correct": config["experiment"]["seed"] == seed and config["dataset"]["elements"] == metadata["system"] and config["environment"]["budget"] == 20,
        "override_list_equals_recorded_command": overrides == metadata["command"][1:],
        "resolved_named_file_equals_saved_composed_config": (attempt / "resolved_config.yaml").read_bytes() == (attempt / "hydra/config.yaml").read_bytes(),
        "unresolved_interpolations": interpolation_values,
        "missing_expected_package_files": [relative for relative in expected_files if not (attempt / relative).is_file()],
        "m5_decisions_absent": not (attempt / "m5_decisions.jsonl").exists(),
        "m4_proposal_events_available": (attempt / "m4_proposal_events.jsonl").exists(),
        "component_memory_record_count": len(m4), "memory_query_1_to_19": [row["query_count"] for row in m4] == list(range(1, 20)),
        "memory_run_identity_correct": {row["run_id"] for row in m4} == {expected_id},
        "console_original_copy_equal": (attempt / "console_attempt_01.log").read_bytes() == (attempt.parent / "console_attempt_01.log").read_bytes(),
        "manifest_target_matches": manifest["target_attempt"] == str(attempt.relative_to(ROOT / "M1/MADE/results")),
        "manifest_recorded_revision": manifest["recorded_revision"], "manifest_source_directory": manifest["source_directory"],
        "protocol_equal_selected_full": metadata["protocol_settings"] == full_meta["protocol_settings"],
        "canonical_reference_sha256": reference_hash(payload["phase_diagram_gt"]),
        "canonical_reference_equal_selected_full": reference_hash(payload["phase_diagram_gt"]) == reference_hash(full_payload["phase_diagram_gt"]),
        "history_source_label": record["source"], "history_query_1_to_20": record["query_counts"] == list(range(1, 21)) and len(history) == 20,
        "history_core_prefix_errors": prefix_errors,
        "mSUN": payload["metrics"][MSUN], "AUDC": payload["metrics"][AUDC],
        "core_history_final_matches_original_endpoints": cumulative == payload["metrics"][MSUN] and area == payload["metrics"][AUDC],
        "original_endpoint_files_agree": all(payload["metrics"][key] == summary["summary"][key]["mean"] == episodes[0][key] for key in (MSUN, AUDC)),
    })

broader = []
prior_audit = read(M2 / "stage_m3full_intake_20261026/audit_m3/m3_full_intake_audit.json")
for entry in prior_audit["broader_source_equivalence"]:
    relative = entry["path"]
    old, new = (FREEZE / relative).read_bytes(), (ROOT / relative).read_bytes()
    broader.append({"path": relative, "LF_equal": old.replace(b"\r\n", b"\n") == new.replace(b"\r\n", b"\n")})

audit = {
    "snapshot_commit": "b36e2a50d9d3e31fc941d827addab94db2c5d3cc",
    "original_freeze_commit": "02e0026bf450f71f4f7862228d295f5b02b49e12",
    "acceptance": {
        "recorded_core_scientific_comparison_accepted": len(units) == 18 and all(
            unit["status"] == "completed" and unit["queries"] == unit["official_queries"] == unit["metadata_budget"] == 20
            and unit["only_exploration_switch_differs"] and unit["protocol_equal_selected_full"] and unit["canonical_reference_equal_selected_full"]
            and unit["original_endpoint_files_agree"] and unit["core_history_final_matches_original_endpoints"] for unit in units),
        "original_configuration_and_component_evidence_package_received": all(not unit["missing_expected_package_files"] for unit in units),
        "named_resolved_config_fully_resolved": False,
        "reconstructed_histories_all_auxiliary_fields_correct": not normalized_errors,
        "boundary": "Core raw results and saved-Hydra one-switch comparison accepted; composed configs are not fully resolved runtime dumps, histories are labelled reconstructions, incorrect normalized-AUDC fields must be excluded or independently recalculated without altering originals.",
    },
    "units": units, "unit_count": len(units), "queries": sum(unit["queries"] for unit in units),
    "coverage_exact_6_dev_systems_3_seeds": {(unit["system"], unit["seed"]) for unit in units} == {
        (system, seed) for system in ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm") for seed in (17, 29, 43)
    } and len(units) == 18,
    "all_off_profiles_TTTFT": all(list(unit["saved_Hydra_flags"].values()) == [True, True, True, False, True] for unit in units),
    "all_saved_override_lists_equal_recorded_commands": all(unit["override_list_equals_recorded_command"] for unit in units),
    "all_named_resolved_files_equal_saved_composed_configs": all(unit["resolved_named_file_equals_saved_composed_config"] for unit in units),
    "original_prior_file_checks": prior_inventory, "prior_files_count": len(prior_inventory),
    "all_prior_files_byte_identical": all(row["byte_equal"] for row in prior_inventory),
    "source_fingerprint_checks": input_checks, "source_fingerprint_count": len(input_checks),
    "source_fingerprints_all_match_original_freeze": all(row["matching_representation"] for row in input_checks),
    "broader_source_checks": broader, "broader_source_count": len(broader), "broader_source_all_equal": all(row["LF_equal"] for row in broader),
    "manifest_checks": manifest_checks, "manifest_entries": len(manifest_checks),
    "manifest_all_hash_and_byte_counts_match": all(row["matching_representation"] for row in manifest_checks),
    "core_reconstructed_prefix_count": sum(len(read(attempt / "m2_metrics_history.json")["metrics_history"]) for attempt in attempts),
    "core_reconstructed_prefix_all_match_recorded_hits": all(not unit["history_core_prefix_errors"] for unit in units),
    "normalized_AUDC_errors": normalized_errors, "normalized_AUDC_mismatch_count": len(normalized_errors),
    "no_model_oracle_agent_calls": True, "no_scientific_runtime_imports": True, "no_remote_mutations": True,
    "scientific_scope": "Existing dev records only; no rerun, proposal, energy calculation or hidden/check evaluation.",
    "metadata_revision_boundary": "Recorded aedf8ca is a shared-repository documentation commit, not original frozen HEAD or MADE upstream. Unchanged original metadata and frozen scientific input hashes are retained; no provenance fields were rewritten.",
    "optional_proposal_capture_boundary": "m4_proposal_events.jsonl is absent in all18 packages. Frozen capture code writes only rejection/error events, so an absent optional sidecar alone does not establish missing scientific outcomes. M4 evaluated-outcome evidence is present for queries1..19 in every unit.",
}
(HERE / "m5_supplement_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
rows = [{key: unit[key] for key in ("unit", "system", "seed", "attempt", "status", "mSUN", "AUDC", "only_exploration_switch_differs", "canonical_reference_equal_selected_full", "core_history_final_matches_original_endpoints", "component_memory_record_count", "attempt_path")} for unit in units]
with (HERE / "m5_supplement_units.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps({key: audit[key] for key in ("acceptance", "unit_count", "queries", "prior_files_count", "all_prior_files_byte_identical", "source_fingerprint_count", "source_fingerprints_all_match_original_freeze", "broader_source_count", "broader_source_all_equal", "manifest_entries", "manifest_all_hash_and_byte_counts_match", "core_reconstructed_prefix_count", "core_reconstructed_prefix_all_match_recorded_hits", "normalized_AUDC_mismatch_count")}, indent=2))
