"""Synthetic walk-through of M3 planning and self-correction (no oracle, no API key).

Drives ``M3ResearchPlanner`` and ``M3StuckReplanPolicy`` for 16 fake queries on
Li-Fe-O. The fake feedback finds a new phase only at queries 3 and 13, so the
policy should flag "no progress" in between and re-plan. The trace is written
to ``M3/evidence/synthetic-demo/m3_demo_trace.json``. It shows the mechanism
only; it is not a discovery result.

    cd M1/MADE   # after: uv run python ../../M3/install.py --install
    uv run python ../../M3/examples/m3_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from pymatgen.core.composition import Composition
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure

from made.agents.m3_planning import M3ResearchPlanner, M3StuckReplanPolicy

OUT = Path(__file__).resolve().parents[1] / "evidence" / "synthetic-demo"
ELEMENTS = ["Li", "Fe", "O"]
BUDGET = 16
DISCOVERY_AT = {3, 13}


def fake_structure(composition: Composition) -> Structure:
    species = [str(el) for el, n in composition.items() for _ in range(int(n))]
    coords = [
        [(i * 0.37) % 1, (i * 0.61) % 1, (i * 0.89) % 1] for i in range(len(species))
    ]
    return Structure(Lattice.cubic(5.0), species, coords)


def main() -> None:
    planner = M3ResearchPlanner(max_stoichiometry=6, seed=17, batch_size=3)
    policy = M3StuckReplanPolicy(window=4, cooldown=2, max_stoichiometry=6, seed=17)
    observation = None
    steps = []
    for query in range(BUDGET):
        state = {
            "elements": ELEMENTS,
            "max_stoichiometry": 6,
            "query_count": query,
            "m1_queries_remaining": BUDGET - query,
            "last_observation": observation,
            "m1_memory": [],
        }
        planner.update_state(state)
        plan = planner.propose(state)
        revised = policy.revise_plan(plan, state)
        chosen = revised.compositions[0]
        new = query + 1 in DISCOVERY_AT
        observation = {
            "proposal": fake_structure(chosen).as_dict(),
            "reduced_formula": chosen.reduced_formula,
            "e_above_hull": 0.0 if new else 0.25,
            "is_stable": new,
            "is_newly_discovered": new,
        }
        steps.append(
            {
                "query": query + 1,
                "subgoal": planner.current_subgoal,
                "planned": [c.formula for c in plan.compositions],
                "evaluated": chosen.formula,
                "replanned": revised is not plan,
                "new_phase": new,
            }
        )
        print(
            f"q{query + 1:02d} subgoal={planner.current_subgoal:<8} "
            f"planned={plan.compositions[0].reduced_formula:<8} "
            f"evaluated={chosen.reduced_formula:<8}"
            f"{' RE-PLAN' if revised is not plan else ''}"
            f"{' NEW PHASE' if new else ''}"
        )

    trace = {
        "note": "Synthetic feedback; demonstrates the mechanism, not performance.",
        "elements": ELEMENTS,
        "steps": steps,
        "planner_reviews": planner.decision_trace,
        "replan_events": policy.events,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "m3_demo_trace.json").write_text(json.dumps(trace, indent=2))
    print(f"{len(policy.events)} re-plans, {planner.num_reviews} reviews -> {OUT}")


if __name__ == "__main__":
    main()
