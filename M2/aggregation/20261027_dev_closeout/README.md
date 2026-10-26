# M2 development-results closeout — 27 October 2026

The complete M5 supplement closes the previous missing-package blocker. The unchanged M2 evaluator accepts **162 development records across nine methods, with no core-metric validation issues**. All currently assigned development packages are received and evaluated. M2 has completed the shared development tables, discovery curves, paired comparisons, cost accounting and assembly material supported by these inputs.

This is a development-results closeout. Held-out evidence and final group assembly remain separate.

## Handoff to M6

- [Results and interpretation](M6_HANDOFF.md)
- [Ready results section](report/RESULTS_SECTION.md)
- [Four-slide editable content](report/M2_FOUR_SLIDE_CONTENT.md), [English speaker notes](report/M2_SPEAKER_NOTES.md) and [rehearsal Q&A](report/REHEARSAL_QA.md)
- [Cost analysis](report/COST_ANALYSIS.md) and [machine-labelled method cost summary](report/method_cost_summary.csv)
- [What is complete and what follows](NEXT_STEPS.md)
- [Project-requirements audit](project_requirements/M2_SCOPE_AUDIT.md)

The four-page contribution is editable source text, tables and chart data for M6's final deck. This release does not claim that a new native PPTX was exported. The old 21 October baseline-only PPTX remains historical.

## Final development data

- [Nine-method metrics, including paired AF/EF](results/per_method_summary.csv)
- [162 per-run scores](results/per_run_with_baseline_comparisons.csv) and [54 per-system method summaries](results/per_system_summary.csv)
- [54 Full-agent ablation pairs](results/paired_full_system_ablations.csv): memory, routing and exploration OFF versus frozen Full
- [36 M3 component pairs](results/paired_m3_component_ablations.csv): planning and self-correction OFF versus `m3_full`
- [Discovery curves by study](results/discovery_curves_by_study.svg) and [editable numeric data](results/aggregate_discovery_curve_data.csv)
- [162 original cost records](results/per_run_costs.csv)
- [Acceptance](results/aggregation_validation.json), [canonical evaluator report](results/m2_evaluator/validation.json), [input receipts](results/input_receipts.json) and [source provenance](results/evaluation_provenance.json)
- [Reproduction](REPRODUCTION.md), [execution checks](reproduction_validation.json), [source audit](audits/source/M5_SUPPLEMENT_AUDIT.md) and [independent metric audit](audits/metrics/INDEPENDENT_REVIEW.md)

Means equally weight the six systems within each seed, then average seeds 17/29/43. Reported SDs are sample SDs across those three seed means. AF/EF are computed on matched system/seed histories before aggregation, using the official zero conventions and actual EF cap of 100. They are discovery measures, not runtime speed ratios.

M3's three profiles keep exploration and routing OFF. Their valid causal comparator is `m3_full`; their component effects are separate from the all-enabled Full study. The received Full-agent ablations cover memory, routing and exploration. Additional Full-agent planning/self-correction experiments are optional study-scope decisions for M1/M6 and do not block acceptance of the assigned dev packages.

## M5 acceptance and auxiliary-field correction

All 18 submitted M5 attempts now pass the unchanged evaluator for the required mSUN, discovery-count, raw AUDC and paired-metric inputs. Their saved Hydra configurations, component evidence and manifests are present, and the prior 18 trajectory/metadata endpoints are unchanged. Exploration OFF averages **9.6667 mSUN / 88.2222 AUDC**, compared with Full **10.0000 / 88.1111**. Full minus OFF is **+0.3333 / −0.1111**, with mixed individual pairs.

The submitted history also contains a nonstandard auxiliary normalized-AUDC formula. It differs from the official formula at 305 of 360 prefixes. M2 preserves the submitted history bytes and corrects **only that auxiliary field in separate M2 analysis views**, using the unchanged official metric function. Required core scores and all original source files remain unchanged. See [auxiliary audit](results/m5_auxiliary_normalization_audit.json), [all corrections](results/m5_normalized_AUDC_corrections.csv) and [both history versions](results/m5_history_analysis_views/). No claim is made that every submitted auxiliary value was correct.

The file named `resolved_config.yaml` preserves the actual saved composed configuration, with both ordinary references and runtime interpolations still present. It is not a fully evaluated YAML export. Critical budget/seed/system fields and saved-config treatment comparisons pass; this provenance boundary remains explicit. Text manifests retain their original Windows-byte fingerprints: 126 files require deterministic LF-to-CRLF restoration to match, and 18 empty logs match directly. All declared fingerprints match one of these documented representations.

Full Ga–Pt–Tm seed17 has **8 mixed and 12 exploit** decisions. The only ternary query is query6, from the UCB pool during mixed mode. M2's [updated case notes](audits/metrics/updated_failure_cases.md) supersede the remaining M5 sentence that calls every other step exploit. No decision mode is invented.

## Preservation and scope

This release changes only M2 files. It retains previous accepted and provisional reports, the previous M5 strict rejection, all submitted originals and original failed/incomplete attempts. No new scientific experiment, agent proposal, model/oracle call or external message is performed.

Earlier M2 routing archives still have the explicitly disclosed missing raw hidden Hydra attachments and deleted temporary checkpoint histories. Required visible payloads and separately labelled reevaluated curves remain verified; the archive is not described as a byte-complete original capture. Machines and dependency versions differ between contributions, and costs remain partial. No controlled hardware-speed, zero-total-resource-cost, statistical-significance or held-out-generalization claim is supported by this dev release.
