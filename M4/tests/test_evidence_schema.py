import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from m4_memory.m1_adapter import M4MemoryManager

spec = importlib.util.spec_from_file_location(
    "m4_export_schema", Path(__file__).resolve().parents[1] / "export_evidence.py"
)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class EvidenceSchemaTests(unittest.TestCase):
    def observation(self):
        return {
            "proposal": {
                "sites": [
                    {"species": [{"element": "Li", "occu": 1}]},
                    {"species": [{"element": "Li", "occu": 1}]},
                    {"species": [{"element": "O", "occu": 1}]},
                ]
            },
            "reduced_formula": "Li2O",
            "is_stable": False,
            "e_above_hull": 0.3,
            "phase_diagram_gt": "never-copy",
        }

    def test_adapter_and_export_share_chemical_identity_and_outcome(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manager = M4MemoryManager(base / "online.jsonl", "run", 0)
            manager.update_state(
                {
                    "elements": ["Li", "Na", "O"],
                    "query_count": 1,
                    "last_observation": self.observation(),
                }
            )
            source = base / "episode.json"
            source.write_text(
                json.dumps(
                    {
                        "trajectory": [self.observation()],
                        "phase_diagram_gt": "never-copy",
                    }
                )
            )
            exporter.export_trajectory(
                source, base / "export.jsonl", "run", 0, elements=["O", "Na", "Li"]
            )
            online = manager.get_memory()[0]
            exported = json.loads((base / "export.jsonl").read_text())
            for key in ("elements", "composition", "outcome", "reason"):
                self.assertEqual(online[key], exported[key])
            self.assertEqual(exported["elements"], ["Li", "Na", "O"])
            self.assertEqual(exported["composition"], {"Li": 2, "O": 1})
            self.assertEqual(exported["outcome"], "unstable")
            self.assertNotIn("never-copy", json.dumps(exported))
            self.assertNotIn("proposal", online)

    def test_wrong_system_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "episode.json"
            source.write_text(json.dumps([self.observation()]))
            with self.assertRaises(ValueError):
                exporter.export_trajectory(
                    source, base / "export.jsonl", "run", 0, elements=["Li"]
                )
            self.assertFalse((base / "export.jsonl").exists())

    def test_missing_structure_stays_unknown_and_episode_remains_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "episode.json"
            source.write_text(json.dumps([{}]))
            exporter.export_trajectory(
                source, base / "export.jsonl", "run", 1, elements=["Li", "O"]
            )
            event = json.loads((base / "export.jsonl").read_text())
            self.assertIsNone(event["composition"])
            self.assertEqual(event["outcome"], "unknown")
            self.assertEqual(event["episode_id"], 1)


if __name__ == "__main__":
    unittest.main()
