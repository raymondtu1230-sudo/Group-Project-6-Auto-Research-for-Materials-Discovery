"""Run one reproducible M1 protocol-v1 system/seed with the official runner."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import runpy
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import yaml
from cost_tracking import build_cost_record

M1_DIR = Path(__file__).resolve().parent
MADE_DIR = M1_DIR / "MADE"
RUNNER = MADE_DIR / "scripts" / "run_benchmark.py"
PROTOCOL = yaml.safe_load((M1_DIR / "protocol" / "protocol_v1.yaml").read_text())
SEEDS = tuple(PROTOCOL["repeats"]["seeds"])
# M3 component ablations, measured against m1_baseline so they do not wait for
# the plugin-complete m1_full: M3 planner + self-correction on top of the
# baseline, then each M3 part switched off.
M3_METHODS = ("m3_full", "m3_planning_off", "m3_self_correction_off")
METHODS = tuple(
    PROTOCOL["methods"]["required"]
    + PROTOCOL["methods"]["ablations"]
    + ["m1_baseline", *M3_METHODS]
)
QUERY_BUDGET = int(PROTOCOL["environment"]["query_budget"])
SWITCHES = (
    "enable_planning",
    "enable_memory",
    "enable_reflection",
    "enable_exploration",
    "enable_tool_routing",
)


def m1_agent_overrides(method: str) -> list[str]:
    """Switch and planner overrides for methods run with ``agent=m1_integrated``."""
    if method == "m1_baseline" or method in M3_METHODS:
        # m1_baseline is the currently runnable M1 reference: planning and
        # bounded memory are active; future member plug-ins remain disabled.
        flags = dict.fromkeys(SWITCHES, False)
        flags["enable_planning"] = True
        flags["enable_memory"] = True
        flags["enable_reflection"] = method != "m1_baseline"
    else:
        flags = dict.fromkeys(SWITCHES, True)
    if method in ("planning_off", "m3_planning_off"):
        flags["enable_planning"] = False
    elif method == "memory_off":
        flags["enable_memory"] = False
    elif method in ("self_correction_off", "m3_self_correction_off"):
        flags["enable_reflection"] = False
    elif method == "exploration_off":
        flags["enable_exploration"] = False
    elif method == "tool_routing_off":
        flags["enable_tool_routing"] = False
    overrides = [f"agent.{key}={str(value).lower()}" for key, value in flags.items()]
    # m1_baseline keeps the diversity planner its recorded runs used; every
    # plug-in method plans with M3's sub-goal planner.
    if method != "m1_baseline":
        overrides.append("agent/planner=m3_research")
    return overrides


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=METHODS, required=True)
    parser.add_argument("--split", choices=("dev", "check"), required=True)
    parser.add_argument(
        "--system", required=True, help="Hyphen-separated element symbols"
    )
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--attempt", type=int, default=1)
    return parser.parse_args()


def installed_versions(names: tuple[str, ...]) -> dict[str, str]:
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return versions


def main() -> None:
    args = parse_args()
    if args.attempt < 1:
        raise SystemExit("--attempt must be a positive integer")
    if Path.cwd().resolve() != MADE_DIR:
        raise SystemExit(f"Run from {MADE_DIR}")

    system = args.system.split("-")
    if len(system) != 3 or not all(system):
        raise SystemExit("--system must be a ternary system such as Mg-Sn-Sr")
    system_file = M1_DIR / "protocol" / f"{args.split}_systems.json"
    allowed_systems = json.loads(system_file.read_text())
    if system not in allowed_systems:
        raise SystemExit(f"{args.system} is not listed in {args.split}_systems.json")

    import modal
    import torch

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    modal.Volume.commit = lambda self: None
    if args.method in {
        "m1_full",
        "m1_baseline",
        *M3_METHODS,
        *[m for m in METHODS if m.endswith("_off")],
    }:
        agent = "m1_integrated"
    else:
        agent = args.method

    overrides = [
        f"agent={agent}",
        f"dataset.elements=[{','.join(system)}]",
        "dataset.thermo_types=[GGA_GGA+U]",
        "oracle=orb",
        f"oracle.model_name={PROTOCOL['oracle']['model_name']}",
        f"oracle.device={PROTOCOL['oracle']['device']}",
        f"oracle.relax={str(PROTOCOL['oracle']['relax']).lower()}",
        f"oracle.relax_kwargs.optimizer={PROTOCOL['oracle']['optimizer']}",
        f"oracle.relax_kwargs.fmax={PROTOCOL['oracle']['fmax']}",
        f"oracle.relax_kwargs.steps={PROTOCOL['oracle']['max_steps']}",
        f"oracle.relax_kwargs.relax_unit_cell={str(PROTOCOL['oracle']['relax_unit_cell']).lower()}",
        f"environment.budget={QUERY_BUDGET}",
        f"environment.max_stoichiometry={PROTOCOL['environment']['max_stoichiometry']}",
        f"environment.stability_tolerance={PROTOCOL['environment']['stability_tolerance_ev_per_atom']}",
        f"environment.filter_by_smact={str(PROTOCOL['environment']['filter_by_smact']).lower()}",
        "environment.include_near_stable_from_ground_truth="
        f"{str(PROTOCOL['environment']['include_near_stable_from_ground_truth']).lower()}",
        "experiment.num_episodes=1",
        f"experiment.seed={args.seed}",
        "experiment.verbose=false",
        "logger.use_wandb=false",
        f"experiment.output_dir=results/protocol_v1/{args.method}/{args.split}/{args.system}/seed_{args.seed}/attempt_{args.attempt:02d}",
    ]

    if agent == "m1_integrated":
        overrides.extend(m1_agent_overrides(args.method))
        overrides.append("agent.generator.seed=${experiment.seed}")
        overrides.append("agent.planner.seed=${experiment.seed}")
        overrides.append("agent.scorer.seed=${experiment.seed}")
    else:
        overrides.extend(
            [
                "++agent.planner.seed=${experiment.seed}",
                "++agent.scorer.seed=${experiment.seed}",
                "++agent.generator.base_generator.seed=${experiment.seed}",
            ]
        )
        if args.method == "chemeleon_generative_baseline":
            overrides.append("agent.generator.base_generator.device=cpu")

    sys.argv = [str(RUNNER), *overrides]
    output_dir = MADE_DIR / Path(
        f"results/protocol_v1/{args.method}/{args.split}/{args.system}/seed_{args.seed}/attempt_{args.attempt:02d}"
    )
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(
            f"Output already exists: {output_dir}; preserve it and use --attempt {args.attempt + 1}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    tracked_inputs = (
        M1_DIR / "run_experiment.py",
        M1_DIR / "EXPERIMENT_PROTOCOL.md",
        M1_DIR / "protocol" / "protocol_v1.yaml",
        *sorted((MADE_DIR / "src/made/agents").rglob("*.py")),
        *sorted((MADE_DIR / "configs").rglob("*.yaml")),
        MADE_DIR / "scripts/run_benchmark.py",
        MADE_DIR / "src/made/envs/convex_hull.py",
        MADE_DIR / "src/made/evaluation/metrics.py",
        MADE_DIR / "src/made/data/chemical_system.py",
        MADE_DIR
        / "data/systems_10_mp_20/systems_ternary_n10_maxatoms20_intermetallic_smact.json",
    )
    metadata = {
        "protocol_version": PROTOCOL["protocol_version"],
        "method": args.method,
        "split": args.split,
        "system": system,
        "seed": args.seed,
        "attempt": args.attempt,
        "query_budget": QUERY_BUDGET,
        "protocol_settings": PROTOCOL,
        "episodes": 1,
        "command": sys.argv,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "machine": platform.node(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "made_upstream_commit": subprocess.check_output(
            ["git", "-C", str(MADE_DIR), "rev-parse", "HEAD"], text=True
        ).strip(),
        "m1_input_sha256": {
            str(path.relative_to(M1_DIR)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in tracked_inputs
        },
        "dependency_versions": installed_versions(
            ("torch", "numpy", "pymatgen", "hydra-core", "orb-models")
        ),
    }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))
    started = time.monotonic()
    try:
        runpy.run_path(str(RUNNER), run_name="__main__")
    except BaseException as error:
        metadata["status"] = "failed"
        metadata["error"] = f"{type(error).__name__}: {error}"
        raise
    else:
        metadata["status"] = "completed"
    finally:
        metadata["wall_time_seconds"] = round(time.monotonic() - started, 3)
        metadata["cost"] = build_cost_record(
            output_dir=output_dir,
            method=args.method,
            status=metadata["status"],
            query_budget=QUERY_BUDGET,
            wall_time_seconds=metadata["wall_time_seconds"],
        )
        metadata_path.write_text(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
