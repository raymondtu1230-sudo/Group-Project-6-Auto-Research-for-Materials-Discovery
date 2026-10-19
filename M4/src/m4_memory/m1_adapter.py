"""Adapter to the M1 MemoryManager contract, ready for framework adoption."""

import copy
import json

from .evidence import candidate_composition, normalize_elements, observed_outcome
from .memory import MemoryModule


class M4MemoryManager:
    """Only ingest allowlisted post-query scalars, never the whole MADE state.

    One manager is scoped to one configured episode. M1 must create a fresh
    instance per episode or restore a checkpoint for the same identity.
    """

    OBSERVATION_FIELDS = (
        "reduced_formula",
        "energy_per_atom",
        "formation_energy_per_atom",
        "e_above_hull",
        "is_stable",
        "is_newly_discovered",
    )

    def __init__(self, log_path, run_id, episode_id, limit=8, max_chars=4000):
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a nonnegative integer")
        if not isinstance(max_chars, int) or max_chars < 0:
            raise ValueError("max_chars must be a nonnegative integer")
        self.memory = MemoryModule(log_path)
        self.run_id = run_id
        self.episode_id = episode_id
        self.limit = limit
        self.max_chars = max_chars
        self.last_query = 0

    def update_state(self, state):
        elements = normalize_elements(state["elements"])
        if self.memory.context is None:
            self.memory.reset(
                {
                    "run_id": self.run_id,
                    "episode_id": self.episode_id,
                    "elements": elements,
                }
            )
        elif elements != self.memory.context["elements"]:
            raise ValueError("Create a fresh manager for a different chemical system")
        step = state.get("query_count", 0)
        if not isinstance(step, int) or isinstance(step, bool) or step < 0:
            raise ValueError("query_count must be a nonnegative integer")
        if step < self.last_query:
            raise ValueError("Query counter decreased: start a new episode manager")
        observation = state.get("last_observation")
        if not observation or step == 0:
            return
        if not isinstance(observation, dict):
            raise ValueError("last_observation must be a dict")
        # A full structure/oracle_result may contain complex or private payloads.
        # They remain in the official trajectory; link by query rather than copy.
        event = {
            "event_id": f"evaluation:{step}",
            "candidate_id": f"query:{step}",
            "step_id": step,
            "query_count": step,
            "status": "evaluated",
        }
        for field in self.OBSERVATION_FIELDS:
            if field in observation:
                value = observation[field]
                if not isinstance(value, (str, int, float, bool, type(None))):
                    raise ValueError(f"{field} must be a JSON scalar")
                event[field] = value
        event["composition"] = candidate_composition(
            observation.get("proposal"), elements
        )
        event["outcome"], event["reason"] = observed_outcome(observation)
        json.dumps(event, allow_nan=False)
        self.memory.record(event)
        self.last_query = step

    def get_memory(self):
        """Bounded JSON records for context['m1_memory']; no direct oracle calls."""
        if self.memory.context is None:
            return []
        # M1 provides no target composition in get_memory(). Relevance by
        # composition is available through the core API, not claimed here.
        result = self.memory.retrieve(limit=self.limit, max_chars=self.max_chars)
        records = []
        for record in result["records"]:
            if (
                len(json.dumps(records + [record], ensure_ascii=False, allow_nan=False))
                <= self.max_chars
            ):
                records.append(record)
        return copy.deepcopy(records)

    def get_state(self):
        return {
            "schema_version": 1,
            "last_query": self.last_query,
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "memory": self.memory.get_state() if self.memory.context else None,
        }

    def load_state(self, state):
        if state.get("schema_version") != 1:
            raise ValueError("Unsupported adapter checkpoint")
        if state["run_id"] != self.run_id or state["episode_id"] != self.episode_id:
            raise ValueError("Checkpoint identity differs from configured episode")
        if state["memory"] is not None:
            self.memory.load_state(state["memory"])
        else:
            self.memory.context = None
            self.memory.events = []
            self.memory._ids = set()
        self.last_query = state["last_query"]
