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
| M1, M2, M6 | The 36 assigned ablation runs on the frozen agent, as complete result folders (`results/frozen_20261025/`) |
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
- M3's runs keep tool routing off and use the default generator, so they do
  not depend on your part.
- **Frozen-agent runs:** `results/frozen_20261025/protocol_v1/` holds the 36
  `m3_planning_off` and `m3_self_correction_off` runs in M1's reference
  layout (resolved config, M4 log, run logs, `m2_metrics_history.json`,
  SHA-256 manifest). `M2/evaluate.py` validates all 36 with no issues. Pair
  them with `m3_full`, not `m1_full`: exploration and routing are off in all
  M3 methods.

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

- M3 compares against `m1_baseline` re-run with the same setup as the M3
  versions (M4 memory on in all of them). Per `PROTOCOL_ADOPTION.md` section 5,
  this goes in the **"component vs M1 reference"** table, separate from the
  frozen agent's ablation table. `M3_RESULTS.md` is titled that way.
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

## Checks (`main` at `24d29d8`, run from `M1/MADE`)

| Check | Result |
| --- | --- |
| `install.py` | M3 files `ok`, M1-owned files `merged` |
| M1 + M3 tests (with M4 on the path) | 41 passed |
| M1 protocol tests | 8 passed |
| M3 tool tests | 17 passed |
| Code style (ruff) | passes |
| M1 + M3 + M4 + M5 tests together | 58 passed, 1 failed (the M4/M5 issue above, not M3) |
