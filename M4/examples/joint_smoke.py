"""Two-query synthetic M1/M3/M4 smoke; run from M1/MADE, argument on or off.

Uses AnalyticOracle, never real-material evidence or a performance benchmark.
Output is preserved under results/m4-joint-synthetic-20261020-<arm>.
Use a fresh output name when repeating; existing output is never overwritten.
"""

import runpy
import sys
from pathlib import Path

import modal

root = Path.cwd()
sys.path.insert(0, str(root.parent))
modal.Volume.commit = lambda self: None
arm = sys.argv[1] if len(sys.argv) == 2 else None
if arm not in {"on", "off"}:
    raise SystemExit("Usage: python ../../M4/examples/joint_smoke.py on|off")
if not (root / "scripts/run_benchmark.py").is_file():
    raise SystemExit("Run from M1/MADE")
output = root / "results" / f"m4-joint-synthetic-20261020-{arm}"
if output.exists():
    raise SystemExit("Preserve existing output; use a new attempt")
runner = root / "scripts/run_benchmark.py"
sys.argv = [
    str(runner),
    "agent=m1_integrated",
    "agent/planner=m3_research",
    "agent._target_=m4_memory.capture.CapturedM1IntegratedAgent",
    f"+agent.capture_path={output}/proposal_events.jsonl",
    f"+agent.capture_run_id=joint-synthetic-{arm}",
    "+agent.capture_episode_id=0",
    f"agent.memory_manager.log_path={output}/memory.jsonl",
    f"agent.memory_manager.run_id=joint-synthetic-{arm}",
    f"agent.enable_memory={str(arm == 'on').lower()}",
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
    f"experiment.output_dir={output}",
]
runpy.run_path(str(runner), run_name="__main__")
