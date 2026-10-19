"""Export both ON/OFF official episode JSON trajectories, including final query.

Usage: python export_evidence.py episode_000.json evidence.jsonl --run-id RUN
       --episode-id 0
The output retains public post-query fields only; it is not an official scorer.
"""

import argparse
import json
from pathlib import Path


def export_trajectory(source, output, run_id, episode_id):
    trajectory = json.loads(Path(source).read_text(encoding="utf-8"))
    if isinstance(trajectory, dict):
        trajectory = trajectory["trajectory"]
    if not isinstance(trajectory, list):
        raise ValueError("Expected an official episode object with trajectory, or a trajectory list")
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
        )
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
    args = parser.parse_args()
    print(export_trajectory(args.source, args.output, args.run_id, args.episode_id))
