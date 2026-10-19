"""Export both ON/OFF official episode JSON trajectories, including final query.

Usage: python export_evidence.py episode_000.json evidence.jsonl --run-id RUN
       --episode-id 0 --elements Mg Sn Sr
The output retains public post-query fields only; it is not an official scorer.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from m4_memory.evidence import (
    candidate_composition,
    normalize_elements,
    observed_outcome,
)


def export_trajectory(source, output, run_id, episode_id, *, elements):
    elements = normalize_elements(elements)
    trajectory = json.loads(Path(source).read_text(encoding="utf-8"))
    if isinstance(trajectory, dict):
        trajectory = trajectory["trajectory"]
    if not isinstance(trajectory, list):
        raise ValueError(
            "Expected an official episode object with trajectory, or a trajectory list"
        )
    records = []
    keys = (
        "proposal",
        "reduced_formula",
        "energy_per_atom",
        "formation_energy_per_atom",
        "e_above_hull",
        "is_stable",
        "is_newly_discovered",
    )
    for step, observation in enumerate(trajectory, 1):
        record = {key: observation[key] for key in keys if key in observation}
        record.update(
            schema_version=1,
            run_id=run_id,
            episode_id=episode_id,
            event_id=f"evaluation:{step}",
            candidate_id=f"query:{step}",
            step_id=step,
            query_count=step,
            status="evaluated",
            elements=elements,
        )
        record["composition"] = candidate_composition(
            observation.get("proposal"), elements
        )
        record["outcome"], record["reason"] = observed_outcome(observation)
        records.append(record)
    # Validate before writing; x mode prevents accidentally overwriting evidence.
    payload = "".join(
        json.dumps(x, ensure_ascii=False, allow_nan=False) + "\n" for x in records
    )
    with Path(output).open("x", encoding="utf-8") as stream:
        stream.write(payload)
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("output")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--episode-id", required=True)
    parser.add_argument(
        "--elements",
        nargs="+",
        required=True,
        help="Complete run chemical system, including unqueried elements",
    )
    args = parser.parse_args()
    print(
        export_trajectory(
            args.source,
            args.output,
            args.run_id,
            args.episode_id,
            elements=args.elements,
        )
    )
