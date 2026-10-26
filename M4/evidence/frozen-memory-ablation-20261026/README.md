# Frozen Memory ablation results

Updated 26 October 2026. Dev split only: six systems × seeds 17/29/43, B=20, CPU ORB. The 18 Memory OFF episodes disable only `enable_memory`; planning, reflection, exploration, tool routing and independent event capture retain the frozen settings.

| Metric | Full reference ON | Memory OFF | ON minus OFF |
| --- | ---: | ---: | ---: |
| mSUN@20 | 10.0000 ± 0.8819 | 9.1111 ± 1.3472 | +0.8889 |
| AUDC | 88.1111 ± 9.4536 | 86.9444 ± 9.0252 | +1.1667 |

Each seed first averages the six systems equally; values are mean ± sample SD across the three seed means. For mSUN, ON is better in 8 of 18 pairs, equal in 3 and worse in 7. For AUDC, ON is better in 9 and worse in 9. Memory has a small positive aggregate difference in this experiment, with mixed pairwise effects. These descriptive results do not establish statistical significance or a uniform benefit.

## Provenance and validation

- Actual Memory OFF run source: `02e0026bf450f71f4f7862228d295f5b02b49e12`.
- M1 reference evidence patch: `ae7fe81991c56dd2d77685220b74ddbef11039c7`. The scientific agent code, Hydra configuration and protocol used here are unchanged between these revisions. Preserve the actual run metadata; do not relabel earlier runs as executed at the later commit.
- All 36 result directories (18 ON and 18 OFF) pass M2's canonical `load_run` validator. Each paired reference snapshot matches. All files listed in the 18 M1 evidence manifests pass byte-size and SHA-256 checks.
- M1's per-query reference histories were reconstructed from its complete frozen trajectories because the original successful-run checkpoint histories were not retained. M1 explicitly records this provenance. The reference histories are not original checkpoint captures. OFF histories were retained by external observation of the official run checkpoints.
- These are frozen-agent development ablations, distinct from the earlier single-pair development pilot. They are not check/hidden results. The earlier negative pilot remains preserved at its original revision.

## Files and handoff

`paired_results.csv` contains all 18 pairs. `summary.json` contains seed-level aggregates. `reference_patch_validation.json` records the final paired validation. `memory_off_raw_results.zip` preserves the complete OFF result directories, including trajectory, summary, metadata, resolved configuration, saved Hydra configuration, complete evidence exports, M3 trace and M5 decisions. An online Memory OFF evidence log may be absent because retrieval is disabled; the full trajectory export is provided. Proposal-event files exist only when the capture wrapper emitted events.

M1's ON evidence remains in `M1/MADE/results/protocol_v1/m1_full/dev/` at the reference evidence revision. The raw archive contains evaluator-only reference data for offline analysis; it must never be supplied to agent memory or decision inputs. No private API configuration is included.

M2: use these 18 Memory OFF units with the frozen full reference in the component-ablation table. AF/EF and any additional group-wide comparisons should use the shared M2 reporting definitions; this handoff reports mSUN and AUDC and does not invent missing cost counters. M6: use the aggregate table and mixed-effects qualification above. The older development-pilot deck remains historical; use the final-result deck listed below.

## Completed analysis and presentation handoff

[Discovery curves](analysis/discovery_curves.png), per-query data, [three traced cases](analysis/TRACED_CASES.md), original per-run cost accounting and official directional OFF-vs-ON AF/EF are now available in the analysis folder. The required comparisons against Random and Chemeleon remain part of M2's shared leaderboard. ON exact review-memory IDs were not retained, so the cases make no record-specific causal claim. The final two-slide deck is M4_Frozen_Memory_Results.pptx, with matching M4_SPEAKER_NOTES.md.
