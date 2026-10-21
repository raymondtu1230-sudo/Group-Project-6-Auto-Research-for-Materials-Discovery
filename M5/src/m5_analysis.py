"""M5 evidence-analysis utilities.

Reconstructs the per-decision exploration log from an official MADE trajectory
(when a sidecar was not configured) and scores episodes against the two
required failure modes: over-exploitation and wasteful exploration.

Pure standard library; operates on files already produced by run_experiment.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_trajectory(path: str | Path) -> list[dict[str, Any]]:
    """Return the per-step observation list from an episode JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("trajectory", []))


def load_decision_log(path: str | Path) -> list[dict[str, Any]]:
    """Parse a per-episode m5_decisions.jsonl sidecar, one record per line."""
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def over_exploitation_score(
    trajectory: list[dict[str, Any]], window: int = 6, min_stable_frac: float = 0.8
) -> dict[str, Any]:
    """Detect long runs where the agent re-tests near one region and stops
    finding new stable materials.

    A window of ``window`` consecutive queries is flagged when at least
    ``min_stable_frac`` of its outcomes are unstable AND the queried formulas
    share at least one element in a dominant (>60%) fraction of steps.
    """
    flags = []
    for start in range(0, max(len(trajectory) - window + 1, 0)):
        chunk = trajectory[start : start + window]
        stable_hits = sum(1 for s in chunk if s.get("is_stable"))
        if stable_hits / window > 1 - min_stable_frac:
            continue  # still finding stable materials; not over-exploiting
        # Dominant element across the window
        elements: dict[str, int] = {}
        for s in chunk:
            formula = s.get("reduced_formula", "")
            for el in ("Mg", "Sn", "Sr", "Li", "O"):  # generalise by parsing if needed
                if el in formula:
                    elements[el] = elements.get(el, 0) + 1
        dom = max(elements.values(), default=0) / window
        if dom >= 0.6:
            flags.append(
                {
                    "window": [start, start + window - 1],
                    "stable_hits": stable_hits,
                    "dominant_element_fraction": round(dom, 2),
                }
            )
    return {"flagged_windows": flags, "score": len(flags)}


def wasteful_exploration_score(
    trajectory: list[dict[str, Any]], window: int = 6, max_stable_frac: float = 0.2
) -> dict[str, Any]:
    """Detect long runs of diverse but unproductive exploration.

    A window is flagged when at most ``max_stable_frac`` of outcomes are stable
    AND the formulas in the window are all distinct (high diversity, low yield).
    """
    flags = []
    for start in range(0, max(len(trajectory) - window + 1, 0)):
        chunk = trajectory[start : start + window]
        stable_hits = sum(1 for s in chunk if s.get("is_stable"))
        formulas = [s.get("reduced_formula") for s in chunk]
        distinct = len(set(formulas)) == len(formulas)
        if stable_hits / window <= max_stable_frac and distinct:
            flags.append(
                {
                    "window": [start, start + window - 1],
                    "stable_hits": stable_hits,
                    "distinct_formulas": len(set(formulas)),
                }
            )
    return {"flagged_windows": flags, "score": len(flags)}


def summarize_episode(trajectory: list[dict[str, Any]]) -> dict[str, Any]:
    """Headline numbers for one episode."""
    stable = [s for s in trajectory if s.get("is_stable")]
    novel_stable = [s for s in stable if s.get("is_newly_discovered")]
    cumulative = 0
    audc = 0
    for s in trajectory:
        if s.get("is_stable") and s.get("is_newly_discovered"):
            cumulative += 1
        audc += cumulative
    return {
        "queries": len(trajectory),
        "stable_count": len(stable),
        "mSUN": len(novel_stable),
        "AUDC": audc,
        "stable_formulas": [s.get("reduced_formula") for s in stable],
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("usage: python m5_analysis.py <episode_000.json>")
    traj = load_trajectory(sys.argv[1])
    print(json.dumps(summarize_episode(traj), indent=2))
    print(json.dumps(over_exploitation_score(traj), indent=2))
    print(json.dumps(wasteful_exploration_score(traj), indent=2))
