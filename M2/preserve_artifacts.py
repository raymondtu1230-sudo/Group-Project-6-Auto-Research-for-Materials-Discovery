"""Preserve exact GitHub artifact ZIPs, independently of scientific scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path


def api(path: str) -> dict:
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", type=int, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = os.environ["GITHUB_REPOSITORY"]
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def save_manifest(complete: bool = False) -> None:
        (args.output / "provenance.json").write_text(json.dumps({
            "kind": "exact_original_artifact_preservation",
            "capture_complete": complete,
            "new_scientific_units": 0,
            "artifacts": records,
            "note": "Copies of existing runs; do not count these as additional experiments.",
        }, indent=2) + "\n")

    save_manifest()
    for run_id in args.run_id:
        run = api(f"repos/{repository}/actions/runs/{run_id}")
        page = 1
        while True:
            values = api(
                f"repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100&page={page}"
            )["artifacts"]
            if not values:
                break
            for artifact in values:
                name = artifact["name"]
                if not name.startswith(("m2-missing-raw-", "m2-batch256-")):
                    continue
                # Artifact names are remote data, never shell fragments or paths.
                if Path(name).name != name or name in (".", ".."):
                    raise ValueError("Unsafe artifact name")
                target = args.output / f"{artifact['id']}-{name}.zip"
                if not target.exists():
                    temporary = target.with_suffix(".tmp")
                    with temporary.open("wb") as stream:
                        subprocess.run(
                            [
                                "gh", "api",
                                f"repos/{repository}/actions/artifacts/{artifact['id']}/zip",
                            ],
                            stdout=stream,
                            check=True,
                        )
                    temporary.replace(target)
                sha256 = hashlib.sha256(target.read_bytes()).hexdigest()
                if artifact.get("digest") != f"sha256:{sha256}":
                    raise ValueError(f"Artifact checksum mismatch: {artifact['id']}")
                extraction = args.output / "raw" / sha256
                with zipfile.ZipFile(target) as archive:
                    for member in archive.namelist():
                        path = Path(member)
                        if path.is_absolute() or ".." in path.parts:
                            raise ValueError("Unsafe ZIP member")
                    archive.extractall(extraction)
                records.append({
                    "source_run_id": run_id,
                    "source_revision": run["head_sha"],
                    "run_status_at_capture": run["status"],
                    "run_conclusion_at_capture": run["conclusion"],
                    "artifact_id": artifact["id"],
                    "artifact_name": name,
                    "file": target.name,
                    "sha256": sha256,
                })
                save_manifest()
            page += 1
    save_manifest(complete=True)
    print(f"Preserved and checksum-verified {len(records)} original ZIPs")


if __name__ == "__main__":
    main()
