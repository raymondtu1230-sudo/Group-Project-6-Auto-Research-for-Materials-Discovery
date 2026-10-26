# Superseded by the complete M3 handoff

26 October 2026: all18 m3_full original runs have now been received and validated. [Current144-run report](../20261026_m3_complete/README.md). The complete54-run M3 component assignment is accepted. The earlier attribution of extra Full-agent planning_off/self_correction_off runs to M3 is withdrawn; M1/M6 decide that additional scope. Below is the preserved earlier intake record, not the current outstanding-work list.

---

# Shared ablation intake and baseline comparisons

26 October 2026. Source snapshot: `95f9c8e38923ac494b1117a9b212702afdc5980f`.

The unchanged M2 evaluator accepts **126 real completed dev episodes across seven methods**, 18 per method, with no validation issues. This includes M4's 18 `memory_off` and M3's 36 `m3_*` OFF episodes, plus the previously validated baselines, Full reference and routing ablation. All 54 newly received peer episodes are included in the shared baseline comparisons.

- [M6 handoff and result tables](M6_HANDOFF.md)
- [Receipt and remaining inputs](RECEIPT_AND_OPEN_ITEMS.md)
- [Two-slide editable assembly text and speaker notes](GROUP_RESULTS_SLIDE_CONTENT.md)
- [Method-level scores and paired baseline metrics](results/per_method_summary.csv)
- [126 per-run scores and Random/Chemeleon AF/EF](results/per_run_with_baseline_comparisons.csv)
- [36 paired Full single-switch comparisons](results/paired_full_system_ablations.csv)
- [Discovery curves by study](results/discovery_curves_by_study.svg) and [numeric curve data](results/aggregate_discovery_curve_data.csv)
- [Per-run machine-labelled costs](results/per_run_costs.csv)
- [Aggregation validation](results/aggregation_validation.json), [evaluator validation](results/m2_evaluator/validation.json), [loading/source provenance](results/evaluation_provenance.json) and [input receipts](results/input_receipts.json)
- [Independent M3 audit](audits/m3/README.md) and [M4 audit and actual test outcomes](audits/m4/INDEPENDENT_AUDIT.md)
- [Reproduction code](aggregate_handoffs.py)

## Correct interpretation

`memory_off` and `tool_routing_off` each change one switch relative to all-enabled `m1_full`. The two M3 profiles additionally turn exploration and routing OFF and belong to a separate component study paired with `m3_full`. M3's OFF result folders validate, while the historical 18-row `m3_full` CSV lacks the complete raw comparator package needed for independent pairing validation. Its context summary is [explicitly unvalidated](results/m3_historical_comparator_unvalidated.json).

All means and standard deviations use the shared seed-first convention: equally average six systems within each seed, then report mean ± sample SD across three seeds. Official AF/EF are calculated per paired system/seed history before aggregation, not by dividing grand means. EF uses the actual default cap of 100 and a safe denominator of 1e-8; a zero-discovery baseline therefore follows that numerical convention, including zero-versus-zero EF=0. AF targets the baseline's final discovery level and follows the official reachability/zero conventions. Large capped EF values should not be interpreted as a measured multiplicative speedup. These are discovery metrics, not runtime ratios.

`m2_evaluator/validation.json` uses the unchanged evaluator's three required core methods (Full, Random and Chemeleon). Its `final_comparison_complete` flag describes that core scoreboard. The separate `aggregation_validation.json` correctly records **`all_group_ablations_complete: false`**: the received M3 profiles do not supply the formal Full `planning_off` / `self_correction_off` methods, M5's formal `exploration_off` has not been found, and the complete `m3_full` raw comparator is missing. M6's check/hidden assembly remains separate from these dev results.

## Evaluation and preservation scope

The original `M2/evaluate.py` executes unchanged, including its own CLI validation, material-reference comparison, AF/EF and reports. A transparent lightweight loader compiles the unchanged official `DiscoveryCurveMetrics` class AST with real frozen-version NumPy, avoiding unrelated model imports. Exact evaluator, metric-module and class hashes are recorded. No metric formula, agent, oracle, protocol or Hydra configuration is changed.

Original run files stay read-only. Eighteen routing evaluation views preserve the original incomplete history file and add a clearly labelled derivative history from the previously verified structure-and-energy reevaluation. This is not recovery of an original successful checkpoint. M1's newly supplied reconstructed histories are also crosschecked against all 18 prior structure-and-energy reevaluated prefixes. M3 histories remain labelled reconstructions; M4 OFF histories retain their captured-checkpoint provenance. Original missing Hydra attachments and failed collection audits remain documented in the earlier M2 archive.

M2 independently passed all 15 standalone M4 tests. The reported 72-test combined selection could not complete locally because its collection requires Hydra and pymatgen; exact commands and outputs are preserved. M4's own 72-pass statement remains attributed to M4.

Known model fees exclude hardware, electricity and uninstrumented work. Costs retain unknown counters and original machine labels. No scientific episode, oracle query, model call or external message was generated by this aggregation. All project changes are under `M2/`.
