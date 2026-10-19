"""Observed-feedback tool routing through the existing M1 plug-in interface.

The router reads only the query count, remaining budget, and last observation.
It selects a configured generator; generation and oracle evaluation stay in
MADE's existing workflow.  The generation adapters add reproducible checkpoint
state without changing the upstream structure-generation algorithms.
"""

from __future__ import annotations

import json
import math
import random
from collections.abc import Mapping, Sequence
from typing import Any

from pymatgen.core.structure import Structure

from made.agents.base import Plan
from made.agents.generators.chemeleon import ChemeleonGenerator
from made.agents.generators.random import RandomGenerator


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def _tuples(value: Any) -> Any:
    return tuple(_tuples(item) for item in value) if isinstance(value, list) else value


class CheckpointedRandomGenerator(RandomGenerator):
    """MADE RandomGenerator with its own RNG restored from JSON checkpoints."""

    def get_state(self) -> dict[str, Any]:
        return {"version": 1, "rng": json.loads(json.dumps(self._rng.getstate()))}

    def load_state(self, state: dict[str, Any]) -> None:
        if state.get("version") != 1:
            raise ValueError("Unsupported random-generator checkpoint version")
        self._rng.setstate(_tuples(state["rng"]))


class CheckpointedChemeleonGenerator(ChemeleonGenerator):
    """Seed each upstream Chemeleon call and preserve the invocation counter.

    Torch, NumPy and Python random streams are restored after generation so a
    routed call does not silently perturb the other components' random streams.
    The shared protocol uses CPU. GPU kernels may be nondeterministic.
    """

    def __init__(self, seed: int = 17, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.seed = _integer(seed, "seed")
        self.calls = 0

    def get_state(self) -> dict[str, Any]:
        return {"version": 1, "seed": self.seed, "calls": self.calls}

    def load_state(self, state: dict[str, Any]) -> None:
        if state.get("version") != 1 or state.get("seed") != self.seed:
            raise ValueError("Chemeleon checkpoint version/seed does not match")
        self.calls = _integer(state.get("calls"), "calls")

    def generate(self, plan: Plan, state: dict[str, Any]) -> list[Structure]:
        import numpy as np
        import torch

        call_seed = (self.seed + self.calls) % (2**32)
        python_state, numpy_state = random.getstate(), np.random.get_state()
        devices = []
        if str(self.device).startswith("cuda") and torch.cuda.is_available():
            devices = list(range(torch.cuda.device_count()))
        try:
            with torch.random.fork_rng(devices=devices):
                # Loading a fresh model may consume random numbers. Finish that
                # before seeding the actual sample, including after a restore.
                if self.dm is None:
                    self.setup()
                random.seed(call_seed)
                np.random.seed(call_seed)
                torch.random.default_generator.manual_seed(call_seed)
                if devices:
                    torch.cuda.manual_seed_all(call_seed)
                result = super().generate(plan, state)
                if not isinstance(result, list) or not all(
                    isinstance(item, Structure) for item in result
                ):
                    raise TypeError("Chemeleon must return list[Structure]")
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
        self.calls += 1
        return result


class OutcomeAwareToolRouter:
    """Allocate queries between tools using feedback from completed queries.

    Try each configured tool once, then use a smoothed observed reward plus a
    UCB bonus. A stable, structurally new outcome earns 1; stable-only earns
    ``stable_reward``; all other outcomes earn 0. These are observed-state
    proxies, not evaluator labels or a replacement definition of mSUN.
    In the final ``late_budget_threshold`` queries, use the smoothed reward
    without the bonus. M5 still owns where compositions are explored.
    """

    def __init__(
        self,
        generator_names: Sequence[str] = ("default", "chemeleon"),
        seed: int = 17,
        exploration_weight: float = 0.5,
        stable_reward: float = 0.25,
        late_budget_threshold: int = 2,
    ) -> None:
        names = list(generator_names)
        if (
            len(names) < 2
            or len(set(names)) != len(names)
            or not all(isinstance(name, str) and name for name in names)
        ):
            raise ValueError("generator_names must contain >=2 distinct nonempty names")
        if not math.isfinite(exploration_weight) or exploration_weight < 0:
            raise ValueError("exploration_weight must be finite and nonnegative")
        if not math.isfinite(stable_reward) or not 0 <= stable_reward <= 1:
            raise ValueError("stable_reward must be between 0 and 1")
        self.generator_names = names
        self.seed = _integer(seed, "seed")
        self.exploration_weight = float(exploration_weight)
        self.stable_reward = float(stable_reward)
        self.late_budget_threshold = _integer(
            late_budget_threshold, "late_budget_threshold"
        )
        self._rng = random.Random(self.seed)
        self.counts = dict.fromkeys(names, 0)
        self.rewards = dict.fromkeys(names, 0.0)
        self.pending: dict[str, Any] | None = None
        self.last_query_count = 0
        self.last_reason = "not_called"
        self.unattributed_queries = 0

    def _config(self) -> dict[str, Any]:
        return {
            "generator_names": self.generator_names,
            "seed": self.seed,
            "exploration_weight": self.exploration_weight,
            "stable_reward": self.stable_reward,
            "late_budget_threshold": self.late_budget_threshold,
        }

    def _observe(self, context: Mapping[str, Any], query_count: int) -> None:
        if self.pending is None or query_count <= self.pending["query_count"]:
            return
        gap = query_count - self.pending["query_count"]
        observation = context.get("last_observation")
        if gap == 1 and isinstance(observation, Mapping):
            name = self.pending["name"]
            stable = observation.get("is_stable") is True
            novel = observation.get("is_newly_discovered") is True
            reward = (1.0 if novel else self.stable_reward) if stable else 0.0
            self.counts[name] += 1
            self.rewards[name] += reward
        else:
            # Never attribute another tool's/latest-only feedback to a stale choice.
            self.unattributed_queries += gap
        self.pending = None

    def select_generator(
        self, context: dict[str, Any], generators: dict[str, Any]
    ) -> str:
        missing = set(self.generator_names).difference(generators)
        if missing:
            raise ValueError(f"Router generators are not configured: {sorted(missing)}")
        query_count = _integer(context.get("query_count", 0), "query_count")
        remaining = _integer(
            context.get("m1_queries_remaining"), "m1_queries_remaining"
        )
        if remaining == 0:
            raise RuntimeError("Cannot route after the query budget is exhausted")
        if query_count < self.last_query_count:
            raise ValueError(
                "Query count moved backwards; use a fresh router per episode"
            )
        if self.pending is not None and query_count == self.pending["query_count"]:
            return str(self.pending["name"])
        self._observe(context, query_count)
        untried = [name for name in self.generator_names if self.counts[name] == 0]
        if untried:
            selected = untried[0]
            self.last_reason = "initial_tool_probe"
        else:
            late = remaining <= self.late_budget_threshold
            total = sum(self.counts.values())
            scores = {}
            for name in self.generator_names:
                count = self.counts[name]
                mean = (self.rewards[name] + 0.5) / (count + 1)
                bonus = (
                    0.0
                    if late
                    else self.exploration_weight
                    * math.sqrt(math.log(total + 1) / count)
                )
                scores[name] = mean + bonus
            best = max(scores.values())
            ties = [name for name in self.generator_names if scores[name] == best]
            selected = self._rng.choice(ties)
            self.last_reason = "late_budget_reward" if late else "observed_reward_ucb"
        self.pending = {"name": selected, "query_count": query_count}
        self.last_query_count = query_count
        return selected

    def get_state(self) -> dict[str, Any]:
        return json.loads(
            json.dumps(
                {
                    "version": 1,
                    "config": self._config(),
                    "counts": self.counts,
                    "rewards": self.rewards,
                    "pending": self.pending,
                    "last_query_count": self.last_query_count,
                    "last_reason": self.last_reason,
                    "unattributed_queries": self.unattributed_queries,
                    "rng": self._rng.getstate(),
                },
                allow_nan=False,
            )
        )

    def load_state(self, state: dict[str, Any]) -> None:
        if state.get("version") != 1 or state.get("config") != self._config():
            raise ValueError("Router checkpoint version/configuration does not match")
        counts, rewards = state["counts"], state["rewards"]
        if set(counts) != set(self.generator_names) or set(rewards) != set(counts):
            raise ValueError("Checkpoint generator keys do not match")
        for name in self.generator_names:
            _integer(counts[name], f"counts[{name}]")
            reward = rewards[name]
            if not isinstance(reward, (int, float)) or not 0 <= reward <= counts[name]:
                raise ValueError("Invalid checkpoint reward")
        pending = state.get("pending")
        if pending is not None:
            if pending.get("name") not in counts:
                raise ValueError("Invalid pending generator")
            _integer(pending.get("query_count"), "pending query_count")
        self._rng.setstate(_tuples(state["rng"]))
        self.counts, self.rewards = dict(counts), dict(rewards)
        self.pending = dict(pending) if pending is not None else None
        self.last_query_count = _integer(state["last_query_count"], "last_query_count")
        self.unattributed_queries = _integer(
            state["unattributed_queries"], "unattributed_queries"
        )
        self.last_reason = str(state["last_reason"])
