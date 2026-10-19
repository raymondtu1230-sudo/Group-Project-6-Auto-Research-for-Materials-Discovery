from __future__ import annotations

from typing import Any

from pymatgen.core.composition import Composition
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure

from made.agents.base import (
    Filter,
    FilterResult,
    Generator,
    Plan,
    Planner,
    Scorer,
    ScoreResult,
)
from made.agents.m1_integrated import M1IntegratedAgent


def sample_structure() -> Structure:
    return Structure(Lattice.cubic(4), ["Li", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])


class FakePlanner(Planner):
    def __init__(self) -> None:
        self.proposals = 0
        self.previous: dict[str, Any] | None = None
        self.plan = Plan(compositions=[Composition("LiO")], num_candidates=9)

    def propose(
        self, state: dict[str, Any], previous: dict[str, Any] | None = None
    ) -> Plan:
        self.proposals += 1
        self.previous = previous
        return self.plan

    def get_state(self) -> dict[str, Any]:
        return {"proposals": self.proposals}

    def load_state(self, state: dict[str, Any]) -> None:
        self.proposals = state.get("proposals", 0)

    def update_state(self, state: dict[str, Any]) -> None:
        pass


class FakeGenerator(Generator):
    def __init__(self) -> None:
        self.generated = 0
        self.last_plan: Plan | None = None

    def generate(self, plan: Plan, state: dict[str, Any]) -> list[Structure]:
        self.last_plan = plan
        self.generated += 1
        return [sample_structure() for _ in range(plan.num_candidates)]

    def get_state(self) -> dict[str, Any]:
        return {"generated": self.generated}

    def load_state(self, state: dict[str, Any]) -> None:
        self.generated = state.get("generated", 0)

    def update_state(self, state: dict[str, Any]) -> None:
        pass


class FakeFilter(Filter):
    def _filter_with_results(
        self, candidates: list[Structure], state: dict[str, Any]
    ) -> tuple[list[Structure], list[FilterResult]]:
        return candidates, [
            FilterResult(passed=True, filter_name="fake") for _ in candidates
        ]

    def get_state(self) -> dict[str, Any]:
        return {}

    def load_state(self, state: dict[str, Any]) -> None:
        pass

    def update_state(self, state: dict[str, Any]) -> None:
        pass


class FakeScorer(Scorer):
    def _score_with_results(
        self, candidates: list[Structure], state: dict[str, Any]
    ) -> tuple[list[float], list[ScoreResult]]:
        scores = [float(index) for index, _ in enumerate(candidates)]
        return scores, [
            ScoreResult(score=score, scorer_name="fake") for score in scores
        ]

    def get_state(self) -> dict[str, Any]:
        return {}

    def load_state(self, state: dict[str, Any]) -> None:
        pass

    def update_state(self, state: dict[str, Any]) -> None:
        pass


class FakeRouter:
    def __init__(self, name: str) -> None:
        self.name = name

    def select_generator(
        self, context: dict[str, Any], generators: dict[str, Any]
    ) -> str:
        return self.name


class FakeExplorationPolicy:
    def __init__(self) -> None:
        self.calls = 0

    def adjust_plan(self, plan: Plan, context: dict[str, Any]) -> Plan:
        self.calls += 1
        assert context["m1_queries_remaining"] == 2
        return Plan(compositions=plan.compositions, num_candidates=1)


class FakeSelfCorrectionPolicy:
    def __init__(self) -> None:
        self.calls = 0

    def revise_plan(self, plan: Plan, context: dict[str, Any]) -> Plan:
        self.calls += 1
        assert context["m1_queries_remaining"] == 2
        return Plan(compositions=plan.compositions, num_candidates=2)


class FakeMemoryManager:
    def __init__(self) -> None:
        self.observations: list[dict[str, Any]] = []

    def update_state(self, state: dict[str, Any]) -> None:
        observation = state.get("last_observation")
        if observation:
            self.observations.append({"formula": observation["reduced_formula"]})

    def get_memory(self) -> list[dict[str, Any]]:
        return list(self.observations)

    def get_state(self) -> dict[str, Any]:
        return {"observations": self.observations}

    def load_state(self, state: dict[str, Any]) -> None:
        self.observations = list(state.get("observations", []))


def make_agent(**kwargs: Any) -> tuple[M1IntegratedAgent, FakePlanner, FakeGenerator]:
    planner = FakePlanner()
    generator = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=planner,
        generator=generator,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        **kwargs,
    )
    return agent, planner, generator


def test_budget_caps_candidates_and_memory_is_checkpointed() -> None:
    agent, _, generator = make_agent(query_budget=2)
    state = {
        "query_count": 1,
        "elements": ["Li", "O"],
        "last_observation": {
            "reduced_formula": "LiO",
            "is_stable": True,
            "is_newly_discovered": True,
            "ground_truth_label": "must not be persisted",
        },
    }

    composition, structure = agent(state)

    assert composition == structure.composition
    assert generator.last_plan is not None
    assert generator.last_plan.num_candidates == 1
    assert agent.memory == [
        {
            "reduced_formula": "LiO",
            "is_stable": True,
            "is_newly_discovered": True,
            "query_count": 1,
        }
    ]
    assert "ground_truth_label" not in str(agent.get_state())

    restored, _, _ = make_agent(query_budget=2)
    restored.load_state(agent.get_state())
    assert restored.memory == agent.memory


def test_budget_caps_total_candidates_for_multi_composition_plan() -> None:
    agent, planner, generator = make_agent(query_budget=2)
    planner.plan = Plan(
        compositions=[Composition("LiO"), Composition("Li2O"), Composition("LiO2")],
        num_candidates=4,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert generator.last_plan is not None
    assert len(generator.last_plan.compositions) == 2
    assert generator.last_plan.num_candidates == 1
    assert (
        generator.last_plan.num_candidates * len(generator.last_plan.compositions) <= 2
    )


def test_planning_ablation_uses_system_elements_without_planner() -> None:
    agent, planner, generator = make_agent(enable_planning=False)

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert planner.proposals == 0
    assert generator.last_plan is not None
    assert generator.last_plan.compositions == [Composition("LiO")]


def test_tool_router_is_only_called_when_enabled() -> None:
    primary = FakeGenerator()
    alternate = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=FakePlanner(),
        generator=primary,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        generators={"alternate": alternate},
        tool_router=FakeRouter("alternate"),
        enable_tool_routing=True,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert primary.generated == 0
    assert alternate.generated == 1
    assert agent.last_generator_name == "alternate"


def test_tool_routing_requires_an_alternative_generator() -> None:
    try:
        make_agent(enable_tool_routing=True, tool_router=FakeRouter("default"))
    except ValueError as error:
        assert "additional generator" in str(error)
    else:
        raise AssertionError("Expected tool routing without alternatives to fail")


def test_disabled_tool_routing_uses_primary_generator() -> None:
    primary = FakeGenerator()
    alternate = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=FakePlanner(),
        generator=primary,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        generators={"alternate": alternate},
        tool_router=FakeRouter("alternate"),
        enable_tool_routing=False,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert primary.generated == 1
    assert alternate.generated == 0


def test_exploration_hook_is_opt_in_and_receives_budget_context() -> None:
    policy = FakeExplorationPolicy()
    agent, _, generator = make_agent(
        query_budget=2,
        enable_exploration=True,
        exploration_policy=policy,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert policy.calls == 1
    assert generator.last_plan is not None
    assert generator.last_plan.num_candidates == 1


def test_exploration_hook_is_not_called_when_disabled() -> None:
    policy = FakeExplorationPolicy()
    agent, _, _ = make_agent(
        enable_exploration=False,
        exploration_policy=policy,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert policy.calls == 0


def test_missing_optional_hooks_default_to_inactive() -> None:
    agent, _, _ = make_agent()

    assert agent.enable_exploration is False
    assert agent.enable_reflection is False
    assert agent.enable_tool_routing is False


def test_enabling_unconfigured_optional_hook_fails_fast() -> None:
    for flag in ("enable_reflection", "enable_exploration", "enable_tool_routing"):
        try:
            make_agent(**{flag: True})
        except ValueError as error:
            assert "must be configured" in str(error)
        else:
            raise AssertionError(f"Expected missing {flag} hook to fail fast")


def test_reflection_hook_is_opt_in_and_receives_budget_context() -> None:
    policy = FakeSelfCorrectionPolicy()
    agent, _, generator = make_agent(
        query_budget=2,
        enable_reflection=True,
        self_correction_policy=policy,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert policy.calls == 1
    assert generator.last_plan is not None
    assert generator.last_plan.num_candidates == 2


def test_reflection_hook_is_not_called_when_disabled() -> None:
    policy = FakeSelfCorrectionPolicy()
    agent, _, _ = make_agent(
        enable_reflection=False,
        self_correction_policy=policy,
    )

    agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})

    assert policy.calls == 0


def test_invalid_reflection_output_is_rejected() -> None:
    class InvalidPolicy:
        def revise_plan(self, plan: Plan, context: dict[str, Any]) -> str:
            return "not a Plan"

    agent, _, _ = make_agent(
        enable_reflection=True,
        self_correction_policy=InvalidPolicy(),
    )

    try:
        agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})
    except TypeError as error:
        assert "must return a MADE Plan" in str(error)
    else:
        raise AssertionError("Expected invalid reflection output to be rejected")


def test_invalid_exploration_output_is_rejected() -> None:
    class InvalidPolicy:
        def adjust_plan(self, plan: Plan, context: dict[str, Any]) -> str:
            return "not a Plan"

    agent, _, _ = make_agent(
        enable_exploration=True, exploration_policy=InvalidPolicy()
    )

    try:
        agent({"query_count": 0, "elements": ["Li", "O"], "last_observation": None})
    except TypeError as error:
        assert "must return a MADE Plan" in str(error)
    else:
        raise AssertionError("Expected invalid exploration output to be rejected")


def test_query_budget_exhaustion_is_rejected() -> None:
    agent, _, _ = make_agent(query_budget=1)

    try:
        agent({"query_count": 1, "elements": ["Li", "O"], "last_observation": None})
    except RuntimeError as error:
        assert "budget was exhausted" in str(error)
    else:
        raise AssertionError("Expected exhausted query budget to be rejected")


def test_memory_manager_hook_updates_and_restores() -> None:
    memory_manager = FakeMemoryManager()
    planner = FakePlanner()
    generator = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=planner,
        generator=generator,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        memory_manager=memory_manager,
    )

    agent(
        {
            "query_count": 1,
            "elements": ["Li", "O"],
            "last_observation": {"reduced_formula": "LiO"},
        }
    )

    assert planner.previous == {"observations": [{"formula": "LiO"}]}
    restored_memory = FakeMemoryManager()
    restored = M1IntegratedAgent(
        planner=FakePlanner(),
        generator=FakeGenerator(),
        scorer=FakeScorer(),
        filter=FakeFilter(),
        memory_manager=restored_memory,
    )
    restored.load_state(agent.get_state())
    assert restored_memory.get_memory() == [{"formula": "LiO"}]


def test_memory_ablation_omits_history_from_planner() -> None:
    agent, planner, _ = make_agent(enable_memory=False)
    state = {
        "query_count": 1,
        "elements": ["Li", "O"],
        "last_observation": {"reduced_formula": "LiO", "is_stable": True},
    }

    agent(state)

    assert planner.previous is None
    assert agent.memory == []
