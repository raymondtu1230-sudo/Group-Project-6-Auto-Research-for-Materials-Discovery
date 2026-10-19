"""Run the local synthetic MADE integration smoke test without editing MADE."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

M1_DIR = Path(__file__).resolve().parent
MADE_DIR = M1_DIR / "MADE"
RUNNER = MADE_DIR / "scripts" / "run_benchmark.py"


def main() -> None:
    if Path.cwd().resolve() != MADE_DIR:
        raise SystemExit(f"Run this script with the working directory set to {MADE_DIR}")

    sys.path.insert(0, str(M1_DIR))

    # The upstream runner commits a Modal volume even for local runs.
    import modal

    modal.Volume.commit = lambda self: None
    sys.argv = [
        str(RUNNER),
        "agent=m1_integrated",
        "dataset._target_=smoke_dataset.SmokeDataset",
        "dataset.elements=[Li,O]",
        "oracle=analytic",
        "oracle.relax=false",
        "oracle.element_reference_energies_path=null",
        "environment.budget=2",
        "environment.start_with_all_stable=false",
        "environment.compute_elemental_from_oracle=true",
        "environment.filter_by_smact=true",
        "environment.max_stoichiometry=4",
        "agent.planner.max_stoichiometry=4",
        "agent.planner.num_candidates=4",
        "experiment.num_episodes=1",
        "experiment.seed=17",
        "logger.use_wandb=false",
    ]
    runpy.run_path(str(RUNNER), run_name="__main__")


if __name__ == "__main__":
    main()
