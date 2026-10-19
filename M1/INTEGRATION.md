# M1 Integration Contract

The detailed handoff specification is [PLUGIN_INTERFACE.md](PLUGIN_INTERFACE.md).
Use it for exact method signatures, context fields, Hydra names, and tests.

All M1-created project files, configurations, logs, and run instructions live under this directory. The official MADE checkout is `M1/MADE`.

## Agent contract

`made.agents.m1_integrated.M1IntegratedAgent` follows MADE's normal `Agent(state) -> (Composition, Structure)` contract and is loaded with `agent=m1_integrated`.

The Hydra switches are:

| Switch | Owner | Enabled behavior | Disabled behavior |
| --- | --- | --- | --- |
| `enable_planning` | M3 | Calls the configured MADE planner | Uses a deterministic composition made from the current system's elements |
| `enable_memory` | M4 | Updates the configured `memory_manager` and passes its summary as `m1_memory`; without one, uses M1's bounded observed-outcome memory | Clears/omits the memory summary |
| `enable_reflection` | M3 | Calls optional `self_correction_policy.revise_plan(plan, context)` hook | Leaves the plan unchanged after planning |
| `enable_exploration` | M5 | Calls the optional `exploration_policy.adjust_plan(plan, context)` hook | Uses the planner's plan unchanged |
| `enable_tool_routing` | M2 | Calls optional `tool_router.select_generator(context, generators)` | Always uses the primary `generator` |

The standalone M1 baseline enables planning and bounded memory. Reflection, exploration, and tool routing default off because their owners' components are optional; enabling any such switch without configuring its component fails fast. For a meaningful ablation, keep all run settings fixed and change exactly one switch. The current default generator, filter, and scorer are MADE's random generator, SMACT validity filter, and random selector.

M4's optional `memory_manager` implements `update_state(state)`, `get_memory() -> list[dict]`, `get_state()`, and `load_state(state)`. The state passed to it contains the observed environment state, not hidden ground truth. M2's router must return a configured generator name or object. M3's optional `self_correction_policy` implements `revise_plan(plan, context) -> Plan`. M5's policy implements `adjust_plan(plan, context) -> Plan`. These hooks may implement `get_state()` and `load_state(state)` for checkpointing. Optional generators are configured as a Hydra mapping under `generators`.

`query_budget` defaults to `${environment.budget}` because MADE's environment is the authoritative query-budget enforcer. Keep any explicit override equal to `environment.budget`; the agent uses it to expose remaining budget to hooks and cap candidates generated for one proposal. Candidate generation is not itself an oracle query. One call to `env.step()` evaluates exactly one selected structure, and MADE stops the episode at the environment budget.

Turning off M4 memory disables only the M1/M4 memory enhancement. The agent still receives the current MADE state and last oracle feedback as required by the benchmark protocol.

## Handover checklist

- M2-M5 should deliver an importable component, its Hydra config/example, a short interface description, and a minimal test by 24 Oct.
- Run `python -m pytest tests/test_m1_integrated.py` and `python ../run_smoke_test.py` from `M1/MADE` before handing off or changing a hook.
- The protocol driver is `python ../run_experiment.py`; it records metadata and fails if an enabled optional hook is missing. Validate completed sweeps with `python ../validate_protocol_results.py --split dev` or `--split check`.
- Keep all proposal selection based only on current environment state and prior queried observations. Do not read hidden ground truth, modify the oracle/evaluator, or log credentials.
- Before the 25 Oct freeze, run the focused tests and one complete official episode with the agreed development configuration.

## Plug-in acceptance checks

- M2 router: returns a configured generator key (preferred) or that exact generator instance; test enabled selection and disabled primary-generator fallback.
- M3 planner: implements MADE `Planner.propose(state, previous) -> Plan`, `update_state`, `get_state`, and `load_state`; check that a plan is returned when enabled and the fallback composition works when disabled.
- M3 self-correction: implements `revise_plan(plan, context) -> Plan`; test enabled plan revision and disabled pass-through.
- M4 memory: implements `update_state`, `get_memory -> list[dict]`, `get_state`, and `load_state`; test that only observed feedback is used and that disabled memory is not passed to the planner.
- M5 exploration: implements `adjust_plan(plan, context) -> Plan`; test both enabled transformation and disabled pass-through, including the remaining-query context.
- Every stateful plug-in should round-trip through checkpoint state. Plug-in tests should use fake MADE state and must not require an oracle/API key.
