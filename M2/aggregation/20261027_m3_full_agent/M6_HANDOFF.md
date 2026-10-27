# M6 handoff: complete frozen-agent ablation table

27 October 2026. Source snapshot `09c9b74300b26176ce5ade37d5192ba98caa240f`; new M3 delivery `62ed42b`. **198 dev runs accepted; unchanged evaluator issues=[]**. The prior 162 results are numerically unchanged. Use this release in place of the older 162-run development handoff.

## Frozen Full, both baselines and all five single-switch ablations

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

| OFF arm | Full − OFF mSUN | Full − OFF AUDC | Full better / equal / worse (mSUN) | Exact sign p |
| --- | ---: | ---: | --- | ---: |
| Planning OFF | +4.7222 | +36.5833 | 15 / 2 / 1 | 0.000518799 |
| Memory OFF | +0.8889 | +1.1667 | 8 / 3 / 7 | 1.000000000 |
| Self-correction OFF | +0.5000 | +8.5278 | 8 / 2 / 8 | 1.000000000 |
| Exploration OFF | +0.3333 | -0.1111 | 8 / 1 / 9 | 1.000000000 |
| Routing OFF | +2.2778 | +17.9722 | 12 / 1 / 5 | 0.143463135 |

Planning OFF averages 5.2778 mSUN and 51.5278 AUDC against Full 10.0000 and 88.1111. Full is better/equal/worse in 15/2/1 mSUN pairs. The two-sided exact sign test, excluding ties, gives p=0.000518798828125 (0.001 to three decimals). Self-correction OFF averages 9.5000 mSUN and 79.5833 AUDC, with 8/2/8 mSUN pairs and p=1.0. The latter does not establish a consistent directional mSUN improvement; it does not prove equivalence or that self-correction has no effect.

The five Full ablation comparisons are now complete. Sign-test values are exploratory and unadjusted for multiple comparisons; their usual interpretation assumes independent non-tied pairs. The six systems and three repeated seeds limit generalization. Full has the highest aggregate mSUN in this Full/baseline table; Exploration OFF has slightly higher raw AUDC (88.2222 versus 88.1111). Do not claim a universal module benefit or held-out performance.

## Separate M3 component study

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| M3 full | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| M3 planning OFF | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| M3 self-correction OFF | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

All three profiles keep exploration and routing OFF. Compare component OFF arms only with `m3_full`: planning adds +1.3889 mSUN/+13.5278 AUDC and self-correction +0.6667/+4.4444 in that setting. The new all-enabled Full ablations above are separate runs and do not replace or relabel this study. Its 36-pair table is byte-identical to the previous release.

## Material ready for assembly

Copy the [results section](report/RESULTS_SECTION.md), [four-slide sources](report/M2_FOUR_SLIDE_CONTENT.md), [short speaking script](report/M2_SPEAKER_NOTES.md) and [Q&A](report/REHEARSAL_QA.md). Use the [two-panel discovery figure](results/discovery_curves_by_study.svg) with [editable values](results/aggregate_discovery_curve_data.csv), [official AF/EF table](results/per_method_summary.csv) and [cost discussion](report/COST_ANALYSIS.md).

M3's new histories are labelled reconstructions from the original trajectories, rather than original checkpoint captures. All 720 new discovery-count prefixes agree with the recorded stable/new-discovery flags; raw AUDC was independently summed with a zero-origin trapezoid and matched the official calculation at every prefix. This is a consistency check of recorded evidence, not a new hull, novelty or oracle evaluation.

M3 declares Chemeleon archive SHA-256 `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`. No run-machine archive-checksum receipt was found in the delivered 36-run artifacts. Accept the core metrics and the documented single-switch configuration comparison; retain model-archive identity as declared rather than independently established. Recovering an existing checksum receipt is a documentation follow-up, not a request to rerun.

Retain earlier qualifications: M5's 305 auxiliary normalized-AUDC discrepancies are corrected only in M2 analysis copies; M5's saved composed configurations retain interpolations; routing histories use labelled record-only reevaluation, and some original routing attachments are missing. Original member evidence and the prior 162-run release remain unchanged. Costs are partial and machines differ.

All assigned Full development ablations are present; the previous statement that Full planning/self-correction remained an optional M1/M6 scope decision is superseded by M3's actual delivery. M6 still owns remaining held-out/check evidence and final group assembly. Publication of files is not evidence that a teammate has received or approved them. No teammate message or course submission has been sent.
