"""Attach Hydra configs and component logs to frozen m1_full check-split attempts.

M2's capture wrapper cannot resolve the frozen config's ``${hydra:runtime.output_dir}``
interpolation (M5's and M4's log paths), so for ``m1_full`` it stops after saving the
run and the live per-query history, before writing ``resolved_config.yaml``. This
script does what ``M1/package_reference_evidence.py`` does for the dev reference,
for the check split, reusing M1's resolver:

- copies ``.hydra/{config,hydra,overrides}.yaml`` into ``<attempt>/hydra/``;
- writes ``<attempt>/resolved_config.yaml``;
- copies the M4/M5 component logs and the runner log;
- checks the resolved config against ``run_metadata.json``;
- writes ``evidence_manifest.json`` with SHA-256 of every added file.

Unlike M1's script it never rewrites ``m2_metrics_history.json``: the check runs
have the history captured live by M2's wrapper, which is kept as recorded. It only
touches completed attempts and refuses a target that already has a resolved config.

Run from the repository root of a checkout at the frozen tag:

    M1/MADE/.venv/bin/python M6/package_check_evidence.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from omegaconf import OmegaConf

REPO = Path(__file__).resolve().parents[1]
MADE = REPO / "M1" / "MADE"
RESULTS = MADE / "results"
CHECK = RESULTS / "protocol_v1" / "m1_full" / "check"
SWITCHES = (
    "enable_planning",
    "enable_memory",
    "enable_reflection",
    "enable_exploration",
    "enable_tool_routing",
)


def m1_resolver():
    spec = importlib.util.spec_from_file_location(
        "m1_package", REPO / "M1" / "package_reference_evidence.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolved_config


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(source_dir: Path, resolved_config) -> Path | None:
    config_path = source_dir / ".hydra" / "config.yaml"
    output = Path(str(OmegaConf.load(config_path).experiment.output_dir))
    attempt = (output if output.is_absolute() else MADE / output).resolve()
    if CHECK.resolve() not in attempt.parents or not attempt.is_dir():
        return None
    metadata = json.loads((attempt / "run_metadata.json").read_text())
    if metadata.get("status") != "completed":
        return None
    if (attempt / "resolved_config.yaml").exists():
        raise SystemExit(f"{attempt} already has resolved_config.yaml; not overwriting")
    history = json.loads((attempt / "m2_metrics_history.json").read_text())
    if not history.get("complete_curve"):
        raise SystemExit(f"{attempt}: captured history is incomplete")

    added: list[Path] = []
    (attempt / "hydra").mkdir(exist_ok=True)
    for name in ("config.yaml", "hydra.yaml", "overrides.yaml"):
        source = source_dir / ".hydra" / name
        if source.is_file():
            added.append(Path(shutil.copy2(source, attempt / "hydra" / name)))
    resolved = attempt / "resolved_config.yaml"
    resolved.write_text(resolved_config(config_path, source_dir))
    added.append(resolved)
    for name in (
        "m4_evidence.jsonl",
        "m4_proposal_events.jsonl",
        "m5_decisions.jsonl",
        "run_benchmark.log",
    ):
        source = source_dir / name
        if source.is_file():
            added.append(Path(shutil.copy2(source, attempt / name)))

    config = OmegaConf.load(resolved)
    if (
        list(config.dataset.elements) != metadata["system"]
        or int(config.experiment.seed) != metadata["seed"]
        or int(config.environment.budget) != metadata["query_budget"]
        or not all(bool(config.agent[name]) for name in SWITCHES)
    ):
        raise SystemExit(f"resolved configuration disagrees with metadata: {attempt}")

    manifest = {
        "source_directory": str(source_dir.relative_to(MADE)),
        "target_attempt": str(attempt.relative_to(MADE)),
        "history": "m2_metrics_history.json captured live by M2/run_baselines.py; unchanged",
        "files": {
            str(path.relative_to(attempt)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(added)
        },
    }
    (attempt / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2))
    return attempt


def main() -> int:
    resolved_config = m1_resolver()
    packaged = []
    for source in sorted(RESULTS.glob("*-orb-m1_integrated")):
        attempt = package(source, resolved_config)
        if attempt is not None:
            packaged.append(attempt)
            print(f"packaged {attempt.relative_to(MADE)}")
    print(f"{len(packaged)} completed check attempt(s) packaged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
