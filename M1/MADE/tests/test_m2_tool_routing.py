"""Executed unit/contract tests; synthetic inputs are not benchmark results."""

from __future__ import annotations

import json
from typing import Any

import pytest
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pymatgen.core.composition import Composition
from test_m1_integrated import FakeFilter, FakePlanner, FakeScorer

from made.agents.base import Plan
from made.agents.m1_integrated import M1IntegratedAgent
from made.agents.m2_tool_routing import (
    CheckpointedChemeleonGenerator,
    CheckpointedRandomGenerator,
    OutcomeAwareToolRouter,
)


def context(query: int, remaining: int = 20, stable: bool = True) -> dict[str, Any]:
    return {
        "query_count": query,
        "m1_queries_remaining": remaining,
        "elements": ["Li", "O"],
        "last_observation": (
            {"is_stable": stable, "is_newly_discovered": stable} if query else None
        ),
    }


def tools() -> dict[str, CheckpointedRandomGenerator]:
    return {
        "default": CheckpointedRandomGenerator(seed=17),
        "alternate": CheckpointedRandomGenerator(seed=29),
    }


def router(**kwargs: Any) -> OutcomeAwareToolRouter:
    return OutcomeAwareToolRouter(generator_names=["default", "alternate"], **kwargs)


def test_completed_feedback_is_attributed_once_to_the_tool_that_was_used() -> None:
    policy, generators = router(), tools()
    assert policy.select_generator(context(0), generators) == "default"
    assert policy.select_generator(context(0), generators) == "default"
    assert sum(policy.counts.values()) == 0
    assert policy.select_generator(context(1), generators) == "alternate"
    assert policy.counts == {"default": 1, "alternate": 0}
    assert (
        policy.select_generator(context(2, remaining=2, stable=False), generators)
        == "default"
    )
    assert policy.counts == {"default": 1, "alternate": 1}
    assert policy.rewards == {"default": 1.0, "alternate": 0.0}


@pytest.mark.parametrize("remaining", [0, -1, None, True, 1.5])
def test_bad_or_exhausted_budget_is_rejected(remaining: Any) -> None:
    with pytest.raises((ValueError, RuntimeError)):
        router().select_generator(context(0, remaining=remaining), tools())


def test_unknown_configured_generator_is_rejected() -> None:
    with pytest.raises(ValueError, match="not configured"):
        router().select_generator(context(0), {"default": tools()["default"]})


def test_skipped_queries_do_not_misattribute_latest_feedback() -> None:
    policy, generators = router(), tools()
    policy.select_generator(context(0), generators)
    policy.select_generator(context(3), generators)
    assert sum(policy.counts.values()) == 0
    assert policy.unattributed_queries == 3


@pytest.mark.parametrize("seed", [17, 29, 43])
def test_router_json_checkpoint_resumes_the_same_decisions(seed: int) -> None:
    first, generators = router(seed=seed), tools()
    for query in range(5):
        first.select_generator(context(query, remaining=20 - query), generators)
    saved = json.loads(json.dumps(first.get_state(), allow_nan=False))
    resumed = router(seed=seed)
    resumed.load_state(saved)
    for query in range(5, 20):
        state = context(query, remaining=20 - query, stable=query % 3 == 0)
        assert resumed.select_generator(state, generators) == first.select_generator(
            state, generators
        )
        assert resumed.get_state() == first.get_state()


def test_checkpoint_rejects_a_changed_configuration_or_corrupt_state() -> None:
    saved = router().get_state()
    with pytest.raises(ValueError, match="configuration"):
        router(seed=43).load_state(saved)
    saved["counts"]["default"] = -1
    with pytest.raises(ValueError, match="integer"):
        router().load_state(saved)


def test_random_generator_checkpoint_restores_real_structure_generation() -> None:
    first = CheckpointedRandomGenerator(seed=17)
    plan = Plan(compositions=[Composition("Li2O")], num_candidates=2)
    first.generate(plan, {"elements": ["Li", "O"]})
    checkpoint = json.loads(json.dumps(first.get_state()))
    expected = first.generate(plan, {"elements": ["Li", "O"]})
    restored = CheckpointedRandomGenerator(seed=999)
    restored.load_state(checkpoint)
    actual = restored.generate(plan, {"elements": ["Li", "O"]})
    assert [s.as_dict() for s in actual] == [s.as_dict() for s in expected]


def test_chemeleon_adapter_configuration_state_round_trip() -> None:
    # This tests state only; no diffusion-model or scientific performance claim.
    first = CheckpointedChemeleonGenerator(seed=17, device="cpu")
    first.calls = 3
    restored = CheckpointedChemeleonGenerator(seed=17, device="cpu")
    restored.load_state(json.loads(json.dumps(first.get_state())))
    assert restored.get_state() == first.get_state()


def integrated(enabled: bool, **kwargs: Any) -> M1IntegratedAgent:
    primary, alternate = tools().values()
    return M1IntegratedAgent(
        planner=FakePlanner(),
        generator=primary,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        query_budget=20,
        generators={"alternate": alternate},
        tool_router=router(),
        enable_tool_routing=enabled,
        **kwargs,
    )


def test_enabled_and_disabled_slots_generate_real_structures() -> None:
    enabled, disabled = integrated(True), integrated(False)
    first = context(0)
    for agent in (enabled, disabled):
        composition, structure = agent(first)
        assert composition == structure.composition
    next_state = context(1)
    next_state["last_observation"]["reduced_formula"] = "LiO"
    enabled(next_state)
    disabled(next_state)
    assert enabled.last_generator_name == "alternate"
    assert disabled.last_generator_name == "default"
    assert disabled.tool_router.get_state()["last_reason"] == "not_called"


def test_full_agent_json_checkpoint_restores_tool_and_generator_state() -> None:
    first = integrated(True)
    first(context(0))
    restored = integrated(True)
    restored.load_state(json.loads(json.dumps(first.get_state(), allow_nan=False)))
    next_state = context(1)
    next_state["last_observation"]["reduced_formula"] = "LiO"
    _, expected = first(next_state)
    _, actual = restored(next_state)
    assert actual.as_dict() == expected.as_dict()
    assert restored.get_state() == first.get_state()


@pytest.mark.parametrize("invalid", ["unknown", object()])
def test_m1_rejects_invalid_router_outputs(invalid: Any) -> None:
    class InvalidRouter:
        def select_generator(self, context: Any, generators: Any) -> Any:
            return invalid

    agent = integrated(True)
    agent.tool_router = InvalidRouter()
    with pytest.raises(ValueError, match="generator"):
        agent(context(0))


@pytest.mark.parametrize("oracle", ["orb", "analytic"])
def test_hydra_instantiates_m2_with_only_its_switch_changed(oracle: str) -> None:
    from pathlib import Path

    configs = Path(__file__).resolve().parents[1] / "configs"
    with initialize_config_dir(config_dir=str(configs), version_base=None):
        off = compose(
            config_name="config",
            overrides=["agent=m1_integrated", "experiment.seed=17", f"oracle={oracle}"],
        )
        on = compose(
            config_name="config",
            overrides=["agent=m2_routing", "experiment.seed=17", f"oracle={oracle}"],
        )
    assert on.agent.enable_tool_routing is True
    assert off.agent.enable_tool_routing is False
    for field in (
        "enable_planning",
        "enable_memory",
        "enable_reflection",
        "enable_exploration",
    ):
        assert on.agent[field] == off.agent[field]
    agent = instantiate(on.agent)
    assert isinstance(agent.tool_router, OutcomeAwareToolRouter)
    assert isinstance(agent.generators["chemeleon"], CheckpointedChemeleonGenerator)
