"""M5 exploration policy: budget-annealed UCB over composition space.

Implements the M1 plug-in contract ``ExplorationPolicy.adjust_plan(plan,
context) -> Plan``. The policy re-composes the plan's composition list from an
exploit pool (the planner's incoming compositions, kept first) and an explore
pool (unqueried stoichiometries ranked by UCB against a Gaussian-process
surrogate fitted on observed ``e_above_hull`` values from ``m1_memory``).

Design note: M5/DESIGN.md. The policy never calls the oracle, never reads
hidden labels, and only uses post-query observations supplied via context.
All state is JSON-serializable for checkpointing and for M4's evidence log.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from pymatgen.core.composition import Composition

from made.agents.base import Plan


def _fraction_vector(composition: Composition, elements: list[str]) -> list[float]:
    """Element-fraction feature vector over the full chemical system."""
    total = sum(composition.get(el, 0.0) for el in elements)
    if total <= 0:
        return [0.0 for _ in elements]
    return [composition.get(el, 0.0) / total for el in elements]


def _rbf_kernel(x_a: np.ndarray, x_b: np.ndarray, length_scale: float) -> np.ndarray:
    """Squared-exponential kernel with unit signal variance."""
    diff = x_a[:, None, :] - x_b[None, :, :]
    sq_dist = np.sum(diff * diff, axis=-1)
    return np.exp(-0.5 * sq_dist / (length_scale * length_scale))


def _gp_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    length_scale: float,
    noise: float,
) -> tuple[np.ndarray, np.ndarray]:
    """GP regression posterior mean/std. Cold start -> mean 0, std 1."""
    if len(x_train) == 0:
        return np.zeros(len(x_test)), np.ones(len(x_test))
    y_centered = y_train - float(np.mean(y_train))
    kernel = _rbf_kernel(x_train, x_train, length_scale)
    kernel += (noise + 1e-10) * np.eye(len(x_train))
    try:
        chol = np.linalg.cholesky(kernel)
    except np.linalg.LinAlgError:
        kernel += 1e-6 * np.eye(len(x_train))
        chol = np.linalg.cholesky(kernel)
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, y_centered))
    k_star = _rbf_kernel(x_train, x_test, length_scale)
    mu = k_star.T @ alpha + float(np.mean(y_train))
    solved = np.linalg.solve(chol, k_star)
    var = 1.0 - np.sum(solved * solved, axis=0)
    sigma = np.sqrt(np.clip(var, 0.0, None))
    return mu, sigma


def _enumerate_stoichiometries(
    elements: list[str], max_stoichiometry: int, max_pool: int
) -> list[Composition]:
    """Reduced integer compositions over the system, total atoms <= max.

    Enumerates compositions with at least two distinct elements (discovery
    targets are compounds), deduplicated by reduced formula, sorted for
    determinism, and truncated to ``max_pool``.
    """
    seen: set[str] = set()
    compositions: list[Composition] = []
    counts = [0] * len(elements)

    def visit(position: int, remaining: int) -> None:
        if len(compositions) >= max_pool:
            return
        if position == len(elements) - 1:
            counts[position] = remaining
            if sum(1 for c in counts if c > 0) >= 2:
                comp = Composition(
                    {el: c for el, c in zip(elements, counts, strict=True) if c > 0}
                )
                key = comp.reduced_formula
                if key not in seen:
                    seen.add(key)
                    compositions.append(comp)
            return
        for amount in range(remaining + 1):
            counts[position] = amount
            visit(position + 1, remaining - amount)

    for total in range(2, max_stoichiometry + 1):
        visit(0, total)
    compositions.sort(key=lambda c: c.reduced_formula)
    return compositions[:max_pool]


class UCBExplorationPolicy:
    """Budget-annealed UCB exploration over composition space.

    ``alpha(t) = alpha0 * (queries_remaining / budget) ** gamma`` sets the
    share of exploration compositions appended to the plan; ``beta(t)`` follows
    the same schedule as the UCB exploration weight. Early episodes buy
    information; late episodes exploit. Deterministic under ``seed``.
    """

    def __init__(
        self,
        alpha0: float = 0.5,
        gamma: float = 1.0,
        beta0: float = 2.0,
        seed: int = 0,
        max_stoichiometry: int = 8,
        length_scale: float = 0.35,
        noise: float = 1e-4,
        max_pool: int = 512,
        log_path: str | None = None,
    ) -> None:
        if not 0.0 <= alpha0 <= 1.0:
            raise ValueError("alpha0 must be in [0, 1]")
        if gamma <= 0 or beta0 < 0:
            raise ValueError("gamma must be positive and beta0 non-negative")
        self.alpha0 = float(alpha0)
        self.gamma = float(gamma)
        self.beta0 = float(beta0)
        self.seed = int(seed)
        self.max_stoichiometry = int(max_stoichiometry)
        self.length_scale = float(length_scale)
        self.noise = float(noise)
        self.max_pool = int(max_pool)
        # Optional per-episode JSONL sidecar (M4 requested). Each adjust_plan
        # call appends one line; parent dirs are created lazily.
        self.log_path = log_path
        self.decision_log: list[dict[str, Any]] = []
        # Cumulative queried-formula set. ``m1_memory`` may be bounded (e.g.
        # M4's manager serves at most `limit` recent records), so formulas that
        # fall out of memory would otherwise be re-proposable. The policy
        # accumulates every formula it ever observes across the episode.
        self._queried_history: set[str] = set()

    # -- surrogate inputs -------------------------------------------------

    def _observations(
        self, context: dict[str, Any]
    ) -> tuple[list[list[float]], list[float], set[str]]:
        """Feature vectors, e_above_hull targets, queried reduced formulas."""
        elements = sorted(context.get("elements") or [])
        xs: list[list[float]] = []
        ys: list[float] = []
        queried: set[str] = set()
        for record in context.get("m1_memory") or []:
            formula = record.get("reduced_formula")
            if not formula:
                continue
            queried.add(formula)
            e_hull = record.get("e_above_hull")
            if e_hull is None or not math.isfinite(float(e_hull)):
                continue
            try:
                comp = Composition(formula)
            except (ValueError, KeyError):
                continue
            xs.append(_fraction_vector(comp, elements))
            ys.append(float(e_hull))
        return xs, ys, queried

    # -- main hook ----------------------------------------------------------

    def adjust_plan(self, plan: Plan, context: dict[str, Any]) -> Plan:
        elements = sorted(context.get("elements") or [])
        incoming = list(plan.compositions)
        remaining = context.get("m1_queries_remaining")
        used = int(context.get("m1_queries_used") or context.get("query_count") or 0)
        budget = (used + remaining) if remaining is not None else None

        fraction_remaining = (
            max(remaining, 0) / budget if budget else 1.0
        )
        alpha_t = self.alpha0 * fraction_remaining**self.gamma
        beta_t = self.beta0 * fraction_remaining**self.gamma
        # Round half up (Python's round() is banker's rounding; round(0.5)==0
        # would silently suppress exploration for single-composition plans).
        n_explore = min(int(alpha_t * len(incoming) + 0.5), self.max_pool)
        if not elements:
            n_explore = 0

        picks: list[Composition] = []
        stats: dict[str, Any] = {}
        if n_explore > 0:
            xs, ys, queried = self._observations(context)
            # Never re-propose a formula seen this episode, even if it fell out
            # of the bounded m1_memory window.
            queried = queried | self._queried_history
            pool = [
                comp
                for comp in _enumerate_stoichiometries(
                    elements, self.max_stoichiometry, self.max_pool
                )
                if comp.reduced_formula not in queried
                and comp.reduced_formula
                not in {c.reduced_formula for c in incoming}
            ]
            if pool:
                x_pool = np.array([_fraction_vector(c, elements) for c in pool])
                mu, sigma = _gp_predict(
                    np.array(xs) if xs else np.empty((0, len(elements))),
                    np.array(ys),
                    x_pool,
                    self.length_scale,
                    self.noise,
                )
                ucb = -mu + beta_t * sigma
                order = sorted(
                    range(len(pool)),
                    key=lambda i: (
                        -float(ucb[i]),
                        pool[i].reduced_formula,
                    ),
                )
                chosen = order[:n_explore]
                picks = [pool[i] for i in chosen]
                stats = {
                    "ucb_mean": [float(mu[i]) for i in chosen],
                    "ucb_std": [float(sigma[i]) for i in chosen],
                }

        mode = "mixed" if picks and incoming else ("explore" if picks else "exploit")
        # Record this decision's outgoing formulas as attempted, so later
        # steps never re-propose them even if memory forgets.
        self._queried_history.update(
            c.reduced_formula for c in incoming + picks
        )
        record = {
            "step": used,
            "query_count": used,
            "m1_queries_remaining": remaining,
            "mode": mode,
            "incoming_compositions": [c.reduced_formula for c in incoming],
            "outgoing_compositions": [c.reduced_formula for c in incoming + picks],
            "composition_source": ["planner"] * len(incoming)
            + ["ucb_explore"] * len(picks),
            "alpha_t": alpha_t,
            "beta": beta_t,
            "rationale": (
                f"alpha={alpha_t:.2f}, {len(picks)}/{len(incoming) + len(picks)}"
                " slots to unexplored stoichiometries"
                if picks
                else f"alpha={alpha_t:.2f}, pure exploitation of planner plan"
            ),
            **stats,
        }
        self.decision_log.append(record)
        if self.log_path:
            self._append_jsonl(record)
        return Plan(
            compositions=incoming + picks,
            num_candidates=int(plan.num_candidates),
            constraints=dict(plan.constraints),
        )

    def _append_jsonl(self, record: dict[str, Any]) -> None:
        """Append one decision record to the per-episode JSONL sidecar."""
        path = Path(self.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    # -- checkpointing ------------------------------------------------------

    def get_state(self) -> dict[str, Any]:
        return {
            "decision_log": list(self.decision_log),
            "queried_formulas": sorted(self._queried_history),
        }

    def load_state(self, state: dict[str, Any]) -> None:
        self.decision_log = list(state.get("decision_log", []))
        self._queried_history = set(state.get("queried_formulas", []))
