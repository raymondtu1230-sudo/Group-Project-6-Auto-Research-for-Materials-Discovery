"""Install M2-owned files into M1's documented slots, preserving other members."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import yaml

M2_DIR = Path(__file__).resolve().parent
REPO = M2_DIR.parent
MADE = REPO / "M1/MADE"


def install() -> dict[str, str]:
    pairs = {
        M2_DIR / "integration/m2_tool_routing.py": MADE
        / "src/made/agents/m2_tool_routing.py",
        M2_DIR / "integration/test_m2_tool_routing.py": MADE
        / "tests/test_m2_tool_routing.py",
        M2_DIR / "configs/m2_routing.yaml": MADE / "configs/agent/m2_routing.yaml",
    }
    if not (MADE / "src/made/agents/m1_integrated.py").is_file():
        raise FileNotFoundError("The M1 MADE integration checkout is required")
    for source in pairs:
        if not source.is_file():
            raise FileNotFoundError(source)
    config_path = MADE / "configs/agent/m1_integrated.yaml"
    text = config_path.read_text()
    config = yaml.safe_load(text)
    expected_target = "made.agents.m2_tool_routing.OutcomeAwareToolRouter"
    current_router = config.get("tool_router")
    if current_router is not None and current_router.get("_target_") != expected_target:
        raise ValueError(
            "A different tool router is configured; refusing to replace it"
        )
    if current_router is None:
        if config.get("generators"):
            raise ValueError("Existing generators need an explicit reviewed merge")
        additions = {
            "generators": {
                "chemeleon": {
                    "_target_": "made.agents.m2_tool_routing.CheckpointedChemeleonGenerator",
                    "task": "csp",
                    "batch_size": 32,
                    "device": "${oc.select:oracle.device,cpu}",
                    "output_dir": None,
                    "seed": "${experiment.seed}",
                }
            },
            "tool_router": {
                "_target_": expected_target,
                "generator_names": ["default", "chemeleon"],
                "seed": "${experiment.seed}",
                "exploration_weight": 0.5,
                "stable_reward": 0.25,
                "late_budget_threshold": 2,
            },
        }
        for field, value in additions.items():
            previous = (
                f"{field}: {{}}\n" if field == "generators" else f"{field}: null\n"
            )
            if text.count(previous) != 1:
                raise ValueError(f"Cannot safely locate the existing {field} field")
            text = text.replace(
                previous, yaml.safe_dump({field: value}, sort_keys=False)
            )
        text = text.replace(
            "\ngenerator:\n  seed:",
            "\ngenerator:\n  _target_: made.agents.m2_tool_routing.CheckpointedRandomGenerator\n  seed:",
        )
    text = text.replace(
        "device: ${oracle.device}", "device: ${oc.select:oracle.device,cpu}"
    )
    manifest = {}
    for source, target in pairs.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest[str(target.relative_to(REPO))] = hashlib.sha256(
            source.read_bytes()
        ).hexdigest()
    config_path.write_text(text)
    manifest[str(config_path.relative_to(REPO))] = hashlib.sha256(
        text.encode()
    ).hexdigest()
    return manifest


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(install(), indent=2))
