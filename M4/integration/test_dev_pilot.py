"""Verify that the development pair differs only in Memory treatment."""

import argparse
import importlib.util
import sys
from pathlib import Path


def test_pilot_pair_preserves_other_scientific_switches(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "run_dev_pilot.py"
    spec = importlib.util.spec_from_file_location("m4_dev_pilot_test", path)
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    monkeypatch.setattr(sys, "argv", [])
    factory = pilot.driver_module
    arms = {}
    for arm in ["on", "off"]:
        driver = factory()
        captured = {}

        def main(driver=driver, captured=captured, arm=arm):
            captured["overrides"] = driver.m1_agent_overrides(f"m4_dev_pilot_{arm}")
            captured["command"] = list(sys.argv)

        driver.main = main
        monkeypatch.setattr(pilot, "driver_module", lambda driver=driver: driver)
        pilot.worker(
            argparse.Namespace(arm=arm, attempt=1),
            f"m4_dev_pilot_{arm}",
            tmp_path / arm,
        )
        # Repeated Hydra keys are resolved by their last occurrence.
        arms[arm] = dict(item.split("=", 1) for item in captured["overrides"])
        assert captured["command"][captured["command"].index("--split") + 1] == "dev"
        assert arms[arm]["agent/planner"] == "m3_research"
        assert arms[arm]["agent.enable_exploration"] == "false"
        assert arms[arm]["agent.enable_tool_routing"] == "false"
    assert arms["on"]["agent.enable_memory"] == "true"
    assert arms["off"]["agent.enable_memory"] == "false"
    for key in [
        "agent.enable_memory",
        "agent.memory_manager.log_path",
        "agent.capture_path",
    ]:
        arms["on"].pop(key)
        arms["off"].pop(key)
    assert arms["on"] == arms["off"]
