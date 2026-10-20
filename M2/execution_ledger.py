"""Atomic M2-only claims and durable receipts in a disposable main checkout."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def commit(root: Path, paths: list[str], message: str) -> None:
    if any(not p.startswith("M2/") or ".." in Path(p).parts for p in paths):
        raise ValueError("Publication is confined to M2")
    git(root, "config", "user.name", "github-actions[bot]")
    git(
        root,
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    git(root, "add", "--", *paths)
    changed = git(root, "diff", "--cached", "--name-only").splitlines()
    if any(not p.startswith("M2/") for p in changed):
        raise ValueError("Staged non-M2 change refused")
    if not changed:
        return
    git(root, "commit", "-m", message)
    # Fast-forward pushes only; rebase our M2-only commit over concurrent work.
    for retry in range(8):
        try:
            git(root, "push", "origin", "HEAD:main")
            return
        except subprocess.CalledProcessError:
            if retry == 7:
                raise
            time.sleep(1 + retry)
            git(root, "pull", "--rebase", "origin", "main")


def claim(
    root: Path, unit: str, attempt: int, source: str, retry_of: int | None
) -> dict:
    if (
        not re.fullmatch(r"[A-Za-z]+-[A-Za-z]+-[A-Za-z]+-(17|29|43)", unit)
        or attempt < 1
    ):
        raise ValueError("Invalid development unit/attempt")
    folder = root / "M2/execution_ledger" / unit
    previous = sorted(
        folder.glob("claim_*.json"), key=lambda p: int(p.stem.split("_")[1])
    )
    if previous:
        latest = json.loads(previous[-1].read_text())
        receipt = folder / f"receipt_{latest['attempt']}.json"
        if retry_of != latest["attempt"] or not receipt.is_file():
            raise ValueError(
                "Duplicate or unresolved claim: explicit retry_of and terminal receipt required"
            )
        status = json.loads(receipt.read_text())["status"]
        if status not in {"failed", "timeout"}:
            raise ValueError("Completed or active attempt must never be rescheduled")
        if attempt <= latest["attempt"]:
            raise ValueError("Retry requires a new increasing attempt")
    elif retry_of is not None:
        raise ValueError("retry_of does not identify an existing claim")
    folder.mkdir(parents=True, exist_ok=True)
    record = {
        "unit": unit,
        "attempt": attempt,
        "source_sha": source,
        "retry_of": retry_of,
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "status": "claimed",
        "mode": "direct_from_scratch",
        "initial_pool_resume": False,
    }
    path = folder / f"claim_{attempt}.json"
    with path.open("x") as stream:
        json.dump(record, stream, indent=2)
    # Two competing same-unit claims modify different files: check again after
    # every rebase before push, rather than blindly allowing both through.
    git(root, "config", "user.name", "github-actions[bot]")
    git(
        root,
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    git(root, "add", "--", str(path.relative_to(root)))
    git(root, "commit", "-m", f"Claim M2 direct {unit} attempt {attempt}")
    for retry in range(8):
        claims = [p for p in folder.glob("claim_*.json") if p != path]
        allowed = {str(p) for p in previous}
        if any(str(p) not in allowed for p in claims):
            raise ValueError("Concurrent duplicate claim detected before any science")
        try:
            git(root, "push", "origin", "HEAD:main")
            return record
        except subprocess.CalledProcessError:
            if retry == 7:
                raise
            time.sleep(1 + retry)
            git(root, "pull", "--rebase", "origin", "main")
    raise RuntimeError("Claim was not published")


def publish(root: Path, source: Path, run_id: str, kind: str) -> None:
    if not re.fullmatch(r"\d+(?:-\d+)?", run_id) or kind not in {"preflight", "direct"}:
        raise ValueError("Unsafe publication path")
    destination = root / f"M2/verification/{kind}-{run_id}"
    if destination.exists():
        raise ValueError("Evidence destination exists; use a new attempt")
    shutil.copytree(source, destination)
    paths = [str(destination.relative_to(root))]
    if kind == "direct":
        for path in destination.rglob("receipt.json"):
            record = json.loads(path.read_text())
            archive = path.parent / record["archive"]
            record["archive"] = str(archive.relative_to(root))
            target = (
                root
                / "M2/execution_ledger"
                / record["unit"]
                / f"receipt_{record['attempt']}.json"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x") as stream:
                json.dump(record, stream, indent=2)
            paths.append(str(target.relative_to(root)))
    commit(root, paths, f"Preserve M2 {kind} evidence {run_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["claim", "publish"])
    parser.add_argument("--publication", type=Path, required=True)
    parser.add_argument("--unit")
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--source")
    parser.add_argument("--retry-of", type=int)
    parser.add_argument("--downloads", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--kind", choices=["preflight", "direct"])
    args = parser.parse_args()
    if args.action == "claim":
        claim(args.publication, args.unit, args.attempt, args.source, args.retry_of)
    else:
        publish(args.publication, args.downloads, args.run_id, args.kind)
