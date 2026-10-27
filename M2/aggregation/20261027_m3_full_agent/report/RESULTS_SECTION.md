# Development results

We evaluated 198 completed episodes across eleven methods on six development systems, seeds 17/29/43, and budget B=20. The unchanged shared evaluator reported no core validation issues. Each seed equally weights all six systems; table uncertainty is sample SD across the three seed means.

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| Random | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Planning OFF | 5.2778 ± 0.5358 | 51.5278 ± 9.2407 |
| Memory OFF | 9.1111 ± 1.3472 | 86.9444 ± 9.0252 |
| Self-correction OFF | 9.5000 ± 1.1667 | 79.5833 ± 6.2489 |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |
| Routing OFF | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |

The all-enabled frozen agent reaches 10.0000 mSUN@20, compared with Random 4.0556 and Chemeleon 6.9444. Its official matched AF/EF averages are 1.73/9.29 versus Random and 1.25/2.42 versus Chemeleon. These discovery metrics are not wall-clock speedups or ratios of aggregate scores.

Planning OFF averages 5.2778 mSUN and 51.5278 AUDC against Full 10.0000 and 88.1111. Full is better/equal/worse in 15/2/1 mSUN pairs. The two-sided exact sign test, excluding ties, gives p=0.000518798828125 (0.001 to three decimals). Self-correction OFF averages 9.5000 mSUN and 79.5833 AUDC, with 8/2/8 mSUN pairs and p=1.0. The latter does not establish a consistent directional mSUN improvement; it does not prove equivalence or that self-correction has no effect.

The five Full ablation comparisons are now complete. Sign-test values are exploratory and unadjusted for multiple comparisons; their usual interpretation assumes independent non-tied pairs. The six systems and three repeated seeds limit generalization. Full has the highest aggregate mSUN in this Full/baseline table; Exploration OFF has slightly higher raw AUDC (88.2222 versus 88.1111). Do not claim a universal module benefit or held-out performance.

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| M3 full | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| M3 planning OFF | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| M3 self-correction OFF | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

The M3 component study keeps exploration and routing disabled in all profiles; its comparator is `m3_full`. Planning adds +1.3889 mSUN/+13.5278 AUDC and self-correction +0.6667/+4.4444 within this setting. These component effects must not be substituted for the Full-agent single-switch effects.

The [discovery curves](../results/discovery_curves_by_study.svg) separate the two studies; shading shows sample SD across seed means. The [complete table](../results/per_method_summary.csv) retains both official baseline comparisons. The [cost report](COST_ANALYSIS.md) documents machine differences, recorded time and missing resource costs.

M3's new histories are labelled reconstructions from the original trajectories, rather than original checkpoint captures. All 720 new discovery-count prefixes agree with the recorded stable/new-discovery flags; raw AUDC was independently summed with a zero-origin trapezoid and matched the official calculation at every prefix. This is a consistency check of recorded evidence, not a new hull, novelty or oracle evaluation.

M3 declares Chemeleon archive SHA-256 `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`. No run-machine archive-checksum receipt was found in the delivered 36-run artifacts. Accept the core metrics and the documented single-switch configuration comparison; retain model-archive identity as declared rather than independently established. Recovering an existing checksum receipt is a documentation follow-up, not a request to rerun.

Retain earlier qualifications: M5's 305 auxiliary normalized-AUDC discrepancies are corrected only in M2 analysis copies; M5's saved composed configurations retain interpolations; routing histories use labelled record-only reevaluation, and some original routing attachments are missing. Original member evidence and the prior 162-run release remain unchanged. Costs are partial and machines differ.

The evidence supports development-set comparisons only. Current Full/Chemeleon check results and a hidden package were not available in this source snapshot; held-out generalization and final group delivery remain pending.
