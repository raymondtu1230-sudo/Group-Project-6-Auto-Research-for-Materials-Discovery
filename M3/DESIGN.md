# M3 one-page design: planning and self-correction

For M1 sign-off (19–20 Oct). The interface is M1's existing plug-in contract
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

Memory (M4): the review reads `context["m1_memory"]`. New phases and near-hull
results (≤ 0.1 eV/atom) in memory raise a sub-goal's score. Formulas that
memory shows failing twice are skipped. With memory off, the list is empty and
only the planner's own counts are used.

## Slot 2: self-correction (`enable_reflection`)

`M3StuckReplanPolicy.revise_plan(plan, context) -> Plan` runs after the planner.

- **Stuck if**, over the last K = 6 observed queries:
  - there was no new phase (`no_progress`); or
  - the plan targets a formula already tried twice (`repetition`).
- **Re-plan**: replace the plan with valid compositions that are the least
  visited and farthest from the recent window.
- **Escalate**: repeated stalls double the candidates per composition.
  Generation is not an oracle query, and M1 still caps the plan.
- **Guards**: a 3-query cooldown between re-plans; any discovery resets the
  escalation level.

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

## Evaluation (26–27 Oct)

All runs use the dev systems × seeds 17/29/43, compared with M1's reference:

- `m3_full`: M3 planner and self-correction on.
- `m3_planning_off`: planning off.
- `m3_self_correction_off`: self-correction off.
