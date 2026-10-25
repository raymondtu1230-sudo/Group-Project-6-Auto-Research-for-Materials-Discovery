"""Report preserved real M2 ablations and the frozen M1 final metrics.

No models, agents, datasets, or oracles are invoked.  The reporter only reads
the original outputs and the collection/validation evidence saved after runs.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import html
import json
import math
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any

METHOD = "tool_routing_off"
REFERENCE = "m1_full"
COMMIT = "02e0026bf450f71f4f7862228d295f5b02b49e12"
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
SEEDS = (17, 29, 43)
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
AUDC = "final/discovery_curve_area_under_discovery_curve"
EXPECTED = {(system, seed) for system in SYSTEMS for seed in SEEDS}
# The live artifact upload excludes hidden files. These raw Hydra originals are
# useful audit attachments, but they are distinct from the required, visible
# resolved_config.yaml. Their absence must remain explicit; their bytes must
# never be reconstructed or a different existing-file hash accepted.
RAW_HYDRA_TRANSPORT_OMISSIONS = {
    ".hydra/config.yaml",
    ".hydra/hydra.yaml",
    ".hydra/overrides.yaml",
}
REQUIRED_VISIBLE_FILES = {
    "run_metadata.json",
    "resolved_config.yaml",
    "trajectories/episode_000.json",
    "summary/summary.json",
    "m4_evidence.jsonl",
    "m5_decisions.jsonl",
    "m2_metrics_history.json",
    "m2_process.log",
    "m2_exit.json",
    "m2_collection.json",
}
DELETED_HISTORY_AUDIT_ERRORS = {
    "Original-evidence collection has missing files or errors",
    "Official checkpoint history does not cover queries1..20",
    "Original official checkpoints were not preserved",
}


def read_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError:
        # macOS provides Psych with Ruby; safe_load permits no executable YAML
        # objects. The captured output is parsed internally and never printed.
        code = "print JSON.generate(YAML.safe_load(File.read(ARGV.fetch(0)), permitted_classes: [], permitted_symbols: [], aliases: false))"
        return json.loads(
            subprocess.check_output(
                ["ruby", "-ryaml", "-rjson", "-e", code, str(path)], text=True
            )
        )
    return yaml.safe_load(path.read_text())


def endpoint_audit(
    run: dict[str, Any],
    original: dict[str, Any],
    collection: dict[str, Any],
    frozen_root: Path | None,
) -> dict[str, Any]:
    """A new independent endpoint audit; original failed audits stay untouched."""
    if (
        original.get("accepted") is not False
        or set(original.get("errors", [])) != DELETED_HISTORY_AUDIT_ERRORS
    ):
        raise ValueError(
            "Original validation failure is outside exact deleted-history whitelist"
        )
    if collection.get("errors") != [
        "No matching original official checkpoint was available"
    ]:
        raise ValueError(
            "Collection failure is not solely the deleted official checkpoint"
        )
    if (
        collection.get("official_checkpoints") != []
        or collection.get("resolved_config_saved") is not True
        or collection.get("original_metadata_unchanged") is not True
    ):
        raise ValueError(
            "Deleted-checkpoint fallback has incompatible collection evidence"
        )
    if frozen_root is None or not (frozen_root / "M1/run_experiment.py").is_file():
        raise ValueError(
            "Independent endpoint audit requires the actual frozen scientific source tree"
        )
    directory, metadata = run["directory"], run["metadata"]
    config = read_yaml(directory / "resolved_config.yaml")
    seed = metadata["seed"]
    if (
        config.get("experiment", {}).get("seed") != seed
        or config.get("experiment", {}).get("num_episodes") != 1
        or config.get("dataset", {}).get("elements") != metadata["system"]
    ):
        raise ValueError("Endpoint resolved seed/system/episode count mismatch")
    if config.get("dataset", {}).get("thermo_types") != ["GGA_GGA+U"]:
        raise ValueError("Endpoint dataset thermo types changed")
    environment = config.get("environment", {})
    expected_environment = {
        "budget": 20,
        "stability_tolerance": 0.1,
        "max_stoichiometry": 20,
        "filter_by_smact": True,
        "include_near_stable_from_ground_truth": True,
        "start_with_all_stable": True,
        "compute_elemental_from_oracle": True,
    }
    if any(
        environment.get(key) != value for key, value in expected_environment.items()
    ):
        raise ValueError("Endpoint environment scientific settings changed")
    oracle = config.get("oracle", {})
    if (
        oracle.get("_target_") != "made.oracles.ORBOracle"
        or oracle.get("model_name") != "orb-v3-conservative-inf-omat"
        or oracle.get("device") != "cpu"
        or oracle.get("relax") is not True
        or oracle.get("relax_kwargs")
        != {"optimizer": "fire", "fmax": 0.02, "steps": 500, "relax_unit_cell": True}
    ):
        raise ValueError("Endpoint CPU ORB/relaxation settings changed")
    agent = config.get("agent", {})
    for key in (
        "enable_planning",
        "enable_memory",
        "enable_reflection",
        "enable_exploration",
        "enable_tool_routing",
    ):
        if agent.get(key) is not (key != "enable_tool_routing"):
            raise ValueError(f"Endpoint component switch differs: {key}")
    generator = agent.get("generator", {})
    if (
        generator.get("_target_")
        != "made.agents.m2_tool_routing.CheckpointedRandomGenerator"
        or generator.get("seed") != seed
        or generator.get("lattice_length_range") != [3.0, 15.0]
        or generator.get("lattice_angle_range") != [60.0, 120.0]
    ):
        raise ValueError("Endpoint frozen primary Random generator changed")
    chemeleon = agent.get("generators", {}).get("chemeleon", {})
    if any(
        chemeleon.get(key) != value
        for key, value in {
            "_target_": "made.agents.m2_tool_routing.CheckpointedChemeleonGenerator",
            "seed": seed,
            "task": "csp",
            "batch_size": 32,
            "device": "cpu",
            "output_dir": None,
        }.items()
    ):
        raise ValueError("Endpoint frozen Chemeleon generator changed")
    if (
        agent.get("planner", {}).get("_target_")
        != "made.agents.m3_planning.M3ResearchPlanner"
        or agent.get("planner", {}).get("seed") != seed
        or agent.get("scorer", {}).get("seed") != seed
    ):
        raise ValueError("Endpoint frozen planner/scorer seed changed")
    log = (directory / "m2_process.log").read_text()
    cleanup = re.findall(
        r"Removed checkpoint file [^\r\n]+/checkpoint\.json after successful completion",
        log,
    )
    if len(cleanup) != 1:
        raise ValueError(
            "Official successful-completion checkpoint cleanup event is missing or ambiguous"
        )
    if (
        read_json(directory / "m2_exit.json").get("exit_code") != 0
        or collection.get("exit_code") != 0
    ):
        raise ValueError("Endpoint original real process did not exit0")
    if run["trajectory"].get("final_env_state", {}).get("query_count") != 20:
        raise ValueError("Endpoint final environment state is not query20")
    for filename, expected in (
        ("m4_evidence.jsonl", list(range(1, 20))),
        ("m5_decisions.jsonl", list(range(20))),
    ):
        records = [
            json.loads(line)
            for line in (directory / filename).read_text().splitlines()
            if line.strip()
        ]
        json.dumps(records, allow_nan=False)
        if [row.get("query_count") for row in records] != expected:
            raise ValueError(
                f"Endpoint component log incomplete or duplicated: {filename}"
            )
    hashes = metadata.get("m1_input_sha256", {})
    if (
        not hashes
        or original.get("source_input_hashes_checked") != len(hashes)
        or original.get("source_input_hash_mismatches") != []
    ):
        raise ValueError("Original source audit count/mismatch record invalid")
    for relative, expected in hashes.items():
        path = frozen_root / "M1" / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(
                f"Independent frozen scientific source SHA256 mismatch: {relative}"
            )
    return {
        "audit_type": "independent_final_endpoint_audit_after_official_checkpoint_cleanup",
        "accepted_final_endpoints": True,
        "original_m2_validation_accepted": False,
        "original_m2_validation_errors": original["errors"],
        "original_m2_validation_sha256": sha256(directory / "m2_validation.json"),
        "original_collection_errors": collection["errors"],
        "official_cleanup_log_event": cleanup[0],
        "independently_checked_source_hashes": len(hashes),
        "resolved_configuration_and_component_logs_verified": True,
        "original_per_query_history_available": False,
        "original_checkpoint_available": False,
        "missing_history_reason": "The unchanged official runner deletes its checkpoint after successful completion; post-exit collection found none.",
        "curve_or_AF_EF_accepted_by_this_audit": False,
        "new_scientific_queries": 0,
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def snapshot_hash(entries: list[dict[str, Any]]) -> str:
    """Use the same independent-data canonicalization as M2/evaluate.py."""
    canonical = copy.deepcopy(entries)
    for entry in canonical:
        attribute = entry.get("attribute")
        structure = attribute.get("structure") if isinstance(attribute, dict) else None
        if not isinstance(structure, dict):
            continue
        lattice = structure.get("lattice", {})
        if "matrix" in lattice:
            for field in ("a", "b", "c", "alpha", "beta", "gamma", "volume"):
                lattice.pop(field, None)
        for site in structure.get("sites", []):
            if "matrix" in lattice and "abc" in site:
                site.pop("xyz", None)
    values = sorted(
        json.dumps(x, sort_keys=True, separators=(",", ":")) for x in canonical
    )
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def label(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_runs(
    root: Path, method: str, own: bool, frozen_root: Path | None = None
) -> tuple[
    dict[tuple[str, int], dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    accepted: dict[tuple[str, int], dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for path in sorted(root.rglob("run_metadata.json")):
        directory = path.parent
        source = label(directory, root)
        try:
            metadata = read_json(path)
            if metadata.get("method") != method or metadata.get("split") != "dev":
                continue
            system, seed = "-".join(metadata["system"]), metadata["seed"]
            key = (system, seed)
            if key not in EXPECTED:
                raise ValueError("Unexpected dev system/seed")
            if metadata.get("status") != "completed":
                failures.append(
                    {
                        "method": method,
                        "system": system,
                        "seed": seed,
                        "attempt": metadata.get("attempt"),
                        "status": metadata.get("status"),
                        "error": metadata.get("error"),
                        "source": source,
                    }
                )
                continue
            if metadata.get("query_budget") != 20 or metadata.get("episodes") != 1:
                raise ValueError("Completed run does not use B20 and one episode")
            trajectory = read_json(directory / "trajectories/episode_000.json")
            summary = read_json(directory / "summary/summary.json")
            metrics = trajectory.get("metrics", {})
            if (
                len(trajectory.get("trajectory", [])) != 20
                or metrics.get("final/queries_used") != 20
            ):
                raise ValueError("Trajectory and final query count do not both equal20")
            if summary.get("episodes") != 1:
                raise ValueError("Summary does not contain one episode")
            for field in ("final/" + MSUN, AUDC):
                if not finite(metrics.get(field)):
                    raise ValueError(f"Nonfinite official final metric: {field}")
                summarized = summary.get("summary", {}).get(field, {}).get("mean")
                if summarized != metrics[field]:
                    raise ValueError(f"Summary/trajectory disagreement: {field}")
            reference = trajectory.get("phase_diagram_gt")
            if not isinstance(reference, list) or not reference:
                raise ValueError("Material reference snapshot missing")
            run = {
                "directory": directory,
                "source": source,
                "metadata": metadata,
                "trajectory": trajectory,
                "mSUN_at_20": metrics["final/" + MSUN],
                "AUDC": metrics[AUDC],
                "reference_hash": snapshot_hash(reference),
            }
            if own:
                validation = read_json(directory / "m2_validation.json")
                endpoint_candidate = (
                    validation.get("accepted") is False
                    and set(validation.get("errors", []))
                    == DELETED_HISTORY_AUDIT_ERRORS
                )
                if not endpoint_candidate and (
                    validation.get("accepted") is not True or validation.get("errors")
                ):
                    raise ValueError("Saved M2 audit did not accept this attempt")
                if (
                    validation.get("actual_git_head") != COMMIT
                    or validation.get("actual_tag_commit") != COMMIT
                ):
                    raise ValueError(
                        "Saved audit does not identify the required frozen commit/tag"
                    )
                if validation.get("tracked_worktree_clean") is not True:
                    raise ValueError("Saved tracked-worktree check was not clean")
                if (
                    validation.get("canonical_material_reference_sha256")
                    != run["reference_hash"]
                ):
                    raise ValueError(
                        "Persisted trajectory reference differs from accepted audit"
                    )
                collection = read_json(directory / "m2_collection.json")
                if collection.get("exit_code") != 0 or (
                    collection.get("collection_complete") is not True
                    and not endpoint_candidate
                ):
                    raise ValueError("Process/collection did not finish successfully")
                if collection.get("original_metadata_sha256") != sha256(path):
                    raise ValueError("Original metadata integrity check failed")
                manifest = read_json(directory / "m2_sha256_manifest.json").get(
                    "files", {}
                )
                if not manifest:
                    raise ValueError("Preserved-file integrity manifest is empty")
                for relative in REQUIRED_VISIBLE_FILES:
                    if relative not in manifest or not (directory / relative).is_file():
                        raise ValueError(
                            f"Required visible result file missing: {relative}"
                        )
                missing_originals = []
                for relative, expected_sha in manifest.items():
                    file = directory / relative
                    if not file.is_file():
                        if relative in RAW_HYDRA_TRANSPORT_OMISSIONS:
                            missing_originals.append(
                                {
                                    "path": relative,
                                    "expected_sha256": expected_sha,
                                    "classification": "missing_hidden_hydra_original_after_transport",
                                    "original_reconstructed": False,
                                }
                            )
                            continue
                        raise ValueError(
                            f"Preserved-file SHA256 check missing file: {relative}"
                        )
                    if sha256(file) != expected_sha:
                        raise ValueError(f"Preserved-file SHA256 mismatch: {relative}")
                if not endpoint_candidate and not any(
                    relative.startswith("official_checkpoints/")
                    for relative in manifest
                ):
                    raise ValueError(
                        "Preserved official checkpoint is missing from manifest"
                    )
                run["required_visible_payload_verified"] = True
                run["raw_hydra_transport_omissions"] = missing_originals
                capture = read_json(directory / "m2_metrics_history.json")
                history = capture.get("metrics_history", [])
                history_available = capture.get("complete_curve") is True and [
                    x.get("queries_used") for x in history
                ] == list(range(1, 21))
                if not history_available and not endpoint_candidate:
                    raise ValueError(
                        "Official saved history does not cover queries1..20"
                    )
                if endpoint_candidate:
                    run["endpoint_audit"] = endpoint_audit(
                        run, validation, collection, frozen_root
                    )
                for point in history if history_available else []:
                    for field in (MSUN, CURVE):
                        if (
                            not finite(point.get(field))
                            or not 0 <= point[field] <= point["queries_used"]
                        ):
                            raise ValueError(
                                f"Invalid official history metric: {field}"
                            )
                if history_available and history[-1][MSUN] != run["mSUN_at_20"]:
                    raise ValueError("Saved official history/final mSUN mismatch")
                recomputed_audc = validation.get("official_audc_recomputed")
                if history_available and (
                    not finite(recomputed_audc)
                    or not math.isclose(
                        recomputed_audc, run["AUDC"], rel_tol=1e-9, abs_tol=1e-9
                    )
                ):
                    raise ValueError(
                        "Saved official AUDC recomputation/final metric mismatch"
                    )
                if history_available:
                    run["history"] = history
                    run["history_source"] = "original_official_checkpoint_history"
                run["original_full_audit_accepted"] = validation.get("accepted") is True
            if key in accepted:
                raise ValueError(
                    "More than one accepted completed attempt for the same unit; deduplicate explicitly"
                )
            accepted[key] = run
        except Exception as error:
            issues.append(
                {
                    "method": method,
                    "source": source,
                    "error": f"{type(error).__name__}: {error}",
                }
            )
    return accepted, failures, issues


def costs(
    runs: dict[tuple[str, int], dict[str, Any]], method: str
) -> list[dict[str, Any]]:
    rows = []
    for (system, seed), run in sorted(runs.items()):
        metadata = run["metadata"]
        cost = metadata.get("cost", {})
        llm = cost.get("llm", {})
        rows.append(
            {
                "method": method,
                "system": system,
                "seed": seed,
                "attempt": metadata.get("attempt"),
                "oracle_queries": 20,
                "wall_time_seconds": metadata.get("wall_time_seconds"),
                "machine": metadata.get("machine"),
                "processor": metadata.get("processor"),
                "platform": metadata.get("platform"),
                "python": metadata.get("python"),
                "total_known_cost_usd": cost.get("total_known_cost_usd"),
                "recorded_total_cost_status": cost.get(
                    "total_cost_status", "not_reported"
                ),
                "report_cost_scope": "partial: hardware/electricity and unpriced failed attempts excluded",
                "llm_calls": llm.get("calls"),
                "llm_input_tokens": llm.get("input_tokens"),
                "llm_output_tokens": llm.get("output_tokens"),
                "llm_cost_usd": llm.get("cost_usd"),
                "source": run["source"],
            }
        )
    return rows


def attach_reevaluated_curves(
    runs: dict[tuple[str, int], dict[str, Any]], root: Path, frozen_root: Path | None
) -> dict[str, Any]:
    """Read separately labelled record-only analysis after its full proof gate."""
    proof = read_json(root / "reevaluation_audit.json")
    required = {
        "accepted": True,
        "baseline_units_validated": 36,
        "original_baseline_prefixes_validated": 720,
        "frozen_reference_units_validated": 18,
        "routing_units_validated": 18,
        "routing_complete": True,
        "original_endpoint_units_validated": 72,
        "all_original_mSUN_and_AUDC_endpoints_match": True,
    }
    if any(proof.get(key) != value for key, value in required.items()):
        raise ValueError(
            "Record-only curve analysis has not passed complete720-prefix/72-endpoint proof"
        )
    if frozen_root is None:
        raise ValueError("Frozen source tree required to verify record-only analysis")
    pending = []
    for (system, seed), run in runs.items():
        attempt = run["metadata"].get("attempt", 1)
        path = (
            root
            / METHOD
            / system
            / f"seed_{seed}"
            / f"attempt_{attempt:02d}"
            / "reevaluated_curve.json"
        )
        curve = read_json(path)
        trajectory_sha = sha256(run["directory"] / "trajectories/episode_000.json")
        if (
            curve.get("accepted") is not True
            or curve.get("analysis_kind") != "offline_recorded_trajectory_re_evaluation"
            or curve.get("historical_checkpoint_recovered") is not False
        ):
            raise ValueError(
                f"Unaccepted or mislabelled record-only curve: {system}/{seed}"
            )
        if (
            curve.get("original_trajectory_sha256") != trajectory_sha
            or curve.get("input_sha256", {}).get("trajectories/episode_000.json")
            != trajectory_sha
            or curve.get("canonical_material_reference_sha256") != run["reference_hash"]
        ):
            raise ValueError(
                f"Record-only curve input identity differs: {system}/{seed}"
            )
        matches = curve.get("original_endpoint_matches", {})
        if len(matches) < 3 or any(value is not True for value in matches.values()):
            raise ValueError(
                f"Record-only endpoint comparison did not pass: {system}/{seed}"
            )
        source_hashes = curve.get("scientific_source_sha256", {})
        if not source_hashes:
            raise ValueError("Record-only scientific source identity missing")
        for relative, expected in source_hashes.items():
            source = frozen_root / relative
            if not source.is_file() or sha256(source) != expected:
                raise ValueError(
                    f"Record-only scientific source SHA256 differs: {relative}"
                )
        history = curve.get("reevaluated_metrics_history", [])
        if [point.get("queries_used") for point in history] != list(range(1, 21)):
            raise ValueError(
                f"Record-only history does not cover queries1..20: {system}/{seed}"
            )
        for point in history:
            if any(
                not finite(point.get(key))
                or not 0 <= point[key] <= point["queries_used"]
                for key in (MSUN, CURVE)
            ):
                raise ValueError(f"Invalid record-only history: {system}/{seed}")
        if (
            history[-1].get(MSUN) != run["mSUN_at_20"]
            or history[-1].get(CURVE)
            != run["trajectory"]["metrics"].get("final/" + CURVE)
            or not math.isclose(
                history[-1].get("discovery_curve_area_under_discovery_curve", -1),
                run["AUDC"],
                abs_tol=1e-9,
                rel_tol=1e-9,
            )
        ):
            raise ValueError(
                f"Record-only history and original final metrics differ: {system}/{seed}"
            )
        pending.append((run, history, path))
    for run, history, path in pending:
        run["history"] = history
        run["history_source"] = (
            "separately_validated_offline_recorded_trajectory_re_evaluation_not_checkpoint_recovery"
        )
        run["curve_analysis_source"] = str(path)
        run["curve_analysis_sha256"] = sha256(path)
    return {
        "accepted": True,
        "global_proof_source": str(root / "reevaluation_audit.json"),
        "global_proof_sha256": sha256(root / "reevaluation_audit.json"),
        "own_histories_attached": len(runs),
        "historical_checkpoint_recovered": False,
        "kind": "offline_recorded_trajectory_re_evaluation",
    }


def curve_svg(runs: dict[tuple[str, int], dict[str, Any]], destination: Path) -> None:
    """Plot actual saved official M2 history; no missing M1 curve is invented."""
    width, height = 1220, 1920
    curve_description = (
        "Mean ± sample SD across three seeds; separately validated record-only re-evaluation, not checkpoint recovery."
        if any("curve_analysis_source" in run for run in runs.values())
        else "Mean ± sample SD across three seeds; points come from original preserved official query histories."
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        "<style>text{font-family:Arial,sans-serif;fill:#17243b}.axis{stroke:#34425a;stroke-width:1}.grid{stroke:#e5eaf2;stroke-width:1}</style>",
        '<text x="65" y="38" font-size="24" font-weight="bold">M2 tool_routing_off: official development discovery curves</text>',
        f'<text x="65" y="64" font-size="14">{html.escape(curve_description)}</text>',
    ]
    for row, system in enumerate(SYSTEMS):
        group = [
            runs[(system, seed)]
            for seed in SEEDS
            if (system, seed) in runs and "history" in runs[(system, seed)]
        ]
        for column, metric in enumerate((MSUN, CURVE)):
            left, top, plot_w, plot_h = 75 + column * 600, 125 + row * 285, 490, 190
            title = "mSUN" if metric == MSUN else "Official AUDC-source count"
            parts.append(
                f'<text x="{left}" y="{top - 20}" font-size="16" font-weight="bold">{html.escape(system)} · {title} (n={len(group)})</text>'
            )
            for tick in (0, 5, 10, 15, 20):
                x, y = left + plot_w * tick / 20, top + plot_h * (1 - tick / 20)
                parts.extend(
                    [
                        f'<line x1="{left}" y1="{y}" x2="{left + plot_w}" y2="{y}" class="grid"/>',
                        f'<text x="{left - 12}" y="{y + 4}" text-anchor="end" font-size="12">{tick}</text>',
                        f'<text x="{x}" y="{top + plot_h + 20}" text-anchor="middle" font-size="12">{tick}</text>',
                    ]
                )
            parts.extend(
                [
                    f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis"/>',
                    f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis"/>',
                    f'<text x="{left + plot_w / 2}" y="{top + plot_h + 42}" text-anchor="middle" font-size="13">Oracle queries</text>',
                ]
            )
            if not group:
                continue
            histories = [
                [0, *[point[metric] for point in run["history"]]] for run in group
            ]
            means = [statistics.mean(values) for values in zip(*histories, strict=True)]
            deviations = [
                statistics.stdev(values) if len(values) > 1 else 0
                for values in zip(*histories, strict=True)
            ]

            def point(
                index: int,
                value: float,
                left=left,
                top=top,
                plot_w=plot_w,
                plot_h=plot_h,
            ) -> str:
                return f"{left + plot_w * index / 20:.2f},{top + plot_h * (1 - value / 20):.2f}"

            upper = [point(i, min(20, means[i] + deviations[i])) for i in range(21)]
            lower = [
                point(i, max(0, means[i] - deviations[i])) for i in reversed(range(21))
            ]
            parts.append(
                f'<polygon points="{" ".join(upper + lower)}" fill="#246ac8" fill-opacity="0.16"/>'
            )
            line = " ".join(point(i, value) for i, value in enumerate(means))
            parts.append(
                f'<polyline points="{line}" fill="none" stroke="#246ac8" stroke-width="2.6"/>'
            )
    parts.extend(
        [
            '<text x="65" y="1870" font-size="14">This figure plots M2 only. Missing original checkpoint histories have not been re-labelled as recovered originals.</text>',
            '<text x="65" y="1895" font-size="13">The zero-query discovery count is zero by protocol. Shading is clipped to the feasible count range [0,20].</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts))


def report(
    results_root: Path,
    reference_root: Path,
    output: Path,
    frozen_root: Path | None = None,
    curve_analysis_root: Path | None = None,
) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Report directory already contains files; choose a new directory"
        )
    if frozen_root is None and len(reference_root.parents) > 5:
        candidate = reference_root.parents[5]
        if (candidate / "M1/run_experiment.py").is_file():
            frozen_root = candidate
    own, failed, issues = load_runs(results_root, METHOD, True, frozen_root)
    reference, reference_failed, reference_issues = load_runs(
        reference_root, REFERENCE, False
    )
    issues.extend(reference_issues)
    curve_audit: dict[str, Any] = {"accepted": False, "status": "not_supplied"}
    if curve_analysis_root is not None:
        try:
            curve_audit = attach_reevaluated_curves(
                own, curve_analysis_root, frozen_root
            )
        except Exception as error:
            curve_audit = {
                "accepted": False,
                "error": f"{type(error).__name__}: {error}",
            }
    paired = []
    missing_audit = []
    for key in sorted(EXPECTED & set(reference)):
        run = reference[key]
        missing = [
            name
            for name in (
                "resolved_config.yaml",
                ".hydra/config.yaml",
                "m2_metrics_history.json",
                "m4_evidence.jsonl",
                "m5_decisions.jsonl",
            )
            if not (run["directory"] / name).is_file()
        ]
        if missing:
            missing_audit.append(
                {
                    "system": key[0],
                    "seed": key[1],
                    "source": run["source"],
                    "missing": missing,
                }
            )
    for (system, seed), run in sorted(own.items()):
        baseline = reference.get((system, seed))
        pair_valid = baseline is not None
        if baseline is not None:
            for field in ("protocol_settings", "m1_input_sha256"):
                if run["metadata"].get(field) != baseline["metadata"].get(field):
                    issues.append(
                        {
                            "method": METHOD,
                            "system": system,
                            "seed": seed,
                            "error": f"Paired frozen-reference {field} mismatch",
                        }
                    )
                    pair_valid = False
            if run["reference_hash"] != baseline["reference_hash"]:
                issues.append(
                    {
                        "method": METHOD,
                        "system": system,
                        "seed": seed,
                        "error": "Paired material-reference revision differs",
                    }
                )
                pair_valid = False
        metadata = run["metadata"]
        paired.append(
            {
                "system": system,
                "seed": seed,
                "method": METHOD,
                "attempt": metadata.get("attempt"),
                "B": 20,
                "oracle_queries": 20,
                "mSUN_at_20": run["mSUN_at_20"],
                "AUDC": run["AUDC"],
                "m1_full_mSUN_at_20": baseline["mSUN_at_20"] if pair_valid else None,
                "m1_full_AUDC": baseline["AUDC"] if pair_valid else None,
                "delta_mSUN_off_minus_full": run["mSUN_at_20"] - baseline["mSUN_at_20"]
                if pair_valid
                else None,
                "delta_AUDC_off_minus_full": run["AUDC"] - baseline["AUDC"]
                if pair_valid
                else None,
                "pair_status": "matched_system_seed_budget_protocol_inputs_material_reference"
                if pair_valid
                else "missing_or_incompatible_reference",
                "wall_time_seconds": metadata.get("wall_time_seconds"),
                "machine": metadata.get("machine"),
                "canonical_material_reference_sha256": run["reference_hash"],
                "source": run["source"],
                "m1_reference_source": baseline["source"] if baseline else None,
                "endpoint_acceptance_scope": "new_endpoint_audit_original_failure_preserved"
                if "endpoint_audit" in run
                else "original_complete_run_audit",
                "per_query_history_source": run.get(
                    "history_source", "unavailable_after_official_checkpoint_cleanup"
                ),
                "curve_analysis_source": run.get("curve_analysis_source"),
                "curve_analysis_sha256": run.get("curve_analysis_sha256"),
                "required_visible_payload_verified": run.get(
                    "required_visible_payload_verified", False
                ),
                "raw_hydra_originals_complete_after_transport": not run.get(
                    "raw_hydra_transport_omissions"
                ),
                "raw_hydra_originals_missing_after_transport": len(
                    run.get("raw_hydra_transport_omissions", [])
                ),
            }
        )
    missing_own = sorted(EXPECTED - set(own))
    missing_reference = sorted(EXPECTED - set(reference))
    complete = (
        not missing_own
        and not missing_reference
        and not issues
        and len(paired) == 18
        and all(row["pair_status"].startswith("matched_") for row in paired)
    )
    transport_omissions = [
        {
            "system": system,
            "seed": seed,
            "source": run["source"],
            "missing_originals": run["raw_hydra_transport_omissions"],
        }
        for (system, seed), run in sorted(own.items())
        if run.get("raw_hydra_transport_omissions")
    ]
    audit = {
        "frozen_commit": COMMIT,
        "split": "dev",
        "method": METHOD,
        "expected_unique_units": 18,
        "accepted_unique_units": len(own),
        "reference_unique_units": len(reference),
        "missing_own_units": missing_own,
        "missing_reference_units": missing_reference,
        "issues": issues,
        "own_failed_attempts_preserved": len(failed),
        "reference_failed_attempts_preserved": len(reference_failed),
        "complete_paired_final_metric_comparison": complete,
        "endpoint_only_new_audit_accepted_units": sum(
            "endpoint_audit" in run for run in own.values()
        ),
        "original_full_pretransport_audit_accepted_units": sum(
            run.get("original_full_audit_accepted", False) for run in own.values()
        ),
        "own_per_query_histories_available": sum(
            "history" in run for run in own.values()
        ),
        "record_only_curve_analysis": curve_audit,
        "original_checkpoint_and_history_collection_complete": len(own) == 18
        and all("endpoint_audit" not in run for run in own.values()),
        "required_visible_m2_payload_verified_units": sum(
            run.get("required_visible_payload_verified", False) for run in own.values()
        ),
        "m2_accepted_attempt_manifest_bytes_all_available_after_transport": not transport_omissions
        and len(own) == 18
        and not issues,
        "m2_raw_hydra_transport_omissions": transport_omissions,
        "m2_transport_omission_audit_scope": "Accepted completed attempts; failed attempts remain separately indexed without an all-bytes-preserved claim.",
        "transport_omission_policy": "Only missing raw .hydra/config.yaml, .hydra/hydra.yaml and .hydra/overrides.yaml are separately recorded as absent originals. Every existing-file hash must match; every other missing manifest entry is fatal. No original is reconstructed.",
        "m1_missing_original_audit_attachments": missing_audit,
        "m1_missing_attachments_block_final_metric_pairing": False,
        "m1_full_curves_and_AF_EF": "not computed: original per-query history unavailable",
        "independent_baseline_comparisons": "not computed: baseline raw runs not supplied to this reporter",
        "aggregation": "six equally weighted systems within each seed; mean and sample SD across the three seed means",
        "cost_scope": "Recorded known fees only; hardware, electricity and all unpriced failed attempts remain excluded.",
    }
    seed_rows, summaries = [], []
    fields = {
        METHOD: ("mSUN_at_20", "AUDC"),
        REFERENCE: ("m1_full_mSUN_at_20", "m1_full_AUDC"),
        "paired_delta_off_minus_full": (
            "delta_mSUN_off_minus_full",
            "delta_AUDC_off_minus_full",
        ),
    }
    for method, (msun_field, audc_field) in fields.items():
        group_rows = []
        for seed in SEEDS:
            units = [row for row in paired if row["seed"] == seed]
            valid = (
                not issues
                and len(units) == 6
                and all(
                    finite(row.get(msun_field)) and finite(row.get(audc_field))
                    for row in units
                )
            )
            row = {
                "method": method,
                "seed": seed,
                "systems_available": len(units),
                "systems_expected": 6,
                "complete_seed": valid,
                "mSUN_at_20_mean": statistics.mean(x[msun_field] for x in units)
                if valid
                else None,
                "AUDC_mean": statistics.mean(x[audc_field] for x in units)
                if valid
                else None,
            }
            seed_rows.append(row)
            group_rows.append(row)
        valid = all(row["complete_seed"] for row in group_rows)
        summaries.append(
            {
                "method": method,
                "complete_18_unit_sweep": valid,
                "seed_n": sum(row["complete_seed"] for row in group_rows),
                "units_expected": 18,
                "mSUN_at_20_mean": statistics.mean(
                    row["mSUN_at_20_mean"] for row in group_rows
                )
                if valid
                else None,
                "mSUN_at_20_seed_sample_SD": statistics.stdev(
                    row["mSUN_at_20_mean"] for row in group_rows
                )
                if valid
                else None,
                "AUDC_mean": statistics.mean(row["AUDC_mean"] for row in group_rows)
                if valid
                else None,
                "AUDC_seed_sample_SD": statistics.stdev(
                    row["AUDC_mean"] for row in group_rows
                )
                if valid
                else None,
            }
        )
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "perunit.csv", paired)
    write_csv(output / "seed_aggregate.csv", seed_rows)
    write_csv(output / "method_summary.csv", summaries)
    write_csv(output / "costs.csv", costs(own, METHOD) + costs(reference, REFERENCE))
    (output / "validation.json").write_text(
        json.dumps(audit, indent=2, allow_nan=False) + "\n"
    )
    (output / "failed_attempts.json").write_text(
        json.dumps(failed + reference_failed, indent=2, allow_nan=False) + "\n"
    )
    (output / "independent_endpoint_audits.json").write_text(
        json.dumps(
            [
                {
                    "system": system,
                    "seed": seed,
                    "source": run["source"],
                    "audit": run["endpoint_audit"],
                }
                for (system, seed), run in sorted(own.items())
                if "endpoint_audit" in run
            ],
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    if any("history" in run for run in own.values()):
        curve_svg(own, output / "official_curves.svg")
    rows = [
        "| Method | mSUN@20 mean ± seed SD | AUDC mean ± seed SD |",
        "| --- | --- | --- |",
    ]
    for summary in summaries:
        if summary["complete_18_unit_sweep"]:
            rows.append(
                f"| {summary['method']} | {summary['mSUN_at_20_mean']:.4f} ± {summary['mSUN_at_20_seed_sample_SD']:.4f} | {summary['AUDC_mean']:.4f} ± {summary['AUDC_seed_sample_SD']:.4f} |"
            )
        else:
            rows.append(f"| {summary['method']} | incomplete | incomplete |")
    text = f"""# M2 frozen development tool-routing ablation

Frozen source: `{COMMIT}` (`m1-freeze-20261025`). Accepted M2 units: {len(own)}/18.
Complete paired final-metric comparison: {complete}.

Final discovery values come from actual original official trajectories and
summaries. Curve sources are labelled separately below. This reporter invokes no agent,
model, oracle, Materials Project request or simulated experiment.

{chr(10).join(rows)}

Each seed mean gives the six systems equal weight. The final mean and sample
standard deviation are calculated across the three seed means, not across18
independent seeds. Delta is `tool_routing_off - m1_full`; positive values favor
the routing-off condition and negative values favor full routing.

`perunit.csv` contains the paired final scores and differences. `seed_aggregate.csv`
and `method_summary.csv` expose the aggregation. `official_curves.svg` plots only
M2's verified per-query histories, when available; mSUN and the official AUDC-source count
are distinct metrics. The SHA256 manifests and preserved attempt directories
remain the evidence source; report CSV files do not replace those directories.

## Official checkpoint cleanup and independent endpoint audits

{sum("endpoint_audit" in run for run in own.values())} units were accepted for
final endpoint comparison by a NEW independent audit. Their original
`m2_validation.json` remains false and unchanged: the unchanged official runner
logged successful completion and removed its checkpoint before the post-exit
collector ran. The new audit permits only that exact three-error failure,
rechecks all frozen scientific source hashes, actual resolved settings,
component logs, process exit and completed20-query trajectory/summary, and is
saved in `independent_endpoint_audits.json`. It does not claim to recover an
original checkpoint or history.

Per-query histories available to this report: {sum("history" in run for run in own.values())}/18.
Separate record-only curve analysis accepted: {curve_audit.get("accepted") is True}.
When supplied, that analysis must first validate all720 original baseline
prefixes and all72 final endpoints, then match each original trajectory hash,
material reference and frozen evaluator source hash. Such curves are labelled
offline re-evaluations of actual recorded structures/energies, never new oracle
queries or recovered checkpoint files. Without original history or a passing
separate proof, no curve is generated for that unit.

## M2 transport audit

{len(transport_omissions)} accepted M2 units have missing raw hidden Hydra attachments in
the received artifact payload. Their exact missing paths and expected original
SHA256 values are recorded in `validation.json`. This is consistent with the
live artifact uploader's default exclusion of hidden files. The original raw
`.hydra/config.yaml`, `.hydra/hydra.yaml` and `.hydra/overrides.yaml` files have
not been reconstructed. The received archive is not claimed to preserve every
original byte when those files are absent.

The required visible payload is checked separately: original run metadata,
full trajectory, official summaries, `resolved_config.yaml`, component logs,
official checkpoint/history, process log and collection/exit records. Every
available file must match its recorded SHA256, and a missing file outside those
three named raw Hydra attachments remains a validation error. Scientific run
acceptance was recorded on the execution runner before artifact transport;
final-score pairing and required visible-payload integrity are distinguished
from availability of these additional original audit attachments.

## M1 reference audit attachments

{len(missing_audit)} reference units lack one or more original Hydra/resolved
configuration, component-log or per-query-history attachments in the supplied
frozen result tree. The missing-file list is in `validation.json`. Final metric
pairing uses the actual official final trajectory/summary values after checking
system, seed, B, protocol, scientific input hashes and canonical material
reference identity. Missing M1 attachments have not been invented or re-labelled
as originals. M1 discovery curves and AF/EF are consequently not reported here.
The original M1 attachments should be supplied separately for the complete audit.

The previously completed Random/Chemeleon baseline results are not re-run or
assumed compatible by this script. Their raw evidence was not an input to this
report, so no new AF/EF or baseline pairing is claimed.

## Cost and failed attempts

`costs.csv` records each method's machine, CPU/OS, elapsed driver time, query
count and known fee fields. A recorded USD0 model fee is not zero total cost.
Hardware, electricity and all unpriced failed attempts remain outside those
fees; unknown LLM calls/tokens stay blank. Different machines are not treated as
a controlled hardware-speed comparison. `failed_attempts.json` indexes preserved
failed attempts. No failed attempt was deleted or used as a completed score.

Input roots:
- M2: `{results_root}`
- Frozen M1 reference: `{reference_root}`
"""
    (output / "README.md").write_text(text)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frozen-root", type=Path)
    parser.add_argument("--curve-analysis-root", type=Path)
    args = parser.parse_args()
    audit = report(
        args.results_root.resolve(),
        args.reference_root.resolve(),
        args.output.resolve(),
        args.frozen_root.resolve() if args.frozen_root else None,
        args.curve_analysis_root.resolve() if args.curve_analysis_root else None,
    )
    print(
        json.dumps(
            {
                "accepted_unique_units": audit["accepted_unique_units"],
                "reference_unique_units": audit["reference_unique_units"],
                "complete": audit["complete_paired_final_metric_comparison"],
                "output": str(args.output),
            }
        )
    )
    if not audit["complete_paired_final_metric_comparison"]:
        raise SystemExit(
            "Incomplete or inconsistent result set; inspect validation.json"
        )
    if (
        args.curve_analysis_root
        and audit["record_only_curve_analysis"].get("accepted") is not True
    ):
        raise SystemExit(
            "Supplied record-only curve analysis failed its proof gate; inspect validation.json"
        )


if __name__ == "__main__":
    main()
