# Independent review of the126-run aggregation

Read-only review of `M2/aggregation/20261026/results` after the actual unmodified M2 evaluator execution. No source, result, raw data, or GitHub file was changed by this review. No agent, oracle, model, or scientific episode was invoked.

## Independently checked

-126 unique method/system/seed rows: seven methods with18 units each.
-126 input receipts: original and derivative-view metadata, full trajectory, and resolved configuration SHA256 values all match their receipts.
-All per-method mSUN, AUDC, AF/EF means and sample SDs reproduce from equal-weight six-system means within each of the three seeds.
-252 paired AF/EF comparisons against Random and Chemeleon independently reproduce from each actual saved history, including the official cap100 and zero-baseline conventions.
-36 formal Full-system ablation rows cover only memory_off and tool_routing_off. Every endpoint difference and directional AF/EF value independently reproduces.
-All18 files listed in the output integrity manifest match their byte counts and SHA256 values.
-The evaluator SHA256, official metric module SHA256, and unchanged DiscoveryCurveMetrics AST SHA256 match the actual source snapshot. The lean loader compiles the exact official class AST with real NumPy; it does not alter metric formulas or invoke model dependencies.
-The plotted curves were visually inspected: readable labels, correct official AUDC-source terminology, and a separate M3 component-study panel. System means are averaged within each seed, with sample SD across three seed means.

No numeric, input-identity, or metric-adapter discrepancy was found in this reviewed output.

## Scope is correctly qualified

The126 accepted rows do not establish completion of all formal group ablations. The36 M3 component-study runs keep exploration and routing OFF and are labelled separately; their missing historical raw m3_full comparator remains unvalidated. Formal Full-system planning_off, self_correction_off and exploration_off results are still absent. The aggregation correctly sets `all_group_ablations_complete=false` and does not manufacture those experiments or causal deltas.

The18 routing histories inserted into derivative evaluation views are explicitly labelled separately validated recorded-trajectory re-evaluations. Original incomplete history files and original failed collection audits remain unchanged. M1's patched reconstructed histories were crosschecked against all18 prior structure/energy re-evaluations. These are not claimed to be recovered historical checkpoints.

The underlying evaluator's `final_comparison_complete` flag covers its required core methods; it must not be described as completion of the entire group ablation matrix. The higher-level aggregation validation preserves that distinction.

## Publication note

The builder was still adding a published-ZIP reproduction fallback when this initial output was reviewed. Regenerate the final results/provenance after source changes so any published aggregation-script hash identifies the final script. This is a provenance housekeeping requirement, not a discrepancy in the reviewed numerical outputs.
