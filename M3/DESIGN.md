# M3 one-page design: planning and self-correction

Agreed with M1. The interface is M1's existing plug-in contract
(`M1/PLUGIN_INTERFACE.md`); nothing in MADE's runner, oracle, evaluator,
environment or budget logic changes.

## Goal

Spend a fixed oracle budget (20 queries per episode in protocol v1) where new
stable phases are most likely, and stop wasting queries when the search stalls.

## Slot 1: planner (`enable_planning`)

`M3ResearchPlanner` implements MADE's `Planner` interface
(`propose(state, previous) -> Plan`, `update_state`, `get_state`, `load_state`).

| Step | What happens |
| --- | --- |
| Plan | Split the chemical system into sub-goals, one per element subset. A ternary A-B-C has four: A-B, A-C, B-C and A-B-C. |
| Propose batch | For `batch_size` (4) queries, target one sub-goal. Pick its least-attempted composition that is farthest from anything already tried. Only SMACT-valid compositions are considered. |
| Review | Re-score every open sub-goal: `(successes + new_in_memory + 0.5·near_hull_in_memory + 1) / (attempts + 2) + 0.5 · unexplored_share`. |
| Update plan | The best-scoring sub-goal becomes the next batch target. Ties are broken by a seeded random choice. |

Here `successes` counts the planner's own stable results. Memory (M4): the
review reads `context["m1_memory"]`. New stable phases and other near-hull
results (≤ 0.1 eV/atom) in memory raise a sub-goal's score. Formulas that
memory shows as unstable twice are skipped. With memory off, the list is empty and
only the planner's own counts are used.

## Slot 2: self-correction (`enable_reflection`)

`M3StuckReplanPolicy.revise_plan(plan, context) -> Plan` runs after the planner.

- **Stuck if**, over the last K = 6 observed queries:
  - there was no new stable phase (`no_progress`; MADE's "newly discovered"
    mark alone does not count, because it is set for unstable structures
    too); or
  - the plan targets a formula already tried twice (`repetition`).
- **Re-plan**: replace the plan with valid compositions that are the least
  visited and farthest from the recent window.
- **Escalate**: repeated stalls double the candidates per composition.
  Generation is not an oracle query, and M1 still caps the plan.
- **Guards**: a 3-query cooldown between re-plans; any new stable phase resets
  the escalation level.

## Rules kept

- **Inputs:** only the public MADE state and post-query observations. Never
  `phase_diagram_gt`, hidden labels or evaluator state, and no oracle calls.
- **Budget:** respects `context["m1_queries_remaining"]`. M1 applies the final
  cap, and one `env.step()` is one query.
- **Determinism:** randomness is seeded from `(experiment.seed, step)`. All
  state is JSON, so checkpoints resume exactly.
- **Cost:** no LLM, so no API key or token cost.

## Configuration

- `agent/planner=m3_research` selects the planner. M1's default stays
  `diversity`, so `m1_baseline` runs remain comparable.
- `self_correction_policy: m3_stuck_replan` is wired into `m1_integrated.yaml`
  and runs only when `enable_reflection=true`.

## Evaluation

All runs use the dev systems × seeds 17/29/43, paired by system and seed.

- **Full-agent ablations** (M3's assigned ablations), against M1's frozen
  `m1_full`: `planning_off` and `self_correction_off`, each with one M3 part
  off and memory, exploration and tool routing on.
- **Component study**, against M1's reference `m1_baseline`, with exploration
  and tool routing off: `m3_full` (both M3 parts on), `m3_planning_off` and
  `m3_self_correction_off`.
