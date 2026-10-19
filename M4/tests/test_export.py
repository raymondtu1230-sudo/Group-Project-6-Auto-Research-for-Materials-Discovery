import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "m4_export", Path(__file__).resolve().parents[1] / "export_evidence.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExportTests(unittest.TestCase):
    def test_final_query_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "episode.json"
            output = Path(directory) / "evidence.jsonl"
            source.write_text(json.dumps([
                {"is_stable": False, "phase_diagram_gt": "must-not-copy"},
                {"is_stable": True, "proposal": {"synthetic": True}},
            ]))
            self.assertEqual(module.export_trajectory(source, output, "mock", 0), 2)
            records = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(records[-1]["step_id"], 2)
            source.write_text(json.dumps({"trajectory": [{"is_stable": True}], "phase_diagram_gt": ["hidden"]}))
            wrapped = Path(directory) / "wrapped.jsonl"
            self.assertEqual(module.export_trajectory(source, wrapped, "mock", 0), 1)
            self.assertNotIn("hidden", wrapped.read_text())
            self.assertNotIn("must-not-copy", output.read_text())
            with self.assertRaises(FileExistsError):
                module.export_trajectory(source, output, "mock", 0)
