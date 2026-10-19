"""Evidence persistence and deterministic retrieval, without oracle access."""

import copy
import json
import math
from pathlib import Path


class MemoryModule:
    SCHEMA_VERSION = 1

    def __init__(self, log_path, enabled=True):
        self.log_path = Path(log_path)
        self.enabled = enabled
        self.context = None
        self.events = []
        self._ids = set()

    def reset(self, context):
        """Start an episode. Never implicitly import another episode's history."""
        required = {"run_id", "episode_id", "elements"}
        if not required <= context.keys():
            raise ValueError(f"context requires {sorted(required)}")
        if not context["elements"]:
            raise ValueError("elements must not be empty")
        self.context = copy.deepcopy(context)
        self.events = []
        self._ids = set()

    def _require_context(self):
        if self.context is None:
            raise RuntimeError("Call reset(context) or load_state(state) first")

    def _key(self, event):
        return (str(event["run_id"]), str(event["episode_id"]), event["event_id"])

    def _read_log(self):
        if not self.log_path.exists():
            return []
        with self.log_path.open(encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]

    def record(self, event):
        """Append once. Identical retries return False; conflicting IDs raise."""
        self._require_context()
        item = copy.deepcopy(event)
        required = {"event_id", "step_id", "candidate_id", "status"}
        if not required <= item.keys():
            raise ValueError(f"event requires {sorted(required)}")
        if not isinstance(item["event_id"], str) or not item["event_id"]:
            raise ValueError("event_id must be a nonempty string")
        if item["status"] not in {"evaluated", "rejected", "error"}:
            raise ValueError("status must be evaluated, rejected or error")
        for name in ("run_id", "episode_id", "elements"):
            if name in item and item[name] != self.context[name]:
                raise ValueError(f"event {name} differs from active episode")
            item[name] = copy.deepcopy(self.context[name])
        item["schema_version"] = self.SCHEMA_VERSION
        # Validate serialization before changing memory or touching disk.
        encoded = json.dumps(item, ensure_ascii=False, allow_nan=False, sort_keys=True)
        key = self._key(item)
        for existing in self._read_log():
            if self._key(existing) == key:
                if existing != item:
                    raise ValueError("Conflicting content for existing event_id")
                if key not in self._ids:
                    self.events.append(item)
                    self._ids.add(key)
                return False
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(encoded + "\n")
        self.events.append(item)
        self._ids.add(key)
        return True

    @staticmethod
    def _fractions(composition):
        if not composition:
            return {}
        if any(
            not isinstance(v, (float, int)) or not math.isfinite(v) or v <= 0
            for v in composition.values()
        ):
            raise ValueError("composition amounts must be finite and positive")
        total = sum(composition.values())
        return {k: v / total for k, v in composition.items()}

    def retrieve(self, query=None, limit=8, max_chars=4000):
        """Return bounded evidence; OFF exposes no retrieved evidence."""
        self._require_context()
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a nonnegative integer")
        if not isinstance(max_chars, int) or max_chars < 0:
            raise ValueError("max_chars must be a nonnegative integer")
        if not self.enabled or limit == 0 or max_chars == 0:
            return {"event_ids": [], "records": [], "summary": ""}
        query = query or {}
        if "elements" in query and set(query["elements"]) != set(
            self.context["elements"]
        ):
            raise ValueError("query chemical system differs from active episode")
        target = self._fractions(query.get("composition"))

        def rank(pair):
            index, item = pair
            fractions = self._fractions(item.get("composition"))
            distance = (
                sum(
                    abs(target.get(k, 0) - fractions.get(k, 0))
                    for k in target.keys() | fractions.keys()
                )
                if target and fractions
                else float("inf")
            )
            return (distance, -index)

        ordered = [item for _, item in sorted(enumerate(self.events), key=rank)]
        selected = ordered[:limit]
        # Reserve bounded slots for contrasting outcomes and the latest trial.
        reserves = [
            next(
                (
                    x
                    for x in reversed(self.events)
                    if x.get("status") == "evaluated" and x.get("is_stable") is True
                ),
                None,
            ),
            next(
                (
                    x
                    for x in reversed(self.events)
                    if x.get("status") in {"error", "rejected"}
                    or x.get("is_stable") is False
                ),
                None,
            ),
            self.events[-1] if self.events else None,
        ]
        if limit >= 4:
            reserved = []
            for item in reserves:
                if item is not None and item not in reserved:
                    reserved.append(item)
            selected = [x for x in ordered if x not in reserved][
                : limit - len(reserved)
            ] + reserved
        lines = []
        included = []
        for item in selected:
            label = item.get("reduced_formula", item["candidate_id"])
            line = (
                f"[{item['event_id']}] {label}; status={item['status']}; "
                f"observed_stable={item.get('is_stable', 'unknown')}; "
                f"e_above_hull_at_evaluation={item.get('e_above_hull', 'unknown')}"
            )
            if len("\n".join(lines + [line])) <= max_chars:
                lines.append(line)
                included.append(item)
        return {
            "event_ids": [x["event_id"] for x in included],
            "records": copy.deepcopy(included),
            "summary": "\n".join(lines),
        }

    def get_state(self):
        self._require_context()
        return copy.deepcopy(
            {
                "schema_version": self.SCHEMA_VERSION,
                "context": self.context,
                "events": self.events,
            }
        )

    def load_state(self, state):
        """Restore logical state; runtime ON/OFF configuration remains unchanged."""
        if state.get("schema_version") != self.SCHEMA_VERSION:
            raise ValueError("Unsupported schema_version")
        # Restore via normal append/deduplication; earlier valid events may be persisted
        # if a later checkpoint event conflicts. This is not a transactional restore.
        restored = MemoryModule(self.log_path, self.enabled)
        restored.reset(state["context"])
        for event in state["events"]:
            restored.record(event)
        self.context = restored.context
        self.events = restored.events
        self._ids = restored._ids
