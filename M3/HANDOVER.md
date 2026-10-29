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
| M2 | Result tables (`results/*.csv`) and results text (`report/M3_RESULTS.md`) |
| M1, M2, M6 | All 90 frozen-agent runs as complete result folders (`results/frozen_20261025/`): the assigned full-agent ablations `planning_off` and `self_correction_off` (vs `m1_full`), and the component study `m3_full`, `m3_planning_off`, `m3_self_correction_off` |
| M6 | Method text (`report/M3_METHOD.md`) and results text (`report/M3_RESULTS.md`) |

## Notes for each teammate

### M1 (integration)

- **Bug fix: done.** The frozen agent's `m3_planning.py` is identical to M3's
  fixed version, so `m1_full` and every ablation use it (see the bug note in
  [README.md](README.md#the-bug-found-along-the-way)).
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
  (15 / 2 / 1, sign p = 0.0005); self_correction_off 9.50 vs 10.00 (8 / 2 / 8,
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
- **Heads-up:** on M1's frozen tag (`ae7fe81`), your test
  `tests/test_m4_memory.py::test_config_constructs_real_agent` fails. M5's
  config sets `log_path: ${hydra:runtime.output_dir}/...`, which only works
  inside a real Hydra run, not in a plain test. Real runs are not affected:
  all 36 of M3's full-agent runs wrote their M5 log with this setting. This is
  between M4 and M5; M3 is not involved.

### M5 (exploration)

- Exploration runs after M3's self-correction and receives its plan. M3's
  test runs keep exploration off.
- **Failure example for you:** M3's hafnium–nickel–zirconium runs are a clear
  case of over-exploitation. The planner stayed on the nickel–zirconium pair
  for 12–16 of its 20 tries and found 6.0 materials per run, against 11.7 for
  the reference. Logs: `evidence/20261021-dev-ablations/m3_trace_lines.tsv`.
- See the M4 heads-up above about the `log_path` setting.

### M6 (protocol, report, slides)

- **Frozen agent's ablation table:** M3's assigned `planning_off` and
  `self_correction_off` (vs `m1_full`) belong here. Planning: 10.00 → 5.28
  mSUN@20, lower in 15 of 18 pairs (p = 0.0005). Self-correction: 10.00 → 9.50,
  no measurable effect (8 / 2 / 8).
- **Component study:** the `m3_*` methods compare against `m3_full` (and the
  development study against `m1_baseline`). Per `PROTOCOL_ADOPTION.md`
  section 5, these go in the separate **"component vs M1 reference"** table.
- **Planner in the frozen agent:** `m1_full` and every `*_off` version use the
  M3 planner; only `m1_baseline` keeps `diversity`. So the memory test runs
  with a planner that reads memory.
- M3 ran on practice (dev) systems only. `run_ablations.py` refuses any other
  system.

## Results and checks

- Results of both studies: [README.md](README.md#results), with the full
  tables and explanation in [report/M3_RESULTS.md](report/M3_RESULTS.md).
- The 90 frozen-agent runs, their layout and the Chemeleon checksum receipt:
  [results/frozen_20261025/](results/frozen_20261025/).
- Latest check record, on the frozen tag: [test_results.txt](test_results.txt).
