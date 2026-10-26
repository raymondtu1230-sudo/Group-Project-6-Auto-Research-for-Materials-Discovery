"""Merge raw Hydra/component evidence into frozen M1 reference attempts."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

from omegaconf import OmegaConf


ROOT = Path(__file__).resolve().parent
MADE = ROOT / "MADE"
RESULTS = MADE / "results"
REFERENCE = RESULTS / "protocol_v1/m1_full/dev"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def configured_output(config_path: Path) -> Path:
    config = OmegaConf.load(config_path)
    output = Path(str(config.experiment.output_dir))
    return output if output.is_absolute() else MADE / output


def resolved_config(config_path: Path, source_dir: Path) -> str:
    resolver_name = "m1_hydra_output_dir"
    OmegaConf.register_new_resolver(
        resolver_name, lambda _key: str(source_dir.resolve()), replace=True
    )
    raw = config_path.read_text().replace(
        "${hydra:runtime.output_dir}",
        f"${{{resolver_name}:runtime.output_dir}}",
    )
    config = OmegaConf.create(raw)
    return OmegaConf.to_yaml(config, resolve=True)


def curve_from_trajectory(attempt: Path) -> dict[str, object]:
    trajectory_path = attempt / "trajectories/episode_000.json"
    payload = json.loads(trajectory_path.read_text())
    trajectory = payload["trajectory"]
    history: list[dict[str, object]] = []
    cumulative = 0
    areas: list[float] = []
    for query, observation in enumerate(trajectory, start=1):
        if observation.get("is_stable") and observation.get("is_newly_discovered"):
            cumulative += 1
        area = sum(
            float(point["num_newly_discovered_stable"]) for point in history
        ) + cumulative / 2.0
        areas.append(area)
        history.append(
            {
                "queries_used": query,
                "num_newly_discovered_stable": cumulative,
                "novelty_stable_unique_novel_count": cumulative,
                "discovery_curve_area_under_discovery_curve": area,
                "discovery_curve_area_under_discovery_curve_normalized": (
                    area / (query**2 / 2.0)
                ),
            }
        )

    metrics = payload["metrics"]
    final_msun = float(metrics["final/novelty_stable_unique_novel_count"])
    final_audc = float(metrics["final/discovery_curve_area_under_discovery_curve"])
    if cumulative != final_msun or not math.isclose(
        areas[-1], final_audc, rel_tol=1e-12, abs_tol=1e-12
    ):
        raise ValueError(f"reconstructed curve disagrees with final metrics: {attempt}")

    return {
        "source": "reconstructed_from_frozen_official_trajectory",
        "provenance_note": (
            "The reference launcher did not retain successful checkpoint histories. "
            "These two official discovery curves are reconstructed losslessly from "
            "the per-query is_stable and is_newly_discovered observations in the "
            "frozen trajectory and verified against its final mSUN and AUDC."
        ),
        "complete_curve": True,
        "query_counts": list(range(1, len(history) + 1)),
        "metrics_history": history,
    }


def package(source_dir: Path) -> Path:
    config_path = source_dir / ".hydra/config.yaml"
    attempt = configured_output(config_path).resolve()
    if REFERENCE.resolve() not in attempt.parents:
        raise ValueError(f"source does not map to the frozen reference: {source_dir}")
    if not attempt.is_dir():
        raise FileNotFoundError(attempt)

    hydra_target = attempt / "hydra"
    hydra_target.mkdir(exist_ok=True)
    copied: list[Path] = []
    for name in ("config.yaml", "hydra.yaml", "overrides.yaml"):
        source = source_dir / ".hydra" / name
        if source.is_file():
            target = hydra_target / name
            shutil.copy2(source, target)
            copied.append(target)

    resolved = attempt / "resolved_config.yaml"
    resolved.write_text(resolved_config(config_path, source_dir))
    copied.append(resolved)

    for name in (
        "m4_evidence.jsonl",
        "m4_proposal_events.jsonl",
        "m5_decisions.jsonl",
        "run_benchmark.log",
    ):
        source = source_dir / name
        if source.is_file():
            target = attempt / name
            shutil.copy2(source, target)
            copied.append(target)

    trajectory = attempt / "trajectories/episode_000.json"
    if trajectory.is_file():
        history = attempt / "m2_metrics_history.json"
        history.write_text(json.dumps(curve_from_trajectory(attempt), indent=2))
        copied.append(history)

    metadata = json.loads((attempt / "run_metadata.json").read_text())
    config = OmegaConf.load(resolved)
    switches = (
        "enable_planning",
        "enable_memory",
        "enable_reflection",
        "enable_exploration",
        "enable_tool_routing",
    )
    if (
        list(config.dataset.elements) != metadata["system"]
        or int(config.experiment.seed) != metadata["seed"]
        or str(config.experiment.output_dir) != str(attempt.relative_to(MADE))
        or int(config.environment.budget) != metadata["query_budget"]
        or not all(bool(config.agent[name]) for name in switches)
    ):
        raise ValueError(f"resolved configuration disagrees with metadata: {attempt}")

    manifest = {
        "source_directory": str(source_dir.relative_to(MADE)),
        "target_attempt": str(attempt.relative_to(MADE)),
        "files": {
            str(path.relative_to(attempt)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(copied)
        },
    }
    (attempt / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2))
    return attempt


def main() -> None:
    sources = sorted(RESULTS.glob("20261025-*-orb-m1_integrated"))
    packaged = [package(source) for source in sources]
    completed = [path for path in packaged if (path / "m2_metrics_history.json").is_file()]
    if len(completed) != 18:
        raise ValueError(f"expected 18 completed references, found {len(completed)}")
    print(f"Packaged {len(packaged)} attempts, including {len(completed)} completed units.")


if __name__ == "__main__":
    main()
