# M3 dev ablations, real runs (21 Oct 2026)

The 72 protocol runs behind `M3/report/M3_RESULTS.md` and
`M3/results/*.csv`: `m1_baseline`, `m3_full`, `m3_planning_off` and
`m3_self_correction_off` on the 6 dev systems with seeds 17, 29 and 43.

## How they were run

- Code: `main` at `81b0e36`, plus `python M3/install.py --install`, which put the
  progress-signal fix into M1 (`m3_planning.py` sha256
  `71a24373…5887d`). Every arm ran from this one checkout.
- Setup: sections 1–3 of `M3/EXPERIMENT_RUNBOOK.md` on one Windows 11 PC
  (AMD Ryzen 7 9700X, 16 threads, 31 GB, CPU only), Python 3.12.15 through uv.
- Command: `uv run python ../../M3/run_ablations.py --jobs 3` from `M1/MADE`,
  so 3 runs at a time with 5 CPU threads each. Wall time 14:13–18:14.
- Protocol: ORB v3 oracle, 20 queries, one episode per seed, M4 memory on in
  every arm. Dev split only.

## Outcome

- 72 of 72 runs completed on the first attempt. None failed, resumed from a
  checkpoint or shared a checkpoint folder.
- Every `m3_*` run recorded the current `m3_planning.py` hash
  (`run_index.csv`, column `m3_code_current`).
- The re-run `m1_baseline` matches M1's recorded 19 Oct values
  (`M1/m1_baseline_dev_summary.csv`) in all 18 pairs, for both mSUN and AUDC.

## Files

| File | Contents |
| --- | --- |
| `run_index.csv` | One row per run: method, system, seed, attempt, status, oracle queries, wall time, recorded M3 code hash |
| `m3_trace_lines.tsv` | Every `M3 review:` (planner sub-goal choice) and `M3 re-plan:` (self-correction) line from all 72 console logs |
| `sweep_console.log` | Output of `run_ablations.py` for the whole sweep |
| `traced-case-Co-Mg-Na-seed17/` | The clearest self-correction case: `m3_full` (re-plans at queries 6 and 13, 7 structures) against `m3_self_correction_off` (3 structures). Run metadata, summary and phase-diagram plot for each |

Full per-run outputs (trajectories, console logs, M4 evidence) are about
1 MB per run and stay out of git. They are in
`M1/MADE/results/protocol_v1/` on the machine that ran them, and the runs can
be reproduced with the command above.
