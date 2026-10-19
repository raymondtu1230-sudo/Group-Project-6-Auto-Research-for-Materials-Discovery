"""M1 integration agent with checkpointable research-policy plug-in slots."""

from __future__ import annotations

from typing import Any

from pymatgen.core.composition import Composition
from pymatgen.core.structure import Structure

from made.agents.base import Plan, WorkflowAgent


class M1IntegratedAgent(WorkflowAgent):
    """Compose MADE components with independent switches for team ablations.

    Optional ``exploration_policy`` objects implement ``adjust_plan(plan,
    context)``. Optional ``tool_router`` objects implement
    ``select_generator(context, generators)`` and return a generator name or
    generator instance. Optional ``self_correction_policy`` objects implement
    ``revise_plan(plan, context)``. These narrow hooks let M2/M3/M5 contribute
    without changing the MADE runner contract.
    """

    def __init__(
        self,
        planner: Any,
        generator: Any,
        scorer: Any,
        filter: Any,
        enable_planning: bool = True,
        enable_memory: bool = True,
        enable_reflection: bool = False,
        enable_exploration: bool = False,
        enable_tool_routing: bool = False,
        query_budget: int | None = None,
        memory_size: int = 20,
        generators: dict[str, Any] | None = None,
        memory_manager: Any | None = None,
        self_correction_policy: Any | None = None,
        exploration_policy: Any | None = None,
        tool_router: Any | None = None,
    ) -> None:
        super().__init__(
            planner=planner, generator=generator, scorer=scorer, filter=filter
        )
        if query_budget is not None and query_budget < 1:
            raise ValueError("query_budget must be positive when supplied")
        if memory_size < 1:
            raise ValueError("memory_size must be positive")
        for enabled, component, label in (
            (enable_reflection, self_correction_policy, "self_correction_policy"),
            (enable_exploration, exploration_policy, "exploration_policy"),
            (enable_tool_routing, tool_router, "tool_router"),
        ):
            if enabled and component is None:
                raise ValueError(f"{label} must be configured when its switch is on")
        if enable_tool_routing and len(generators or {}) < 1:
            raise ValueError(
                "at least one additional generator is required when tool routing is on"
            )

        self.enable_planning = enable_planning
        self.enable_memory = enable_memory
        self.enable_reflection = enable_reflection
        self.enable_exploration = enable_exploration
        self.enable_tool_routing = enable_tool_routing
        self.query_budget = query_budget
        self.memory_size = memory_size
        self.generators = dict(generators or {})
        self.generators.setdefault("default", generator)
        self.memory_manager = memory_manager
        self.self_correction_policy = self_correction_policy
        self.exploration_policy = exploration_policy
        self.tool_router = tool_router
        self.memory: list[dict[str, Any]] = []
        self.last_generator_name = "default"

    def _context(self, state: dict[str, Any]) -> dict[str, Any]:
        context = dict(state)
        context["m1_memory"] = self._memory_context()
        query_count = int(state.get("query_count", 0))
        context["m1_queries_used"] = query_count
        context["m1_queries_remaining"] = (
            max(self.query_budget - query_count, 0)
            if self.query_budget is not None
            else None
        )
        return context

    def _memory_context(self) -> list[dict[str, Any]]:
        if not self.enable_memory:
            return []
        if self.memory_manager is not None:
            memory = self.memory_manager.get_memory()
            if not isinstance(memory, list):
                raise TypeError("memory_manager.get_memory must return a list")
            return memory
        return list(self.memory)

    @staticmethod
    def _memory_record(observation: dict[str, Any], query_count: int) -> dict[str, Any]:
        # Keep only post-query evidence exposed by MADE; never persist hidden truth.
        keys = (
            "reduced_formula",
            "formation_energy_per_atom",
            "energy_per_atom",
            "e_above_hull",
            "is_stable",
            "is_newly_discovered",
        )
        record = {key: observation[key] for key in keys if key in observation}
        record["query_count"] = query_count
        return record

    def update_state(self, state: dict[str, Any]) -> None:
        action = self._update_last_step(state)
        if action == "skip":
            return

        observation = state.get("last_observation")
        if self.enable_memory and self.memory_manager is not None:
            self.memory_manager.update_state(state)
        elif self.enable_memory and observation:
            self.memory.append(
                self._memory_record(observation, int(state.get("query_count", 0)))
            )
            self.memory = self.memory[-self.memory_size :]

        context = self._context(state)
        self.planner.update_state(context)
        self.generator.update_state(context)
        self.filter.update_state(context)
        self.scorer.update_state(context)
        for generator in self.generators.values():
            if generator is not self.generator:
                generator.update_state(context)

    def _plan(self, context: dict[str, Any]) -> Plan:
        if self.enable_planning:
            previous = (
                {"observations": self._memory_context()} if self.enable_memory else None
            )
            plan = self.planner.propose(context, previous=previous)
        else:
            elements = context.get("elements", [])
            if not elements:
                raise ValueError(
                    "MADE state must include elements when planning is disabled"
                )
            plan = Plan(
                compositions=[Composition(dict.fromkeys(elements, 1))], num_candidates=1
            )

        if self.enable_reflection and self.self_correction_policy is not None:
            plan = self.self_correction_policy.revise_plan(plan, context)
            if not isinstance(plan, Plan):
                raise TypeError(
                    "self_correction_policy.revise_plan must return a MADE Plan"
                )

        if self.enable_exploration and self.exploration_policy is not None:
            plan = self.exploration_policy.adjust_plan(plan, context)
            if not isinstance(plan, Plan):
                raise TypeError(
                    "exploration_policy.adjust_plan must return a MADE Plan"
                )

        remaining = context["m1_queries_remaining"]
        if remaining is not None:
            if remaining <= 0:
                raise RuntimeError(
                    "Agent called after its configured query budget was exhausted"
                )
            if len(plan.compositions) > remaining:
                plan.compositions = plan.compositions[:remaining]
            compositions_per_plan = max(len(plan.compositions), 1)
            candidates_per_composition = max(remaining // compositions_per_plan, 1)
            plan.num_candidates = min(
                max(int(plan.num_candidates), 1), candidates_per_composition
            )
        return plan

    def _generator_for(self, context: dict[str, Any]) -> Any:
        if not self.enable_tool_routing or self.tool_router is None:
            self.last_generator_name = "default"
            return self.generator
        selected = self.tool_router.select_generator(context, self.generators)
        if isinstance(selected, str):
            if selected not in self.generators:
                raise ValueError(f"tool_router selected unknown generator: {selected}")
            self.last_generator_name = selected
            return self.generators[selected]
        for name, generator in self.generators.items():
            if selected is generator:
                self.last_generator_name = name
                return generator
        raise ValueError(
            "tool_router must return a configured generator name or instance"
        )

    def propose_composition_and_structure(
        self, state: dict[str, Any]
    ) -> tuple[Composition, Structure]:
        context = self._context(state)
        plan = self._plan(context)
        candidates = self._generator_for(context).generate(plan, context)
        if not candidates:
            raise RuntimeError("No candidate structures generated")

        filtered = self.filter.filter(candidates, context)
        if not filtered:
            filtered = candidates
        selected = self.scorer.select(filtered, context)
        return selected.composition, selected

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state.update(
            {
                "m1_memory": self.memory,
                "memory_manager": self._component_state(self.memory_manager),
                "self_correction_policy": self._component_state(
                    self.self_correction_policy
                ),
                "last_generator_name": self.last_generator_name,
                "exploration_policy": self._component_state(self.exploration_policy),
                "tool_router": self._component_state(self.tool_router),
            }
        )
        for name, generator in self.generators.items():
            if generator is not self.generator:
                state.setdefault("generators", {})[name] = generator.get_state()
        return state

    def load_state(self, state: dict[str, Any]) -> None:
        super().load_state(state)
        self.memory = list(state.get("m1_memory", []))[-self.memory_size :]
        self.last_generator_name = state.get("last_generator_name", "default")
        self._load_component_state(self.memory_manager, state.get("memory_manager"))
        self._load_component_state(
            self.self_correction_policy, state.get("self_correction_policy")
        )
        self._load_component_state(
            self.exploration_policy, state.get("exploration_policy")
        )
        self._load_component_state(self.tool_router, state.get("tool_router"))
        for name, component_state in state.get("generators", {}).items():
            if name in self.generators and self.generators[name] is not self.generator:
                self.generators[name].load_state(component_state)

    @staticmethod
    def _component_state(component: Any | None) -> dict[str, Any] | None:
        if component is None or not hasattr(component, "get_state"):
            return None
        return component.get_state()

    @staticmethod
    def _load_component_state(
        component: Any | None, state: dict[str, Any] | None
    ) -> None:
        if (
            component is not None
            and state is not None
            and hasattr(component, "load_state")
        ):
            component.load_state(state)
