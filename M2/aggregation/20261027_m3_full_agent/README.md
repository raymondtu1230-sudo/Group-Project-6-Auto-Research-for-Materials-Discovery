# M2: 198-run development closeout with all five Full ablations

27 October 2026, Asia/Hong_Kong. M3's new `planning_off` and `self_correction_off` delivery at commit `62ed42b0b546f19d20178484e48b03df3a112508` is accepted for required core metrics. The unchanged M2 evaluator validates **198 real dev runs, 11 methods × 18 units, with issues=[]**. This adds 36 results to the retained [162-run release](../20261027_dev_closeout/README.md); it launches no scientific episodes.

The required Full-agent ablation table now contains planning, memory, self-correction, exploration and routing OFF against the hash-pinned `m1_full` reference. The earlier `m3_*` component study remains separate against `m3_full`.

- [M6 handoff and final tables](M6_HANDOFF.md)
- [Results prose](report/RESULTS_SECTION.md), [four-slide content](report/M2_FOUR_SLIDE_CONTENT.md), [speaker notes](report/M2_SPEAKER_NOTES.md), [rehearsal Q&A](report/REHEARSAL_QA.md)
- [All method metrics and AF/EF](results/per_method_summary.csv), [198 individual scores](results/per_run_with_baseline_comparisons.csv), [90 Full pairs](results/paired_full_system_ablations.csv), [36 separate M3 component pairs](results/paired_m3_component_ablations.csv)
- [Five ablation effect summaries](results/full_ablation_effect_summary.csv), [discovery curves](results/discovery_curves_by_study.svg), [editable curve data](results/aggregate_discovery_curve_data.csv), [cost analysis](report/COST_ANALYSIS.md)
- [New M3 acceptance](results/new_m3_acceptance.json), [source and configuration audit](SOURCE_AUDIT.md), [independent checks and continuity](verification.json), [reproduction](REPRODUCTION.md)
- [Checksum receipt follow-up text](M3_CHECKSUM_FOLLOWUP.md), [remaining group work](NEXT_STEPS.md)

There are 396 matched baseline comparisons, 90 Full ablation pairs and 36 M3 component pairs. Systems are equally averaged within each seed; reported means and sample SDs are across seed means 17/29/43. SD is not a confidence interval. AF/EF use the official matched-history zero/cap rules and are not runtime speedups.

## Main Full study

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

Planning OFF averages 5.2778 mSUN and 51.5278 AUDC against Full 10.0000 and 88.1111. Full is better/equal/worse in 15/2/1 mSUN pairs. The two-sided exact sign test, excluding ties, gives p=0.000518798828125 (0.001 to three decimals). Self-correction OFF averages 9.5000 mSUN and 79.5833 AUDC, with 8/2/8 mSUN pairs and p=1.0. The latter does not establish a consistent directional mSUN improvement; it does not prove equivalence or that self-correction has no effect.

The five Full ablation comparisons are now complete. Sign-test values are exploratory and unadjusted for multiple comparisons; their usual interpretation assumes independent non-tied pairs. The six systems and three repeated seeds limit generalization. Full has the highest aggregate mSUN in this Full/baseline table; Exploration OFF has slightly higher raw AUDC (88.2222 versus 88.1111). Do not claim a universal module benefit or held-out performance.

## Evidence boundaries

M3's new histories are labelled reconstructions from the original trajectories, rather than original checkpoint captures. All 720 new discovery-count prefixes agree with the recorded stable/new-discovery flags; raw AUDC was independently summed with a zero-origin trapezoid and matched the official calculation at every prefix. This is a consistency check of recorded evidence, not a new hull, novelty or oracle evaluation.

M3 declares Chemeleon archive SHA-256 `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`. No run-machine archive-checksum receipt was found in the delivered 36-run artifacts. Accept the core metrics and the documented single-switch configuration comparison; retain model-archive identity as declared rather than independently established. Recovering an existing checksum receipt is a documentation follow-up, not a request to rerun.

Retain earlier qualifications: M5's 305 auxiliary normalized-AUDC discrepancies are corrected only in M2 analysis copies; M5's saved composed configurations retain interpolations; routing histories use labelled record-only reevaluation, and some original routing attachments are missing. Original member evidence and the prior 162-run release remain unchanged. Costs are partial and machines differ.

This completes M2's received development-results validation and assembly handoff. M6's missing Full/Chemeleon check and hidden packages, final group report/deck assembly, rehearsal and course submission remain separate. Editable slide sources are provided; no new native PPTX export or message to teammates is claimed.
