# M5 Exploration Ablation — Results

Owner: Chen Mingsong (M5). For M2 (final results table) and M6 (report).
Date: 26 Oct. Protocol v1, frozen revision, dev systems, B=20, seeds 17/29/43.

## Method

`exploration_off` disables only `enable_exploration` in `m1_integrated.yaml`
(α₀ = 0.8, γ = 1.0, β₀ = 2.0 frozen). Comparison arm is M1's frozen `m1_full`
(same config, exploration on), 18 episodes each (6 systems × 3 seeds), same
machine family, same seeds/budgets.

## Paired results (mean ± population std over 3 seeds)

| System | ON mSUN | OFF mSUN | ΔmSUN | ON AUDC | OFF AUDC | ΔAUDC |
|---|---|---|---|---|---|---|
| Co-Mg-Na | 9.0±3.6 | 3.3±1.2 | **+5.7** | 68.2 | 17.0 | **+51.2** |
| Hf-Ni-Zr | 9.3±2.1 | 6.7±1.7 | **+2.7** | 91.7 | 57.0 | **+34.7** |
| Au-K-Tb | 13.0±2.2 | 12.0±2.2 | +1.0 | 106.5 | 98.7 | +7.8 |
| Mg-Sn-Sr | 10.0±1.4 | 12.0±2.9 | −2.0 | 96.0 | 119.7 | −23.7 |
| Co-Dy-W | 7.3±0.9 | 8.3±4.5 | −1.0 | 57.7 | 84.2 | −26.5 |
| Ga-Pt-Tm | 10.3±1.2 | 15.7±2.1 | **−5.3** | 101.8 | 152.8 | **−51.0** |
| **Overall** | 9.8±2.7 | 9.7±4.8 | +0.2 | 87.0±28.5 | 88.2±49.3 | −1.2 |

Raw per-episode tables are in the exploration_off result tree (committed to
`M1/MADE/results/protocol_v1/exploration_off/`); the m1_full reference is at
`M1/MADE/results/protocol_v1/m1_full/`.

## Interpretation (for the report's discussion)

The exploration policy does **not** uniformly improve or hurt discovery; it
**reduces risk on hard systems and costs budget on easy ones**:

- **Helps where the base agent stalls.** Co-Mg-Na (OFF mSUN 3.3) and Hf-Ni-Zr
  (OFF 6.7) gain the most. UCB-driven probes force the agent out of low-yield
  regions early, and the episode-level no-reproposal guarantee stops it from
  re-testing spent stoichiometries.
- **Costs where the generator is already productive.** Ga-Pt-Tm (OFF 15.7)
  and, to a lesser extent, Mg-Sn-Sr / Co-Dy-W lose budget to exploration
  probes while the planner alone already found a rich region.
- **Lowers variance.** Overall std drops from 4.8 (off) to 2.7 (on): the
  policy makes performance more consistent across systems.
- Overall mean is a wash (+0.2 mSUN), which is the honest headline: with the
  single-composition planner limiting exploration to ~1 slot/step, the policy
  is a stabiliser and a hard-system rescue, not a uniform accuracy boost.

## Failure trajectories (two required examples)

1. **Over-exploitation** — `exploration_off` Mg-Sn-Sr seed 29. After finding
   Sn₉Sr₁ stable at query 1, the agent spends queries 1–15 on the Sn–Sr
   binary line (14 consecutive binaries, 8 stable but all the *same* region)
   and only touches the ternary Mg–Sn–Sr space at queries 16–19 — where it
   immediately finds two more stable compositions (Mg₂Sn₅Sr₂, Mg₈Sn₇Sr₃).
   The missed ternary region is the cost of never leaving the known good area.

2. **Wasteful exploration** — `m1_full` Ga-Pt-Tm seed 17. The Ga–Tm binary
   line is rich (10 stable hits), but the exploration policy repeatedly probes
   ternary Ga–Pt–Tm mixes (queries 5, 12, 13, 14, 15, 18 — all unstable,
   e_hull 0.12–0.42) while the productive binary line was still open. Sibling
   OFF run reaches mSUN 15.7 vs ON 10.3 on the same seed.

Trajectory files: `M1/MADE/results/protocol_v1/exploration_off/dev/Mg-Sn-Sr/seed_29/...`
and `.../m1_full/dev/Ga-Pt-Tm/seed_17/...`.

## Open item for M2/M6

The frozen `m1_full` reference runs (from M1's machine) do not contain the
`m5_decisions.jsonl` sidecar, so the wasteful-exploration example above is
annotated from the trajectory only. If per-step mode/rationale annotations are
required, either M1 re-runs with the sidecar-enabled code or we annotate the
chosen steps from the trajectory manually (mode = explore for the ternary
probes, per the UCB pool in the α₀=0.8 schedule).
