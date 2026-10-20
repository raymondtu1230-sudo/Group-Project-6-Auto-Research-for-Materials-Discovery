"""Read-only audit of published dev-baseline reports and checksum-pinned ZIPs.

This does not run a model, call an API/oracle, or recalculate scientific metrics.
The official offline evaluator must produce the input report first. Missing M1
references are reported by that evaluator but do not block this baseline audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZipFile

BASELINES = {"random_generator_baseline", "chemeleon_generative_baseline"}
SEEDS = {17, 29, 43}
ORIGINAL_MANIFEST_SHA256 = (
    "11c6e0dfd27c7c57d1b51d31cdd588be6475e0c804d4069e5e88d8522f4f2fee"
)
FINAL_ATTEMPT = 3943257052701
FINAL_UNITS = {"Au-K-Tb-17", "Co-Dy-W-43"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to((root / "M2").resolve()):
        raise ValueError("Evidence/output path must stay in M2")
    return path


def validate_coverage(validation: dict, rows: list[dict], systems: list) -> dict:
    """Check identity, completeness and coverage without inventing metrics."""
    if validation["split"] != "dev" or validation["issues"]:
        raise ValueError("Official dev report has validation issues")
    expected = {
        (method, "-".join(system), seed)
        for method in BASELINES
        for system in systems
        for seed in SEEDS
    }
    if len(expected) != 36:
        raise ValueError("Unexpected dev protocol size; review rather than adapt")
    completed = set()
    for row in rows:
        key = (row["method"], row["system"], int(row["seed"]))
        if row["split"] != "dev" or key not in expected or key in completed:
            raise ValueError("Duplicate or unexpected scientific unit")
        if int(row["B"]) != 20 or int(row["oracle_queries"]) != 20:
            raise ValueError("Only complete B=20 results may be accepted")
        completed.add(key)
    missing = expected - completed
    reported_missing = {
        (method, system, seed)
        for method, split, system, seed in validation["missing_baseline_units"]
        if split == "dev"
    }
    if (
        validation["validated_runs"] != len(rows)
        or missing != reported_missing
        or validation["baseline_sweep_complete"] != (not missing)
    ):
        raise ValueError("Report coverage and per-run evidence disagree")
    return {
        "verified_baseline_units": len(completed),
        "expected_baseline_units": 36,
        "by_method": {
            method: sum(key[0] == method for key in completed)
            for method in sorted(BASELINES)
        },
        "missing_baseline_units": [list(key) for key in sorted(missing)],
        "baseline_data_complete": not missing,
    }


def audit(root: Path, report: Path, terminal: bool = False) -> dict:
    report = owned_path(root, str(report))
    validation = json.loads((report / "validation.json").read_text())
    rows = list(csv.DictReader((report / "per_run.csv").open()))
    systems = json.loads((root / "M1/protocol/dev_systems.json").read_text())
    result = validate_coverage(validation, rows, systems)
    manifest = root / "M2/configs/verified_baselines.json"
    if sha256(manifest) != ORIGINAL_MANIFEST_SHA256:
        raise ValueError("Original 19-result manifest changed")
    archives = json.loads(manifest.read_text())["archives"]
    terminal_receipts = {}
    for path in sorted((root / "M2/execution_ledger").glob("*/receipt_*.json")):
        receipt = json.loads(path.read_text())
        if receipt["status"] == "verified_completed":
            archives.append({"path": receipt["archive"], "sha256": receipt["sha256"]})
        if receipt["attempt"] == FINAL_ATTEMPT and receipt["unit"] in FINAL_UNITS:
            terminal_receipts[receipt["unit"]] = receipt
    if terminal and set(terminal_receipts) != FINAL_UNITS:
        raise ValueError("Both current attempts must have durable terminal receipts")
    selected = {}
    for record in archives:
        selected.setdefault(record["sha256"], record)
    required = set()
    for row in rows:
        match = re.search(r"/reused/([0-9a-f]{64})/", row["source"])
        if not match or match[1] not in selected:
            raise ValueError("Per-run source lacks a checksum-pinned published archive")
        required.add(match[1])
    checks = []
    records = [selected[digest] for digest in sorted(required)]
    records.extend(terminal_receipts.values())
    for record in records:
        name = record.get("path", record.get("archive"))
        path = owned_path(root, name)
        if sha256(path) != record["sha256"]:
            raise ValueError(f"Archive checksum mismatch: {name}")
        with ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Archive CRC failure: {name}")
        checks.append({"path": name, "sha256": record["sha256"], "crc": "passed"})
    report_files = [
        "validation.json", "per_run.csv", "per_method_summary.csv",
        "per_system_summary.csv", "discovery_curves.svg",
    ]
    result.update({
        "observed_at_utc": datetime.now(UTC).isoformat(),
        "report": str(report.relative_to(root)),
        "report_sha256": {name: sha256(report / name) for name in report_files},
        "original_19_manifest_sha256": sha256(manifest),
        "archives": checks,
        "current_attempt": FINAL_ATTEMPT,
        "current_terminal_receipts": terminal_receipts,
        "terminal_audit": terminal,
        "scope": "Dev baseline data only; document/deck closeout and handoff remain separate checks.",
        "whole_M2_complete": False,
        "cost_caveat": "Recorded model fees do not price hardware, electricity or all failed attempts.",
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--terminal", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root, Path(args.report), args.terminal)
    target = owned_path(root, args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError("Keep prior audit; choose a new output instead of overwriting")
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "verified_baseline_units", "baseline_data_complete", "terminal_audit"
    )}))


if __name__ == "__main__":
    main()
