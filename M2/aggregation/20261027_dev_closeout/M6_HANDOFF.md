# M6 assembly handoff — complete assigned dev packages

27 October 2026. Source snapshot `b36e2a50d9d3e31fc941d827addab94db2c5d3cc`. M5 has supplied the requested evidence, so the former package-pending label is closed for the required core metrics. The shared evaluator accepts 162 records, nine methods × 18 dev units, with no core validation issues.

## Full study and baselines

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| Random | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Memory OFF | 9.1111 ± 1.3472 | 86.9444 ± 9.0252 |
| Routing OFF | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |

These are equally weighted system means within each seed, then mean and sample SD across three seed means. They are not pooled-run SDs or confidence intervals.

Full minus exploration OFF is +0.3333 mSUN and −0.1111 AUDC. Full has better/equal/worse mSUN in 8/1/9 pairs and better/worse AUDC in 9/9. Pooled population mSUN SD across the 18 outcomes is OFF 4.8305 versus Full 2.7285; label it separately if used. Exploration's overall effect is small and heterogeneous. Do not describe Full as having the highest raw AUDC: exploration OFF is slightly higher here.

## M3 component study

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| `m3_full` | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| `m3_planning_off` | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| `m3_self_correction_off` | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

Exploration and routing remain OFF throughout this component study. Comparator-minus-OFF gains are +1.3889 mSUN / +13.5278 AUDC for planning, and +0.6667 / +4.4444 for self-correction. These are valid paired component effects in this setting, not all-enabled Full-agent effects. M3's assigned handoff is complete. Extra Full-agent planning/self-correction is an M1/M6 scope decision.

## Ready assembly files

- [Results prose](report/RESULTS_SECTION.md), [four-slide content](report/M2_FOUR_SLIDE_CONTENT.md), [speaker notes](report/M2_SPEAKER_NOTES.md) and [Q&A](report/REHEARSAL_QA.md).
- [Discovery curves](results/discovery_curves_by_study.svg), [chart data](results/aggregate_discovery_curve_data.csv), [all scores and baseline AF/EF](results/per_method_summary.csv).
- [Cost discussion](report/COST_ANALYSIS.md), [method-level cost table](report/method_cost_summary.csv) and [per-run records](results/per_run_costs.csv).

The figure has separate Full and M3 panels. M5's curve is now accepted for core metrics and no longer carries a package-pending marker. All 324 baseline comparisons, 54 Full ablation pairs and 36 M3 pairs use the shared official definitions. Always retain AF/EF direction and zero/cap conventions.

The four-slide contribution is current editable text/tables/chart data. A new native PPTX was not exported in this session. M6 assembles it into the final deck; the old M2 baseline-only PPTX is historical.

## Corrections and limitations to retain

- M5's raw mSUN/AUDC and other required core fields agree. Its auxiliary normalized-AUDC field had 305 wrong prefix values. M2 corrects only analysis copies with official `area / (queries²/2)` normalization and retains both versions. Do not copy the uncorrected auxiliary values.
- M5's saved composed configs retain ordinary and runtime interpolations. They are actual saved evidence, not a claim of fully evaluated YAML.
- OFF Mg–Sn–Sr seed29 first16 queries are binaries with six stable hits. Queries19/20 are stable ternaries. This is delayed coverage, not proof of an unobserved counterfactual.
- Full Ga–Pt–Tm seed17 has one ternary query6, in mixed mode; the complete log has 8 mixed and 12 exploit steps. The same-seed OFF/ON mSUN is16/10 and AUDC168/93. The remaining “all other steps exploit” sentence in M5 prose is inaccurate; use [actual case evidence](audits/metrics/updated_failure_cases.md).
- Retain reconstruction/reevaluation provenance, archived failures, known missing original routing attachments, machine/dependency differences and partial cost accounting. The results do not establish statistical significance, universal module benefit or held-out generalization.

All assigned dev packages are now received and evaluated. Final group completion still depends on M6's remaining check/hidden material, final report/deck assembly and the team review/submission steps. The repository currently contains only the historical 12-run Random check package; it does not provide current Full/Chemeleon check results or a hidden package. No messages or submissions have been sent on the user's behalf.
