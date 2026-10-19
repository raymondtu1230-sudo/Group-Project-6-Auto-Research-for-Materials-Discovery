import tempfile
import unittest
from pathlib import Path

from m4_memory import MemoryModule


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "evidence.jsonl"
        self.memory = MemoryModule(self.path)
        self.context = {"run_id": "test", "episode_id": 0, "elements": ["Li", "O"]}
        self.memory.reset(self.context)

    def event(self, identifier="a", **extra):
        return dict(
            event_id=identifier,
            step_id=1,
            candidate_id=identifier,
            status="evaluated",
            composition={"Li": 2, "O": 1},
            **extra,
        )

    def test_retry_and_conflict(self):
        self.assertTrue(self.memory.record(self.event()))
        self.assertFalse(self.memory.record(self.event()))
        with self.assertRaises(ValueError):
            self.memory.record(self.event(is_stable=False))
        self.assertEqual(len(self.path.read_text().splitlines()), 1)

    def test_off_still_logs_and_checkpoint_does_not_enable(self):
        self.memory.record(self.event())
        other = MemoryModule(self.path, enabled=False)
        other.load_state(self.memory.get_state())
        self.assertEqual(other.retrieve()["records"], [])
        other.record(self.event("b"))
        self.assertEqual(len(self.path.read_text().splitlines()), 2)

    def test_episode_isolation(self):
        self.memory.record(self.event())
        self.memory.reset({**self.context, "episode_id": 1})
        self.assertEqual(self.memory.retrieve()["records"], [])
        self.assertTrue(self.memory.record(self.event()))
        with self.assertRaises(ValueError):
            self.memory.record({**self.event("b"), "episode_id": 0})

    def test_polymorphs_not_collapsed_and_proximity(self):
        self.memory.record(self.event("a"))
        self.memory.record(self.event("b"))
        self.memory.record({**self.event("c"), "composition": {"Li": 1, "O": 2}})
        result = self.memory.retrieve({"composition": {"Li": 4, "O": 2}}, limit=2)
        self.assertEqual(result["event_ids"], ["b", "a"])
        result["records"][0]["candidate_id"] = "changed"
        self.assertEqual(self.memory.events[1]["candidate_id"], "b")

    def test_contrasting_outcomes_and_final_event(self):
        self.memory.record(self.event("success", is_stable=True))
        self.memory.record(
            {**self.event("error"), "status": "error", "reason": "timeout"}
        )
        for i in range(8):
            self.memory.record(self.event(str(i)))
        ids = self.memory.retrieve(limit=4)["event_ids"]
        self.assertEqual(len(ids), 4)
        self.assertTrue({"success", "error", "7"} <= set(ids))

    def test_prompt_limit_and_trace_alignment(self):
        self.memory.record(self.event())
        self.assertEqual(self.memory.retrieve(max_chars=1)["event_ids"], [])
        result = self.memory.retrieve(max_chars=200)
        self.assertLessEqual(len(result["summary"]), 200)
        self.assertEqual(
            result["event_ids"], [x["event_id"] for x in result["records"]]
        )

    def test_restore_and_nonfinite_rejection(self):
        self.memory.record(self.event())
        other = MemoryModule(self.path)
        other.load_state(self.memory.get_state())
        self.assertEqual(other.retrieve(), self.memory.retrieve())
        with self.assertRaises(ValueError):
            self.memory.record(self.event("bad", energy_per_atom=float("nan")))
        self.assertEqual(len(self.path.read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
