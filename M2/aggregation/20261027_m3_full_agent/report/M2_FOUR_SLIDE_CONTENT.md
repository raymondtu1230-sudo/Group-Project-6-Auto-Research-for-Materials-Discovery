# M2 current four-slide contribution

27 October 2026. Editable slide text, tables and figures for M6 assembly; no native PPTX export is claimed. [Speaking script](M2_SPEAKER_NOTES.md).

## Slide 1 — Tools chosen from observed feedback

- Route between configured Random and Chemeleon generators using observed reward plus an upper-confidence bonus.
- Use the existing proposal/filter/scoring workflow; only public query feedback and remaining budget enter routing.
- Six dev systems, seeds 17/29/43, B=20; official ORB CPU protocol.
- 198 accepted episodes, eleven methods; M2's original 54 experiments were reused.

## Slide 2 — Complete frozen Full ablation table

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

Full−Planning OFF is +4.72 mSUN/+36.58 AUDC; Full better/equal/worse 15/2/1. Full−Routing OFF is +2.28/+17.97. Self-correction mSUN pairs are 8/2/8; do not claim equivalence. Exploration OFF has slightly higher raw AUDC than Full. SD is across three seed means, not a confidence interval.

Visual: left panel of [discovery curves](../results/discovery_curves_by_study.svg); [editable values](../results/aggregate_discovery_curve_data.csv). Exact sign p for planning is 0.0005188 (unadjusted, exploratory).

## Slide 3 — Keep M3's component study separate

| Method | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: |
| M3 full | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| M3 planning OFF | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| M3 self-correction OFF | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

Exploration and routing remain OFF in these three profiles. Comparator is m3_full: planning +1.39 mSUN/+13.53 AUDC; self-correction +0.67/+4.44. These are separate from M3's new all-enabled Full ablations. Visual: right panel of the shared figure.

## Slide 4 — Evidence, cost and remaining work

- 198 episodes × 20 budgeted queries = 3,960 recorded successful-episode budget queries; initialization and failed-attempt costs are outside this count.
- Different machines and partial costs prevent a controlled runtime ranking. [Cost table](method_cost_summary.csv).
- M3 declares the shared model archive; its run-machine checksum receipt remains unverified. No rerun is requested.
- Preserve trajectory-reconstruction labels, M5 auxiliary corrections and known routing evidence gaps.
- M2 dev aggregation is ready for M6. Held-out/check evidence, final group assembly and rehearsal remain later work.
