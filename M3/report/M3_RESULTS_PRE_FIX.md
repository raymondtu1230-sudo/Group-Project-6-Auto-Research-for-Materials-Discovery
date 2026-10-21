# M3 results BEFORE the progress-signal fix (21 Oct, 72 runs)

_Kept as the pre-fix record. In these runs M3 counted any `is_newly_discovered` observation as progress. MADE sets that flag on every query (360 of 360 in `m3_full`; 96 were stable), so self-correction's no-progress trigger never fired and the planner's memory review counted every remembered query as a success. The fixed rerun is in `M3_RESULTS.md`._

Setup: protocol v1 development systems, ORB v3 oracle, budget 20 queries, seeds 17/29/43, one episode per seed. mSUN = stable, unique, novel structures found (primary metric); AUDC = area under the discovery curve.

## Per-method summary (mean ± std over runs)

| Method | Runs | mSUN@20 | mSUN fraction | AUDC | AF | EF | Re-plans / run |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `m1_baseline_recorded` | 18 | 5.00 ± 4.41 | 0.25 ± 0.22 | 39.39 ± 36.13 | n/a | n/a | n/a |
| `m1_baseline` | 18 | 5.00 ± 4.41 | 0.25 ± 0.22 | 39.39 ± 36.13 | 0.00 ± 0.00 | 0.00 ± 0.00 | n/a |
| `m3_full` | 18 | 5.33 ± 2.99 | 0.27 ± 0.15 | 51.83 ± 32.30 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.0 |
| `m3_planning_off` | 18 | 5.06 ± 3.13 | 0.25 ± 0.16 | 47.69 ± 29.77 | 0.00 ± 0.00 | 0.00 ± 0.00 | 6.0 |
| `m3_self_correction_off` | 18 | 5.33 ± 2.99 | 0.27 ± 0.15 | 51.83 ± 32.30 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.0 |

`m1_baseline_recorded` is M1's reference as recorded on 19 Oct (`M1/m1_baseline_dev_summary.csv`). It ran before M4's memory manager became the default memory in `m1_integrated.yaml`, so it is shown for context only and is not used in the paired comparisons below.

## Component vs M1 reference (paired by system and seed)

Following M6's `PROTOCOL_ADOPTION.md` section 5, this table compares M3 configurations with `m1_baseline`. It is not the frozen agent's component ablation (`m1_full` with one switch off), which is reported separately.

| Comparison | Measures | Pairs | Δ mSUN (mean ± std) | Better / same / worse | Δ AUDC |
| --- | --- | --- | --- | --- | --- |
| `m3_full` − `m1_baseline` | M3 (planner + self-correction) vs M1 reference | 18 | +0.33 ± 5.05 | 7 / 3 / 8 | 12.44 |
| `m3_full` − `m3_planning_off` | contribution of M3 planning | 18 | +0.28 ± 4.48 | 11 / 0 / 7 | 4.14 |
| `m3_full` − `m3_self_correction_off` | contribution of M3 self-correction | 18 | +0.00 ± 0.00 | 0 / 18 / 0 | 0.00 |

## What changed (generated)

- M3 (planner + self-correction) vs M1 reference: `m3_full` found 0.33 more stable-unique-novel structures per run than `m1_baseline` on average, better in 7 of 18 paired runs, the same in 3 and worse in 8.
- Contribution of M3 planning: `m3_full` found 0.28 more stable-unique-novel structures per run than `m3_planning_off` on average, better in 11 of 18 paired runs, the same in 0 and worse in 7.
- Contribution of M3 self-correction: `m3_full` found the same number of stable-unique-novel structures per run as `m3_self_correction_off` on average, better in 0 of 18 paired runs, the same in 18 and worse in 0.
- Self-correction re-planned 108 times across 36 runs with it on (0 for no progress in the window, 108 for repeated formulas).

Per-run values: `M3/results/pre_fix/m3_ablation_runs.csv`.
