"""Real M1/M3/M4 boundary tests using public synthetic observations only."""

import json

import pytest
from m4_memory.capture import CapturedM1IntegratedAgent
from m4_memory.m1_adapter import M4MemoryManager
from test_m1_integrated import FakeFilter, FakeGenerator, FakeScorer, sample_structure

from made.agents.m1_integrated import M1IntegratedAgent
from made.agents.m3_planning import M3ResearchPlanner


class RejectFilter(FakeFilter):
    def filter(self, candidates, state):
        return []


class BrokenGenerator(FakeGenerator):
    def generate(self, plan, state):
        raise ValueError("secret text must not be logged")


def state(query=1):
    return {
        "elements": ["Fe", "Li", "O"],
        "query_count": query,
        "last_observation": {
            "reduced_formula": "Li2O",
            "is_stable": True,
            "is_newly_discovered": True,
            "e_above_hull": 0.0,
        }
        if query
        else None,
        "hidden_label": "never-copy",
    }


def agent(tmp_path, enabled=True, captured=True, generator=None, filter=None):
    kwargs = {
        "planner": M3ResearchPlanner(seed=7, max_stoichiometry=4, num_candidates=2),
        "generator": generator or FakeGenerator(),
        "filter": filter or FakeFilter(),
        "scorer": FakeScorer(),
        "enable_memory": enabled,
        "query_budget": 20,
        "memory_manager": M4MemoryManager(tmp_path / "memory.jsonl", "joint", 0),
    }
    if captured:
        return CapturedM1IntegratedAgent(
            capture_path=tmp_path / "audit.jsonl",
            capture_run_id="joint",
            capture_episode_id=0,
            **kwargs,
        )
    return M1IntegratedAgent(**kwargs)


@pytest.mark.parametrize("enabled", [True, False])
def test_real_m3_consumption_and_checkpoint(tmp_path, enabled):
    a = agent(tmp_path, enabled)
    a(state())
    trace = a.planner.decision_trace[-1]
    assert trace["memory_used"] is enabled
    assert bool(trace["memory_ids"]) is enabled
    checkpoint = json.loads(json.dumps(a.get_state(), allow_nan=False))
    b = agent(tmp_path, enabled)
    b.load_state(checkpoint)
    assert b.memory_manager.get_memory() == a.memory_manager.get_memory()
    assert b.planner.decision_trace == a.planner.decision_trace
    fresh = agent(tmp_path / "fresh", enabled)
    fresh(state(0))
    assert fresh.planner.decision_trace[-1]["memory_ids"] == []


@pytest.mark.parametrize("enabled", [True, False])
def test_filter_fallback_unchanged_and_audit_separate(tmp_path, enabled):
    a = agent(tmp_path / "captured", enabled, filter=RejectFilter())
    plain = agent(tmp_path / "plain", enabled, captured=False, filter=RejectFilter())
    comp, structure = a(state())
    other_comp, other_structure = plain(state())
    assert comp == other_comp
    assert structure == other_structure == sample_structure()
    events = a.capture.events
    assert events and all(e["status"] == "rejected" for e in events)
    assert all(e["fallback_to_unfiltered"] and e["evaluated"] is None for e in events)
    assert all(
        e["query_count"] == 1 and e["m1_queries_remaining"] == 19 for e in events
    )
    assert all(e["status"] == "evaluated" for e in a.memory_manager.get_memory())
    assert "never-copy" not in json.dumps(a.get_state())
    checkpoint = json.loads(json.dumps(a.get_state()))
    restored = agent(tmp_path / "captured", enabled, filter=RejectFilter())
    restored.load_state(checkpoint)
    assert restored.capture_sequence == a.capture_sequence
    assert len(restored.capture.events) == len(events)
    restored(state(2))
    assert len(restored.capture.events) > len(events)
    assert len({e["event_id"] for e in restored.capture.events}) == len(
        restored.capture.events
    )


def test_generator_error_reraised_without_sensitive_message(tmp_path):
    a = agent(tmp_path, generator=BrokenGenerator())
    with pytest.raises(ValueError, match="secret text"):
        a(state())
    assert a.capture.events[0]["error_type"] == "ValueError"
    assert "secret text" not in (tmp_path / "audit.jsonl").read_text()


class PartialFilter(FakeFilter):
    def filter(self, candidates, state):
        return candidates[:1]


class EmptyGenerator(FakeGenerator):
    def generate(self, plan, state):
        return []


class BrokenFilter(FakeFilter):
    def filter(self, candidates, state):
        raise RuntimeError("private filter details")


def test_partial_filter_duplicate_instances_and_original_result(tmp_path):
    a = agent(tmp_path, filter=PartialFilter())
    comp, structure = a(state())
    assert structure == sample_structure()
    assert comp == structure.composition
    assert len(a.capture.events) == 1
    event = a.capture.events[0]
    assert event["candidate_index"] == 1
    assert event["fallback_to_unfiltered"] is False
    assert event["proposal"] == structure.as_dict()


def test_empty_batch_keeps_m1_failure(tmp_path):
    a = agent(tmp_path, generator=EmptyGenerator())
    with pytest.raises(RuntimeError, match="No candidate structures"):
        a(state())
    assert a.capture.events[0]["reason"] == "empty_generation"


def test_filter_exception_is_preserved(tmp_path):
    a = agent(tmp_path, filter=BrokenFilter())
    with pytest.raises(RuntimeError, match="private filter"):
        a(state())
    assert a.capture.events[0]["stage"] == "filter"
    assert a.capture.events[0]["error_type"] == "RuntimeError"
    assert "private filter" not in (tmp_path / "audit.jsonl").read_text()


def test_capture_checkpoint_rejects_other_episode(tmp_path):
    a = agent(tmp_path)
    checkpoint = json.loads(json.dumps(a.get_state()))
    checkpoint["m4_capture"]["episode_id"] = 9
    with pytest.raises(ValueError, match="identity/version"):
        a.load_state(checkpoint)


def test_hydra_profile_constructs_and_runs_real_components(tmp_path):
    from pathlib import Path

    from hydra import compose, initialize_config_dir
    from hydra.utils import instantiate

    config_dir = Path(__file__).resolve().parents[2] / "M1/MADE/configs"
    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        config = compose(
            config_name="config",
            overrides=[
                "agent=m1_integrated",
                "agent/planner=m3_research",
                "experiment.seed=17",
                "agent.planner.max_stoichiometry=4",
                "agent.planner.num_candidates=2",
                "agent._target_=m4_memory.capture.CapturedM1IntegratedAgent",
                f"+agent.capture_path={tmp_path / 'audit.jsonl'}",
                "+agent.capture_run_id=hydra-check",
                "+agent.capture_episode_id=0",
            ],
        )
        config.agent.memory_manager.log_path = str(tmp_path / "memory.jsonl")
        config.agent.memory_manager.run_id = "hydra-check"
        config.agent.memory_manager.episode_id = 0
        a = instantiate(config.agent)
    assert isinstance(a, CapturedM1IntegratedAgent)
    assert isinstance(a.planner, M3ResearchPlanner)
    composition, structure = a(state())
    assert structure.composition == composition
    assert a.planner.decision_trace[-1]["memory_ids"] == ["evaluation:1"]
    json.dumps(a.get_state(), allow_nan=False)
