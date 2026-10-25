"""Collect and audit real frozen M2 runs without changing scientific inputs.

The only experiment entrypoint is M1/run_experiment.py.  This module reads its
outputs after exit and preserves original metadata, configurations and records.
Only standard-library modules are imported until collection/validation is used.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FROZEN_COMMIT = "02e0026bf450f71f4f7862228d295f5b02b49e12"
FROZEN_TAG = "m1-freeze-20261025"
METHOD = "tool_routing_off"
MODEL = "orb-v3-conservative-inf-omat"
SWITCHES = (
    "enable_planning", "enable_memory", "enable_reflection",
    "enable_exploration", "enable_tool_routing",
)
SYSTEMS = {
    "Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm",
}
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
MANIFEST = "m2_sha256_manifest.json"


def _read(path: Path) -> Any:
    return json.loads(path.read_text())


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _save(path: Path, value: Any) -> None:
    """Create a sidecar; never replace differing bytes in an existing attempt."""
    data = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    _save_bytes(path, data)


def _save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to replace existing evidence: {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def _copy(source: Path, target: Path) -> None:
    if source.resolve() == target.resolve():
        return
    if source.is_symlink():
        raise ValueError(f"Evidence must be a regular file, not a symlink: {source}")
    _save_bytes(target, source.read_bytes())


def _run_path(made: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or "${" in value:
        return None
    path = Path(value)
    return (path if path.is_absolute() else made / path).resolve()


def _manifest(attempt: Path) -> None:
    # Validation is generated after collection and is deliberately excluded.
    excluded = {MANIFEST, "m2_validation.json"}
    files = {
        str(path.relative_to(attempt)): _sha(path)
        for path in sorted(attempt.rglob("*"))
        if path.is_file() and str(path.relative_to(attempt)) not in excluded
    }
    _save(attempt / MANIFEST, {"algorithm": "sha256", "files": files})


def _resolve_config(config_path: Path, hydra_path: Path, output: Path) -> None:
    from omegaconf import OmegaConf

    recorded_hydra = OmegaConf.load(hydra_path)
    name = "m2_saved_hydra_" + _sha(hydra_path)[:16]
    if OmegaConf.has_resolver(name):
        raise ValueError("Unexpected pre-existing M2 recorded-runtime resolver")

    def recorded_value(key: str) -> Any:
        value = OmegaConf.select(recorded_hydra, "hydra." + str(key))
        if value is None:
            raise ValueError(f"Missing recorded Hydra runtime value: {key}")
        if OmegaConf.is_config(value):
            return OmegaConf.to_container(value, resolve=True)
        return value

    # A temporary resolver name avoids modifying the global Hydra resolver.
    # Raw originals are retained bytewise; only this in-memory representation
    # is rewritten, so every runtime value comes from the actual saved run.
    raw = config_path.read_text().replace("${hydra:", "${" + name + ":")
    OmegaConf.register_new_resolver(name, recorded_value)
    try:
        config = OmegaConf.create(raw)
        resolved = OmegaConf.to_yaml(config, resolve=True)
    finally:
        OmegaConf.clear_resolver(name)
    if "${" in resolved:
        raise ValueError("Resolved configuration still contains interpolation")
    _save_bytes(output, resolved.encode())


def collect(
    frozen_repo: Path, attempt_dir: Path, log: Path, exit_code: int
) -> dict[str, Any]:
    """Preserve actual outputs, also when the experiment failed or was partial."""
    import yaml

    frozen_repo, attempt = Path(frozen_repo).resolve(), Path(attempt_dir).resolve()
    made = frozen_repo / "M1/MADE"
    expected_root = (made / "results/protocol_v1" / METHOD / "dev").resolve()
    if not attempt.is_relative_to(expected_root):
        raise ValueError("Collector is restricted to frozen tool_routing_off/dev attempts")
    attempt.mkdir(parents=True, exist_ok=True)
    previous = attempt / "m2_collection.json"
    if previous.is_file():
        return _read(previous)
    errors: list[str] = []
    report: dict[str, Any] = {
        "collection_version": "m2-frozen-v1",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_entrypoint": "M1/run_experiment.py",
        "exit_code": exit_code,
        "attempt_path": str(attempt.relative_to(frozen_repo)),
        "original_metadata_unchanged": True,
        "errors": errors,
    }
    metadata_path = attempt / "run_metadata.json"
    if metadata_path.is_file():
        report["original_metadata_sha256"] = _sha(metadata_path)
    else:
        errors.append("Original driver metadata is missing")
    _save(attempt / "m2_exit.json", {"exit_code": exit_code, "returncode": exit_code})
    if Path(log).is_file():
        report["original_process_log_sha256"] = _sha(Path(log))
        data = Path(log).read_bytes()
        # Keep secrets out of deliverables if an external library prints one.
        redacted = False
        for key in ("MATERIALS_PROJECT_API_KEY", "TUWEIKANG_MATERIALS_PROJECT_API_KEY"):
            secret = os.environ.get(key)
            if secret and secret.encode() in data:
                data = data.replace(secret.encode(), b"[REDACTED]")
                redacted = True
        _save_bytes(attempt / "m2_process.log", data)
        report["process_log_known_secret_redaction"] = redacted
    else:
        errors.append("Process stdout/stderr log is missing")

    runtimes: list[Path] = []
    for path in sorted((made / "results").glob("*/.hydra/config.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
            configured = data.get("experiment", {}).get("output_dir")
            if _run_path(made, configured) == attempt:
                runtimes.append(path.parent.parent)
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    if len(runtimes) != 1:
        errors.append(f"Expected one matching original Hydra runtime; found {len(runtimes)}")
    else:
        runtime = runtimes[0]
        report["original_hydra_runtime"] = str(runtime.relative_to(frozen_repo))
        report["config_resolution_environment"] = {
            name: os.environ.get(name, fallback)
            for name, fallback in (("M4_RUN_ID", "m4-local"), ("M4_EPISODE_ID", "0"))
        }
        for path in sorted(runtime.rglob("*")):
            if path.is_file():
                try:
                    _copy(path, attempt / path.relative_to(runtime))
                except (OSError, ValueError) as error:
                    errors.append(str(error))
        try:
            _resolve_config(
                attempt / ".hydra/config.yaml", attempt / ".hydra/hydra.yaml",
                attempt / "resolved_config.yaml",
            )
            report["resolved_config_saved"] = True
        except Exception as error:
            report["resolved_config_saved"] = False
            errors.append(f"Actual saved configuration resolution failed: {type(error).__name__}: {error}")

    best: list[dict[str, Any]] = []
    best_source: Path | None = None
    checkpoint_records: list[dict[str, Any]] = []
    for path in sorted((made / "checkpoints").rglob("checkpoint.json")):
        try:
            payload = _read(path)
            configured = payload.get("config", {}).get("experiment", {}).get("output_dir")
            if _run_path(made, configured) != attempt:
                continue
            relative = path.relative_to(made / "checkpoints")
            _copy(path, attempt / "official_checkpoints" / relative)
            history = payload.get("metrics_history", [])
            checkpoint_records.append({
                "source": str(path.relative_to(frozen_repo)),
                "sha256": _sha(path), "metrics_history_rows": len(history),
                "query_count": payload.get("query_count"),
            })
            if isinstance(history, list) and len(history) > len(best):
                best, best_source = copy.deepcopy(history), path
        except (OSError, ValueError, TypeError, AttributeError) as error:
            errors.append(f"Checkpoint collection failed for {path.name}: {error}")
    report["official_checkpoints"] = checkpoint_records
    final_added = False
    trajectory = attempt / "trajectories/episode_000.json"
    try:
        final = {
            key.removeprefix("final/"): value
            for key, value in _read(trajectory).get("metrics", {}).items()
            if key.startswith("final/")
        }
        # The final metrics are from the real official trajectory, never a
        # replay, a cumulative observation approximation or a new oracle call.
        counts = [row.get("queries_used") for row in best]
        if final.get("queries_used") == 20 and counts == list(range(1, 20)):
            best.append(final)
            final_added = True
    except (OSError, ValueError, TypeError, AttributeError) as error:
        if exit_code == 0:
            errors.append(f"Official final metrics could not be read: {error}")
    counts = [row.get("queries_used") for row in best]
    _save(attempt / "m2_metrics_history.json", {
        "source": "official_runner_checkpoint_metrics_history",
        "source_checkpoint": str(best_source.relative_to(frozen_repo)) if best_source else None,
        "source_checkpoint_sha256": _sha(best_source) if best_source else None,
        "final_row_from_official_trajectory": final_added,
        "complete_curve": counts == list(range(1, 21)),
        "query_counts": counts, "metrics_history": best,
    })
    if not checkpoint_records:
        errors.append("No matching original official checkpoint was available")
    if metadata_path.is_file() and _sha(metadata_path) != report.get("original_metadata_sha256"):
        errors.append("Original metadata changed during collection")
        report["original_metadata_unchanged"] = False
    report["collection_complete"] = not errors
    _save(previous, report)
    _manifest(attempt)
    return report


def _valid_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Non-object JSONL record in {path.name}")
            json.dumps(row, allow_nan=False)
            rows.append(row)
    return rows


def _reference_hash(entries: list[dict[str, Any]]) -> str:
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
    values = sorted(json.dumps(x, sort_keys=True, separators=(",", ":")) for x in canonical)
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def validate(frozen_repo: Path, attempt_dir: Path) -> dict[str, Any]:
    """Audit one real episode independently; return failures rather than hide them."""
    import yaml

    repo, attempt = Path(frozen_repo).resolve(), Path(attempt_dir).resolve()
    errors: list[str] = []
    report: dict[str, Any] = {"validation_version": "m2-frozen-v1", "accepted": False, "errors": errors}

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        metadata = _read(attempt / "run_metadata.json")
        config = yaml.safe_load((attempt / "resolved_config.yaml").read_text())
        trajectory = _read(attempt / "trajectories/episode_000.json")
        summary = _read(attempt / "summary/summary.json")
        capture = _read(attempt / "m2_metrics_history.json")
        collection = _read(attempt / "m2_collection.json")
        report.update({"method": metadata.get("method"), "system": metadata.get("system"),
                       "seed": metadata.get("seed"), "attempt": metadata.get("attempt")})
        require(metadata.get("method") == METHOD, "Unexpected experiment method")
        require(metadata.get("split") == "dev", "Ablation must run only on dev")
        require("-".join(metadata.get("system", [])) in SYSTEMS, "System is not one of the six frozen dev systems")
        require(metadata.get("seed") in (17, 29, 43), "Seed is outside frozen seed set")
        require(metadata.get("status") == "completed", "Driver did not mark the real run completed")
        require(collection.get("exit_code") == 0, "Real experiment process exited unsuccessfully")
        require(collection.get("collection_complete") is True, "Original-evidence collection has missing files or errors")
        require(metadata.get("query_budget") == 20 and metadata.get("episodes") == 1, "Metadata B/episode count differs from frozen protocol")
        protocol = yaml.safe_load((repo / "M1/protocol/protocol_v1.yaml").read_text())
        require(metadata.get("protocol_settings") == protocol, "Recorded protocol differs from the frozen protocol")
        require(config.get("experiment", {}).get("seed") == metadata.get("seed"), "Resolved seed differs from metadata")
        require(config.get("experiment", {}).get("num_episodes") == 1, "Resolved configuration does not use one episode")
        require(config.get("dataset", {}).get("elements") == metadata.get("system"), "Resolved chemical system differs from metadata")
        require(config.get("environment", {}).get("budget") == 20, "Resolved budget is not20")
        oracle = config.get("oracle", {})
        require(oracle.get("_target_") == "made.oracles.ORBOracle" and oracle.get("model_name") == MODEL and oracle.get("device") == "cpu", "Resolved oracle/model/device differ from CPU ORB v3 conservative")
        require(oracle.get("relax") is True and oracle.get("relax_kwargs") == {"optimizer": "fire", "fmax": 0.02, "steps": 500, "relax_unit_cell": True}, "ORB relaxation settings changed")
        agent = config.get("agent", {})
        for key in SWITCHES:
            require(agent.get(key) is (key != "enable_tool_routing"), f"Incorrect component switch: {key}")
        require(agent.get("planner", {}).get("_target_") == "made.agents.m3_planning.M3ResearchPlanner", "Frozen M3 planner is not active")
        require(agent.get("generator", {}).get("_target_") == "made.agents.m2_tool_routing.CheckpointedRandomGenerator", "Frozen primary generator changed")
        require(summary.get("episodes") == 1, "Official summary does not contain one episode")
        metrics = trajectory.get("metrics", {})
        require(len(trajectory.get("trajectory", [])) == 20 and metrics.get("final/queries_used") == 20, "Full trajectory/query count is not20")
        require(trajectory.get("final_env_state", {}).get("query_count") == 20, "Final environment query count is not20")
        history = capture.get("metrics_history", [])
        require(capture.get("complete_curve") is True and [x.get("queries_used") for x in history] == list(range(1, 21)), "Official checkpoint history does not cover queries1..20")
        for point in history:
            for key in (MSUN, CURVE):
                value = point.get(key)
                require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= point.get("queries_used", -1), f"Invalid official history value: {key}")
        if history:
            require(history[-1].get(MSUN) == metrics.get("final/" + MSUN), "Final mSUN differs from official history")
            require(history[-1].get(CURVE) == metrics.get("final/" + CURVE), "Final AUDC-source count differs from official history")
            source = repo / "M1/MADE/src/made/evaluation/metrics.py"
            spec = importlib.util.spec_from_file_location("m2_audit_frozen_metrics", source)
            if spec is None or spec.loader is None:
                raise ImportError("Cannot load frozen official metrics module")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            calculated = module.DiscoveryCurveMetrics.area_under_discovery_curve(history, metric_key=CURVE)
            reported = metrics.get("final/discovery_curve_area_under_discovery_curve")
            require(isinstance(reported, (int, float)) and math.isclose(reported, calculated, rel_tol=1e-9, abs_tol=1e-9), "Recorded AUDC disagrees with frozen official calculation")
            report["official_audc_recomputed"] = calculated
        for key in ("final/" + MSUN, "final/discovery_curve_area_under_discovery_curve"):
            require(summary.get("summary", {}).get(key, {}).get("mean") == metrics.get(key), f"Official summary/trajectory disagree: {key}")
        for filename, expected, query_key, query_range in (
            ("m5_decisions.jsonl", 20, "query_count", list(range(20))),
            ("m4_evidence.jsonl", 19, "query_count", list(range(1, 20))),
        ):
            rows = _valid_jsonl(attempt / filename)
            report[filename + "_records"] = len(rows)
            require(len(rows) == expected and [row.get(query_key) for row in rows] == query_range, f"Component evidence incomplete or duplicated: {filename}")
        frozen_meta = _read(repo / "M1/MADE/results/protocol_v1/m1_full/dev/Mg-Sn-Sr/seed_17/attempt_02/run_metadata.json")
        expected_hashes = frozen_meta.get("m1_input_sha256", {})
        hashes = metadata.get("m1_input_sha256", {})
        require(bool(expected_hashes) and hashes == expected_hashes, "Run source-input hashes differ from frozen reference metadata")
        mismatches = []
        for path, expected in hashes.items():
            candidate = repo / "M1" / path
            if not candidate.is_file() or _sha(candidate) != expected:
                mismatches.append(path)
        report["source_input_hashes_checked"] = len(hashes)
        report["source_input_hash_mismatches"] = mismatches
        require(not mismatches, "Actual frozen scientific source files fail input-hash audit")
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        tag = subprocess.check_output(["git", "-C", str(repo), "rev-parse", FROZEN_TAG + "^{commit}"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"], text=True)
        report.update({"actual_git_head": head, "actual_tag_commit": tag, "tracked_worktree_clean": not dirty})
        require(head == FROZEN_COMMIT and tag == FROZEN_COMMIT and not dirty, "Frozen revision/tag or clean tracked worktree check failed")
        require(_sha(attempt / "run_metadata.json") == collection.get("original_metadata_sha256"), "Original driver metadata bytes changed after collection")
        require(bool(collection.get("official_checkpoints")), "Original official checkpoints were not preserved")
        manifest = _read(attempt / MANIFEST).get("files", {})
        for path, expected in manifest.items():
            candidate = attempt / path
            require(candidate.is_file() and _sha(candidate) == expected, f"Preserved evidence SHA256 mismatch: {path}")
        require(bool(manifest), "No file integrity manifest")
        reference = trajectory.get("phase_diagram_gt")
        require(isinstance(reference, list) and bool(reference), "Actual materials reference snapshot is missing")
        if isinstance(reference, list) and reference:
            report["canonical_material_reference_sha256"] = _reference_hash(reference)
        report["mSUN_at_20"] = metrics.get("final/" + MSUN)
        report["AUDC"] = metrics.get("final/discovery_curve_area_under_discovery_curve")
        report["wall_time_seconds"] = metadata.get("wall_time_seconds")
    except Exception as error:
        errors.append(f"Validation could not finish: {type(error).__name__}: {error}")
    report["accepted"] = not errors
    _save(attempt / "m2_validation.json", report)
    return report
