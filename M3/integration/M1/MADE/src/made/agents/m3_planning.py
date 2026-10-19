"""M3 planning and self-correction plug-ins for ``M1IntegratedAgent``.

``M3ResearchPlanner`` decomposes the discovery goal into sub-goals (one per
element subset of the chemical system, e.g. the Li-O edge or the Li-Mn-O
interior) and runs a plan -> propose batch -> review -> update plan loop over
them. ``M3StuckReplanPolicy`` detects unproductive search (no new discovery in
the last K queries, or repeated formulas) and re-plans toward unvisited,
distant compositions.

Both components use only the public MADE state and post-query observations.
They never call the oracle and never read ``phase_diagram_gt`` or other
evaluator-only fields. All checkpoint state is JSON-serializable.
"""

from __future__ import annotations

import logging
import math
import random
from functools import lru_cache
from itertools import product
from typing import Any

from pymatgen.core.composition import Composition
from pymatgen.core.structure import Structure

from made.agents.base import Plan
from made.agents.planners.grid_search import CompositionStats, GridSearchPlanner
from made.evaluation.metrics import is_smact_valid

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------- helpers
def _subgoal_key(composition: Composition) -> str:
    return "-".join(sorted(el.symbol for el in composition.elements))


def _rkey(value: Any) -> str:
    """Canonical reduced-formula key ("Li2O2", "LiO" and MADE's "Li1 O1" all match)."""
    try:
        composition = (
            value if isinstance(value, Composition) else Composition(str(value))
        )
        return composition.reduced_composition.alphabetical_formula
    except Exception:
        return str(value)


def _fractions(composition: Composition, elements: list[str]) -> list[float]:
    frac = composition.fractional_composition
    return [float(frac[el]) if el in frac else 0.0 for el in elements]


def _distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _progress(record: dict[str, Any]) -> bool:
    """A query counts as progress if it found a new (or, failing that, stable) phase."""
    if "is_newly_discovered" in record:
        return bool(record["is_newly_discovered"])
    return bool(record.get("is_stable", False))


def _observation_formula(observation: dict[str, Any]) -> str | None:
    proposal = observation.get("proposal")
    if isinstance(proposal, dict):
        try:
            return Structure.from_dict(proposal).composition.formula
        except Exception:  # malformed proposal payloads are ignored
            return None
    if isinstance(proposal, Structure):
        return proposal.composition.formula
    return None


@lru_cache(maxsize=32)
def enumerate_compositions(
    elements: tuple[str, ...], max_stoich: int
) -> tuple[str, ...]:
    """SMACT-valid, non-elemental compositions with at most ``max_stoich`` atoms."""
    formulas: list[str] = []
    for amounts in product(range(max_stoich + 1), repeat=len(elements)):
        if sum(amounts) == 0 or sum(amounts) > max_stoich:
            continue
        composition = Composition(dict(zip(elements, amounts, strict=True)))
        if len(composition.elements) > 1 and is_smact_valid(composition):
            formulas.append(composition.formula)
    return tuple(sorted(set(formulas)))


# ---------------------------------------------------------------- planner
class M3ResearchPlanner(GridSearchPlanner):
    """Sub-goal planner with periodic batch review.

    Plan: the system is split into sub-goals by element subset. Propose: each
    batch of ``batch_size`` queries targets one sub-goal, choosing its least
    attempted, most novel compositions. Review: after a batch, every open
    sub-goal is re-scored from observed successes and, when memory is on,
    ``m1_memory`` evidence (new phases, near-hull misses). Update: the best
    scoring sub-goal becomes the next batch target.
    """

    def __init__(
        self,
        batch_size: int = 4,
        coverage_weight: float = 0.5,
        near_hull_threshold: float = 0.1,
        max_attempts_per_composition: int = 2,
        memory_failure_limit: int = 2,
        max_trace: int = 20,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("selection_strategy", "diversity")
        super().__init__(**kwargs)
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        self.seed = kwargs.get("seed")
        self.batch_size = batch_size
        self.coverage_weight = coverage_weight
        self.near_hull_threshold = near_hull_threshold
        self.max_attempts_per_composition = max_attempts_per_composition
        self.memory_failure_limit = memory_failure_limit
        self.max_trace = max_trace
        self.elements: list[str] = []
        self.current_subgoal: str | None = None
        self.batch_used = 0
        self.num_reviews = 0
        self.decision_trace: list[dict[str, Any]] = []

    # -- state updates -------------------------------------------------
    def update_state(self, state: dict[str, Any]) -> None:
        if not self.composition_stats:
            self._initialize(state)
        observation = state.get("last_observation")
        if not observation or not isinstance(observation, dict):
            return
        formula = _observation_formula(observation)
        if formula is None or formula not in self.composition_stats:
            return
        stats = self.composition_stats[formula]
        stats.num_attempts += 1
        if observation.get("is_stable"):
            stats.num_successes += 1
        ehull = _finite(observation.get("e_above_hull"))
        if ehull is not None:
            stats.best_score = max(stats.best_score, -ehull)
            stats.last_score = -ehull
        stats.last_attempted_step = self.current_step
        # Every observed query consumes the current batch, including queries
        # redirected by self-correction, so a review always follows.
        self.batch_used += 1

    def _initialize(self, state: dict[str, Any]) -> None:
        elements = [str(e) for e in state.get("elements", [])]
        if not elements:
            raise ValueError("M3ResearchPlanner requires 'elements' in state")
        self.elements = sorted(elements)
        self.composition_stats = self._init_composition_stats(elements)
        if state.get("phase_diagram_all_entries"):
            try:
                self._update_stats_from_state(state)
            except Exception as error:  # empty/degenerate observed hull
                logger.debug("Skipping initial hull statistics: %s", error)

    # -- planning ------------------------------------------------------
    def propose(
        self, state: dict[str, Any], previous: dict[str, Any] | None = None
    ) -> Plan:
        if not self.composition_stats:
            self._initialize(state)
        if not self.elements:
            self.elements = sorted(
                {
                    el.symbol
                    for s in self.composition_stats.values()
                    for el in s.composition.elements
                }
            )
        memory = self._memory_records(state, previous)
        groups = self._open_subgoals()
        if not groups:  # everything attempted: reopen the full space
            groups = self._subgoals(open_only=False)

        if self.current_subgoal not in groups or self.batch_used >= self.batch_size:
            self.current_subgoal = self._review(groups, memory)
            self.batch_used = 0

        count = self.num_compositions
        remaining = state.get("m1_queries_remaining")
        if isinstance(remaining, int) and remaining > 0:
            count = min(count, remaining)
        compositions = self._select(groups[self.current_subgoal], memory, count)
        self.current_step += 1
        return Plan(compositions=compositions, num_candidates=self.num_candidates)

    def _memory_records(
        self, state: dict[str, Any], previous: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        """Bounded M4/M1 records from ``context["m1_memory"]``.

        M1 sets ``m1_memory`` to ``[]`` when the memory switch is off, so an
        empty list (first query, or memory disabled) simply means "no
        evidence" and the planner falls back to its own attempt counts.
        ``previous["observations"]`` carries the same records and is only
        used if a caller omits ``m1_memory``.
        """
        records = state.get("m1_memory")
        if records is None and previous is not None:
            records = previous.get("observations")
        if not isinstance(records, list):
            return []
        return [r for r in records if isinstance(r, dict)]

    def _subgoals(self, open_only: bool) -> dict[str, list[CompositionStats]]:
        groups: dict[str, list[CompositionStats]] = {}
        for formula in sorted(self.composition_stats):
            stats = self.composition_stats[formula]
            if open_only and stats.num_attempts >= self.max_attempts_per_composition:
                continue
            groups.setdefault(_subgoal_key(stats.composition), []).append(stats)
        return groups

    def _open_subgoals(self) -> dict[str, list[CompositionStats]]:
        return self._subgoals(open_only=True)

    def _review(
        self,
        groups: dict[str, list[CompositionStats]],
        memory: list[dict[str, Any]],
    ) -> str:
        all_groups = self._subgoals(open_only=False)
        evidence: dict[str, dict[str, float]] = {}
        used_ids: list[str] = []
        for record in memory:
            try:
                key = _subgoal_key(Composition(str(record.get("reduced_formula"))))
            except Exception:
                continue
            bucket = evidence.setdefault(key, {"new": 0.0, "near": 0.0})
            ehull = _finite(record.get("e_above_hull"))
            if record.get("is_newly_discovered"):
                bucket["new"] += 1
            elif ehull is not None and ehull <= self.near_hull_threshold:
                bucket["near"] += 1
            used_ids.append(
                str(record.get("event_id", f"query:{record.get('query_count', '?')}"))
            )

        scores: dict[str, float] = {}
        for key in sorted(groups):
            members = all_groups.get(key, groups[key])
            attempts = sum(s.num_attempts for s in members)
            successes = sum(s.num_successes for s in members)
            ev = evidence.get(key, {"new": 0.0, "near": 0.0})
            yield_rate = (successes + ev["new"] + 0.5 * ev["near"] + 1.0) / (
                attempts + 2.0
            )
            unexplored = sum(1 for s in members if s.num_attempts == 0) / max(
                len(members), 1
            )
            scores[key] = yield_rate + self.coverage_weight * unexplored

        best = max(scores.values())
        tied = [key for key, score in scores.items() if math.isclose(score, best)]
        choice = self._rng("review").choice(sorted(tied))
        self.num_reviews += 1
        self.decision_trace.append(
            {
                "step": int(self.current_step),
                "subgoal": choice,
                "scores": {k: round(v, 4) for k, v in scores.items()},
                "memory_used": bool(memory),
                "memory_ids": used_ids[-10:],
            }
        )
        self.decision_trace = self.decision_trace[-self.max_trace :]
        logger.info(
            "M3 review: step=%d subgoal=%s memory_records=%d",
            self.current_step,
            choice,
            len(memory),
        )
        return choice

    def _select(
        self,
        members: list[CompositionStats],
        memory: list[dict[str, Any]],
        count: int,
    ) -> list[Composition]:
        failures: dict[str, int] = {}
        for record in memory:
            if not _progress(record) and not record.get("is_stable"):
                key = _rkey(record.get("reduced_formula"))
                failures[key] = failures.get(key, 0) + 1
        candidates = [
            s
            for s in members
            if failures.get(_rkey(s.composition), 0) < self.memory_failure_limit
        ] or members

        attempted = [
            _fractions(s.composition, self.elements)
            for s in self.composition_stats.values()
            if s.num_attempts > 0
        ] + [_fractions(Composition(el), self.elements) for el in self.elements]

        rng = self._rng("select")
        ranked = sorted(
            candidates,
            key=lambda s: (
                -min(
                    _distance(_fractions(s.composition, self.elements), a)
                    for a in attempted
                )
                / (1 + s.num_attempts),
                rng.random(),
            ),
        )
        selected: list[Composition] = []
        seen_reduced: set[str] = set()
        for stats in ranked:
            if _rkey(stats.composition) in seen_reduced:
                continue
            selected.append(stats.composition)
            seen_reduced.add(_rkey(stats.composition))
            if len(selected) >= max(count, 1):
                break
        return selected

    def _rng(self, purpose: str) -> random.Random:
        # Derived from (seed, step) so checkpoint/resume reproduces decisions.
        return random.Random(f"{self.seed}:{self.current_step}:{purpose}")

    # -- checkpointing -------------------------------------------------
    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        state["m3"] = {
            "elements": list(self.elements),
            "current_subgoal": self.current_subgoal,
            "batch_used": int(self.batch_used),
            "num_reviews": int(self.num_reviews),
            "decision_trace": list(self.decision_trace),
        }
        return state

    def load_state(self, state: dict[str, Any]) -> None:
        super().load_state(state)
        m3 = state.get("m3", {})
        self.elements = list(m3.get("elements", self.elements))
        self.current_subgoal = m3.get("current_subgoal")
        self.batch_used = int(m3.get("batch_used", 0))
        self.num_reviews = int(m3.get("num_reviews", 0))
        self.decision_trace = list(m3.get("decision_trace", []))


# ---------------------------------------------------------------- self-correction
class M3StuckReplanPolicy:
    """Detect a stalled search and re-plan toward unvisited compositions.

    Stuck signals over the last ``window`` observed queries:
    - ``no_progress``: no newly discovered (or stable) phase;
    - ``repetition``: the plan targets a reduced formula already tried
      ``max_repeat`` times in the window.
    On a signal (outside the cooldown), the plan's compositions are replaced
    by valid compositions that are least visited and farthest from the recent
    window. Consecutive stalls escalate: from level 2 the candidate count per
    composition is doubled (generation is not an oracle query; M1 still caps
    the plan by remaining budget).
    """

    def __init__(
        self,
        window: int = 6,
        max_repeat: int = 2,
        cooldown: int = 3,
        max_stoichiometry: int = 20,
        max_candidates: int = 32,
        seed: int | None = None,
        max_history: int = 64,
        max_events: int = 50,
    ) -> None:
        if window < 1 or max_repeat < 1 or cooldown < 0:
            raise ValueError("window/max_repeat must be positive, cooldown >= 0")
        self.window = window
        self.max_repeat = max_repeat
        self.cooldown = cooldown
        self.max_stoichiometry = max_stoichiometry
        self.max_candidates = max_candidates
        self.seed = seed
        self.max_history = max(max_history, window)
        self.max_events = max_events
        self.history: list[dict[str, Any]] = []
        self.visits: dict[str, int] = {}
        self.last_query = 0
        self.last_replan_query = -(10**9)
        self.level = 0
        self.events: list[dict[str, Any]] = []

    def revise_plan(self, plan: Plan, context: dict[str, Any]) -> Plan:
        if not isinstance(plan, Plan):
            raise TypeError("M3StuckReplanPolicy.revise_plan expects a MADE Plan")
        self._ingest(context)
        reason = self._stuck_reason(plan)
        if reason is None:
            return plan
        query = int(context.get("query_count", 0))
        if query - self.last_replan_query < self.cooldown:
            return plan

        compositions = self._replan(plan, context)
        if not compositions:
            return plan
        self.level += 1
        self.last_replan_query = query
        num_candidates = int(plan.num_candidates)
        if self.level >= 2:
            num_candidates = min(max(num_candidates * 2, 1), self.max_candidates)
        self.events.append(
            {
                "query": query,
                "reason": reason,
                "level": self.level,
                "before": [c.formula for c in plan.compositions],
                "after": [c.formula for c in compositions],
            }
        )
        self.events = self.events[-self.max_events :]
        logger.info(
            "M3 re-plan: query=%d reason=%s level=%d before=%s after=%s",
            query,
            reason,
            self.level,
            self.events[-1]["before"],
            self.events[-1]["after"],
        )
        return Plan(
            compositions=compositions,
            num_candidates=num_candidates,
            constraints=dict(plan.constraints),
        )

    # -- evidence --------------------------------------------------------
    def _ingest(self, context: dict[str, Any]) -> None:
        query = context.get("query_count", 0)
        observation = context.get("last_observation")
        if not isinstance(query, int) or query <= self.last_query:
            return
        self.last_query = query
        if not isinstance(observation, dict):
            return
        formula = _observation_formula(observation)
        record = {
            "query": query,
            "formula": formula,
            "reduced_formula": str(observation.get("reduced_formula", "")),
            "progress": _progress(observation),
        }
        self.history.append(record)
        self.history = self.history[-self.max_history :]
        if formula:
            self.visits[formula] = self.visits.get(formula, 0) + 1
        if record["progress"]:
            self.level = 0

    def _recent(self) -> list[dict[str, Any]]:
        return self.history[-self.window :]

    def _stuck_reason(self, plan: Plan) -> str | None:
        recent = self._recent()
        if not recent:
            return None
        counts: dict[str, int] = {}
        for record in recent:
            key = self._reduced(record)
            counts[key] = counts.get(key, 0) + 1
        planned = {_rkey(c) for c in plan.compositions}
        if any(counts.get(f, 0) >= self.max_repeat for f in planned):
            return "repetition"
        if len(recent) >= self.window and not any(r["progress"] for r in recent):
            return "no_progress"
        return None

    @staticmethod
    def _reduced(record: dict[str, Any]) -> str:
        return _rkey(record.get("formula") or record.get("reduced_formula", ""))

    # -- re-planning -----------------------------------------------------
    def _replan(self, plan: Plan, context: dict[str, Any]) -> list[Composition]:
        elements = sorted(str(e) for e in context.get("elements", []))
        if len(elements) < 2:
            return []
        max_stoich = int(context.get("max_stoichiometry") or self.max_stoichiometry)
        pool = enumerate_compositions(tuple(elements), max_stoich)
        recent_reduced = {self._reduced(r) for r in self._recent()}
        recent_vectors = [
            _fractions(Composition(r["formula"]), elements)
            for r in self._recent()
            if r.get("formula")
        ] or [_fractions(c, elements) for c in plan.compositions]

        rng = random.Random(f"{self.seed}:{self.last_query}:{self.level}")
        options = [Composition(f) for f in pool if _rkey(f) not in recent_reduced]
        if not options:
            return []
        options.sort(
            key=lambda c: (
                self.visits.get(c.formula, 0),
                -min(_distance(_fractions(c, elements), v) for v in recent_vectors),
                rng.random(),
            )
        )
        count = max(len(plan.compositions), 1)
        chosen: list[Composition] = []
        reduced_seen: set[str] = set()
        for composition in options:
            if _rkey(composition) in reduced_seen:
                continue
            chosen.append(composition)
            reduced_seen.add(_rkey(composition))
            if len(chosen) >= count:
                break
        return chosen

    # -- checkpointing ---------------------------------------------------
    def get_state(self) -> dict[str, Any]:
        return {
            "history": list(self.history),
            "visits": dict(self.visits),
            "last_query": int(self.last_query),
            "last_replan_query": int(self.last_replan_query),
            "level": int(self.level),
            "events": list(self.events),
        }

    def load_state(self, state: dict[str, Any]) -> None:
        self.history = list(state.get("history", []))[-self.max_history :]
        self.visits = {str(k): int(v) for k, v in state.get("visits", {}).items()}
        self.last_query = int(state.get("last_query", 0))
        self.last_replan_query = int(state.get("last_replan_query", -(10**9)))
        self.level = int(state.get("level", 0))
        self.events = list(state.get("events", []))[-self.max_events :]
