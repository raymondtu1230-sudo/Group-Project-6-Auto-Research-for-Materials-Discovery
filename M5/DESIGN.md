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

## Open questions — all resolved (20 Oct, M1 answers)

1. ~~B=20 final?~~ — **Resolved: B=20 is M1's protocol-v1 team choice**, not a
   TA-mandated value. Applied consistently across methods; any future course
   conflict becomes a versioned protocol amendment. The annealing denominator
   is stable.
2. ~~Does `plan.constraints` reach the generator?~~ — **Resolved: the Plan
   (including constraints) is passed to `generator.generate(plan, context)`,
   but the built-in Random and Chemeleon generators do not consume
   `plan.constraints`.** Composition steering through `plan.compositions` is
   the only effective lever — which is exactly what this policy uses.
3. ~~`e_above_hull` availability under M4 memory~~ — **Resolved (confirmed by
   M1)**: M4's adapter allowlists `e_above_hull`, the ConvexHull observation
   includes it, and records are exposed via `context["m1_memory"]` to the next
   policy decision. GP training inputs are complete under `m1_full`.

## Dependencies

- numpy only (GP regression implemented directly); no new heavy dependencies.
- M4 log format: confirmation sent separately (M5/M4_LOG_CONFIRMATION.md).
