# M5 Exploration Policy — One-Page Design

Owner: Chen Mingsong (M5). Interface contract: `M1/PLUGIN_INTERFACE.md`.
Status: draft v1 for M1 alignment (target 20 Oct).

## What the policy controls

The hook is `ExplorationPolicy.adjust_plan(plan, context) -> Plan`, called after
planning/reflection and before M1's budget cap. The only levers are the Plan
itself:

- `plan.compositions`: which compositions the generator will build structures for
- `plan.num_candidates`: how many structures per composition
- `plan.constraints`: optional hints passed through to the generator

So "exploration vs exploitation" is implemented as **composing the plan's
composition list from two pools** and setting how many candidates each pool gets.
The policy never calls the oracle, never reads hidden labels, and stays inside
M1's post-hook budget cap.

## Inputs

- `context["m1_queries_remaining"]` — remaining oracle budget (B=20 per protocol v1)
- `context["m1_memory"]` — bounded observed-outcome records
  (`reduced_formula`, `e_above_hull`, `is_stable`, `is_newly_discovered`,
  `query_count`); empty when memory is off
- `context["elements"]`, `context["max_stoichiometry"]` — chemical system bounds
- incoming `plan` from M3's planner (exploit-biased by construction: the
  diversity planner works near attempted compositions)

## Algorithm: budget-annealed UCB over composition space

1. **Featurize** each composition as its element-fraction vector
   (len = |elements|, sorted; e.g. Mg-Sn-Sr → (x_Mg, x_Sn, x_Sr)).
2. **Surrogate**: Gaussian-process regression (RBF kernel) fit on observed
   `(fraction vector -> e_above_hull)` from `m1_memory`. With n ≤ 20 observations
   this is milliseconds per fit. Lower predicted `e_above_hull` = more promising.
3. **Explore pool**: enumerate unqueried stoichiometries within
   `max_stoichiometry`, score with **UCB** = -μ + β(t)·σ
   (minimization form: exploit term -μ, explore term βσ).
   Take the top-k as exploration compositions.
4. **Exploit pool**: the planner's incoming compositions, kept as-is.
5. **Annealing**: exploration share α(t) = α₀ · (remaining/B)^γ
   (defaults α₀=0.5, γ=1). Early in the episode ~half the plan is exploration;
   as the budget drains the plan converges to pure exploitation of the best
   regions. β(t) follows the same schedule (β = β₀ · (remaining/B)^γ).
6. **Plan assembly**: `compositions = exploit[:m_e] + explore[:m_x]` with
   m_x = round(α(t) · len(plan.compositions)); `num_candidates` left to M1's cap.
   Composition cap is applied before M1's, so the hook is always budget-safe.
7. **Determinism**: all sampling seeded from `experiment.seed`; tie-breaks by
   sorted formula string.

## Failure-mode instrumentation (feeds M4's evidence log)

Every `adjust_plan` call appends one JSON-serializable decision record to
`self.decision_log` (also exported via `get_state()` for checkpointing):

```
step, m1_queries_remaining, mode (explore|exploit|mixed),
incoming_compositions, outgoing_compositions, composition_source
(planner|ucb_explore), ucb_mean, ucb_std, beta, alpha_t, rationale (short string)
```

This is exactly the data the two required failure trajectories need:
- **Over-exploitation**: many consecutive steps with mode=exploit, compositions
  clustered around one formula, no new stable finds.
- **Wasteful exploration**: high α with UCB picks that repeatedly return
  unstable outcomes.

## Ablation

`enable_exploration: false` → plan passes through untouched (already covered by
M1's contract test). ON vs OFF at identical seeds/budgets is the ablation pair.

## Open questions for M1 (20 Oct)

1. Protocol v1 fixes B=20 — is this final, or pending TA confirmation?
2. May `plan.constraints` carry generator hints (e.g. preferred spacegroups), or
   do the configured generators ignore it? (Affects how much the explore pool can
   steer structure generation vs only composition choice.)

## Resolved (20 Oct)

3. ~~`m1_memory` contents under M4's memory_manager~~ — **Confirmed: M4's
   records are served, and they include `e_above_hull`** (M4's
   `OBSERVATION_FIELDS` exposes it). GP training inputs are complete under
   `m1_full`. One caveat found while verifying: M4's manager bounds the window
   to `limit` (default 8) records, so the policy now keeps its own cumulative
   `_queried_history` so nothing re-enters the explore pool when records age
   out of the window (commit `bc97609`).

## Dependencies

- numpy only (GP regression implemented directly); no new heavy dependencies.
- M4 log format: confirmation sent separately (M5/M4_LOG_CONFIRMATION.md).
