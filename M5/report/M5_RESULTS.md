# M5 Exploration Ablation — Results (corrected 26 Oct)

Owner: Chen Mingsong (M5). For M2 (final results table) and M6 (report).
Protocol v1, frozen revision, dev systems, B=20, seeds 17/29/43.

## Method

`exploration_off` disables only `enable_exploration` in `m1_integrated.yaml`
(α₀ = 0.8, γ = 1.0, β₀ = 2.0 frozen). Comparison arm is M1's frozen `m1_full`
reference (successful attempts: `attempt_02` for Mg-Sn-Sr seeds 17/29,
`attempt_01` elsewhere, per M1's freeze note), 18 paired episodes
(6 systems × 3 seeds), same seeds/budgets.

## Paired results (seed means ± sample SD over 3 seeds)

| System | ON mSUN | OFF mSUN | ΔmSUN | ON AUDC | OFF AUDC | ΔAUDC |
|---|---|---|---|---|---|---|
| Co-Mg-Na | 9.00±4.36 | 3.33±1.53 | **+5.67** | 68.17 | 17.00 | **+51.17** |
| Hf-Ni-Zr | 9.33±2.52 | 6.67±2.08 | **+2.67** | 91.67 | 57.00 | **+34.67** |
| Au-K-Tb | 13.00±2.65 | 12.00±2.65 | +1.00 | 106.50 | 98.67 | +7.83 |
| Mg-Sn-Sr | 11.00±1.73 | 12.00±3.61 | −1.00 | 102.83 | 119.67 | −16.83 |
| Co-Dy-W | 7.33±1.15 | 8.33±5.51 | −1.00 | 57.67 | 84.17 | −26.50 |
| Ga-Pt-Tm | 10.33±1.53 | 15.67±2.52 | **−5.33** | 101.83 | 152.83 | **−51.00** |
| **Overall** | **10.0000** | **9.6667** | **+0.3333** | **88.1111** | **88.2222** | **−0.1111** |

Overall values match M2's accepted frozen-Full audit
(`M2/aggregation/20261026_m5_intake/`). Separately, the pooled population SD
of mSUN across all 18 episodes drops from 4.83 (OFF) to 2.73 (ON) — reported
here as a pooled population SD, not to be confused with the per-system
seed-mean sample SDs in the table.

## Interpretation (for the report's discussion)

Exploration ON trades a small amount of mean performance for a large
consistency gain: +0.33 mSUN overall, pooled population SD 4.83 → 2.73. The
per-system pattern is heterogeneous:

- Largest gains on Co-Mg-Na (+5.67 mSUN) and Hf-Ni-Zr (+2.67), the two
  systems where OFF scores lowest.
- Largest loss on Ga-Pt-Tm (−5.33 mSUN), the system where OFF scores highest.

**Interpretation boundary (per M2's audit):** the reading "exploration
rescues hard systems and costs easy ones" is a hypothesis consistent with
the endpoint pattern, not a measured per-query attribution. The trajectories
below show the observed behaviour; the counterfactual (what earlier or later
probing would have yielded) is unobserved.

## Failure trajectories (two required examples)

1. **Over-exploitation** — `exploration_off` Mg-Sn-Sr seed 29
   (`.../exploration_off/dev/Mg-Sn-Sr/seed_29/attempt_01/trajectories/episode_000.json`).
   Observed: the first 16 queries (one-based 1–16) are all Sn–Sr binaries,
   yielding 6 stable hits; Sn₉Sr₁ is stable already at query 2
   (e_hull = 0.082). Only queries 17–20 touch the ternary Mg–Sn–Sr space —
   where queries 19 (Mg₂Sn₅Sr₂, e_hull = 0.071) and 20 (Mg₈Sn₇Sr₃,
   e_hull = 0.068) are immediately stable. All 20 proposals are unique
   structures (no duplicate-structure mode collapse). The observed behaviour
   is delayed ternary sampling: the agent stayed on the known-good binary
   line until the budget was nearly spent, and the ternary region it reached
   late produced 2 stable hits in 4 queries.

2. **Wasteful exploration** — `m1_full` Ga-Pt-Tm seed 17
   (`.../m1_full/dev/Ga-Pt-Tm/seed_17/attempt_01/trajectories/episode_000.json`,
   with the original 20-record `m5_decisions.jsonl` in the same attempt dir).
   Observed: 10 stable discoveries (9 Ga–Tm binaries + 1 Pt–Tm binary);
   exactly one ternary query — query 6, Ga₁Pt₄Tm₃, unstable,
   e_hull = 0.417 — which the decision log records as mode `mixed` with the
   ternary composition coming from the UCB explore pool. The same-seed OFF
   run reaches mSUN 16 (AUDC 168) vs ON 10 (AUDC 93). (System means over the
   three seeds are OFF 15.7 vs ON 10.3.) On this system the single UCB
   ternary probe and the shifted early-step choices coincide with a much
   worse endpoint than the OFF arm; the log shows all other steps were
   `exploit` mode on planner compositions.

## Evidence packaging (26 Oct, per M2's request)

Each of the 18 `exploration_off` attempts now contains: `hydra/` (saved
config/hydra/overrides), `m4_evidence.jsonl`, `run_benchmark.log`,
`console_attempt_01.log`, `resolved_config.yaml` (composed config from the
saved Hydra files; runtime-only interpolations kept verbatim),
`m2_metrics_history.json` (lossless reconstruction from the official
trajectory, labelled in-file; verified to match the official mSUN and AUDC
endpoints of all 18 attempts exactly), and `evidence_manifest.json`
(sha256 + bytes per file, recorded revision `aedf8ca`). No rerun was
performed; no original attempt was overwritten. `m5_decisions.jsonl` is
absent from the OFF arm by design — the exploration hook is disabled, so no
decisions exist.

Note: `m1_full/dev/Mg-Sn-Sr/seed_17/attempt_05..08` are M5's pre-freeze
dry runs (21 Oct, pre-freeze code), preserved untouched per the
preserve-failed-runs rule and excluded from the frozen reference by M1's
attempt selection.
