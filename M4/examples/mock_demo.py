"""Synthetic integration demonstration; no material discovery claims."""
import json
import tempfile
from pathlib import Path

from m4_memory import MemoryModule

with tempfile.TemporaryDirectory() as directory:
    memory = MemoryModule(Path(directory) / "evidence.jsonl")
    memory.reset({"run_id": "mock", "episode_id": 0, "elements": ["Li", "O"]})
    memory.record({"event_id": "evaluation:1", "step_id": 1,
                   "candidate_id": "synthetic-structure-A", "status": "evaluated",
                   "composition": {"Li": 2, "O": 1}, "reduced_formula": "Li2O",
                   "e_above_hull": 0.25, "is_stable": False,
                   "provenance": {"source": "synthetic mock; not oracle output"}})
    print("ON:", json.dumps(memory.retrieve(), ensure_ascii=False, indent=2))
    memory.enabled = False
    print("OFF:", json.dumps(memory.retrieve(), ensure_ascii=False))
