"""Offline re-evaluation of original recorded trajectories with frozen metrics.

This is an analysis artifact, never a recovered historical checkpoint. It does
not initialize an environment, dataset, model, oracle or agent. Original inputs
are read only. All structures and energies come from the original trajectory.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zipfile import ZipFile

FREEZE = "02e0026bf450f71f4f7862228d295f5b02b49e12"
SEEDS = (17, 29, 43)
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
BASELINES = ("random_generator_baseline", "chemeleon_generative_baseline")
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
AUDC = "discovery_curve_area_under_discovery_curve"


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path: Path, value: Any) -> None:
    data = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(
                f"Refuse to overwrite differing analysis evidence: {path}"
            )
        return
    with path.open("xb") as stream:
        stream.write(data)


def exact_entry_key(value: dict[str, Any]) -> str:
    """Independent entry data, without rounding or relaxed matching.

    Ignore only display/schema tags and derived lattice/Cartesian fields.
    Energies, matrix, fractional coordinates, species, charge and properties
    retain their exact numeric values. The name is a formula display label.
    """
    entry = copy.deepcopy(value)
    for key in ("@module", "@class", "@version", "name"):
        entry.pop(key, None)
    entry["energy"] = float(entry["energy"])
    entry["composition"] = {k: float(v) for k, v in entry["composition"].items()}
    structure = entry.get("attribute", {}).get("structure")
    if isinstance(structure, dict):
        for key in ("@module", "@class", "@version"):
            structure.pop(key, None)
        lattice = structure.get("lattice", {})
        if "matrix" in lattice:
            for key in ("a", "b", "c", "alpha", "beta", "gamma", "volume"):
                lattice.pop(key, None)
        for site in structure.get("sites", []):
            if "matrix" in lattice and "abc" in site:
                site.pop("xyz", None)
    return json.dumps(entry, sort_keys=True, separators=(",", ":"), allow_nan=False)


def material_reference_hash(entries: list[dict[str, Any]]) -> str:
    """Existing M2/evaluate.py independent-data snapshot canonicalization."""
    canonical = copy.deepcopy(entries)
    for entry in canonical:
        attribute = entry.get("attribute")
        structure = attribute.get("structure") if isinstance(attribute, dict) else None
        if not isinstance(structure, dict):
            continue
        lattice = structure.get("lattice", {})
        if "matrix" in lattice:
            for key in ("a", "b", "c", "alpha", "beta", "gamma", "volume"):
                lattice.pop(key, None)
        for site in structure.get("sites", []):
            if "matrix" in lattice and "abc" in site:
                site.pop("xyz", None)
    return sha_bytes(
        "\n".join(
            sorted(
                json.dumps(x, sort_keys=True, separators=(",", ":")) for x in canonical
            )
        ).encode()
    )


def load_runtime(repo: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo / "M1/MADE/src"))
    import yaml
    from pymatgen.analysis.phase_diagram import PDEntry, PhaseDiagram
    from pymatgen.analysis.structure_matcher import StructureMatcher
    from pymatgen.core import Structure

    import made.envs.convex_hull as env_module
    import made.evaluation.metrics as metrics_module
    import made.utils.convex_hull_utils as utils_module

    for module in (env_module, metrics_module, utils_module):
        if not Path(module.__file__).resolve().is_relative_to(repo):
            raise RuntimeError(
                f"Imported scientific code is outside frozen reference: {module.__file__}"
            )
    settings = yaml.safe_load(
        (repo / "M1/MADE/configs/environment/convex_hull.yaml").read_text()
    )
    matcher = {
        "ltol": settings["structure_matcher_ltol"],
        "stol": settings["structure_matcher_stol"],
        "angle_tol": settings["structure_matcher_angle_tol"],
        "primitive_cell": settings["structure_matcher_primitive_cell"],
    }
    return {
        "PDEntry": PDEntry,
        "PhaseDiagram": PhaseDiagram,
        "StructureMatcher": StructureMatcher,
        "Structure": Structure,
        "Env": env_module.ConvexHullEnvironment,
        "Novelty": metrics_module.NoveltyMetrics,
        "Discovery": metrics_module.DiscoveryCurveMetrics,
        "entry": utils_module.structure_result_to_entry,
        "extract": utils_module.extract_structure_from_entry,
        "matcher_settings": matcher,
        "scientific_source_sha256": {
            str(Path(m.__file__).resolve().relative_to(repo)): sha_file(
                Path(m.__file__)
            )
            for m in (env_module, metrics_module, utils_module)
        },
    }


def read_directory(path: Path) -> dict[str, Any]:
    names = (
        "run_metadata.json",
        "trajectories/episode_000.json",
        "summary/summary.json",
    )
    raw = {name: (path / name).read_bytes() for name in names}
    history = path / "m2_metrics_history.json"
    if history.is_file():
        candidate = json.loads(history.read_text())
        if candidate.get("complete_curve") is True:
            raw["m2_metrics_history.json"] = history.read_bytes()
    return {
        "metadata": json.loads(raw[names[0]]),
        "trajectory": json.loads(raw[names[1]]),
        "summary": json.loads(raw[names[2]]),
        "original_history": json.loads(raw["m2_metrics_history.json"]).get(
            "metrics_history"
        )
        if "m2_metrics_history.json" in raw
        else None,
        "input_sha256": {k: sha_bytes(v) for k, v in raw.items()},
        "source": str(path),
    }


def read_baselines(repo: Path, manifest: Path) -> list[dict[str, Any]]:
    result = []
    for record in json.loads(manifest.read_text())["archives"]:
        archive = repo / record["path"]
        measured = sha_file(archive)
        if measured != record["sha256"]:
            raise ValueError(f"Original baseline archive hash differs: {archive}")
        with ZipFile(archive) as z:
            metadata = [n for n in z.namelist() if n.endswith("run_metadata.json")]
            if len(metadata) != 1:
                raise ValueError(
                    f"Expected one run per verified baseline archive: {archive}"
                )
            prefix = metadata[0].removesuffix("run_metadata.json")
            names = (
                "run_metadata.json",
                "trajectories/episode_000.json",
                "summary/summary.json",
                "m2_metrics_history.json",
            )
            raw = {name: z.read(prefix + name) for name in names}
        capture = json.loads(raw["m2_metrics_history.json"])
        if capture.get("complete_curve") is not True:
            raise ValueError(f"Baseline lacks original complete history: {archive}")
        result.append(
            {
                "metadata": json.loads(raw[names[0]]),
                "trajectory": json.loads(raw[names[1]]),
                "summary": json.loads(raw[names[2]]),
                "original_history": capture["metrics_history"],
                "input_sha256": {k: sha_bytes(v) for k, v in raw.items()},
                "archive_sha256": measured,
                "source": str(archive) + "::" + prefix,
            }
        )
    return result


def select_directories(root: Path, method: str) -> list[dict[str, Any]]:
    selected = {}
    for path in sorted(root.rglob("run_metadata.json")):
        m = json.loads(path.read_text())
        if (
            m.get("method") != method
            or m.get("status") != "completed"
            or m.get("split") != "dev"
        ):
            continue
        key = ("-".join(m["system"]), m["seed"])
        if key in selected:
            raise ValueError(f"Duplicate completed scientific unit: {method}/{key}")
        selected[key] = read_directory(path.parent)
    return list(selected.values())


def reevaluate(unit: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    """Apply frozen discovery/novelty metrics to immutable recorded prefixes."""
    m, payload = unit["metadata"], unit["trajectory"]
    observations = payload["trajectory"]
    if (
        m.get("status") != "completed"
        or m.get("query_budget") != 20
        or m.get("episodes") != 1
        or payload["metrics"].get("final/queries_used") != 20
        or len(observations) != 20
    ):
        raise ValueError(
            "Re-evaluation requires an original completed B20 single episode"
        )
    settings = m["protocol_settings"]
    if (
        settings["oracle"]["device"] != "cpu"
        or settings["oracle"]["model_name"] != "orb-v3-conservative-inf-omat"
        or settings["environment"]["stability_tolerance_ev_per_atom"] != 0.1
    ):
        raise ValueError("Unexpected original scientific settings")
    structures = [
        runtime["Structure"].from_dict(obs["proposal"]) for obs in observations
    ]
    proposals = [
        runtime["entry"](s, obs["oracle_result"])
        for s, obs in zip(structures, observations, strict=True)
    ]
    final_serialized = payload["final_env_state"]["phase_diagram_all_entries"]
    final_keys = [exact_entry_key(x) for x in final_serialized]
    pending = Counter(exact_entry_key(e.as_dict()) for e in proposals)
    initial_serialized = []
    removed_indices = []
    for index, (entry, key) in enumerate(
        zip(final_serialized, final_keys, strict=True)
    ):
        if pending[key] > 0:
            pending[key] -= 1
            removed_indices.append(index)
        else:
            initial_serialized.append(entry)
    if sum(pending.values()) != 0 or len(removed_indices) != 20:
        raise ValueError(
            "Cannot exactly subtract every original proposal from the original final entry multiset"
        )
    if Counter(final_keys) != Counter(
        exact_entry_key(e) for e in initial_serialized
    ) + Counter(exact_entry_key(e.as_dict()) for e in proposals):
        raise ValueError("Original final-entry multiset recovery proof failed")
    initial = [runtime["PDEntry"].from_dict(x) for x in initial_serialized]
    # No constructor, reset, step, oracle object or agent is used in this analysis.
    state = runtime["Env"].__new__(runtime["Env"])
    state.stability_tolerance = float(
        settings["environment"]["stability_tolerance_ev_per_atom"]
    )
    matcher = runtime["matcher_settings"]
    state.structure_matcher_ltol = matcher["ltol"]
    state.structure_matcher_stol = matcher["stol"]
    state.structure_matcher_angle_tol = matcher["angle_tol"]
    state.structure_matcher = runtime["StructureMatcher"](**matcher)
    state.observed_entries = list(initial)
    state.observed_pd = runtime["PhaseDiagram"](state.observed_entries)
    state.initial_structures = [
        s for e in initial if (s := runtime["extract"](e)) is not None
    ]
    state.proposed_entries = []
    state.newly_discovered_entries = []
    if (
        len(state.initial_structures)
        != payload["metrics"]["final/num_initial_structures"]
    ):
        raise ValueError(
            "Recovered initial structure count differs from original official metrics"
        )
    history = []
    observations_checked = []
    for query, (entry, observation) in enumerate(
        zip(proposals, observations, strict=True), 1
    ):
        state.proposed_entries.append(entry)
        state.observed_entries.append(entry)
        state.observed_pd = runtime["PhaseDiagram"](state.observed_entries)
        ehull = state._safe_e_above_hull(state.observed_pd, entry)
        stable = ehull <= state.stability_tolerance
        novel = state._check_structural_novelty(entry)
        if (
            stable != observation["is_stable"]
            or novel != observation["is_newly_discovered"]
        ):
            raise ValueError(
                f"Frozen re-evaluation differs from original stability/novelty observation at query {query}"
            )
        if not math.isclose(
            ehull, observation["e_above_hull"], rel_tol=1e-8, abs_tol=1e-8
        ):
            raise ValueError(
                f"Frozen hull distance differs from original observation at query {query}"
            )
        stable_flags = [
            state._safe_e_above_hull(state.observed_pd, e) <= state.stability_tolerance
            for e in state.proposed_entries
        ]
        stable_new = sum(
            state._safe_e_above_hull(state.observed_pd, e) <= state.stability_tolerance
            for e in state.newly_discovered_entries
        )
        novelty = runtime["Novelty"].calculate(
            candidate_structures=structures[:query],
            reference_structures=state.initial_structures,
            stable_flags=stable_flags,
            ltol=matcher["ltol"],
            stol=matcher["stol"],
            angle_tol=matcher["angle_tol"],
        )
        row = {
            "queries_used": query,
            "num_newly_discovered_structures": len(state.newly_discovered_entries),
            CURVE: stable_new,
            MSUN: novelty["stable_unique_novel_count"],
        }
        history.append(row)
        row[AUDC] = runtime["Discovery"].area_under_discovery_curve(
            history, metric_key=CURVE
        )
        observations_checked.append(
            {
                "query": query,
                "original_stability_matches": True,
                "original_novelty_matches": True,
                "original_hull_distance_matches": True,
            }
        )
    endpoint_checks = {
        MSUN: history[-1][MSUN] == payload["metrics"]["final/" + MSUN],
        CURVE: history[-1][CURVE] == payload["metrics"]["final/" + CURVE],
        AUDC: math.isclose(
            history[-1][AUDC],
            payload["metrics"]["final/" + AUDC],
            rel_tol=1e-9,
            abs_tol=1e-9,
        ),
    }
    if not all(endpoint_checks.values()):
        raise ValueError(
            f"Re-evaluated endpoint differs from original official endpoint: {endpoint_checks}"
        )
    original = unit.get("original_history")
    prefix_checks = []
    if original is not None:
        if [x.get("queries_used") for x in original] != list(range(1, 21)):
            raise ValueError("Original baseline history does not cover queries1..20")
        for old, new in zip(original, history, strict=True):
            matches = {k: old.get(k) == new[k] for k in (CURVE, MSUN)}
            if not all(matches.values()):
                raise ValueError(
                    f"Re-evaluated prefix differs from original saved history at query {new['queries_used']}: {matches}"
                )
            prefix_checks.append({"query": new["queries_used"], **matches})
    return {
        "analysis_kind": "offline_recorded_trajectory_re_evaluation",
        "historical_checkpoint_recovered": False,
        "model_calls": 0,
        "oracle_calls": 0,
        "new_agent_proposals": 0,
        "new_scientific_episode": False,
        "method": m["method"],
        "system": "-".join(m["system"]),
        "seed": m["seed"],
        "attempt": m.get("attempt"),
        "source": unit["source"],
        "input_sha256": unit["input_sha256"],
        "archive_sha256": unit.get("archive_sha256"),
        "original_trajectory_sha256": unit["input_sha256"][
            "trajectories/episode_000.json"
        ],
        "canonical_material_reference_sha256": material_reference_hash(
            payload["phase_diagram_gt"]
        ),
        "analysis_script_sha256": sha_file(Path(__file__)),
        "scientific_source_sha256": runtime["scientific_source_sha256"],
        "executed_official_analysis_methods": [
            "structure_result_to_entry",
            "ConvexHullEnvironment._safe_e_above_hull",
            "ConvexHullEnvironment._check_structural_novelty",
            "NoveltyMetrics.calculate",
            "DiscoveryCurveMetrics.area_under_discovery_curve",
        ],
        "scientific_interaction_methods_not_invoked": [
            "ConvexHullEnvironment.__init__",
            "ConvexHullEnvironment.reset",
            "ConvexHullEnvironment.step",
            "Oracle.evaluate",
            "Agent.__call__",
        ],
        "initial_entry_recovery": {
            "original_final_entry_count": len(final_serialized),
            "subtracted_recorded_proposals": 20,
            "removed_original_final_entry_indices": removed_indices,
            "recovered_initial_entries": len(initial),
            "recovered_initial_structures": len(state.initial_structures),
            "original_initial_structures": payload["metrics"][
                "final/num_initial_structures"
            ],
            "exact_final_multiset_restored": True,
            "initial_entries_sha256": sha_bytes(
                "\n".join(
                    sorted(exact_entry_key(x) for x in initial_serialized)
                ).encode()
            ),
            "final_entries_sha256": sha_bytes("\n".join(sorted(final_keys)).encode()),
            "identity_rule": "Exact independent structure/energy data; no rounding, energy prediction, relaxed structure matching or new data retrieval",
        },
        "original_observations_checked": observations_checked,
        "original_saved_history_prefix_checks": prefix_checks,
        "original_saved_history_prefix_count": len(prefix_checks),
        "original_endpoint_matches": endpoint_checks,
        "reevaluated_metrics_history": history,
        "accepted": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-repo", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path)
    parser.add_argument("--routing-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.reference_repo.resolve()
    manifest = (
        args.baseline_manifest
        or repo / "M2/configs/current_stage_verified_baselines.json"
    ).resolve()
    output = args.output.resolve()
    started = time.monotonic()
    runtime = load_runtime(repo)
    baselines = read_baselines(repo, manifest)
    expected = {(m, s, seed) for m in BASELINES for s in SYSTEMS for seed in SEEDS}
    actual = {
        (
            u["metadata"]["method"],
            "-".join(u["metadata"]["system"]),
            u["metadata"]["seed"],
        )
        for u in baselines
    }
    if len(baselines) != 36 or actual != expected:
        raise ValueError(
            "Mandatory original36 baseline validation set is incomplete or duplicated"
        )
    full = select_directories(
        repo / "M1/MADE/results/protocol_v1/m1_full/dev", "m1_full"
    )
    if len(full) != 18:
        raise ValueError(
            "Mandatory frozen18 reference endpoint validation set is incomplete"
        )
    routing = (
        select_directories(args.routing_root.resolve(), "tool_routing_off")
        if args.routing_root
        else []
    )
    reports = []
    # All36 original baseline histories are validated before reference/routing use.
    for unit in baselines + full + routing:
        m = unit["metadata"]
        relative = (
            Path(m["method"])
            / "-".join(m["system"])
            / f"seed_{m['seed']}"
            / f"attempt_{m.get('attempt', 1):02d}"
            / "reevaluated_curve.json"
        )
        target = output / relative
        if target.is_file():
            report = json.loads(target.read_text())
            if (
                report.get("input_sha256") != unit["input_sha256"]
                or report.get("scientific_source_sha256")
                != runtime["scientific_source_sha256"]
                or report.get("analysis_script_sha256") != sha_file(Path(__file__))
                or report.get("accepted") is not True
            ):
                raise ValueError(
                    f"Existing offline analysis provenance differs: {target}"
                )
        else:
            report = reevaluate(unit, runtime)
            save(target, report)
        reports.append(report)
        print(
            json.dumps(
                {
                    "completed_offline_units": len(reports),
                    "method": report["method"],
                    "system": report["system"],
                    "seed": report["seed"],
                    "original_history_prefixes_checked": report[
                        "original_saved_history_prefix_count"
                    ],
                    "mSUN": report["reevaluated_metrics_history"][-1][MSUN],
                    "AUDC": report["reevaluated_metrics_history"][-1][AUDC],
                },
                allow_nan=False,
            ),
            flush=True,
        )
    prefix_count = sum(x["original_saved_history_prefix_count"] for x in reports[:36])
    if prefix_count != 720:
        raise ValueError("Mandatory720 original baseline prefix checks did not pass")
    index = {(r["method"], r["system"], r["seed"]): r for r in reports}
    paired = []
    for proposal_method in ("m1_full", "tool_routing_off"):
        for system in SYSTEMS:
            for seed in SEEDS:
                proposal = index.get((proposal_method, system, seed))
                if proposal is None:
                    continue
                comparators = (
                    (*BASELINES, "m1_full")
                    if proposal_method == "tool_routing_off"
                    else BASELINES
                )
                for baseline_method in comparators:
                    baseline = index[(baseline_method, system, seed)]
                    if (
                        proposal["canonical_material_reference_sha256"]
                        != baseline["canonical_material_reference_sha256"]
                    ):
                        raise ValueError(
                            "Paired material references differ; refuse AF/EF aggregation"
                        )
                    ph, bh = (
                        proposal["reevaluated_metrics_history"],
                        baseline["reevaluated_metrics_history"],
                    )
                    af = float(
                        runtime["Discovery"].acceleration_factor(
                            ph, bh, metric_key=CURVE
                        )
                    )
                    ef = float(
                        runtime["Discovery"].enhancement_factor(
                            ph, bh, metric_key=CURVE
                        )
                    )
                    paired.append(
                        {
                            "proposal_method": proposal_method,
                            "baseline_method": baseline_method,
                            "system": system,
                            "seed": seed,
                            "AF": af if math.isfinite(af) else None,
                            "AF_status": "finite"
                            if math.isfinite(af)
                            else "official_positive_infinity",
                            "EF": ef,
                            "EF_cap": 100.0,
                            "metric_key": CURVE,
                            "analysis_kind": "offline_recorded_trajectory_re_evaluation",
                            "proposal_final_discoveries": ph[-1][CURVE],
                            "baseline_final_discoveries": bh[-1][CURVE],
                            "official_zero_target_convention": "AF=1 when both first reach baseline target at query0; EF=min(proposal_final/max(baseline_final,1e-8),100)",
                            "proposal_trajectory_sha256": proposal[
                                "original_trajectory_sha256"
                            ],
                            "baseline_trajectory_sha256": baseline[
                                "original_trajectory_sha256"
                            ],
                        }
                    )
    summary = {
        "kind": "offline_recorded_trajectory_re_evaluation_audit",
        "frozen_commit": FREEZE,
        "historical_checkpoint_recovered": False,
        "new_scientific_episodes": 0,
        "oracle_calls": 0,
        "model_calls": 0,
        "baseline_units_validated": 36,
        "original_baseline_prefixes_validated": prefix_count,
        "frozen_reference_units_validated": 18,
        "routing_units_validated": len(routing),
        "routing_complete": len(routing) == 18,
        "original_endpoint_units_validated": len(reports),
        "all_original_mSUN_and_AUDC_endpoints_match": True,
        "paired_AF_EF_rows": len(paired),
        "paired_AF_EF_metric_key": CURVE,
        "paired_AF_EF_official_functions": [
            "DiscoveryCurveMetrics.acceleration_factor",
            "DiscoveryCurveMetrics.enhancement_factor",
        ],
        "baseline_manifest_sha256": sha_file(manifest),
        "analysis_script_sha256": sha_file(Path(__file__)),
        "scientific_source_sha256": runtime["scientific_source_sha256"],
        "wall_time_seconds": round(time.monotonic() - started, 3),
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "accepted": True,
        "limitations": [
            "Re-evaluated curves are analysis outputs from original recorded structures and energies, not recovered historical checkpoints.",
            "Originalmetadata, trajectories, summaries and failed attempts were read only and remain unchanged.",
        ],
    }
    save(output / "reevaluation_audit.json", summary)
    af_path = output / "paired_AF_EF.csv"
    if paired and not af_path.exists():
        with af_path.open("x", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(paired[0]))
            writer.writeheader()
            writer.writerows(paired)
    csv_path = output / "reevaluated_metrics_history.csv"
    if not csv_path.exists():
        with csv_path.open("x", newline="") as stream:
            fields = [
                "method",
                "system",
                "seed",
                "attempt",
                "queries_used",
                CURVE,
                MSUN,
                AUDC,
            ]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for report in reports:
                for row in report["reevaluated_metrics_history"]:
                    writer.writerow(
                        {
                            **{k: report[k] for k in fields[:4]},
                            **{k: row[k] for k in fields[4:]},
                        }
                    )
    print(json.dumps(summary, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
