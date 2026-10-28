# Group Project 6: Auto Research for Materials Discovery

NTU Group Project 6 (instructor Prof. Bo An, TA Dr Xiao Yushan). An Auto Research agent that
chooses which crystal structures to send to the fixed MADE oracle under a budget of
20 queries per chemical system. The oracle, base model, evaluator and tools are unchanged;
only the research strategy is ours.

- **Report:** [Group 6 Final Report (Google Doc)](https://docs.google.com/document/d/1cFLFI4ynmty_PtoWm6DKmu1vml9z80SAl3uNZMMFm1Y/edit)
- **Slides:** [Group6_Slides (Google Slides)](https://docs.google.com/presentation/d/1v9F-VjoZj9hmEPx-rK8zRO7CWAS5yPSpCopfnp7pH4g/edit)
- **Frozen agent:** git tag `m1-freeze-20261025` ([`M1/FREEZE_RECORD.md`](M1/FREEZE_RECORD.md))

## Results

mSUN@20 (stable, unique, novel structures found within 20 queries; higher is better).

| Method | Development (6 systems × 3 seeds) | Held-out public check set (4 systems, seed 17) |
| --- | --- | --- |
| **Frozen agent (`m1_full`)** | **10.00 ± 0.88** | **14.00** |
| Chemeleon baseline | 6.94 ± 1.11 | 7.25 |
| Random baseline | 4.06 ± 0.63 | 6.25 |

Ablations (frozen agent with one switch off, development): planning −4.72,
tool routing −2.28, memory −0.89, self-correction −0.50, exploration −0.33 mSUN@20.
The course did not release a hidden test set; the check set is our held-out split and
is not the course hidden test. Held-out uses one seed per method because of compute.

Full tables, AF/EF, discovery curves, costs and failure cases are in the report.
Per-material results: [`M6/results/20261028-per-material-table/`](M6/results/20261028-per-material-table/).

## Repository map

| Folder | Owner | Contents |
| --- | --- | --- |
| [`M1/`](M1/) | M1 · integration | Vendored MADE (`M1/MADE`, upstream `bffda0c9`), integrated agent and switches, protocol v1 (`M1/protocol/`), runner `run_experiment.py`, freeze record, frozen reference runs |
| [`M2/`](M2/) | M2 · tool routing, evaluation | Router, baseline runs and evidence, evaluator `evaluate.py`, 198-run aggregation (`M2/aggregation/20261027_m3_full_agent/`) |
| [`M3/`](M3/) | M3 · planning, self-correction | Planner and self-correction, planning/self-correction ablations, component study |
| [`M4/`](M4/) | M4 · memory | Memory manager and evidence capture, memory ablation |
| [`M5/`](M5/) | M5 · exploration | UCB exploration policy, decision logs, exploration ablation, failure trajectories |
| [`M6/`](M6/) | M6 · experiment design, report | Protocol adoption, held-out (check) runs and scoring, generalization analysis, requirements checklist |

## Reproduce

```bash
git checkout m1-freeze-20261025
cd M1/MADE && uv sync --locked          # Python 3.12, locked dependencies
# put MATERIALS_PROJECT_API_KEY in the ignored M1/MADE/.env
uv run python ../../M2/run_baselines.py --method m1_full --split dev --system Mg-Sn-Sr --seed 17 --attempt 1
uv run python ../../M2/evaluate.py --results-root results/protocol_v1 --output <new dir> --split dev
```

Methods: `m1_full`, `random_generator_baseline`, `chemeleon_generative_baseline`, and the
ablations `planning_off`, `memory_off`, `self_correction_off`, `exploration_off`,
`tool_routing_off` (development only). For `m1_full`, put `M4/src` on `PYTHONPATH`.
Seeds 17, 29, 43; B = 20; ORB `orb-v3-conservative-inf-omat` on CPU. Raw trajectories,
configs, histories and failed attempts behind every number are in the member folders
with SHA-256 checksums. See [`M1/EXPERIMENT_PROTOCOL.md`](M1/EXPERIMENT_PROTOCOL.md),
[`M2/aggregation/20261027_m3_full_agent/REPRODUCTION.md`](M2/aggregation/20261027_m3_full_agent/REPRODUCTION.md)
and [`M6/PROTOCOL_ADOPTION.md`](M6/PROTOCOL_ADOPTION.md).
