"""Real M1 boundary tests using synthetic structures; no scientific oracle."""

import json

import pytest
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from m4_memory.capture import CapturedM1IntegratedAgent
from m4_memory.m1_adapter import M4MemoryManager
from test_m1_integrated import make_agent


def observation():
    return {
        "query_count": 1,
        "elements": ["Li", "O"],
        "last_observation": {
            "reduced_formula": "LiO",
            "is_stable": False,
            "e_above_hull": 0.3,
            "ground_truth_label": "never-copy",
        },
    }


@pytest.mark.parametrize("enabled", [True, False])
def test_real_switch_and_checkpoint(tmp_path, enabled):
    manager = M4MemoryManager(tmp_path / "log.jsonl", "test", 0)
    agent, planner, _ = make_agent(
        query_budget=3, enable_memory=enabled, memory_manager=manager
    )
    agent(observation())
    if enabled:
        assert planner.previous["observations"][0]["e_above_hull"] == 0.3
        assert "never-copy" not in json.dumps(manager.get_state())
    else:
        assert planner.previous is None
        assert manager.get_memory() == []
        assert not (tmp_path / "log.jsonl").exists()
    restored_manager = M4MemoryManager(tmp_path / "log.jsonl", "test", 0)
    restored, _, _ = make_agent(
        query_budget=3, enable_memory=enabled, memory_manager=restored_manager
    )
    restored.load_state(json.loads(json.dumps(agent.get_state())))
    assert restored_manager.get_memory() == manager.get_memory()


def test_manager_json_bound(tmp_path):
    manager = M4MemoryManager(tmp_path / "log.jsonl", "test", 0, max_chars=500)
    for step in range(1, 12):
        manager.update_state({**observation(), "query_count": step})
    assert len(json.dumps(manager.get_memory(), ensure_ascii=False)) <= 500
    assert len(manager.get_memory()) <= 8


def test_config_constructs_real_agent(tmp_path):
    from pathlib import Path

    config_dir = Path(__file__).resolve().parents[1] / "configs"
    with initialize_config_dir(config_dir=str(config_dir), version_base=None):
        config = compose(
            config_name="config",
            overrides=["agent=m1_integrated", "experiment.seed=0"],
        )
        config.agent.memory_manager.log_path = str(tmp_path / "log.jsonl")
        config.agent.capture_path = str(tmp_path / "capture.jsonl")
        agent = instantiate(config.agent)
    assert isinstance(agent, CapturedM1IntegratedAgent)
    assert isinstance(agent.memory_manager, M4MemoryManager)


def test_invalid_observation_rejected(tmp_path):
    manager = M4MemoryManager(tmp_path / "log.jsonl", "test", 0)
    agent, _, _ = make_agent(memory_manager=manager)
    with pytest.raises(ValueError, match="JSON scalar"):
        agent({**observation(), "last_observation": {"is_stable": []}})
