# Independent M5 metrics and case review

Snapshot: `a27634d9edbf231d0c034273fa9f977f9d5e799e`. Original source and M5 handoff were read only. All files written by this audit are under this M2 audit directory. No model, agent, Materials Project or oracle calls were made.

The 18 actual `exploration_off` endpoints and 18 successful frozen `m1_full` endpoints pass the read-only metric audit. The M5 narrative needs corrections before reuse. Full numeric evidence is in `m5_metrics_independent_audit.json`; the real per-query case evidence and original mode-log joins are in `failure_cases.json` and `failure_cases.md`.

## Comparator and metric checks

Each accepted system/seed has exactly one completed dev episode, trajectory length and final query count20. Full Mg–Sn–Sr seeds17 and29 correctly use `attempt_02`; the two unsuccessful/incomplete `attempt_01` directories remain preserved and excluded. Other16 Full units use `attempt_01`. OFF has18 successful `attempt_01` units.

For all36 accepted endpoints, the unchanged M1 `curve_from_trajectory` function reconstructed the actual recorded `is_stable` and `is_newly_discovered` observations. The exact unchanged official `DiscoveryCurveMetrics` class, executed with real NumPy2.3.5, reproduced every saved endpoint AUDC. All36 endpoint counts, both summary files, recorded command flag profiles, and18 paired canonical material-reference/protocol comparisons passed. There were720 recorded-observation prefixes and zero mismatches. M5's original18 raw directories do not contain `m2_metrics_history.json`; this audit has not edited them or relabelled derived curves as original history.

This is an independent consistency and area-arithmetic check of actual saved observations. It does not independently recompute hulls, physical energies, structure matching or novelty. It does not recover deleted runtime checkpoints.

Endpoint verification is not complete package acceptance: the current18 M5 raw directories lack original `resolved_config.yaml`, and the unchanged strict M2 evaluator therefore accepts0 of these new18 packages. Their numerical results are labelled endpoint verified / package pending. The prior144 accepted records remain separate. This audit has not reconstructed an alleged original resolved configuration from command arguments.

For OFF Ga–Pt–Tm43, AUDC126.5 is correct. Its first query is stable and newly discovered, so the official class prepends the query0/count0 origin to the saved cumulative series. Integrating only query1–20 yields126.0 and omits the first0.5 triangle. Adding the official origin gives126.5, matching both the unmodified M1 helper and original endpoint without any endpoint correction. The explicit proof is in `zero_origin_AUDC_proof.json`.

## Correct headline statistics

The primary project statistic first averages the six systems within each seed, then reports the mean and sample SD of the three seed means.

| Method | mSUN mean ± seed sample SD | AUDC mean ± seed sample SD |
|---|---:|---:|
| Frozen Full, exploration ON | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |
| Paired ON minus OFF | +0.3333 ± 1.8559 | −0.1111 ± 18.8947 |

The report's overall ON9.8, ON AUDC87.0, effect+0.2 and AUDC effect−1.2 are incorrect. Primary mSUN ON/OFF seed means are respectively `[9,10.3333333,10.6666667]` and `[10.3333333,10.3333333,8.3333333]`. Across18 pairs, ON mSUN wins8, ties1 and loses9; AUDC wins9 and loses9. These figures support mixed system-dependent outcomes without an established universal advantage.

As a separately labelled descriptive supplement, pooled18-episode mSUN population SD is ON2.72845 versus OFF4.83046. Thus the rounded4.8→2.7 statement is numerically correct for pooled system/seed dispersion; it is not the primary seed-level sample SD or proof of causal stabilisation. Pooled AUDC population SD is ON28.81770 and OFF49.29368; the report's ON28.5 should be28.8.

## Per-system corrections

All deltas below are ON minus OFF. Per-system SD here is the population SD over three seeds, matching the report's explicitly named per-system convention; the machine-readable audit also retains sample SD.

| System | ON mSUN ± pop. SD | OFF mSUN ± pop. SD | ΔmSUN | ON AUDC | OFF AUDC | ΔAUDC |
|---|---:|---:|---:|---:|---:|---:|
| Mg–Sn–Sr | 11.000 ± 1.414 | 12.000 ± 2.944 | −1.000 | 102.833 | 119.667 | −16.833 |
| Au–K–Tb | 13.000 ± 2.160 | 12.000 ± 2.160 | +1.000 | 106.500 | 98.667 | +7.833 |
| Co–Mg–Na | 9.000 ± 3.559 | 3.333 ± 1.247 | +5.667 | 68.167 | 17.000 | +51.167 |
| Hf–Ni–Zr | 9.333 ± 2.055 | 6.667 ± 1.700 | +2.667 | 91.667 | 57.000 | +34.667 |
| Co–Dy–W | 7.333 ± 0.943 | 8.333 ± 4.497 | −1.000 | 57.667 | 84.167 | −26.500 |
| Ga–Pt–Tm | 10.333 ± 1.247 | 15.667 ± 2.055 | −5.333 | 101.833 | 152.833 | −51.000 |

The Mg–Sn–Sr ON values in the report are wrong: actual mSUN12/9/12 and AUDC105/98.5/105 give means11 and102.833, not10 and96. Its corrected deltas are−1mSUN and−16.833AUDC, not−2 and−23.7. The other five per-system rows agree with actual records at the report's rounding precision.

## Actual case evidence

- OFF Mg–Sn–Sr29: the first16 queries are Sn–Sr binaries, with6 stable hits, followed by4 ternary queries with2 stable hits. Sn9Sr1 occurs at zero-based index1, which is one-based query2. All20 structures are newly discovered and exact serialized structures differ; delayed ternary sampling is observed, while duplicate-structure collapse is not established.
- Full Ga–Pt–Tm17: only one ternary was evaluated, at zero-based index5 / one-based query6, with hull distance0.41701856 and unstable label. The five other alleged ternary probes are actually Ga–Tm binaries. Full has9 stable Ga–Tm hits plus1 stable Pt–Tm hit. Its actual20-record `m5_decisions.jsonl` exists; the joined record marks index5 `mixed` and the five alleged additional probes `exploit/planner`. Do not replace those real labels with inferred `explore` labels.
- The same-seed17 Ga–Pt–Tm comparison is OFF16 versus ON10 mSUN and AUDC168 versus93. Report15.7/10.3 are three-seed system means, not same-seed values. Existing saved logs close the report's claimed missing-sidecar item without rerunning science or manually inventing modes.

The records support the observed binary/ternary selection and outcomes. Earlier discovery in an unqueried counterfactual, easy/hard-system categorisation, a hard-system rescue mechanism, and opportunity-cost explanations remain hypotheses. Recorded `is_stable` uses the protocol tolerance0.1eV/atom, not a claim of exactly zero hull distance.

The report's “same machine family” claim is also inaccurate: Full metadata is macOS arm MacBook, while OFF metadata is Windows AMD64/AuthenticAMD. Both record CPU ORB under the same protocol; runtime speedups should not be inferred from this cross-machine comparison.

## Reproduce this audit

Run `M2/stage_aggregation_20261026/venv/bin/python M2/stage_m5_intake_20261026/audit_metrics/verify_m5_metrics.py` from the project root. It reads the pinned snapshot and writes only `m5_metrics_independent_audit.json` in this audit directory. The JSON contains source hashes, exact unit paths, preserved excluded attempts, every endpoint check, per-seed aggregates, per-system statistics and paired deltas.

The separate M2 aggregation output was also compared against this independent audit: all18 OFF endpoint rows, four primary mean/SD statistics,18 Full paired deltas,36 directional AF/EF values and360 derived query points match, with zero errors. Its strict0-accepted/18-package-pending labels are correct; see `m5_aggregation_independent_review.json`.
