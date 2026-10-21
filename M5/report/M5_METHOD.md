# M5 Method Section — Exploration Policy

Owner: Chen Mingsong (M5). For M6 to slot into the group report.
Status: draft v1 (21 Oct). Revision after ablation results (27 Oct).

## What the exploration policy controls

The M1 integration agent calls each plug-in through a narrow hook. Ours runs
after planning and self-correction and before the budget cap:

```
planner.propose(...) -> self_correction.revise_plan(...)
  -> exploration.adjust_plan(plan, context) -> M1 budget cap -> generator
```

The hook receives the planner's `Plan` and a context dict, and must return a
modified `Plan`. The only effective steering lever is `Plan.compositions`:
which chemical compositions the generator will build structures for. (M1
confirmed the built-in generators ignore `Plan.constraints`, so composition
choice is the entire decision surface.)

## Algorithm: budget-annealed UCB over composition space

The policy treats the 20-query oracle budget as a finite-horizon explore /
exploit problem over the composition simplex of the current chemical system.

1. **Surrogate.** A Gaussian-process regressor (RBF kernel, Cholesky solve) is
   fitted at every step on the observed `(composition -> e_above_hull)` pairs
   drawn from `context["m1_memory"]`. With at most 20 observations the fit
   costs milliseconds.
2. **Explore pool.** Unqueried integer stoichiometries over the current
   elements (reduced formulas, total atoms ≤ `max_stoichiometry`) are scored
   with UCB = −μ + β(t)·σ, where μ, σ are the GP posterior mean and std.
   Minimisation form: low predicted `e_above_hull` (exploit) or high
   uncertainty (explore) both raise the score.
3. **Annealing schedule.** Both the exploration share and the UCB weight decay
   with remaining budget:

   ```
   α(t) = α₀ · (queries_remaining / B)^γ
   β(t) = β₀ · (queries_remaining / B)^γ
   ```

   Defaults α₀ = 0.5, β₀ = 2.0, γ = 1.0. Early episodes buy information;
   late episodes exploit the best regions as the budget runs out.
4. **Plan assembly.** `n_explore = round(α(t) · |plan.compositions|)` UCB picks
   are appended after the planner's compositions, which are kept unchanged
   (exploit pool). M1's budget cap runs after the hook, so the policy cannot
   overspend. All sampling is seeded from `experiment.seed`; ties break by
   sorted formula string, so behaviour is deterministic under the protocol
   seed.
5. **Episode-level memory.** Because `m1_memory` may be bounded (M4's manager
   returns at most `limit` recent records), the policy keeps its own cumulative
   set of queried formulas in checkpointed state, so no composition is ever
   re-proposed once it leaves the memory window.

## Decision log (feeds M4's evidence log)

Every `adjust_plan` call appends one JSON record to an in-memory log and,
when configured, to a per-episode `m5_decisions.jsonl` sidecar. Fields: step,
`m1_queries_remaining`, mode (`explore`/`exploit`/`mixed`), incoming and
outgoing composition lists, per-composition source (`planner`/`ucb_explore`),
GP posterior statistics for each pick, α(t), β(t), and a short rationale
string. The log is the primary data source for the failure-mode trajectories
in Section [failure analysis]; it round-trips through agent checkpoints, and
`load_state` truncates the sidecar on resume so replayed steps never
duplicate entries.

## Dry-run findings (dev system Mg-Sn-Sr, seed 17, B=20)

A full `m1_full` episode was run before the freeze as an integration dry run
(wall time ≈ 15 min on the local RTX 4070 laptop). Headline numbers versus
the M1 reference (`m1_baseline`, diversity planner + bounded memory, no
plug-ins):

| Metric | m1_baseline | m1_full (α₀=0.5) | m1_full (α₀=0.8) |
|---|---|---|---|
| mSUN@20 | 7 | 9 | 9 |
| AUDC | 49.5 | 66.5 | **84.5** |
| stable+novel fraction | 0.35 | 0.45 | 0.45 |

**α₀ tuning.** Because the M3 planner emits a single composition per step,
`n_explore = round(α(t) · 1)` is at most one, and only when α(t) ≥ 0.5.
Under the initial default α₀ = 0.5 the explore slot opens only at step 0 and
closes immediately; a companion run with α₀ = 0.8 keeps it open while
remaining/B ≥ 0.5 (roughly the first half of the budget) and raises AUDC
from 66.5 to 84.5 on the same seed. The α₀ = 0.8 run also surfaces a stable
Mg–Sr compound (MgSr, e_hull = 0.019) that the α₀ = 0.5 run never reached.
α₀ = 0.8 is therefore adopted as the default for the ablation; α₀ = 0.5 is
retained as the conservative arm.

The α₀ = 0.5 trajectory shows the expected three-phase behaviour: an early
exploration phase (1 stable hit in the first 6 queries), a mid-episode dip
when the policy left the Sn–Sr binary line to probe Sr-rich compositions
(1 hit in steps 10–15), and a late exploitation phase that recovered 5
stable materials in the final 6 queries. The α₀ = 0.8 trajectory shifts
discovery earlier: 7 of its 9 stable hits land in the first 10 queries.

**Limitation.** The policy's per-step leverage is one composition slot under
the current single-composition planner output. Its contributions are
concentrated at early steps and in the episode-level no-reproposal guarantee
(cumulative queried-formula set), not in per-step dominance of the plan.
A multi-composition planner would give the policy more room — noted under
Future Plans.

## Ablations (26–27 Oct, pending)

- `m1_full` (exploration on, α₀ = 0.8) vs `exploration_off` at identical
  seeds/budgets/systems. Expected signal: the difference concentrates in
  the first half of the episode, where the explore slot is open.
- Failure trajectories: one over-exploitation and one wasteful-exploration
  case will be drawn from `m5_decisions.jsonl` and M4's evidence log, with
  per-step mode/budget/rationale annotations.
