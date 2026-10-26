# Updated shared result slides for M6

Editable assembly text and speaker notes. This release does not export or visually validate a new PPTX. M3/M4 native decks remain in their own report folders.

## Slide 1 — Frozen Full, baselines and single-switch ablations

6 dev systems × 3 seeds; CPU ORB v3 conservative; B=20. Mean ± sample SD across three seed means, with equal system weights within each seed.

| Method | mSUN@20 | AUDC |
| --- | ---: | ---: |
| Random | 4.06 ± 0.63 | 40.58 ± 9.46 |
| Chemeleon | 6.94 ± 1.11 | 71.31 ± 9.50 |
| Full | 10.00 ± 0.88 | 88.11 ± 9.45 |
| Routing OFF | 7.72 ± 1.18 | 70.14 ± 1.61 |
| Memory OFF | 9.11 ± 1.35 | 86.94 ± 9.03 |

Full leads these aggregate dev results. Memory effects are mixed across individual pairs. Do not imply statistical significance, uniform benefit or hidden-set generalization.

Figure: left panel of `results/discovery_curves_by_study.svg`.

Speaker text: We evaluate the same six development systems and three seeds under a twenty-query budget. The Full reference averages ten novel stable discoveries. Routing OFF gives 7.72 and Memory OFF gives 9.11. The aggregate memory difference is positive but small, with mixed individual results. These are descriptive development results, so we do not infer statistical significance or hidden-set performance.

## Slide 2 — Complete M3 component study

Exploration and routing remain OFF throughout this study. The correct comparator is `m3_full`.

| Method | mSUN@20 | AUDC | Units |
| --- | ---: | ---: | ---: |
| M3 full | 6.50 ± 1.30 | 62.75 ± 9.03 | 18 |
| Planning OFF | 5.11 ± 0.35 | 49.22 ± 4.51 | 18 |
| Self-correction OFF | 5.83 ± 0.88 | 58.31 ± 7.78 | 18 |

Within this component setting, comparator minus OFF gives **+1.39 mSUN / +13.53 AUDC for planning**, and **+0.67 mSUN / +4.44 AUDC for self-correction**. All 54 original result folders are received and validated. Histories retain their trajectory-reconstruction provenance.

Figure: right panel of `results/discovery_curves_by_study.svg`, now including the actual supplied M3-full curve.

Speaker text: M3's component study keeps exploration and routing off. We therefore pair both OFF arms with M3 full. The complete fifty-four-run package has now been independently validated. Planning adds 1.39 novel stable discoveries on average, while self-correction adds 0.67 in this setting. These comparisons are separate from the all-enabled Full agent. Any additional Full-agent planning or self-correction ablations are a scope decision for M1 and M6.
