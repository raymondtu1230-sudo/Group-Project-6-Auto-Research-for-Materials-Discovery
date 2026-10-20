"""Optional M1 subclass for public proposal-stage audit; no oracle interception."""

import json
from collections import Counter

from made.agents.m1_integrated import M1IntegratedAgent

from .evidence import candidate_composition, normalize_elements
from .memory import MemoryModule


def _fingerprint(structure):
    return json.dumps(structure.as_dict(), sort_keys=True, allow_nan=False)


class _Stage:
    def __init__(self, delegate, owner, name):
        self.delegate, self.owner, self.name = delegate, owner, name

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def generate(self, plan, context):
        try:
            result = self.delegate.generate(plan, context)
        except Exception as exc:
            self.owner._capture(
                context, "error", self.name, error_type=type(exc).__name__
            )
            raise
        if not result:
            self.owner._capture(context, "error", self.name, reason="empty_generation")
        return result

    def filter(self, candidates, context, *args, **kwargs):
        try:
            result = self.delegate.filter(candidates, context, *args, **kwargs)
        except Exception as exc:
            self.owner._capture(
                context, "error", self.name, error_type=type(exc).__name__
            )
            raise
        filtered = result[0] if isinstance(result, tuple) else result
        kept = Counter(_fingerprint(item) for item in filtered)
        fallback = not filtered
        for index, item in enumerate(candidates):
            key = _fingerprint(item)
            if kept[key]:
                kept[key] -= 1
            else:
                self.owner._capture(
                    context,
                    "rejected",
                    self.name,
                    reason="candidate_not_returned_by_filter",
                    candidate_index=index,
                    composition=candidate_composition(
                        item.as_dict(), context["elements"]
                    ),
                    reduced_formula=item.composition.reduced_formula,
                    proposal=item.as_dict(),
                    rejection_scope="filter_decision",
                    fallback_to_unfiltered=fallback,
                    evaluated=None,
                )
        return result


class CapturedM1IntegratedAgent(M1IntegratedAgent):
    """Delegate scientific decisions to M1; audit optional proposal-stage events.

    Enable identically in both arms. Events never enter m1_memory. Filter rejects
    are not oracle outcomes. Oracle/runner exceptions are outside this boundary.
    """

    def __init__(self, *, capture_path, capture_run_id, capture_episode_id, **kwargs):
        super().__init__(**kwargs)
        self.capture = MemoryModule(capture_path, enabled=False)
        self.capture_identity = (capture_run_id, capture_episode_id)
        self.capture_sequence = 0
        original = self.generator
        wrappers = {}
        for name, generator in self.generators.items():
            # Preserve alias identity when the same object has multiple names.
            if id(generator) not in wrappers:
                wrappers[id(generator)] = _Stage(generator, self, f"generator:{name}")
            self.generators[name] = wrappers[id(generator)]
        self.generator = wrappers[id(original)]
        self.filter = _Stage(self.filter, self, "filter")

    def _capture(self, context, status, stage, **fields):
        elements = normalize_elements(context["elements"])
        if self.capture.context is None:
            self.capture.reset(
                {
                    "run_id": self.capture_identity[0],
                    "episode_id": self.capture_identity[1],
                    "elements": elements,
                }
            )
        elif elements != self.capture.context["elements"]:
            raise ValueError("Create a fresh capture agent per chemical system")
        used = context.get("m1_queries_used", context.get("query_count", 0))
        self.capture_sequence += 1
        event_id = f"proposal:{used}:{stage}:{self.capture_sequence}"
        self.capture.record(
            {
                "event_id": event_id,
                "candidate_id": event_id,
                "step_id": used + 1,
                "query_count": used,
                "status": status,
                "stage": stage,
                "m1_queries_remaining": context.get("m1_queries_remaining"),
                **fields,
            }
        )

    def get_state(self):
        state = super().get_state()
        state["m4_capture"] = {
            "schema_version": 1,
            "run_id": self.capture_identity[0],
            "episode_id": self.capture_identity[1],
            "sequence": self.capture_sequence,
            "evidence": self.capture.get_state() if self.capture.context else None,
        }
        return state

    def load_state(self, state):
        audit = state.get("m4_capture")
        if audit is not None:
            if (
                audit.get("schema_version") != 1
                or (audit.get("run_id"), audit.get("episode_id"))
                != self.capture_identity
            ):
                raise ValueError("Capture checkpoint identity/version mismatch")
            sequence = audit.get("sequence")
            if type(sequence) is not int or sequence < 0:
                raise ValueError("Invalid capture sequence")
        super().load_state(state)
        if audit is not None:
            if audit["evidence"] is not None:
                self.capture.load_state(audit["evidence"])
            self.capture_sequence = audit["sequence"]
