# Independent development closeout review

Pinned source snapshot: `b36e2a50d9d3e31fc941d827addab94db2c5d3cc`. This audit reads the actual saved experiment records. It does not run a model, agent, oracle or new scientific episode, and it edits only this M2 audit directory.

## Strict M5 metric acceptance

The unchanged actual `M2/evaluate.py::load_run` accepts all18 newly completed M5 packages and all18 approved frozen Full comparison units. Its official `DiscoveryCurveMetrics` dependency is the exact unchanged class AST executed with real NumPy2.3.5. No formulas or evaluator conditions were replaced.

All360 M5 query prefixes match the unchanged M1 `curve_from_trajectory` helper for query number, stable discoveries, mSUN and raw AUDC. All36 saved endpoints and18 canonical material-reference/protocol pairs agree. All126 previously published original M5 files in the earlier intake are byte-identical. No original run metadata or trajectory has been rewritten.

The Full selection is explicit: Mg–Sn–Sr seeds17 and29 use `attempt_02`; the other16 units use `attempt_01`. The failed/incomplete Mg `attempt_01` directories are preserved and excluded. Selection never means the latest or any other completed attempt. The M5 report mentions pre-freeze `attempt_05..08`; no such files occur in this downloaded pinned snapshot, and they are not among the approved18 paths.

The resulting primary statistics remain:

| Method | mSUN mean ± seed sample SD | AUDC mean ± seed sample SD |
|---|---:|---:|
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |

Each seed first averages the six systems; the three seed means determine the mean and sample SD. Paired Full minus OFF effects remain+0.3333mSUN and−0.1111AUDC. Histories are labelled actual saved-observation reconstructions; this audit does not claim recovered original runtime checkpoints or an independent physical hull/novelty recalculation.

## Supplementary normalized-field discrepancy

Although required mSUN, raw AUDC, AF and EF inputs are correct, the submitted histories contain305 supplementary normalized-AUDC values that differ from the official definition. The official prefix normalization is raw area divided by `queries_used**2/2`. For example, Ga–Pt–Tm43 at query20 has raw AUDC126.5, so the official normalized value is0.6325; the submitted value is0.48653846.

This supplementary field is neither a required shared metric nor read by the unchanged strict M2 evaluator. Therefore it does not invalidate the accepted required metrics. It must remain explicitly disclosed and must not be reused as an official normalized value. The initial comparison containing every discrepancy is retained in `initial_all_history_fields_comparison.json`; the final audit separately exposes primary acceptance and `all_submitted_history_fields_match_official=false`. Source histories are not edited. Any correction in a new M2 analysis view must preserve the submitted history, list each of the305 differences, and retain all core fields unchanged.

Ga–Pt–Tm43 raw AUDC126.5 includes the official origin(0,0). Omitting that origin gives126.0 by losing the first0.5 triangle. This audit and the exact helper retain the official origin without arbitrary endpoint corrections.

## Saved composed configurations

All18 `resolved_config.yaml` files are byte-identical to each attempt's original saved `hydra/config.yaml`. Concrete dataset, experiment seed, budget20, episode1, CPU ORB v3 conservative and all five switches agree with actual metadata; exploration alone is disabled. This verifies correspondence to the actual saved composed configuration, rather than constructing an alleged original config from command arguments.

Each saved configuration retains17 interpolated values:10 static references/selectors and7 runtime resolver values. These include module seed references, the agent budget reference, the generator device selector and runtime log/environment references. Thus “all values fully resolved” and “only runtime references remain” would overstate the delivered YAML. The strict evaluator's required concrete settings are verified. The audit retains every unresolved path and original string explicitly.

## Updated M5 narrative

The revised M5 results table corrects the previous means, system effects, per-system sample SD convention and same-seed values. The two observed case counts are now accurate, and the original Full decision log is correctly acknowledged.

One remaining factual sentence needs qualification: Full Ga–Pt–Tm17 has8 `mixed` records at queries1–8 and12 `exploit` records at queries9–20. It is false that every step except the ternary query is `exploit`. Executed compositions match the UCB outgoing pool at queries1,2,3,4,6; the remaining15 executed compositions match the planner. The only ternary remains query6; other UCB selections can be binary. See `updated_failure_cases.json` for the actual record-to-trajectory join.

The phrase “trades a small amount of mean performance” is also imprecise: mean mSUN rises0.3333, while mean AUDC falls0.1111. Pooled population dispersion decreases, but this descriptive spread across heterogeneous systems does not establish a causal stabilisation mechanism. “Wasteful exploration” and “over-exploitation” should be treated as discussion hypotheses tied to the observed selections, not proven counterfactual outcomes. These narrative qualifications do not change the accepted data.

## Final162-run aggregation review

The completed `M2/aggregation/20261027_dev_closeout/results` passed a separate independent audit against actual strict-loaded evaluation views:

- 162 unique accepted units,9 methods×18, with all144 prior original metadata/trajectory/configuration hashes unchanged and all18 M5 original endpoints unchanged.
- 324 baseline comparison pairs, comprising648 directional AF/EF scalar checks;144 seed-first method mean/sample-SD scalar checks;54 Full ablation pairs;36 M3 component pairs and their aggregate effects.
- 360 M5 analysis-view normalized prefixes verified against both the exact official function and unchanged M1 helper; all305 discrepancy receipts verified. Each of18 original histories and its as-submitted copy remains byte-identical to the initial strict audit. The18 published as-submitted/corrected history copy pairs match their corresponding originals and separate evaluation views. Removing only the supplementary normalized field leaves each source/view history document identical.
- 189 aggregate-curve points checked for mean and sample SD,162 cost/machine records checked, and64 output-manifest files verified by size/SHA256. Evaluator/class/script provenance hashes match actual files.

The PNG figure was also visually inspected. It clearly separates Full-system ablations from the M3 component study, shows exploration OFF as an accepted method, and labels the stable-discovery curve used by official AUDC. No pending-package label remains on the accepted M5 series.

There were zero arithmetic, preservation, pairing or receipt errors. The remaining qualifications are the original supplementary-field discrepancy, retained configuration interpolations and the M5 prose-mode sentence described above. No new science was performed to close this development-data intake.

## Reproduction

Run `M2/stage_aggregation_20261026/venv/bin/python M2/stage_dev_closeout_20261027/audit_metrics/verify_m5_complete.py` from the project root to reproduce the strict metric/configuration audit. Run the same interpreter with `M2/stage_dev_closeout_20261027/audit_metrics/verify_162_aggregation.py` to reproduce the independent162-run aggregate audit. Both scripts write only JSON audits in this directory. The source/manifests audit belongs to the independent source-audit task.
