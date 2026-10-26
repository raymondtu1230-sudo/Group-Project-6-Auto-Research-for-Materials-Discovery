# M3 ablations on the frozen agent

M3's two assigned ablations, run on M1's frozen agent and returned as complete
result folders, as the team's freeze instructions ask.

| | |
| --- | --- |
| Methods | `m3_planning_off` (planning off), `m3_self_correction_off` (self-correction off) |
| Runs | 2 methods × 6 dev systems × seeds 17, 29, 43 = 36 runs, all `attempt_01` |
| Failures | None; no attempt overwritten |
| Frozen version | Tag `m1-freeze-20261025` |
| Machine | Windows 11 PC, AMD Ryzen 7 9700X, CPU only, 3 runs at a time |

**Version note.** The runs were made when the tag pointed to `02e0026`. M1
then moved the tag to `ae7fe81`, which adds reference evidence only: agent
code, configuration, protocol, dependencies and runner are identical between
the two commits. The working tree had no modified tracked files.

## What each method switches off

Checked from every run's `resolved_config.yaml`:

| Method | Planning | Memory | Self-correction | Exploration | Tool routing |
| --- | --- | --- | --- | --- | --- |
| `m3_full` (for comparison) | on | on | on | off | off |
| `m3_planning_off` | **off** | on | on | off | off |
| `m3_self_correction_off` | on | on | **off** | off | off |

Each method switches off exactly one M3 part compared with `m3_full`.
Exploration (M5) and tool routing (M2) are off in all three, so compare these
runs with `m3_full`, not with `m1_full`, which has all five parts on.

## Results

| Method | mSUN@20 (mean of 18) | AUDC (mean of 18) |
| --- | --- | --- |
| `m3_planning_off` | 5.11 | 49.2 |
| `m3_self_correction_off` | 5.83 | 58.3 |

All 36 runs reproduce the earlier pre-freeze runs exactly, run by run (mSUN
and AUDC); with `m3_full` at 6.50, planning adds +1.39 and self-correction
+0.67. Full analysis: [../../report/M3_RESULTS.md](../../report/M3_RESULTS.md).

## Folder layout

```
protocol_v1/<method>/dev/<system>/seed_<seed>/attempt_01/
```

Each `attempt_01` folder holds the same files as M1's frozen reference runs:

| File | What it is |
| --- | --- |
| `run_metadata.json` | Status, settings, cost and input hashes |
| `trajectories/episode_000.json` | Full 20-query trajectory |
| `summary/` | Official metrics and plots |
| `hydra/` | Original Hydra configuration and overrides |
| `resolved_config.yaml` | Fully resolved configuration |
| `m4_evidence.jsonl` | M4 memory component log |
| `run_benchmark.log` | MADE's log (empty: MADE's runner resets logging) |
| `run_console.log` | Full console output, including `M3 review:` and `M3 re-plan:` lines |
| `m2_metrics_history.json` | Per-query mSUN and AUDC, rebuilt from the trajectory with M1's `curve_from_trajectory` and checked against the final metrics |
| `evidence_manifest.json` | SHA-256 and size of every added file |

No M5 log is present because exploration is off in these methods.
`protocol_v1/<method>/dev/m3-ablation-sweep-20261025.log` is the sweep's
console output.

## Checks

- `M2/evaluate.py` validates all 36 runs with no issues; both methods are
  complete (18 of 18).
- Every per-query curve matches its run's final mSUN and AUDC.
- The Materials Project API key appears in none of the files.

## How they were run

From `M1/MADE` on the frozen tag, with M4 installed:

```bash
uv run python ../../M3/run_ablations.py --methods m3_planning_off m3_self_correction_off --no-baseline --jobs 3
```

`run_ablations.py` calls `M1/run_experiment.py` once per run with the same
arguments as the team's loop, plus an explicit `--attempt` and a unique
`M4_RUN_ID` per run.
