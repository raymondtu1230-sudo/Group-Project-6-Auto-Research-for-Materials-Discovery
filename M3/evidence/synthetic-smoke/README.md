# Synthetic smoke run (M3 planner + self-correction)

One episode through MADE's official `scripts/run_benchmark.py`, run on
19 Oct 2026 (Windows, CPU). It checks that M3 loads through Hydra and runs end
to end. It is **not** a performance result: the dataset is M1's synthetic Li-O
smoke set and the oracle is MADE's analytic Lennard-Jones oracle.

- **Overrides:** `overrides.yaml` lists them. They are M1's smoke settings plus
  `agent/planner=m3_research`, `agent.enable_reflection=true` and
  `environment.budget=12`.
- **Config:** `resolved_config.yaml` confirms `M3ResearchPlanner` and
  `M3StuckReplanPolicy` were instantiated.
- **Result:** 12 of 12 queries were used. `summary.json` holds the official
  metrics, and `episode_000.json` the per-query trajectory.
  `phase_diagram_episode_000.png` is the final observed hull.
- **M3 activity:** `m3_log_lines.txt` holds three `M3 review:` lines (one per
  4-query batch, with memory records growing 0, 4, 8). No re-plan fired:
  almost every query on this tiny system found a new phase, so the search
  never stalled. `../synthetic-demo/` shows re-plans firing.
