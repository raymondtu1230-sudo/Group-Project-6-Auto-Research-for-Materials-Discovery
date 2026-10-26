# Development results section for M6

We evaluated nine methods on six development systems with seeds 17, 29 and 43. Each unit contains one episode with a budget of 20 queries. The completed dataset has 162 accepted episodes. The unchanged M2 evaluator checks the required configuration fields, protocol, material references, query histories and endpoints. Full-reference selection follows M1's approved attempts and excludes all nonapproved records. The separate pre-freeze dry-run note is not used as a reference.

Each seed equally averages six systems. We report the mean and sample standard deviation across those three seed means. The Full study and generator baselines are:

| Method | mSUN@20 | AUDC |
| --- | ---: | ---: |
| Random | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Routing OFF | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |
| Memory OFF | 9.1111 ± 1.3472 | 86.9444 ± 9.0252 |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |

Full improves aggregate mSUN over both generator baselines. Relative to Routing OFF, it adds 2.2778 mSUN and 17.9722 AUDC. Memory's average contribution is smaller: 0.8889 mSUN and 1.1667 AUDC, with mixed individual pairs. Exploration adds 0.3333 mSUN while AUDC changes by −0.1111. Exploration OFF therefore has slightly higher aggregate AUDC; Full is not the highest-AUDC method across this table. These descriptive differences do not establish statistical significance or uniform improvement.

The M3 component study uses a separate setting with exploration and routing OFF throughout:

| Method | mSUN@20 | AUDC |
| --- | ---: | ---: |
| M3 full | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| M3 planning OFF | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| M3 self-correction OFF | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

Paired with M3 full, planning adds 1.3889 mSUN/13.5278 AUDC and self-correction adds 0.6667/4.4444. These do not identify the corresponding single-switch effects inside all-enabled Full. M3's assigned package is complete; any additional Full-agent planning/self-correction experiment is an M1/M6 scope decision.

The [complete leaderboard](../results/per_method_summary.csv) includes official AF/EF against both generator baselines. Full's mean AF/EF is 1.7345/9.2901 versus Random and 1.2537/2.4171 versus Chemeleon. Metrics are computed for each matched system/seed history before aggregation, not by dividing grand means. The official EF cap is 100 with the original zero-denominator convention; AF retains the official baseline-target/reachability rules. Neither is a measured wall-time speedup.

The [discovery curves](../results/discovery_curves_by_study.svg) retain separate study panels. Histories have explicit provenance: retained records, labelled trajectory reconstructions, or independently validated record-only reevaluations. M5's 305 incorrect supplementary normalized-AUDC values are corrected only in separate M2 analysis views; primary counts, raw AUDC and original files are unchanged. Its saved composed configuration retains interpolations and is not described as a fully resolved runtime dump. Earlier routing archive omissions remain disclosed.

The two selected cases support observed-behaviour descriptions rather than counterfactual claims. OFF Mg–Sn–Sr29 makes 16 binary queries before sampling ternaries. Full Ga–Pt–Tm17 contains one unsuccessful ternary query; its actual log has eight mixed and twelve exploit steps, not six ternary exploration probes.

[Cost analysis](COST_ANALYSIS.md) reports machine-labelled elapsed times and known fees. The 3,240 budgeted queries exclude uninstrumented initialization work, and USD 0 known model fees exclude total resource cost. Token counters remain unreported. All assigned development packages are now available. M6's remaining Full/Chemeleon check and course hidden comparisons, final assembly and submission are still separate; no held-out generalization claim follows from this development result.
