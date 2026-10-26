# Independent M4 handoff audit

Read-only audit of repository snapshot `95f9c8e38923ac494b1117a9b212702afdc5980f`, including normalized analysis handoff `9a75966b0c6e3d3fe0da41197f8e013170096110`. No M4, M1, shared source, or GitHub file was modified. No scientific episode, oracle call, or model call was run by this audit.

## Result

The 18 real `memory_off` development episodes and their paired endpoint/curve data are suitable for M2's shared aggregation, subject to the two documentation/evidence qualifications below. The parent task independently executes M2's canonical evaluator; this audit does not replace that execution.

| Check | Independent result |
| --- | --- |
| Raw archive | 5,103,853 bytes; SHA256 `2bf7d980571157c54d90a22b82157bf405034b6f6d110ddb0c45be9e554e392b`; ZIP CRC passed; 288 members |
| Units | 18 unique memory_off/dev units, six systems and seeds 17/29/43; all attempt_01, completed, one episode, B20 and20 trajectory steps/queries |
| Treatment | Every actual resolved config has only enable_memory=false; planning/reflection/exploration/tool routing=true; CPU `orb-v3-conservative-inf-omat` |
| Paired resolved configuration | Across all18 pairs, differences are only enable_memory, experiment output directory, component log paths, and capture/memory run IDs; no other configuration value differs |
| Actual source inputs | All74 per-run M1 input SHA256 values match the snapshot for all18 OFF episodes |
| Frozen runtime identity | All98 examined M1 runner/src/config and M4 src/pyproject files have unchanged Git blob identities relative to m1-freeze-20261025 |
| Histories/components | Every OFF history covers queries1..20 and labels official checkpoint capture; M5 has20 records with query_count0..19; complete exported M4 evidence has20 records |
| Additional raw files | Resolved config, saved Hydra config/hydra/overrides YAML, full trajectory, official summaries/episodes, M3 trace and complete M4 evidence exports are present |
| Handoff integrity | All17 files in M4 checksums.json match recorded byte counts and SHA256 |
| Published curves | 720 rows =36 groups×20 queries; history sources explicitly distinguish reconstructed M1 ON curves from checkpoint-captured OFF curves |
| Numeric checks | All36 curve mSUN endpoints and all36 zero-origin official trapezoid AUDCs agree with paired_results.csv; all18 directional OFF-vs-ON AF/EF values independently agree |

Aggregation uses equal-weight six-system means within each seed and sample SD across the three seed means:

| Arm | mSUN@20 mean ± seed SD | AUDC mean ± seed SD |
| --- | ---: | ---: |
| Frozen full ON | 10.0000 ±0.8819 | 88.1111 ±9.4536 |
| Memory OFF | 9.1111 ±1.3472 | 86.9444 ±9.0252 |

The reported mixed-effects qualification is appropriate: ON mSUN wins8/ties3/loses7; AUDC wins9/loses9. No uniform-benefit, significance, or held-out-generalization claim is supported by this dev comparison alone.

## Qualifications to carry into M2's report

1. **EF cap documentation typo.** M4 analysis/README.md says the official EF cap is10. The actual frozen function signature is `cap: float = 100.0`; its older docstring also misleadingly says10. M4/build_frozen_report.py calls that actual default. All18 published EF values are below1.56, so this typo does not alter these numeric results. M2 should document the actual cap100 convention and keep directional OFF-vs-ON AF/EF separate from comparisons against Random/Chemeleon.
2. **72-test claim is not independently reproduced.** closeout_validation.json records72 passed and an exact command. The committed raw transcripts M4/test_results.txt and joint_test_results.txt show historical36 and69 passes. After the parent prepared an isolated M2 venv, this audit actually attempted the original72-test selection with bytecode/cache/temp paths isolated under this audit directory. It exited2 during collection:4 import errors due to absent pymatgen and Hydra. This is an environment-blocked attempt, not evidence of a scientific or implementation failure and not a72-pass result. The15 standalone M4 tests were then actually executed and all passed in0.03s. Exact commands/results are in actual_72_suite_attempt.json/.txt and actual_standalone_suite.json/.txt. No heavy dependencies were installed by this audit. Label72 as M4-reported until the complete scientific environment permits independent rerun or a fresh original log is provided.

Additional provenance boundaries: the original run metadata preserves the official MADE upstream commit and74 source input hashes, while the outer freeze checkout/clean-worktree assertion is documented at handoff level. The raw ZIP does not retain an independent preflight git-HEAD/worktree transcript. The M1 ON history is a documented reconstruction, not an original checkpoint capture. OFF online retrieval-memory logs can correctly be absent because memory is disabled; complete exported queried-observation evidence is supplied. Cost accounting is partial: original driver times are ON5639.179s and OFF5758.163s total, on differently named machines/OS versions; initialization oracle work and LLM counters are not fully instrumented. No hardware speedup or zero-total-cost claim should be made.

## Primary paths

- `M4/evidence/frozen-memory-ablation-20261026/memory_off_raw_results.zip`
- `M4/evidence/frozen-memory-ablation-20261026/{summary.json,paired_results.csv,reference_patch_validation.json,checksums.json,closeout_validation.json}`
- `M4/evidence/frozen-memory-ablation-20261026/analysis/{per_query_curves.csv,paired_AF_EF_OFF_vs_ON.csv,cost_summary.json,README.md}`
- `M4/build_frozen_report.py`
- `M1/MADE/src/made/evaluation/metrics.py` enhancement_factor signature and zero-origin discovery-curve extraction
- `M4/test_results.txt`, `M4/joint_test_results.txt`
