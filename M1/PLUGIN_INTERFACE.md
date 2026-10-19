# M1 Plug-in Interface Specification

This is the hand-off contract for M2, M3, M4, and M5. Plug-ins are optional
components of `made.agents.m1_integrated.M1IntegratedAgent`; they must not
modify the official oracle, evaluator, or environment budget logic.

## Integration Boundary

MADE calls the agent as:

```python
composition, structure = agent(state)
```

One returned structure is evaluated by one `env.step()` call, which is one
oracle query. Plug-ins may propose, transform, route, or rank candidates, but
must not call the oracle, access `phase_diagram_gt`, inspect held-out labels, or
read evaluator-only state.

The call order is:

```text
update_state(state)
  -> context and bounded memory
  -> planner.propose(...)
  -> self_correction_policy.revise_plan(...)  [optional]
  -> exploration_policy.adjust_plan(...)      [optional]
  -> M1 budget cap
  -> tool_router.select_generator(...)        [optional]
  -> generator.generate(plan, context)
  -> filter.filter(candidates, context)
  -> scorer.select(candidates, context)
  -> return one Composition and Structure
```

A plug-in is called only when its switch is enabled. Disabling one switch must
leave all other components and protocol settings unchanged.

## Context Contract

Hooks receive a `dict[str, Any]`. Stable fields are:

| Field | Meaning |
| --- | --- |
| `elements` | Elements in the current chemical system |
| `max_stoichiometry` | Maximum allowed atoms in a composition |
| `stability_tolerance` | Stability threshold in eV/atom |
| `query_count` | Oracle queries already used |
| `m1_queries_used` | M1 alias of `query_count` |
| `m1_queries_remaining` | Remaining budget, clamped at zero |
| `last_observation` | Most recent post-query observation, if present |
| `m1_memory` | Bounded observed-outcome records, or `[]` when memory is off |
| other MADE state | Existing public state fields supplied by the runner |

Treat unknown fields as optional and do not mutate the input context. Typical
observation fields include `reduced_formula`, energy values, `e_above_hull`,
`is_stable`, and `is_newly_discovered`. These are post-query observations, not
hidden ground truth.

## Plug-in Interfaces

### M3 planner

Use the normal MADE `Planner` interface:

```python
class Planner:
    def propose(self, state: dict[str, Any], previous: dict[str, Any] | None = None) -> Plan: ...
    def update_state(self, state: dict[str, Any]) -> None: ...
    def get_state(self) -> dict[str, Any]: ...
    def load_state(self, state: dict[str, Any]) -> None: ...
```

Return a MADE `Plan`, not a dict. `Plan.compositions` contains pymatgen
`Composition` objects and `Plan.num_candidates` is the number per composition.
M1 applies the final budget cap after reflection and exploration.

### M3 self-correction / reflection

```python
class SelfCorrectionPolicy:
    def revise_plan(self, plan: Plan, context: dict[str, Any]) -> Plan: ...
```

Return a MADE `Plan`. This hook runs after planning and before exploration.

### M4 memory

```python
class MemoryManager:
    def update_state(self, state: dict[str, Any]) -> None: ...
    def get_memory(self) -> list[dict[str, Any]]: ...
    def get_state(self) -> dict[str, Any]: ...
    def load_state(self, state: dict[str, Any]) -> None: ...
```

`get_memory()` must always return a bounded list of JSON-serializable records.
Do not store `phase_diagram_gt`, evaluator state, API keys, or hidden labels.

### M5 exploration

```python
class ExplorationPolicy:
    def adjust_plan(self, plan: Plan, context: dict[str, Any]) -> Plan: ...
```

Use `context["m1_queries_remaining"]`; return a MADE `Plan`. M1 caps the plan
after this hook, so the policy cannot bypass the budget.

### M2 tool router

```python
class ToolRouter:
    def select_generator(self, context: dict[str, Any], generators: dict[str, Generator]) -> str | Generator: ...
```

Return a configured generator name (preferred) or the exact configured object.
Unknown names and unrelated objects are errors. At least one additional
generator besides `default` is required when routing is enabled. Each routed
generator must implement `generate`, `update_state`, `get_state`, and
`load_state`.

## Hydra Configuration

Use `configs/agent/m1_integrated.yaml` and keep these field names:

```yaml
enable_planning: true
enable_memory: true
enable_reflection: false
enable_exploration: false
enable_tool_routing: false
memory_manager: null
self_correction_policy: null
exploration_policy: null
tool_router: null
generators: {}
```

An enabled optional hook without its component must fail fast. This prevents a
silent no-op from being reported as a completed ablation or full method.

## Independent Switch Tests

From `M1/MADE`, run the contract suite without an API key:

```bash
uv run pytest -q tests/test_m1_integrated.py
```

The suite verifies planning, memory, reflection, exploration, routing, missing
component failures, budget caps, checkpoint round-trips, invalid outputs, and
exhausted-budget behavior. Each contributor must add at least one fake-component
test for their own behavior, asserting both enabled and disabled paths. Tests
must use synthetic state and structures and must not require an API key.

Run the focused checks before handoff:

```bash
uv run pytest -q tests/test_m1_integrated.py
uv run ruff check src/made/agents/<your_module>.py tests/<your_test>.py
uv run python ../run_smoke_test.py
```

## Handoff Checklist

Submit an importable implementation, Hydra config, short design note, enabled
and disabled tests, JSON-serializable checkpoint state for stateful components,
and passing test output. Do not submit credentials, hidden labels, evaluator
state, or oracle changes. M1 will integrate the component, run the full suite,
and execute one official protocol unit before freezing the reference revision.
