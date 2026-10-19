"""Package a finished Actions sweep for an M2-only publication on main."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def package(downloads: Path, report: Path, destination: Path, run_id: str) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    archives = []
    for folder in sorted(downloads.iterdir()):
        if not folder.is_dir() or not folder.name.startswith("m2-missing-raw-"):
            continue
        archive = destination / f"{folder.name}.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as target:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    target.write(path, path.relative_to(folder))
        archives.append(
            {
                "file": archive.name,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
        )
    for path in report.iterdir():
        if path.is_file():
            shutil.copy2(path, destination / path.name)
    audit = json.loads((report / "validation.json").read_text())
    provenance = {
        "workflow_run_id": run_id,
        "raw_archives": archives,
        "validated_runs": audit["validated_runs"],
        "missing_baseline_units": len(audit["missing_baseline_units"]),
        "issues": audit["issues"],
        "scope": "Partial development baseline evidence. No full-reference or hidden-test claim.",
    }
    (destination / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    (destination / "README.md").write_text(
        f"# Missing-only development baseline run {run_id}\n\n"
        f"Validated runs: {audit['validated_runs']}. Missing baseline units: {len(audit['missing_baseline_units'])}.\n\n"
        "Original retained Random/Chemeleon Mg-Sn-Sr/17 units are reused once. "
        "The matrix runs only previously missing Random units. Chemeleon remains capacity-blocked. "
        "Raw ZIPs preserve successful and failed attempts. See validation.json before using scores. "
        "Counts are completed scientific units, distinct from CI and synthetic smoke.\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("downloads", "report", "destination"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    package(args.downloads, args.report, args.destination, args.run_id)
