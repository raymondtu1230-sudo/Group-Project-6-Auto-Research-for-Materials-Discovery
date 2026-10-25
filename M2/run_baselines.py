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
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

M2_DIR = Path(__file__).resolve().parent
REPO = M2_DIR.parent
MADE = REPO / "M1/MADE"


def process_progress(pid: int, log_path: Path) -> dict[str, Any]:
    """Observe CPU work and safe generation markers, never scientific labels.

    A heartbeat, log growth, and CPU activity are different signals. None alone
    establishes that an oracle query finished or that a process is stalled.
    Linux process counters are optional so other supported hosts still run.
    """
    cpu_seconds = None
    try:
        # Some execution hosts expose a host /proc tree with namespace-local
        # subprocess IDs. Never report another process's counters in that case.
        self_stat = Path("/proc/self/stat").read_text()
        if int(self_stat.split(" ", 1)[0]) != os.getpid():
            raise OSError("Process IDs do not map to this /proc namespace")
        stat = Path(f"/proc/{pid}/stat").read_text()
        fields = stat.rsplit(") ", 1)[1].split()
        cpu_seconds = round(
            (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK"), 3
        )
    except (OSError, ValueError, IndexError, AttributeError):
        pass
    log_bytes, generation_batch, generation_batch_size = 0, None, None
    sampling_step, sampling_total, sampling_elapsed_seconds = None, None, None
    try:
        with log_path.open("rb") as stream:
            log_bytes = stream.seek(0, os.SEEK_END)
            stream.seek(max(0, log_bytes - 65536))
            tail = stream.read().decode("utf-8", errors="replace")
        # Emit only the known numeric marker, not arbitrary log content which
        # might contain credentials, private paths, or thousands of formulas.
        batches = re.findall(r"Generating batch #(\d+) with (\d+) samples", tail)
        if batches:
            generation_batch, generation_batch_size = map(int, batches[-1])
        samples = re.findall(
            r"Sampling:\s+\d+%\|[^\r\n]*?\|\s*(\d+)/(\d+)\s+\[([\d:]+)<",
            tail,
        )
        if samples:
            step, total, elapsed = samples[-1]
            sampling_step, sampling_total = int(step), int(total)
            sampling_elapsed_seconds = 0
            for part in elapsed.split(":"):
                sampling_elapsed_seconds = sampling_elapsed_seconds * 60 + int(part)
    except OSError:
        pass
    return {
        "process_cpu_seconds": cpu_seconds,
        "process_log_bytes": log_bytes,
        "generation_batch": generation_batch,
        "generation_batch_size": generation_batch_size,
        "sampling_step": sampling_step,
        "sampling_total": sampling_total,
        "sampling_elapsed_seconds": sampling_elapsed_seconds,
    }


def checkpoint_history(
    output_dir: Path,
    checkpoints: Path,
    seen: dict[Path, tuple[int, int]] | None = None,
) -> list[dict[str, Any]]:
    longest: list[dict[str, Any]] = []
    for path in checkpoints.glob("**/checkpoint.json"):
        try:
            stat = path.stat()
            identity = (stat.st_mtime_ns, stat.st_size)
            if seen is not None and seen.get(path) == identity:
                continue
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if seen is not None:
            seen[path] = identity
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
    log_path = output_dir / "m2_process.log"
    # The M1 driver rejects a nonempty output directory. Keep its capture log
    # outside that directory until the subprocess has finished.
    live_log = output_dir.parent / f"attempt_{attempt:02d}.process.log"
    progress_log = output_dir.parent / f"attempt_{attempt:02d}.progress.jsonl"
    if (
        (output_dir.exists() and any(output_dir.iterdir()))
        or live_log.exists()
        or progress_log.exists()
    ):
        raise ValueError("Run output already exists; preserve it and use a new attempt")
    output_dir.mkdir(parents=True, exist_ok=True)
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
    seen: dict[Path, tuple[int, int]] = {}
    previous_cpu = None
    started, last_progress = time.monotonic(), 0.0
    print(f"Starting real protocol unit: {method} {system} seed={seed}", flush=True)
    with live_log.open("w") as log:
        process = subprocess.Popen(
            command,
            cwd=MADE,
            stdout=log,
            stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        try:
            while process.poll() is None:
                observed = checkpoint_history(output_dir, MADE / "checkpoints", seen)
                if len(observed) > len(history):
                    history = observed
                    print(
                        f"Official checkpoint: {history[-1].get('queries_used')} queries",
                        flush=True,
                    )
                if time.monotonic() - last_progress >= 45:
                    last_progress = time.monotonic()
                    progress = process_progress(process.pid, live_log)
                    cpu = progress["process_cpu_seconds"]
                    progress.update(
                        elapsed_seconds=int(last_progress - started),
                        captured_queries=len(history),
                        cpu_advanced=(
                            cpu > previous_cpu
                            if cpu is not None and previous_cpu is not None
                            else None
                        ),
                        scope="process_diagnostics_not_discovery_metrics",
                    )
                    previous_cpu = cpu
                    encoded = json.dumps(progress, allow_nan=False)
                    with progress_log.open("a") as stream:
                        stream.write(encoded + "\n")
                    print(f"Progress diagnostics: {encoded}", flush=True)
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
    if progress_log.exists():
        progress_log.replace(output_dir / "m2_progress.jsonl")
    metadata_path = output_dir / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.is_file() else {}
    completed = process.returncode == 0 and metadata.get("status") == "completed"
    record = preserve_history(history, output_dir, completed)
    config_saved = preserve_configuration(output_dir, MADE / "results")
    if metadata:
        metadata["m2_capture"] = {
            "complete_curve": record["complete_curve"],
            "resolved_config_saved": config_saved,
            "progress_diagnostics_saved": (output_dir / "m2_progress.jsonl").is_file(),
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
    from frozen_routing import active
    from frozen_routing import main as frozen_main

    if active():
        frozen_main("compute")
    else:
        main()
