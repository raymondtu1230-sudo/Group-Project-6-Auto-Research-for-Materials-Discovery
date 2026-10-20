"""Run M3's protocol ablations through M1's ``run_experiment.py``.

Each (method, system, seed) is one official one-episode invocation. Completed
runs are skipped, and a failed run is retried under the next attempt number so
the failure stays on disk, as the protocol requires.

``m1_baseline`` is re-run by default. M1's recorded baseline runs predate M4's
memory manager becoming the default in ``m1_integrated.yaml``, so a fair paired
comparison needs a baseline run under the same configuration as the M3 runs.
Each run gets its own ``M4_RUN_ID``, as M4's adoption notes require.

Use ``--jobs N`` to run N episodes at once; each gets ``cores // N`` CPU
threads, the same for every arm.

Run from ``M1/MADE`` after putting ``MATERIALS_PROJECT_API_KEY`` in
``M1/MADE/.env`` and installing M4 (``uv pip install --no-deps -e ../../M4``)::

    uv run python ../../M3/run_ablations.py --dry-run
    uv run python ../../M3/run_ablations.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from summarize_ablations import run_problem

M3_DIR = Path(__file__).resolve().parent
M1_DIR = M3_DIR.parent / "M1"
MADE_DIR = M1_DIR / "MADE"
RESULTS = MADE_DIR / "results" / "protocol_v1"
PROTOCOL = yaml.safe_load((M1_DIR / "protocol" / "protocol_v1.yaml").read_text())
M3_METHODS = ("m3_full", "m3_planning_off", "m3_self_correction_off")
BASELINE = "m1_baseline"
AGENT_CONFIG = MADE_DIR / "configs" / "agent" / "m1_integrated.yaml"
M4_INSTALL = "uv pip install --no-deps -e ../../M4"
KEY_NAME = "MATERIALS_PROJECT_API_KEY"
# MADE names each run's checkpoint folder after its start second; runs started
# in the same second would share (and could resume from) one checkpoint file.
LAUNCH_GAP_SECONDS = 30


def dev_systems() -> list[str]:
    systems = json.loads((M1_DIR / "protocol" / "dev_systems.json").read_text())
    return ["-".join(system) for system in systems]


def run_dir(method: str, system: str, seed: int) -> Path:
    return RESULTS / method / "dev" / system / f"seed_{seed}"


def attempts(method: str, system: str, seed: int) -> list[Path]:
    return sorted(
        p for p in run_dir(method, system, seed).glob("attempt_*") if p.is_dir()
    )


def console_log(attempt_dir: Path) -> Path:
    # MADE's runner resets logging handlers, leaving run_benchmark.log empty, so
    # the console (with M3's review/re-plan lines) is saved beside the run.
    # run_experiment.py refuses a non-empty attempt folder, hence a sibling file.
    return attempt_dir.parent / f"console_{attempt_dir.name}.log"


def is_completed(path: Path) -> bool:
    """Completed and clean (no checkpoint resume, no shared checkpoint folder)."""
    metadata = path / "run_metadata.json"
    if not metadata.is_file():
        return False
    if json.loads(metadata.read_text()).get("status") != "completed":
        return False
    return run_problem(path, RESULTS) is None


def next_attempt(method: str, system: str, seed: int) -> int:
    existing = attempts(method, system, seed)
    if not existing:
        return 1
    return int(existing[-1].name.split("_")[1]) + 1


def has_api_key() -> bool:
    if os.environ.get(KEY_NAME):
        return True
    env_file = MADE_DIR / ".env"
    if not env_file.is_file():
        return False
    for line in env_file.read_text().splitlines():
        name, _, value = line.partition("=")
        if name.strip() == KEY_NAME:
            value = value.strip().strip("'\"")
            return bool(value) and not value.startswith("replace_with")
    return False


def m4_missing() -> bool:
    """True if the agent config uses M4's memory manager but M4 is not installed."""
    uses_m4 = "m4_memory" in AGENT_CONFIG.read_text(encoding="utf-8")
    return uses_m4 and importlib.util.find_spec("m4_memory") is None


def run_env(
    method: str, system: str, seed: int, attempt: int, threads: int | None = None
) -> dict[str, str]:
    # M4 asks for a unique run ID per experiment attempt; one episode per run.
    env = dict(os.environ)
    env["M4_RUN_ID"] = f"{method}-{system}-seed{seed}-attempt{attempt:02d}"
    env["M4_EPISODE_ID"] = "0"
    env["PYTHONUNBUFFERED"] = "1"  # stream the console log while the run is going
    if threads:
        # Same CPU thread count for every arm, so parallel runs stay comparable.
        for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
            env[name] = str(threads)
    return env


def order_runs(
    methods: list[str], systems: list[str], seeds: list[int]
) -> list[tuple[str, str, int]]:
    """System by system, seed by seed, all methods together.

    Complete paired sets (baseline + every M3 arm) finish early, so a partial
    sweep is still analysable.
    """
    return [
        (method, system, seed)
        for system in systems
        for seed in seeds
        for method in methods
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--methods", nargs="+", default=list(M3_METHODS))
    parser.add_argument("--systems", nargs="+", default=dev_systems())
    parser.add_argument(
        "--seeds", nargs="+", type=int, default=PROTOCOL["repeats"]["seeds"]
    )
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="skip re-running m1_baseline under the current configuration",
    )
    parser.add_argument(
        "--jobs", type=int, default=1, help="runs to execute at the same time"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="CPU threads per run (default: cores // jobs when --jobs > 1)",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def check_dev_only(systems: list[str]) -> None:
    # M6's protocol: m1_baseline and the m3_* methods run on dev systems only,
    # never on check or hidden systems.
    outside = [s for s in systems if s not in dev_systems()]
    if outside:
        raise SystemExit(f"M3 ablations run on dev systems only; not dev: {outside}")


def main() -> None:
    args = parse_args()
    if Path.cwd().resolve() != MADE_DIR:
        raise SystemExit(f"Run from {MADE_DIR}")
    check_dev_only(args.systems)
    methods = ([] if args.no_baseline else [BASELINE]) + [
        m for m in args.methods if m != BASELINE
    ]
    todo = [
        run
        for run in order_runs(methods, args.systems, args.seeds)
        if not any(is_completed(p) for p in attempts(*run))
    ]
    total = len(methods) * len(args.systems) * len(args.seeds)
    print(f"{total - len(todo)} of {total} runs already completed; {len(todo)} to run")
    if args.dry_run:
        for method, system, seed in todo:
            print(f"  {method} {system} seed {seed}")
        return
    if todo and not has_api_key():
        raise SystemExit(
            f"Set {KEY_NAME} in {MADE_DIR / '.env'} (copy .env.example) first"
        )
    if todo and m4_missing():
        raise SystemExit(
            "m1_integrated.yaml uses M4's memory manager; install M4 first:\n"
            f"  {M4_INSTALL}"
        )

    jobs = max(args.jobs, 1)
    threads = args.threads or (
        max((os.cpu_count() or 1) // jobs, 1) if jobs > 1 else None
    )
    print(f"jobs={jobs} threads_per_run={threads or 'default'}", flush=True)
    failures: list[tuple[str, str, int, int]] = []
    lock = threading.Lock()
    launch_lock = threading.Lock()
    last_launch = [0.0]

    def run_one(index: int, method: str, system: str, seed: int) -> None:
        with launch_lock:  # stagger starts so checkpoint folder names never clash
            wait = last_launch[0] + LAUNCH_GAP_SECONDS - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            last_launch[0] = time.monotonic()
            attempt = next_attempt(method, system, seed)
            log_path = console_log(
                run_dir(method, system, seed) / f"attempt_{attempt:02d}"
            )
            log_path.parent.mkdir(parents=True, exist_ok=True)
            print(
                f"[{index}/{len(todo)}] start {method} {system} seed {seed}"
                f" attempt {attempt}",
                flush=True,
            )
        started = time.monotonic()
        process = subprocess.Popen(
            [
                sys.executable,
                str(M1_DIR / "run_experiment.py"),
                "--method",
                method,
                "--split",
                "dev",
                "--system",
                system,
                "--seed",
                str(seed),
                "--attempt",
                str(attempt),
            ],
            env=run_env(method, system, seed, attempt, threads),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        with log_path.open("w", encoding="utf-8") as log:
            for line in process.stdout:  # type: ignore[union-attr]
                log.write(line)
                if "M3 re-plan" in line or "Traceback" in line:
                    print(f"    {method} {system} {seed}: {line.rstrip()[-140:]}")
        returncode = process.wait()
        elapsed = time.monotonic() - started
        attempt_dir = run_dir(method, system, seed) / f"attempt_{attempt:02d}"
        problem = run_problem(attempt_dir, RESULTS) if returncode == 0 else None
        if problem:
            returncode = -1  # completed but unusable; rerun under a new attempt
        status = (
            "ok"
            if returncode == 0
            else f"INVALID ({problem})"
            if problem
            else f"FAILED ({returncode}, see {log_path})"
        )
        with lock:
            print(
                f"[{index}/{len(todo)}] {status}: {method} {system} seed {seed}"
                f" in {elapsed:.0f}s",
                flush=True,
            )
            if returncode != 0:
                failures.append((method, system, seed, attempt))

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for index, run in enumerate(todo, start=1):
            pool.submit(run_one, index, *run)

    if failures:
        print("Failed runs (rerun this script to retry under a new attempt):")
        for method, system, seed, attempt in failures:
            print(f"  {method} {system} seed {seed} attempt {attempt}")
        raise SystemExit(1)
    print("All runs completed. Next: uv run python ../../M3/summarize_ablations.py")


if __name__ == "__main__":
    main()
