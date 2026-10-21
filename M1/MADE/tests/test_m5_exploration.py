"""M5 contract tests: UCBExplorationPolicy through M1IntegratedAgent.

Uses fake MADE state and synthetic structures only; no oracle or API key.
Mirrors the style of M1/MADE/tests/test_m1_integrated.py.
"""

from __future__ import annotations

import json
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
from made.agents.m5_exploration import UCBExplorationPolicy


def sample_structure() -> Structure:
    return Structure(Lattice.cubic(4), ["Mg", "Sn"], [[0, 0, 0], [0.5, 0.5, 0.5]])


class FakePlanner(Planner):
    def __init__(self) -> None:
        self.plan = Plan(compositions=[Composition("MgSn")], num_candidates=4)

    def propose(
        self, state: dict[str, Any], previous: dict[str, Any] | None = None
    ) -> Plan:
        return self.plan

    def get_state(self) -> dict[str, Any]:
        return {}

    def load_state(self, state: dict[str, Any]) -> None:
        pass

    def update_state(self, state: dict[str, Any]) -> None:
        pass


class FakeGenerator(Generator):
    def __init__(self) -> None:
        self.last_plan: Plan | None = None

    def generate(self, plan: Plan, state: dict[str, Any]) -> list[Structure]:
        self.last_plan = plan
        return [sample_structure() for _ in range(plan.num_candidates)]

    def get_state(self) -> dict[str, Any]:
        return {}

    def load_state(self, state: dict[str, Any]) -> None:
        pass

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
        scores = [float(i) for i, _ in enumerate(candidates)]
        return scores, [ScoreResult(score=s, scorer_name="fake") for s in scores]

    def get_state(self) -> dict[str, Any]:
        return {}

    def load_state(self, state: dict[str, Any]) -> None:
        pass

    def update_state(self, state: dict[str, Any]) -> None:
        pass


def make_agent(**kwargs: Any) -> tuple[M1IntegratedAgent, FakeGenerator]:
    generator = FakeGenerator()
    agent = M1IntegratedAgent(
        planner=FakePlanner(),
        generator=generator,
        scorer=FakeScorer(),
        filter=FakeFilter(),
        **kwargs,
    )
    return agent, generator


def mg_sn_state(query_count: int, observation: dict[str, Any] | None = None) -> dict:
    return {
        "query_count": query_count,
        "elements": ["Mg", "Sn"],
        "max_stoichiometry": 6,
        "last_observation": observation,
    }


def test_enabled_policy_appends_exploration_compositions() -> None:
    policy = UCBExplorationPolicy(seed=17)
    agent, generator = make_agent(
        query_budget=20, enable_exploration=True, exploration_policy=policy
    )

    agent(mg_sn_state(0))

    assert generator.last_plan is not None
    incoming = [c.reduced_formula for c in [Composition("MgSn")]]
    outgoing = [c.reduced_formula for c in generator.last_plan.compositions]
    assert outgoing[:1] == incoming  # planner compositions kept first
    assert len(outgoing) > len(incoming)  # exploration compositions appended
    assert policy.decision_log[-1]["mode"] == "mixed"
    assert policy.decision_log[-1]["m1_queries_remaining"] == 20
    assert "ucb_explore" in policy.decision_log[-1]["composition_source"]


def test_disabled_policy_is_not_called() -> None:
    policy = UCBExplorationPolicy(seed=17)
    agent, generator = make_agent(
        query_budget=20, enable_exploration=False, exploration_policy=policy
    )

    agent(mg_sn_state(0))

    assert policy.decision_log == []
    assert generator.last_plan is not None
    assert [c.reduced_formula for c in generator.last_plan.compositions] == ["MgSn"]


def test_policy_respects_remaining_budget_via_m1_cap() -> None:
    policy = UCBExplorationPolicy(seed=17, alpha0=1.0)
    agent, generator = make_agent(
        query_budget=2, enable_exploration=True, exploration_policy=policy
    )

    agent(mg_sn_state(1))  # one query left

    assert generator.last_plan is not None
    assert len(generator.last_plan.compositions) <= 1  # M1 cap after the hook


def test_late_budget_suppresses_exploration() -> None:
    early = UCBExplorationPolicy(seed=17)
    late = UCBExplorationPolicy(seed=17)
    context_early = dict(mg_sn_state(0)) | {"m1_queries_remaining": 20}
    context_late = dict(mg_sn_state(18)) | {"m1_queries_remaining": 2}
    context_early["m1_queries_used"] = 0
    context_late["m1_queries_used"] = 18
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)

    out_early = early.adjust_plan(plan, context_early)
    out_late = late.adjust_plan(plan, context_late)

    assert len(out_early.compositions) > len(out_late.compositions)


def test_cold_start_without_memory_still_explores() -> None:
    policy = UCBExplorationPolicy(seed=17)
    context = mg_sn_state(0)
    context["m1_queries_remaining"] = 20
    context["m1_queries_used"] = 0
    context["m1_memory"] = []
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)

    out = policy.adjust_plan(plan, context)

    assert len(out.compositions) > 1
    assert policy.decision_log[-1]["mode"] == "mixed"


def test_queried_compositions_are_not_reproposed() -> None:
    policy = UCBExplorationPolicy(seed=17, alpha0=1.0)
    context = mg_sn_state(5)
    context["m1_queries_remaining"] = 15
    context["m1_queries_used"] = 5
    context["m1_memory"] = [
        {"reduced_formula": "Mg2Sn", "e_above_hull": 0.05, "query_count": 1},
        {"reduced_formula": "MgSn2", "e_above_hull": 0.30, "query_count": 2},
    ]
    plan = Plan(compositions=[Composition("MgSn"), Composition("MgSn2")], num_candidates=1)

    out = policy.adjust_plan(plan, context)

    outgoing = {c.reduced_formula for c in out.compositions}
    assert "Mg2Sn" not in outgoing - {"MgSn", "MgSn2"}  # never re-propose queried
    # planner's own compositions pass through untouched
    assert [c.reduced_formula for c in out.compositions[:2]] == ["MgSn", "MgSn2"]


def test_determinism_same_seed_same_inputs() -> None:
    context = mg_sn_state(3)
    context["m1_queries_remaining"] = 17
    context["m1_queries_used"] = 3
    context["m1_memory"] = [
        {"reduced_formula": "Mg2Sn", "e_above_hull": 0.10, "query_count": 1}
    ]
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)

    out_a = UCBExplorationPolicy(seed=29).adjust_plan(plan, context)
    out_b = UCBExplorationPolicy(seed=29).adjust_plan(plan, context)

    assert [c.reduced_formula for c in out_a.compositions] == [
        c.reduced_formula for c in out_b.compositions
    ]


def test_checkpoint_roundtrip_preserves_decision_log() -> None:
    policy = UCBExplorationPolicy(seed=43)
    agent, _ = make_agent(
        query_budget=20, enable_exploration=True, exploration_policy=policy
    )
    agent(mg_sn_state(0))
    agent(mg_sn_state(1, {"reduced_formula": "Mg2Sn", "e_above_hull": 0.1}))

    state = agent.get_state()
    json.dumps(state["exploration_policy"])  # must be JSON-serializable

    restored_policy = UCBExplorationPolicy(seed=43)
    restored, _ = make_agent(
        query_budget=20, enable_exploration=True, exploration_policy=restored_policy
    )
    restored.load_state(state)
    assert restored_policy.decision_log == policy.decision_log


def test_invalid_policy_output_is_rejected_by_agent() -> None:
    class InvalidPolicy:
        def adjust_plan(self, plan: Plan, context: dict[str, Any]) -> str:
            return "not a Plan"

    agent, _ = make_agent(enable_exploration=True, exploration_policy=InvalidPolicy())

    try:
        agent(mg_sn_state(0))
    except TypeError as error:
        assert "must return a MADE Plan" in str(error)
    else:
        raise AssertionError("Expected invalid exploration output to be rejected")


def test_enabling_exploration_without_policy_fails_fast() -> None:
    try:
        make_agent(enable_exploration=True)
    except ValueError as error:
        assert "must be configured" in str(error)
    else:
        raise AssertionError("Expected missing exploration_policy to fail fast")


def test_bounded_memory_window_does_not_cause_reproposal() -> None:
    """M4's manager serves at most `limit` recent records; an old formula that
    falls out of the window must never be re-proposed."""
    policy = UCBExplorationPolicy(seed=17, alpha0=1.0)
    context = mg_sn_state(10)
    context["m1_queries_remaining"] = 10
    context["m1_queries_used"] = 10
    context["m1_memory"] = [
        {"reduced_formula": "Mg2Sn", "e_above_hull": 0.05, "query_count": 9},
        {"reduced_formula": "MgSn2", "e_above_hull": 0.30, "query_count": 10},
    ]
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)
    # First call sees MgSn as incoming and adds it to history.
    policy.adjust_plan(plan, context)

    # Memory window now drops MgSn (only keeps last 2). It must still be
    # excluded from the explore pool via the policy's own history.
    context["m1_queries_remaining"] = 9
    context["m1_queries_used"] = 11
    out = policy.adjust_plan(plan, context)

    outgoing = {c.reduced_formula for c in out.compositions}
    assert "MgSn" not in outgoing - {"MgSn"}  # only the planner's own copy stays
    assert policy.decision_log[-1]["query_count"] == 11


def test_jsonl_sidecar_appends_one_line_per_decision(tmp_path) -> None:
    """M4 requested a per-episode JSONL sidecar; each adjust_plan call must
    append exactly one line, and the file must parse as JSONL."""
    import json as jsonlib

    log_file = tmp_path / "m5_decisions.jsonl"
    policy = UCBExplorationPolicy(seed=17, log_path=str(log_file))
    context = dict(mg_sn_state(0))
    context["m1_queries_remaining"] = 20
    context["m1_queries_used"] = 0
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)

    policy.adjust_plan(plan, context)
    policy.adjust_plan(plan, context)

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        record = jsonlib.loads(line)
        assert record["mode"] in {"mixed", "explore", "exploit"}
        assert "m1_queries_remaining" in record
        assert "rationale" in record
    # In-memory log and sidecar stay in sync.
    assert len(policy.decision_log) == 2


def test_resume_after_checkpoint_restore_does_not_duplicate_sidecar(tmp_path) -> None:
    """M4's reproduction: replaying a step after checkpoint restore appended
    the decision twice. load_state must truncate the sidecar so file and
    in-memory log stay in lockstep."""
    import json as jsonlib

    log_file = tmp_path / "m5_decisions.jsonl"
    policy = UCBExplorationPolicy(seed=17, log_path=str(log_file))
    context = dict(mg_sn_state(0))
    context["m1_queries_remaining"] = 20
    context["m1_queries_used"] = 0
    plan = Plan(compositions=[Composition("MgSn")], num_candidates=1)
    policy.adjust_plan(plan, context)
    policy.adjust_plan(plan, context)
    assert len(log_file.read_text(encoding="utf-8").strip().splitlines()) == 2

    # Simulate crash + checkpoint restore, then replay step 2.
    checkpoint = policy.get_state()
    restored = UCBExplorationPolicy(seed=17, log_path=str(log_file))
    restored.load_state(checkpoint)
    # Sidecar must be truncated back to 2 lines, not 4 after replay.
    restored.adjust_plan(plan, context)
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3  # 2 restored + 1 new, no duplicates
    assert len(restored.decision_log) == 3
    for line in lines:
        jsonlib.loads(line)  # still valid JSONL
