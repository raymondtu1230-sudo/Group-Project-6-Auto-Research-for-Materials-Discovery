"""Run M1's unchanged official protocol driver and preserve its query metrics.

An external parent process observes the official runner's existing, atomic
checkpoint files. It records evaluation history after queries, without changing
the runner, environment, oracle, evaluator, agent state, or query budget.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

M2_DIR = Path(__file__).resolve().parent
REPO = M2_DIR.parent
MADE = REPO / "M1/MADE"


def checkpoint_history(output_dir: Path, checkpoints: Path) -> list[dict[str, Any]]:
    longest: list[dict[str, Any]] = []
    for path in checkpoints.glob("**/checkpoint.json"):
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        configured = payload.get("config", {}).get("experiment", {}).get("output_dir")
        if not isinstance(configured, str):
            continue
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = MADE / candidate
        if candidate.resolve() != output_dir.resolve():
            continue
        history = payload.get("metrics_history", [])
        if isinstance(history, list) and len(history) > len(longest):
            longest = history
    return longest


def preserve_history(
    history: list[dict[str, Any]], output_dir: Path, completed: bool
) -> dict[str, Any]:
    trajectory_path = output_dir / "trajectories/episode_000.json"
    if completed and trajectory_path.is_file():
        payload = json.loads(trajectory_path.read_text())
        final = {
            key.removeprefix("final/"): value
            for key, value in payload.get("metrics", {}).items()
            if key.startswith("final/")
        }
        final_query = final.get("queries_used")
        if final_query and (
            not history or history[-1].get("queries_used", -1) < final_query
        ):
            history = [*history, final]
    query_counts = [row.get("queries_used") for row in history]
    queries = int(query_counts[-1]) if query_counts else 0
    complete_curve = query_counts == list(range(1, queries + 1)) and queries > 0
    record = {
        "source": "official_runner_checkpoint_metrics_history",
        "complete_curve": complete_curve,
        "query_counts": query_counts,
        "metrics_history": history,
    }
    target = output_dir / "m2_metrics_history.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, allow_nan=False))
    return record


def preserve_configuration(output_dir: Path, results_root: Path) -> bool:
    """Copy the matching official Hydra configuration; never recompose a run."""
    import yaml
    from omegaconf import OmegaConf

    for path in sorted(results_root.glob("*/.hydra/config.yaml")):
        raw = path.read_text()
        data = yaml.safe_load(raw)
        configured = data.get("experiment", {}).get("output_dir")
        if not isinstance(configured, str):
            continue
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = MADE / candidate
        if candidate.resolve() != output_dir.resolve():
            continue
        resolved = OmegaConf.to_yaml(OmegaConf.create(data), resolve=True)
        secret = os.environ.get("MATERIALS_PROJECT_API_KEY")
        if secret:
            raw = raw.replace(secret, "[REDACTED]")
            resolved = resolved.replace(secret, "[REDACTED]")
        target = output_dir / "hydra"
        target.mkdir(exist_ok=True)
        (target / "config.yaml").write_text(raw)
        (output_dir / "resolved_config.yaml").write_text(resolved)
        overrides = path.with_name("overrides.yaml")
        if overrides.is_file():
            text = overrides.read_text()
            if secret:
                text = text.replace(secret, "[REDACTED]")
            (target / "overrides.yaml").write_text(text)
        return True
    return False


def run_unit(method: str, split: str, system: str, seed: int, attempt: int) -> int:
    output_dir = (
        MADE
        / "results/protocol_v1"
        / method
        / split
        / system
        / f"seed_{seed}"
        / f"attempt_{attempt:02d}"
    )
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Run output already exists; preserve it and use a new attempt")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "m2_process.log"
    # The M1 driver rejects a nonempty output directory. Keep its capture log
    # outside that directory until the subprocess has finished.
    live_log = output_dir.parent / f"attempt_{attempt:02d}.process.log"
    command = [
        sys.executable,
        str(REPO / "M1/run_experiment.py"),
        "--method",
        method,
        "--split",
        split,
        "--system",
        system,
        "--seed",
        str(seed),
        "--attempt",
        str(attempt),
    ]
    history: list[dict[str, Any]] = []
    started, last_progress = time.monotonic(), 0.0
    print(f"Starting real protocol unit: {method} {system} seed={seed}", flush=True)
    with live_log.open("w") as log:
        process = subprocess.Popen(
            command,
            cwd=MADE,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        try:
            while process.poll() is None:
                observed = checkpoint_history(output_dir, MADE / "checkpoints")
                if len(observed) > len(history):
                    history = observed
                    print(
                        f"Official checkpoint: {history[-1].get('queries_used')} queries",
                        flush=True,
                    )
                if time.monotonic() - last_progress >= 45:
                    last_progress = time.monotonic()
                    print(
                        f"Process active; elapsed={int(last_progress - started)}s, "
                        f"captured_queries={len(history)}",
                        flush=True,
                    )
                time.sleep(0.1)
        except BaseException:
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    secret = os.environ.get("MATERIALS_PROJECT_API_KEY")
    if secret:
        live_log.write_text(live_log.read_text().replace(secret, "[REDACTED]"))
    live_log.replace(log_path)
    metadata_path = output_dir / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.is_file() else {}
    completed = process.returncode == 0 and metadata.get("status") == "completed"
    record = preserve_history(history, output_dir, completed)
    config_saved = preserve_configuration(output_dir, MADE / "results")
    if metadata:
        metadata["m2_capture"] = {
            "complete_curve": record["complete_curve"],
            "resolved_config_saved": config_saved,
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "made_upstream_commit": metadata.get("protocol_settings", {}).get(
                "made_upstream_commit"
            ),
            "shared_repository_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
            ).strip(),
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, allow_nan=False))
    print(
        json.dumps(
            {
                "method": method,
                "system": system,
                "seed": seed,
                "completed": completed,
                "complete_curve": record["complete_curve"],
                "output": str(output_dir.relative_to(REPO)),
                "returncode": process.returncode,
            }
        )
    )
    if process.returncode:
        # Output is already masked by Actions when it contains a configured secret.
        # The benchmark should never print credentials; retain its failure context.
        print(log_path.read_text()[-12000:], file=sys.stderr)
    captured = record["complete_curve"] and config_saved
    return process.returncode or (0 if completed and captured else 1)


def main() -> None:
    key = os.environ.get("MATERIALS_PROJECT_API_KEY")
    if key:
        os.environ["MATERIALS_PROJECT_API_KEY"] = key.strip()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", required=True)
    parser.add_argument("--split", choices=("dev", "check"), default="dev")
    parser.add_argument("--system", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--attempt", type=int, default=1)
    args = parser.parse_args()
    if args.attempt < 1:
        parser.error("attempt must be positive")
    raise SystemExit(
        run_unit(args.method, args.split, args.system, args.seed, args.attempt)
    )


if __name__ == "__main__":
    main()
