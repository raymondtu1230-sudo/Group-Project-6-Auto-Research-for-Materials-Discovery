# M2 final development slide contribution

27 October 2026. Four editable slide sources for M6 assembly. This file and its linked figures are current material; no new native PPTX export is claimed. The spoken text is in [M2_SPEAKER_NOTES.md](M2_SPEAKER_NOTES.md).

## Slide 1 — Choosing tools from observed feedback

**Main point:** route between the configured Random and Chemeleon generators while keeping the scientific workflow fixed.

- Try each tool, then use observed reward with an upper-confidence bonus.
- Use the current reward greedily for the last two queries.
- Read public query feedback and remaining budget. The reward is a policy proxy, separate from official mSUN.
- Controlled routing ablation: only `enable_tool_routing=false`; the primary generator remains Random in the integrated agent.

**Protocol strip:** six dev systems; seeds 17/29/43; B=20; one episode per unit; CPU ORB v3 conservative. The runner, oracle, evaluator and scientific configuration stay fixed.

**Visual:** a compact sequence: observed feedback → tool choice → existing proposal/filter/scoring workflow → one queried structure → next feedback. M1's architecture slide owns the complete system diagram.

## Slide 2 — Full study and required baselines

Each method has 18 units. Mean ± sample SD across three seed means; each seed equally averages six systems.

| Method | mSUN@20 | AUDC |
| --- | ---: | ---: |
| Random | 4.06 ± 0.63 | 40.58 ± 9.46 |
| Chemeleon | 6.94 ± 1.11 | 71.31 ± 9.50 |
| Full | 10.00 ± 0.88 | 88.11 ± 9.45 |
| Routing OFF | 7.72 ± 1.18 | 70.14 ± 1.61 |
| Memory OFF | 9.11 ± 1.35 | 86.94 ± 9.03 |
| Exploration OFF | 9.67 ± 1.15 | 88.22 ± 11.54 |

**Takeaway:** Full has higher aggregate mSUN than both generator baselines. Full minus Routing OFF is +2.28 mSUN and +17.97 AUDC. Memory and exploration effects vary across pairs; exploration's aggregate AUDC difference is close to zero.

**Metric note:** Full AF/EF versus Random are 1.73/9.29; versus Chemeleon, 1.25/2.42. These are averages of matched official discovery metrics, with the original zero/cap rules. They are not wall-time speedups or ratios of the table means.

**Visual:** the left panel of [discovery_curves_by_study.svg](../results/discovery_curves_by_study.svg). Shading is seed-mean sample SD, not a confidence interval. Editable values: [per_method_summary.csv](../results/per_method_summary.csv) and [aggregate_discovery_curve_data.csv](../results/aggregate_discovery_curve_data.csv).

## Slide 3 — M3's separate component study

Exploration and routing remain OFF throughout this study. The comparator is `m3_full`.

| M3 profile | mSUN@20 | AUDC |
| --- | ---: | ---: |
| M3 full | 6.50 ± 1.30 | 62.75 ± 9.03 |
| Planning OFF | 5.11 ± 0.35 | 49.22 ± 4.51 |
| Self-correction OFF | 5.83 ± 0.88 | 58.31 ± 7.78 |

**Within this setting:** planning adds +1.39 mSUN/+13.53 AUDC; self-correction adds +0.67/+4.44. Do not relabel these as single-switch effects inside all-enabled Full. M3's assigned 54-run package is complete; any additional Full planning/self-correction runs are an M1/M6 decision.

**Visual:** the right panel of the shared discovery-curve figure. All three curves come from the supplied, labelled reconstructed histories. Source: [paired_m3_component_ablations.csv](../results/paired_m3_component_ablations.csv).

## Slide 4 — Cost, evidence and lessons

**Cost examples, mean launcher minutes per accepted episode:** Random 15.99 and Chemeleon 234.31 on the recorded Linux GitHub runners; Full 5.22 on the macOS ARM reference machine. This is descriptive accounting across different machines, not a controlled runtime comparison. Complete method/machine labels are in [COST_ANALYSIS.md](COST_ANALYSIS.md) and [method_cost_summary.csv](method_cost_summary.csv).

- 162 accepted dev episodes contain 3,240 budgeted queries. Initialization and other uninstrumented work remain outside that count.
- Recorded known model fees are USD 0; hardware, electricity, unpriced attempts and unreported counters remain unmeasured.
- Preserve original attempts; distinguish retained checkpoints, trajectory reconstructions and separate analysis views.
- Inspect matched configurations and trajectories before explaining a score difference.
- All assigned dev packages are available. Held-out generalization, final group assembly and presentation rehearsal remain later work.

**Written-report caveats:** M5's saved composed configuration retains interpolations; its 305 incorrect supplementary normalized-AUDC values are corrected only in M2 analysis views, with originals preserved. Primary mSUN/raw AUDC and official paired AF/EF are unchanged. Historical M2 routing archive omissions remain disclosed. Avoid a significance or hidden-performance claim.
