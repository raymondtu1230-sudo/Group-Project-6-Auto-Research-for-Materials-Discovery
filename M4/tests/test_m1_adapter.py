import json
import tempfile
import unittest
from pathlib import Path

from m4_memory.m1_adapter import M4MemoryManager


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "events.jsonl"
        self.adapter = M4MemoryManager(self.path, "mock", 0)
        self.state = {
            "elements": ["Li", "O"],
            "query_count": 1,
            "last_observation": {
                "reduced_formula": "Li2O", "is_stable": False, "e_above_hull": 0.3
            },
        }

    def test_allowlist_no_mutation_and_dedup(self):
        state = {**self.state, "phase_diagram_gt": "DO_NOT_COPY"}
        state["last_observation"] = {**state["last_observation"], "api_key": "secret"}
        before = json.dumps(state)
        self.adapter.update_state(state)
        self.adapter.update_state(state)
        self.assertEqual(json.dumps(state), before)
        records = self.adapter.get_memory()
        self.assertEqual(len(records), 1)
        self.assertNotIn("secret", json.dumps(self.adapter.get_state()))
        self.assertNotIn("DO_NOT_COPY", json.dumps(records))

    def test_checkpoint_roundtrip(self):
        self.adapter.update_state(self.state)
        checkpoint = json.loads(json.dumps(self.adapter.get_state()))
        restored = M4MemoryManager(self.path, "mock", 0)
        restored.load_state(checkpoint)
        restored.update_state(self.state)
        self.assertEqual(restored.get_memory(), self.adapter.get_memory())

    def test_bad_output_and_episode_reset(self):
        with self.assertRaises(ValueError):
            self.adapter.update_state(
                {**self.state, "last_observation": {"is_stable": []}}
            )
        self.adapter.update_state(self.state)
        with self.assertRaises(ValueError):
            self.adapter.update_state({**self.state, "query_count": 0})

    def test_published_switch_contract_simulation(self):
        # Simulates the documented boundary, not the unavailable real M1 agent.
        self.adapter.update_state(self.state)
        for enabled in (True, False):
            context = {"m1_memory": self.adapter.get_memory() if enabled else []}
            self.assertEqual(bool(context["m1_memory"]), enabled)


if __name__ == "__main__":
    unittest.main()
