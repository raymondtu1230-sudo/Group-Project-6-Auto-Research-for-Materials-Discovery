# A1 Speaker Notes

Target length: about two minutes across the two slides.

## Slide 1: Integrated agent architecture

M1’s contribution is the integration boundary that lets the group’s research components work together inside MADE’s normal agent contract. MADE provides the current environment state and the feedback from previously queried structures. The planner proposes where to search. A3’s self-correction hook can revise a plan when the run stalls, and A5’s exploration hook can adjust which compositions the plan covers. A2’s router chooses a configured generator. The existing workflow then generates candidates, applies the validity filter, scores the survivors, and returns one selected structure for the environment to evaluate.

Each component has its own configuration switch, so the team can disable one part while keeping the rest of a comparison fixed. Stateful components can also save and restore their state through MADE’s checkpoint mechanism. M4’s memory summarizes observed outcomes for later decisions. The key boundary is that every proposal uses public state and observed feedback only. The runner, oracle, and evaluator stay unchanged, and hidden ground truth never guides the search.

## Slide 2: Query budget, checkpointing, and evidence

For protocol v1, the team set a budget of twenty oracle queries per episode. That is our agreed experimental setting, not a value I am attributing to the teaching team. The environment enforces the limit and ends the episode when the budget is used. M1 exposes the remaining-query count to the policy hooks and caps candidate generation accordingly. Generating candidates does not consume oracle calls; one call to `env.step()` evaluates exactly one selected structure.

The frozen release is `m1-freeze-20261025`. Its protocol uses the ORB v3 conservative model on CPU, seeds 17, 29, and 43, and six public development systems. Checkpoints preserve the agent and the stateful components, while each run records its resolved configuration, system, seed, trajectory, metrics, cost fields, wall time, and machine. Those records let us reproduce and audit the comparison. We keep oracle-query count, model or API cost, and elapsed time separate because they measure different resources.

## Sources

- `M1/PLUGIN_INTERFACE.md` and `M1/INTEGRATION.md` - component contract, switches, state, budget behavior, and observed-feedback boundary.
- `M1/protocol/protocol_v1.yaml` and `M1/EXPERIMENT_PROTOCOL.md` - protocol-v1 settings and metric definitions.
- `M1/FREEZE_RECORD.md` - frozen tag, acceptance canary, and development reference status.
- `M1/REPRODUCE.md` - run metadata, cost fields, and reproduction workflow.
