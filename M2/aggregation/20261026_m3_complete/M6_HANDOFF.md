# Shared results after the complete M3 handoff — 26 October 2026

M3 has now supplied all 18 original `m3_full` result directories. Together with its two OFF arms, the complete 54-run component study is available for independent paired evaluation. This release supersedes the earlier 126-run intake and its missing-comparator qualification.

## Frozen Full study and generator baselines

| Method | Units | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: | ---: |
| Random | 18 | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon | 18 | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen M1 Full | 18 | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Tool routing OFF | 18 | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |
| Memory OFF | 18 | 9.1111 ± 1.3472 | 86.9444 ± 9.0252 |

The memory comparison remains mixed across pairs: Full wins/ties/loses 8/3/7 mSUN pairs and wins/loses 9/9 AUDC pairs. The positive aggregate difference does not imply a uniform benefit or statistical significance.

## Complete M3 component study

Exploration and tool routing are OFF in all three M3 profiles. Planning, memory and self-correction are ON in `m3_full`; each OFF arm changes only its named component relative to that comparator.

| Method | Validated units | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: | ---: |
| `m3_full` | 18 | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| `m3_planning_off` | 18 | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| `m3_self_correction_off` | 18 | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

The paired component differences, comparator minus OFF, are **+1.3889 mSUN / +13.5278 AUDC for planning** and **+0.6667 mSUN / +4.4444 AUDC for self-correction**. These are effects within this M3 component setting. Do not relabel them as isolated effects in the all-enabled `m1_full` agent or as held-out results.

All tables equally average the six dev systems within each seed, then report mean and sample SD across the three seed means. This differs from SD over 18 pooled runs. Every unit uses seeds 17/29/43, CPU ORB v3 conservative, B=20 and one episode.

## Assembly files and metric direction

The shared report contains all 144 real accepted episodes across eight methods. `per_run_with_baseline_comparisons.csv` and `per_method_summary.csv` include all 288 system/seed comparisons against Random and Chemeleon, including baseline self-comparisons. `paired_m3_component_ablations.csv` contains the 36 matched M3 comparisons. Its score differences use `m3_full minus OFF`; its directional AF/EF use `proposal=OFF, baseline=m3_full`. Keep those directions explicit. Full-agent memory/routing comparisons remain separate.

The discovery-curve figure now plots the actual supplied `m3_full` history alongside both M3 OFF arms in its own panel. There is no endpoint interpolation or fabricated missing history. The official EF default cap is 100, with the original safe-denominator and zero conventions; AF/EF are computed per paired history before seed-first aggregation. They are discovery metrics, not machine-runtime ratios.

## Source and history provenance

The M3 OFF arms retain their actual `02e0026bf450f71f4f7862228d295f5b02b49e12` execution revision. New `m3_full` units retain `ae7fe81991c56dd2d77685220b74ddbef11039c7`. The latter adds reference evidence; scientific source/configuration fingerprints are checked for compatibility. No original metadata is rewritten to make the revisions appear identical. Windows checkout line endings are handled explicitly in the source audit.

M3's histories remain labelled reconstructions from its original trajectories. Prefix and AUDC checks validate those supplied records and arithmetic; they do not constitute a new independent hull/novelty calculation. M1 histories retain their reconstruction label. M2 routing histories remain separately validated offline reevaluations of recorded structures and energies; original incomplete capture records stay preserved. M4 OFF histories retain checkpoint-capture provenance.

Costs retain original elapsed times, machine labels and unknown counters. Known USD 0 model fees exclude hardware, electricity and uninstrumented work. No model, oracle, agent, or Materials Project call is made in this aggregation.

## Current responsibility and remaining group work

**M3's assigned 54-run component package is complete.** The complete comparator request is closed. Per M3's clarification and the user's instruction, full-agent `planning_off` / `self_correction_off` are **not an outstanding M3 assignment**. M1/M6 decide whether those additional Full-agent experiments belong in the final study and who would run them. The two profiles must remain distinct if both are eventually reported.

M5's complete frozen `exploration_off` package and M6's remaining check/hidden material were not found in this snapshot. Existing historical Random check results remain separate. M6 owns final report/deck assembly; this release provides current tables, curves and editable slide text, and does not claim a new PPTX export. All project edits remain under `M2/`, with previous live handoff files backed up. No receipt message was sent on the user's behalf.
