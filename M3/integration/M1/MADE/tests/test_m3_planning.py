"""M3 planner and self-correction tests with synthetic MADE state (no API key)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pymatgen.core.composition import Composition
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
from test_m1_integrated import (  # sibling test module (pytest prepend mode)
    FakeFilter,
    FakeGenerator,
    FakePlanner,
    FakeScorer,
)

from made.agents.base import Plan
from made.agents.m1_integrated import M1IntegratedAgent
from made.agents.m3_planning import (
    M3ResearchPlanner,
    M3StuckReplanPolicy,
    _rkey,
    _subgoal_key,
)

ELEMENTS = ["Fe", "Li", "O"]


def structure_for(formula: str) -> Structure:
    comp = Composition(formula)
    species = [str(el) for el, n in comp.items() for _ in range(int(n))]
    coords = [[i / len(species)] * 3 for i in range(len(species))]
    return Structure(Lattice.cubic(5), species, coords)


def observation(
    formula: str, *, new: bool = False, stable: bool = False, ehull: float = 0.5
) -> dict[str, Any]:
    return {
        "proposal": structure_for(formula).as_dict(),
        "reduced_formula": Composition(
            formula
        ).reduced_composition.alphabetical_formula,
        "e_above_hull": ehull,
        "is_stable": stable,
        "is_newly_discovered": new,
    }


def state(
    query: int, obs: dict[str, Any] | None = None, **extra: Any
) -> dict[str, Any]:
    return {
        "query_count": query,
        "elements": ELEMENTS,
        "last_observation": obs,
        **extra,
    }


def make_planner(**kwargs: Any) -> M3ResearchPlanner:
    params = {
        "max_stoichiometry": 4,
        "num_compositions": 1,
        "num_candidates": 2,
        "seed": 7,
    }
    params.update(kwargs)
    planner = M3ResearchPlanner(**params)
    planner.update_state(state(0))
    return planner


# ------------------------------------------------------------------ planner
def test_planner_returns_plan_inside_one_subgoal() -> None:
    planner = make_planner(num_compositions=2)
    plan = planner.propose(state(0, m1_queries_remaining=10))

    assert isinstance(plan, Plan)
    assert len(plan.compositions) == 2
    assert all(isinstance(c, Composition) for c in plan.compositions)
    assert {_subgoal_key(c) for c in plan.compositions} == {planner.current_subgoal}
    assert len({_rkey(c) for c in plan.compositions}) == 2


def test_planner_respects_remaining_query_budget() -> None:
    planner = make_planner(num_compositions=3)
    plan = planner.propose(state(0, m1_queries_remaining=1))
    assert len(plan.compositions) == 1


def test_planner_consumes_memory_in_review_and_skips_failed_formulas() -> None:
    memory = [
        {
            "event_id": "evaluation:1",
            "reduced_formula": "Li2O",
            "is_newly_discovered": True,
            "is_stable": True,
            "e_above_hull": 0.0,
        },
        {
            "event_id": "evaluation:2",
            "reduced_formula": "Li2O",
            "is_newly_discovered": True,
            "is_stable": True,
            "e_above_hull": 0.0,
        },
        {
            "event_id": "evaluation:3",
            "reduced_formula": "LiO",
            "is_newly_discovered": True,  # MADE sets this for every new structure
            "is_stable": False,
            "e_above_hull": 1.0,
        },
        {
            "event_id": "evaluation:4",
            "reduced_formula": "LiO",
            "is_newly_discovered": True,  # MADE sets this for every new structure
            "is_stable": False,
            "e_above_hull": 1.0,
        },
    ]
    with_memory = make_planner()
    plan = with_memory.propose(state(0, m1_memory=memory))

    assert with_memory.current_subgoal == "Li-O"
    # LiO (and Li2O2, same reduced composition) failed twice in memory
    assert [_rkey(c) for c in plan.compositions] == [_rkey("Li2O")]
    trace = with_memory.decision_trace[-1]
    assert trace["memory_used"] is True
    assert trace["memory_ids"] == [r["event_id"] for r in memory]

    without_memory = make_planner()
    plan = without_memory.propose(state(0, m1_memory=[]))  # memory switch off
    assert plan.compositions
    assert without_memory.decision_trace[-1]["memory_used"] is False
    assert without_memory.decision_trace[-1]["memory_ids"] == []


def test_planner_review_ignores_new_but_unstable_memory() -> None:
    # Many unstable "newly discovered" records must not make Fe-O look promising.
    unstable = [
        {
            "event_id": f"evaluation:{i}",
            "reduced_formula": formula,
            "is_newly_discovered": True,
            "is_stable": False,
            "e_above_hull": 0.8,
        }
        for i, formula in enumerate(["FeO", "Fe2O3", "FeO2", "Fe3O4"], start=1)
    ]
    stable = {
        "event_id": "evaluation:9",
        "reduced_formula": "Li2O",
        "is_newly_discovered": True,
        "is_stable": True,
        "e_above_hull": 0.0,
    }
    planner = make_planner()
    planner.propose(state(0, m1_memory=[*unstable, stable]))
    scores = planner.decision_trace[-1]["scores"]
    assert scores["Li-O"] > scores["Fe-O"]
    assert planner.current_subgoal != "Fe-O"


def test_planner_falls_back_to_previous_observations() -> None:
    planner = make_planner()
    records = [
        {
            "event_id": "evaluation:1",
            "reduced_formula": "Li2O",
            "is_newly_discovered": True,
        }
    ]
    planner.propose(state(0), previous={"observations": records})
    assert planner.decision_trace[-1]["memory_ids"] == ["evaluation:1"]


def test_planner_reviews_after_each_batch() -> None:
    planner = make_planner(batch_size=2)
    plan = planner.propose(state(0))
    assert planner.num_reviews == 1
    for query in (1, 2):
        formula = plan.compositions[0].formula
        planner.update_state(state(query, observation(formula)))
        plan = planner.propose(state(query))
    # two observed queries close the first batch; the third proposal re-reviews
    assert planner.num_reviews == 2
    assert planner.batch_used == 0


def test_planner_checkpoint_round_trip_is_json_and_deterministic() -> None:
    planner = make_planner(batch_size=2)
    for query in range(3):
        plan = planner.propose(state(query))
        planner.update_state(
            state(query + 1, observation(plan.compositions[0].formula))
        )

    saved = json.loads(json.dumps(planner.get_state()))
    restored = M3ResearchPlanner(
        max_stoichiometry=4, num_compositions=1, num_candidates=2, seed=7
    )
    restored.load_state(saved)

    assert restored.current_subgoal == planner.current_subgoal
    assert restored.decision_trace == planner.decision_trace
    assert (
        planner.propose(state(3)).compositions
        == restored.propose(state(3)).compositions
    )


def test_planner_requires_elements() -> None:
    planner = M3ResearchPlanner(max_stoichiometry=4)
    with pytest.raises(ValueError, match="elements"):
        planner.update_state(
            {"query_count": 0, "elements": [], "last_observation": None}
        )


def test_planner_ignores_malformed_observations() -> None:
    planner = make_planner()
    planner.update_state(state(1, {"proposal": "garbage", "is_stable": True}))
    planner.update_state(state(2, "not-a-dict"))  # type: ignore[arg-type]
    assert sum(s.num_attempts for s in planner.composition_stats.values()) == 0


# ------------------------------------------------------------------ self-correction
def plan_of(*formulas: str, n: int = 2) -> Plan:
    return Plan(compositions=[Composition(f) for f in formulas], num_candidates=n)


def ctx(query: int, obs: dict[str, Any] | None = None) -> dict[str, Any]:
    return state(query, obs, max_stoichiometry=4)


def feed(
    policy: M3StuckReplanPolicy, formulas: list[str], start: int = 1, **flags: Any
) -> int:
    """Record observations only; returns the last query fed."""
    query = start - 1
    for query, formula in enumerate(formulas, start=start):
        policy._ingest(ctx(query, observation(formula, **flags)))
    return query


def test_policy_passes_plan_through_while_progressing() -> None:
    policy = M3StuckReplanPolicy(window=3, cooldown=0, max_stoichiometry=4, seed=1)
    query = feed(policy, ["Li2O", "FeO", "LiFeO2"], new=True, stable=True)
    plan = plan_of("Fe2O3")
    assert policy.revise_plan(plan, ctx(query)) is plan
    assert policy.events == []


def test_policy_replans_after_no_progress_window() -> None:
    policy = M3StuckReplanPolicy(
        window=3, max_repeat=5, cooldown=0, max_stoichiometry=4, seed=1
    )
    query = feed(policy, ["Li2O", "LiO", "Li2O2"])
    plan = plan_of("Li3O")
    revised = policy.revise_plan(plan, ctx(query))

    assert isinstance(revised, Plan)
    assert revised is not plan
    recent = {_rkey("Li2O"), _rkey("LiO")}  # Li2O2 reduces to LiO
    assert not recent & {_rkey(c) for c in revised.compositions}
    assert policy.events[-1]["reason"] == "no_progress"
    assert policy.events[-1]["level"] == 1


def test_policy_treats_new_but_unstable_queries_as_no_progress() -> None:
    # Real MADE observations: every query is "newly discovered", most unstable.
    policy = M3StuckReplanPolicy(
        window=3, max_repeat=5, cooldown=0, max_stoichiometry=4, seed=1
    )
    query = feed(policy, ["Li2O", "FeO", "LiFeO2"], new=True, stable=False)
    revised = policy.revise_plan(plan_of("Li3O"), ctx(query))
    assert policy.events[-1]["reason"] == "no_progress"
    assert revised.compositions

    # A new *stable* phase is progress and resets the escalation level.
    feed(policy, ["Fe2O3"], start=query + 1, new=True, stable=True)
    assert policy.level == 0


def test_policy_detects_repetition_and_escalates_then_resets() -> None:
    policy = M3StuckReplanPolicy(
        window=6, max_repeat=2, cooldown=0, max_stoichiometry=4, seed=1
    )
    query = feed(policy, ["FeO", "Fe2O2"])
    first = policy.revise_plan(plan_of("FeO", n=2), ctx(query))
    assert policy.events[-1]["reason"] == "repetition"
    assert first.num_candidates == 2

    query = feed(policy, ["FeO"], start=query + 1)
    second = policy.revise_plan(plan_of("FeO", n=2), ctx(query))
    assert policy.level == 2
    assert second.num_candidates == 4  # escalation widens the candidate pool

    feed(policy, ["LiFeO2"], start=query + 1, new=True, stable=True)
    assert policy.level == 0


def test_policy_cooldown_blocks_back_to_back_replans() -> None:
    policy = M3StuckReplanPolicy(
        window=2, max_repeat=9, cooldown=3, max_stoichiometry=4, seed=1
    )
    query = feed(policy, ["Li2O", "LiO"])
    policy.revise_plan(plan_of("FeO"), ctx(query))
    assert len(policy.events) == 1
    query = feed(policy, ["FeO"], start=query + 1)
    plan = plan_of("Fe2O3")
    assert policy.revise_plan(plan, ctx(query)) is plan
    assert len(policy.events) == 1


def test_policy_rejects_invalid_input_and_survives_bad_context() -> None:
    policy = M3StuckReplanPolicy(window=1, cooldown=0)
    with pytest.raises(TypeError, match="MADE Plan"):
        policy.revise_plan("not a plan", state(1))  # type: ignore[arg-type]
    plan = plan_of("FeO")
    bad = {"query_count": 1, "elements": ["Fe"], "last_observation": {"proposal": 3}}
    assert policy.revise_plan(plan, bad) is plan  # single element: nothing to re-plan


def test_policy_checkpoint_round_trip() -> None:
    policy = M3StuckReplanPolicy(window=2, cooldown=0, max_stoichiometry=4, seed=3)
    query = feed(policy, ["Li2O", "LiO"])
    policy.revise_plan(plan_of("FeO"), ctx(query))

    restored = M3StuckReplanPolicy(window=2, cooldown=0, max_stoichiometry=4, seed=3)
    restored.load_state(json.loads(json.dumps(policy.get_state())))
    assert restored.get_state() == policy.get_state()

    next_plan = plan_of("Li3O")
    context = ctx(query)
    assert (
        policy.revise_plan(next_plan, context).compositions
        == restored.revise_plan(next_plan, context).compositions
    )


# ------------------------------------------------------------------ M1 switches
def make_agent(**kwargs: Any) -> tuple[M1IntegratedAgent, FakeGenerator]:
    generator = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=kwargs.pop("planner", None) or make_planner(),
        generator=generator,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        query_budget=20,
        **kwargs,
    )
    return agent, generator


def test_m1_planning_switch_on_uses_m3_planner() -> None:
    planner = make_planner()
    agent, generator = make_agent(planner=planner, enable_planning=True)
    agent(state(0))
    assert planner.num_reviews == 1
    assert generator.last_plan is not None
    assert _subgoal_key(generator.last_plan.compositions[0]) == planner.current_subgoal


def test_m1_planning_switch_off_bypasses_m3_planner() -> None:
    planner = make_planner()
    agent, generator = make_agent(planner=planner, enable_planning=False)
    agent(state(0))
    assert planner.num_reviews == 0
    assert generator.last_plan.compositions == [Composition("FeLiO")]


def test_m1_reflection_switch_controls_m3_policy() -> None:
    def run(enabled: bool) -> tuple[M3StuckReplanPolicy, FakeGenerator]:
        policy = M3StuckReplanPolicy(
            window=1, max_repeat=1, cooldown=0, max_stoichiometry=4, seed=1
        )
        fake = FakePlanner()
        fake.plan = Plan(compositions=[Composition("Li2O")], num_candidates=1)
        agent, generator = make_agent(
            planner=fake, enable_reflection=enabled, self_correction_policy=policy
        )
        agent(state(0))
        agent(state(1, observation("Li2O")))
        return policy, generator

    policy, generator = run(True)
    assert policy.events and policy.events[-1]["reason"] == "repetition"
    assert _rkey(generator.last_plan.compositions[0]) != _rkey("Li2O")

    policy, generator = run(False)
    assert policy.events == [] and policy.last_query == 0
    assert _rkey(generator.last_plan.compositions[0]) == _rkey("Li2O")


def test_m1_checkpoint_round_trips_m3_components() -> None:
    policy = M3StuckReplanPolicy(window=2, cooldown=0, max_stoichiometry=4, seed=1)
    agent, _ = make_agent(enable_reflection=True, self_correction_policy=policy)
    agent(state(0))
    agent(state(1, observation("Li2O")))
    saved = json.loads(json.dumps(agent.get_state()))

    restored_policy = M3StuckReplanPolicy(
        window=2, cooldown=0, max_stoichiometry=4, seed=1
    )
    restored, _ = make_agent(
        enable_reflection=True, self_correction_policy=restored_policy
    )
    restored.load_state(saved)
    assert restored_policy.get_state() == policy.get_state()
    assert restored.planner.get_state() == agent.planner.get_state()


# ------------------------------------------------------------------ Hydra
def _compose_agent(*extra: str) -> Any:
    config_dir = str(Path(__file__).resolve().parents[1] / "configs")
    with initialize_config_dir(config_dir=config_dir, version_base=None):
        return compose(
            config_name="config",
            overrides=[
                "agent=m1_integrated",
                "environment.budget=5",
                "experiment.seed=11",
                "agent.planner.max_stoichiometry=4",
                *extra,
            ],
        )


def test_hydra_config_instantiates_m3_components() -> None:
    cfg = _compose_agent("agent/planner=m3_research")
    planner = instantiate(cfg.agent.planner)
    policy = instantiate(cfg.agent.self_correction_policy)
    assert isinstance(planner, M3ResearchPlanner)
    assert planner.seed == 11 and planner.num_candidates == 8  # M1 planner block
    assert isinstance(policy, M3StuckReplanPolicy)
    assert policy.max_stoichiometry == 4 and policy.seed == 11
    assert cfg.agent.enable_reflection is False  # M1 baseline default unchanged


def test_hydra_default_planner_stays_m1_baseline_diversity() -> None:
    # m1_baseline's recorded reference runs used the diversity planner.
    cfg = _compose_agent()
    planner = instantiate(cfg.agent.planner)
    assert type(planner).__name__ == "GridSearchPlanner"
    assert not isinstance(planner, M3ResearchPlanner)
    assert cfg.agent.self_correction_policy._target_.endswith("M3StuckReplanPolicy")


# ------------------------------------------------------------------ M4 memory
@pytest.mark.parametrize("enable_memory", [True, False])
def test_m4_memory_reaches_m3_planner_decision(
    tmp_path: Path, enable_memory: bool
) -> None:
    m4 = pytest.importorskip("m4_memory.m1_adapter")
    manager = m4.M4MemoryManager(
        log_path=str(tmp_path / "m4.jsonl"), run_id="m3-test", episode_id=0, limit=8
    )
    planner = make_planner(batch_size=1)
    agent, _ = make_agent(
        planner=planner, enable_memory=enable_memory, memory_manager=manager
    )
    agent(state(0))
    agent(state(1, observation("Li2O", new=True, stable=True, ehull=0.0)))

    trace = planner.decision_trace[-1]
    if enable_memory:
        assert trace["memory_used"] is True
        assert trace["memory_ids"] == ["evaluation:1"]
    else:
        assert trace["memory_used"] is False
        assert trace["memory_ids"] == []
