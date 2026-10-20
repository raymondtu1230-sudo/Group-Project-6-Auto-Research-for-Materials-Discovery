from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

M1_DIR = Path(__file__).resolve().parents[1]
MADE_DIR = M1_DIR / "MADE"
sys.path.insert(0, str(M1_DIR))

from validate_protocol_results import canonical_hash, expected_methods  # noqa: E402


def test_system_split_is_disjoint_and_matches_frozen_source_order() -> None:
    source = json.loads(
        (
            MADE_DIR
            / "data/systems_10_mp_20/systems_ternary_n10_maxatoms20_intermetallic_smact.json"
        ).read_text()
    )
    dev = json.loads((M1_DIR / "protocol/dev_systems.json").read_text())
    check = json.loads((M1_DIR / "protocol/check_systems.json").read_text())

    assert dev == source[:6]
    assert check == source[6:]
    assert set(map(tuple, dev)).isdisjoint(set(map(tuple, check)))


def test_protocol_fixes_required_methods_budget_and_repeats() -> None:
    protocol = yaml.safe_load((M1_DIR / "protocol/protocol_v1.yaml").read_text())

    assert protocol["environment"]["query_budget"] == 20
    assert protocol["repeats"] == {"seeds": [17, 29, 43], "episodes_per_process": 1}
    assert protocol["methods"]["required"] == [
        "m1_full",
        "random_generator_baseline",
        "chemeleon_generative_baseline",
    ]
    assert set(protocol["methods"]["ablations"]) == {
        "planning_off",
        "memory_off",
        "self_correction_off",
        "exploration_off",
        "tool_routing_off",
    }


def test_check_split_excludes_ablations_and_snapshot_hash_ignores_entry_order() -> None:
    assert expected_methods("check") == [
        "m1_full",
        "random_generator_baseline",
        "chemeleon_generative_baseline",
    ]
    entries = [
        {"composition": {"Li": 1}, "energy": 0.0},
        {"composition": {"O": 1}, "energy": 0.0},
    ]
    assert canonical_hash(entries) == canonical_hash(list(reversed(entries)))


def test_m3_methods_run_against_m1_baseline_without_other_plugins() -> None:
    from run_experiment import METHODS, m1_agent_overrides

    baseline = m1_agent_overrides("m1_baseline")
    assert "agent/planner=m3_research" not in baseline
    assert "agent.enable_reflection=false" in baseline

    expected = {
        "m3_full": ("true", "true"),
        "m3_planning_off": ("false", "true"),
        "m3_self_correction_off": ("true", "false"),
    }
    for method, (planning, reflection) in expected.items():
        assert method in METHODS
        overrides = m1_agent_overrides(method)
        assert "agent/planner=m3_research" in overrides
        assert f"agent.enable_planning={planning}" in overrides
        assert "agent.enable_memory=true" in overrides
        assert f"agent.enable_reflection={reflection}" in overrides
        assert "agent.enable_exploration=false" in overrides
        assert "agent.enable_tool_routing=false" in overrides


def test_plugin_complete_methods_keep_all_switches_and_use_m3_planner() -> None:
    from run_experiment import m1_agent_overrides

    full = m1_agent_overrides("m1_full")
    assert "agent/planner=m3_research" in full
    assert all(o.endswith("=true") for o in full if o.startswith("agent.enable_"))
    assert "agent.enable_planning=false" in m1_agent_overrides("planning_off")
    assert "agent.enable_reflection=false" in m1_agent_overrides("self_correction_off")
