"""Run M3's protocol ablations through M1's ``run_experiment.py``.

Each (method, system, seed) is one official one-episode invocation. Completed
runs are skipped, and a failed run is retried under the next attempt number so
the failure stays on disk, as the protocol requires.

``m1_baseline`` is re-run by default. M1's recorded baseline runs predate M4's
memory manager becoming the default in ``m1_integrated.yaml``, so a fair paired
comparison needs a baseline run under the same configuration as the M3 runs.
Each run gets its own ``M4_RUN_ID``, as M4's adoption notes require.

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
import time
from pathlib import Path

import yaml

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
    metadata = path / "run_metadata.json"
    if not metadata.is_file():
        return False
    return json.loads(metadata.read_text()).get("status") == "completed"


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


def run_env(method: str, system: str, seed: int, attempt: int) -> dict[str, str]:
    # M4 asks for a unique run ID per experiment attempt; one episode per run.
    env = dict(os.environ)
    env["M4_RUN_ID"] = f"{method}-{system}-seed{seed}-attempt{attempt:02d}"
    env["M4_EPISODE_ID"] = "0"
    return env


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
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if Path.cwd().resolve() != MADE_DIR:
        raise SystemExit(f"Run from {MADE_DIR}")
    methods = ([] if args.no_baseline else [BASELINE]) + [
        m for m in args.methods if m != BASELINE
    ]
    todo = [
        (method, system, seed)
        for method in methods
        for system in args.systems
        for seed in args.seeds
        if not any(is_completed(p) for p in attempts(method, system, seed))
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

    failures = []
    for index, (method, system, seed) in enumerate(todo, start=1):
        attempt = next_attempt(method, system, seed)
        print(
            f"[{index}/{len(todo)}] {method} {system} seed {seed} attempt {attempt}",
            flush=True,
        )
        started = time.monotonic()
        log_path = console_log(run_dir(method, system, seed) / f"attempt_{attempt:02d}")
        log_path.parent.mkdir(parents=True, exist_ok=True)
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
            env=run_env(method, system, seed, attempt),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        with log_path.open("w", encoding="utf-8") as log:
            for line in process.stdout:  # type: ignore[union-attr]
                log.write(line)
                if "M3 re-plan" in line or "Traceback" in line or "Error" in line:
                    print(f"    {line.rstrip()[-160:]}", flush=True)
        returncode = process.wait()
        elapsed = time.monotonic() - started
        status = (
            "ok" if returncode == 0 else f"FAILED ({returncode}, see {log_path.name})"
        )
        print(f"    {status} in {elapsed:.0f}s", flush=True)
        if returncode != 0:
            failures.append((method, system, seed, attempt))

    if failures:
        print("Failed runs (rerun this script to retry under a new attempt):")
        for method, system, seed, attempt in failures:
            print(f"  {method} {system} seed {seed} attempt {attempt}")
        raise SystemExit(1)
    print("All runs completed. Next: uv run python ../../M3/summarize_ablations.py")


if __name__ == "__main__":
    main()
