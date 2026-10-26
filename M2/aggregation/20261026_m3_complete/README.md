# Shared aggregation — complete M3 comparator received

26 October 2026. Data snapshot: `dcd3481a44f5bd9e0f9d7e58778a7f59a5a81210`.

The unchanged M2 evaluator accepts **144 real completed dev episodes across eight methods, with no issues**. M3's three methods now have all 54 original result folders and pass independent pairing checks. The previous missing-`m3_full` request is closed.

M3's assigned component handoff is complete. Any additional Full-agent `planning_off` / `self_correction_off` experiments are a scope and ownership decision for **M1/M6**, not an unfinished M3 assignment. This corrects the earlier M2 intake wording. The M3 study remains separate because exploration and routing are OFF in all three profiles.

## Current assembly material

- [M6 handoff and result tables](M6_HANDOFF.md)
- [Receipt and remaining group work](RECEIPT_AND_OPEN_ITEMS.md)
- [Editable slide text and speaker notes](GROUP_RESULTS_SLIDE_CONTENT.md)
- [Eight-method scores and baseline AF/EF](results/per_method_summary.csv)
- [144 per-run scores and baseline comparisons](results/per_run_with_baseline_comparisons.csv)
- [36 matched M3 component comparisons](results/paired_m3_component_ablations.csv)
- [36 Full-agent memory/routing comparisons](results/paired_full_system_ablations.csv)
- [Discovery curves by study](results/discovery_curves_by_study.svg), now including the supplied M3-full curve
- [Numeric discovery curves](results/aggregate_discovery_curve_data.csv) and [per-run costs](results/per_run_costs.csv)
- [Aggregation validation](results/aggregation_validation.json), [M3-only validation](results/m3_only_validation.json), [source/loading provenance](results/evaluation_provenance.json) and [input receipts](results/input_receipts.json)
- [Reproduction instructions](REPRODUCTION.md) and [reproduction checks](reproduction_validation.json)
- [Independent source/configuration audit](audits/source/README.md) and [trajectory/metric audit](audits/metrics/m3_metrics_independent_audit.json)

M3 full averages **6.5000 mSUN@20 / 62.7500 AUDC**. Paired comparator-minus-OFF gains are **+1.3889 / +13.5278** for planning and **+0.6667 / +4.4444** for self-correction. Planning wins/ties/loses 12/1/5 mSUN pairs; self-correction 7/10/1. Effects vary across pairs; these are descriptive dev results, without a significance or held-out generalization claim.

The previously accepted seven methods retain their numerical aggregates, and the earlier Full memory/routing pair table is byte-identical. All means equally weight six systems within each seed, then report mean and sample SD across three seed means. There are 288 baseline comparisons: each of 144 results against Random and Chemeleon, including baseline self-comparisons. Official AF/EF are recomputed from paired histories, with the actual cap-100 EF and zero conventions; the original unpaired zero fields in M3 summaries are not treated as paired scores.

## Evidence and preservation boundaries

New `m3_full` records retain actual source `ae7fe81991c56dd2d77685220b74ddbef11039c7`; the OFF arms retain `02e0026bf450f71f4f7862228d295f5b02b49e12`. All 54×74 recorded source fingerprints are compatible, and 108 examined source/configuration/protocol/dependency/data files establish scientific equivalence across the evidence-only revision. Windows text fingerprints and manifests use explicit deterministic newline normalization; this is not a claim that every Git-normalized text file preserves the original Windows byte stream. All 36 M3 resolved-configuration pairs differ only in the intended treatment switch and run-specific paths.

All 1,080 M3 history prefixes agree with the unchanged M1 trajectory-history function, and all 54 endpoints/AUDCs agree. These histories are explicitly reconstructed from trajectories, not original checkpoint captures. The prefix check verifies recorded-flag/history consistency, not a new independent hull/novelty reevaluation. The separately labelled M2 routing and M1 history checks retain their earlier provenance; no original incomplete history or failure audit is deleted.

The analysis uses the unchanged evaluator and unchanged official metric-class source, with real frozen-version NumPy and a documented lightweight import. No agent, model, oracle, Materials Project request, or simulated scientific episode is invoked. Unknown costs remain unknown, with original machine labels preserved. All writes and backed-up handoff changes are under `M2/`; other members' files remain untouched.

The [previous 126-run report](../20261026/README.md) remains a dated intake record. Current group completion is still open for M5's exploration handoff, M6's remaining check/hidden assembly, and any additional Full-agent scope decision. This is separate from accepting M3's completed assignment. No external receipt message or new PPTX export is claimed.
