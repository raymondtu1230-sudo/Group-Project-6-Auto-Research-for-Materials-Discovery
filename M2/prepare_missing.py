"""Verify retained results and plan only missing development baseline units.

Offline execution only: this script never starts a model, reads a credential or
calls an oracle. Run the generated units through the unchanged run_baselines.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from M2.evaluate import BASELINES, collect, compare, unit_key, write_csv  # noqa: E402


def import_verified_archives(
    manifest: Path, destination: Path, published_root: Path | None = None
) -> None:
    """Import immutable, checksum-pinned evidence without rewriting its bytes."""
    records = json.loads(manifest.read_text())["archives"]
    if published_root:
        for provenance in sorted(published_root.glob("missing-*/provenance.json")):
            for item in json.loads(provenance.read_text())["raw_archives"]:
                source = provenance.parent / item["file"]
                if not source.resolve().is_relative_to(provenance.parent.resolve()):
                    raise ValueError("Published evidence path escapes its folder")
                records.append(
                    {"path": str(source.resolve()), "sha256": item["sha256"]}
                )
    for record in records:
        archive = REPO / record["path"]
        if hashlib.sha256(archive.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Retained archive checksum mismatch: {record['path']}")
        target = destination / record["sha256"]
        with ZipFile(archive) as source:
            for member in source.infolist():
                path = target / member.filename
                if not path.resolve().is_relative_to(target.resolve()):
                    raise ValueError("Archive member escapes its evidence directory")
                if member.is_dir():
                    continue
                data = source.read(member)
                if path.exists() and path.read_bytes() != data:
                    raise ValueError("Existing evidence differs; refusing overwrite")
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_bytes(data)


def prepare(results: Path, protocol_path: Path, systems_path: Path) -> dict:
    protocol = yaml.safe_load(protocol_path.read_text())
    systems = json.loads(systems_path.read_text())
    seeds = protocol["repeats"]["seeds"]
    methods = [m for m in protocol["methods"]["required"] if m in BASELINES]
    if set(methods) != set(BASELINES):
        raise ValueError("Protocol must require both official baselines")
    expected = {
        (method, "dev", "-".join(system), seed)
        for method in methods
        for system in systems
        for seed in seeds
    }
    runs, issues = collect(results, "dev")
    fatal = [issue for issue in issues if issue["kind"] != "superseded_attempt"]
    if fatal:
        raise ValueError(f"Results need explicit review before scheduling: {fatal}")
    accepted = []
    for run in runs:
        if run.metadata["method"] not in BASELINES:
            continue
        if run.metadata.get("unit_test_fixture"):
            raise ValueError("Synthetic fixture cannot be reused as a real baseline")
        if run.metadata["protocol_settings"] != protocol:
            raise ValueError("Retained result protocol differs from current protocol")
        if unit_key(run.metadata) not in expected:
            raise ValueError("Retained baseline is outside the development protocol")
        accepted.append(run)
    compare(accepted)
    completed = {unit_key(run.metadata): run for run in accepted}
    units = []
    for method, split, system, seed in sorted(expected):
        key = (method, split, system, seed)
        run = completed.get(key)
        units.append(
            {
                "method": method,
                "split": split,
                "system": system,
                "seed": seed,
                "B": protocol["environment"]["query_budget"],
                "status": "completed" if run else "missing",
                "source": str(run.path.relative_to(REPO))
                if run and run.path.is_relative_to(REPO)
                else str(run.path)
                if run
                else None,
            }
        )
    missing = [u for u in units if u["status"] == "missing"]
    # Chemeleon has no proven checkpoint during initial pool generation. The
    # measured 263 min plus M6's 50% uncertainty exceeds a hosted 6-hour job.
    random_units = [u for u in missing if u["method"] == BASELINES[0]]
    chemeleon = [u for u in missing if u["method"] == BASELINES[1]]
    matrix = [{k: u[k] for k in ("method", "system", "seed")} for u in random_units]
    return {
        "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "expected_baseline_units": len(expected),
        "completed_baseline_units": len(completed),
        "missing_baseline_units": len(missing),
        "running_units": [],
        "failed_units": [],
        "scope": "Validated inputs only. Query GitHub before dispatch for active jobs. Historical failed attempts remain in verification/20261019-chemeleon-timeout.",
        "units": units,
        "missing_units": missing,
        "hosted_random_matrix": {"include": matrix},
        "capacity_blocked_chemeleon_units": chemeleon,
        "capacity_reason": "Initial sampling is not resumable. Need a verified persistent CPU host with enough runtime and result-save margin before admitting these units.",
        "superseded_attempts": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path, default=REPO / "M2/configs/verified_baselines.json"
    )
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--import-only", action="store_true")
    parser.add_argument("--published-root", type=Path)
    args = parser.parse_args()
    import_verified_archives(args.manifest, args.results_root, args.published_root)
    if args.import_only:
        return
    plan = prepare(
        args.results_root,
        REPO / "M1/protocol/protocol_v1.yaml",
        REPO / "M1/protocol/dev_systems.json",
    )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "inventory.json").write_text(json.dumps(plan, indent=2) + "\n")
    write_csv(args.output / "units.csv", plan["units"])
    if args.github_output:
        with args.github_output.open("a") as stream:
            print("matrix=" + json.dumps(plan["hosted_random_matrix"]), file=stream)
            print(
                "has_work="
                + str(bool(plan["hosted_random_matrix"]["include"])).lower(),
                file=stream,
            )
    print(
        json.dumps(
            {k: plan[k] for k in ("completed_baseline_units", "missing_baseline_units")}
        )
    )


if __name__ == "__main__":
    main()
