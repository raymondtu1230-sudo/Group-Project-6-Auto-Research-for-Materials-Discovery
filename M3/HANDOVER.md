# M3 handover

What M3 gives each teammate, and what each of them needs to know. For an
overview of M3 itself, start with [README.md](README.md).

## What M3 delivers

M3 adds two components to M1's agent: a **planner** (where to spend the 20
tries) and **self-correction** (notice a stuck search and change course). Both
plug into slots M1's agent already had. All of M3's code is in
`M3/integration/`, laid out where it goes in M1's folder;
`python M3/install.py` checks it is in place.

| To | What |
| --- | --- |
| M1 | One-page design ([DESIGN.md](DESIGN.md)); code, settings and tests (`integration/`, merged by M1 in `2fcc214`) |
| M1 | The bug fix, installed with `python M3/install.py --install` |
| M2 | Result tables (`results/*.csv`) and results text (`report/M3_RESULTS.md`) |
| M1, M2, M6 | All 90 frozen-agent runs as complete result folders (`results/frozen_20261025/`): the assigned full-agent ablations `planning_off` and `self_correction_off` (vs `m1_full`), and the component study `m3_full`, `m3_planning_off`, `m3_self_correction_off` |
| M6 | Method text (`report/M3_METHOD.md`), results text and slides (`report/`) |

## Notes for each teammate

### M1 (integration)

- **Install the bug fix in the final agent.** Your full agent (`m1_full`)
  uses the M3 planner, so it needs the fix described below. Run
  `python M3/install.py --install`. It updates only M3's own two files in your
  folder (`m3_planning.py` and its test); your files are not touched.
- `install.py` shows your agent config as `merged`: you added M4's and M5's
  settings and kept M3's lines. That is expected.
- The default planner is still your `diversity` planner, so `m1_baseline`
  stays reproducible. `run_experiment.py` switches in the M3 planner for every
  plug-in version and adds `m3_full`, `m3_planning_off` and
  `m3_self_correction_off`.

### M2 (baselines and results table)

- Files for you: `results/m3_ablation_runs.csv` (one row per run) and
  `results/m3_ablation_summary.csv` (one row per version), plus
  `report/M3_RESULTS.md`.
- **M3's assigned ablations:** `results/frozen_20261025/protocol_v1/planning_off`
  and `.../self_correction_off`, 18 runs each, are `m1_full` with only that
  part off (memory, exploration and routing on, same Chemeleon archive). Pair
  them with M1's `m1_full` reference: planning_off 5.28 vs 10.00 mSUN@20
  (15 / 2 / 1, sign p = 0.001); self_correction_off 9.50 vs 10.00 (8 / 2 / 8,
  p = 1.0).
- **Component study:** the same folder holds `m3_full`, `m3_planning_off` and
  `m3_self_correction_off` (exploration and routing off). Pair those with
  `m3_full`, not `m1_full`.
- All 90 runs are in M1's reference layout (resolved config, M4 and M5 logs,
  run logs, `m2_metrics_history.json`, SHA-256 manifest), and `M2/evaluate.py`
  validates all 90 with no issues.
- The component-study tables in `results/*.csv` come from development runs
  with tool routing off and the default generator, so they do not depend on
  your part.

### M4 (memory)

- The planner reads your memory each time it compares areas. You confirmed
  that M3's decision log shows memory in use when it is on, and none when it is
  off.
- Every M3 run sets its own `M4_RUN_ID`, as your adoption notes ask.
- **Heads-up:** on `main` at `24d29d8`, your test
  `tests/test_m4_memory.py::test_config_constructs_real_agent` fails. M5's
  config change added `log_path: ${hydra:runtime.output_dir}/...`, which only
  works inside a real Hydra run, not in a plain test. This is between M4 and
  M5; M3 is not involved, and M3's runs used the earlier config.

### M5 (exploration)

- Exploration runs after M3's self-correction and receives its plan. M3's
  test runs keep exploration off.
- **Failure example for you:** M3's hafnium–nickel–zirconium runs are a clear
  case of over-exploitation. The planner stayed on the nickel–zirconium pair
  for 12–16 of its 20 tries and found 6.0 materials per run, against 11.7 for
  the reference. Logs: `evidence/20261021-dev-ablations/m3_trace_lines.tsv`.
- See the M4 heads-up above about the new `log_path` setting.

### M6 (protocol, report, slides)

- **Frozen agent's ablation table:** M3's assigned `planning_off` and
  `self_correction_off` (vs `m1_full`) belong here. Planning: 10.00 → 5.28
  mSUN@20, lower in 15 of 18 pairs (p = 0.001). Self-correction: 10.00 → 9.50,
  no measurable effect (8 / 2 / 8).
- **Component study:** the `m3_*` methods compare against `m3_full` (and the
  development study against `m1_baseline`). Per `PROTOCOL_ADOPTION.md`
  section 5, these go in the separate **"component vs M1 reference"** table.
- **Planner in the frozen agent:** `m1_full` and every `*_off` version use the
  M3 planner; only `m1_baseline` keeps `diversity`. So the memory test runs
  with a planner that reads memory.
- M3 ran on practice (dev) systems only. `run_ablations.py` refuses any other
  system.

## The bug and the fix

- **What happened:** in the first full set of runs, results with
  self-correction on and off were identical in all 18 pairs.
- **Why:** the simulator marks every new structure as "newly discovered",
  even unstable ones (360 of 360 tries in `m3_full`; only 96 were stable).
  M3 read that mark as progress, so it never thought it was stuck, and the
  planner counted every remembered try as a success.
- **Fix:** progress now means a new **stable** material, and memory failures
  are unstable results. The tests now use realistic simulator outputs.
- **Re-runs:** all 72 runs were redone with the fix. The summary script only
  accepts M3 runs made with the current M3 code (it checks a fingerprint of the
  file), so old runs cannot slip in. The old results remain in the git history
  (commit `e1a40d8`).

## Results (fixed code)

All 72 runs ran on one PC (AMD Ryzen 7 9700X, CPU only) from the same code,
following section 0 of [EXPERIMENT_RUNBOOK.md](EXPERIMENT_RUNBOOK.md). All
finished on the first attempt, and the reference matched M1's earlier recorded
numbers exactly in all 18 pairs. Evidence:
[evidence/20261021-dev-ablations/](evidence/20261021-dev-ablations/).

| Comparison | Change in materials found per run | Better / same / worse (of 18) |
| --- | --- | --- |
| M3 vs reference | +1.50 (6.50 vs 5.00) | 9 / 3 / 6 |
| Effect of planning | +1.39 | 12 / 1 / 5 |
| Effect of self-correction | +0.67 | 7 / 10 / 1 |

M3 helps on hard systems and loses on easy ones; the explanation is in
`report/M3_RESULTS.md`, section "Why".

## Results on the frozen agent

| Method (18 runs each) | mSUN@20 | Compared with | Better / same / worse |
| --- | --- | --- | --- |
| `planning_off` | 5.28 | `m1_full` 10.00 | `m1_full` better in 15 / 2 / 1 (p = 0.001) |
| `self_correction_off` | 9.50 | `m1_full` 10.00 | 8 / 2 / 8 (p = 1.0) |
| `m3_planning_off` | 5.11 | `m3_full` 6.50 | identical to the development runs |
| `m3_self_correction_off` | 5.83 | `m3_full` 6.50 | identical to the development runs |

Details and folder layout: [results/frozen_20261025/README.md](results/frozen_20261025/README.md).

## Checks (`main` at `24d29d8`, run from `M1/MADE`)

| Check | Result |
| --- | --- |
| `install.py` | M3 files `ok`, M1-owned files `merged` |
| M1 + M3 tests (with M4 on the path) | 41 passed |
| M1 protocol tests | 8 passed |
| M3 tool tests | 17 passed |
| Code style (ruff) | passes |
| M1 + M3 + M4 + M5 tests together | 58 passed, 1 failed (the M4/M5 issue above, not M3) |
