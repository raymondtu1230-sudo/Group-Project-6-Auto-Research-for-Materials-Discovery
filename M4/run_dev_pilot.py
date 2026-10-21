"""Run a dev-only M3/M4 Memory pilot through M1; never a frozen-full score.

Run from M1/MADE: python ../../M4/run_dev_pilot.py --arm on --attempt 1
Each arm retains protocol-v1 ORB/settings and a separate development method ID.
The official M1/MADE runner and scientific components are not edited.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MADE = ROOT / "M1/MADE"


def driver_module():
    sys.path.insert(0, str(ROOT / "M1"))
    spec = importlib.util.spec_from_file_location(
        "pilot_m1_driver", ROOT / "M1/run_experiment.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker(args, method, output):
    driver = driver_module()
    original = driver.m1_agent_overrides
    # Extend only this process's CLI allow-list, not the shared team protocol.
    driver.METHODS = (*driver.METHODS, method)
    driver.M3_METHODS = (*driver.M3_METHODS, method)

    def overrides(_method):
        return [
            *original("m3_full"),
            f"agent.enable_memory={str(args.arm == 'on').lower()}",
            f"agent.memory_manager.log_path={output}/m4_evidence.jsonl",
            f"agent.capture_path={output}/m4_proposal_events.jsonl",
        ]

    driver.m1_agent_overrides = overrides
    sys.argv = [
        "run_experiment.py",
        "--method",
        method,
        "--split",
        "dev",
        "--system",
        "Mg-Sn-Sr",
        "--seed",
        "17",
        "--attempt",
        str(args.attempt),
    ]
    try:
        driver.main()
    finally:
        path = output / "run_metadata.json"
        if path.exists():
            metadata = json.loads(path.read_text())
            metadata.update(
                development_only=True,
                pilot_scope="M3 planner/reflection + M4; exploration/routing off",
                memory_arm=args.arm,
            )
            path.write_text(json.dumps(metadata, indent=2, allow_nan=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=["on", "off"], required=True)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if Path.cwd().resolve() != MADE or args.attempt < 1:
        parser.error("Run from M1/MADE; attempt must be positive")
    method = f"m4_dev_pilot_{args.arm}"
    output = (
        MADE
        / f"results/protocol_v1/{method}/dev/Mg-Sn-Sr/seed_17/attempt_{args.attempt:02d}"
    )
    if args.worker:
        worker(args, method, output)
        return
    sys.path.insert(0, str(ROOT / "M2"))
    from run_baselines import (
        checkpoint_history,
        preserve_configuration,
        preserve_history,
    )

    log = output.parent / f"attempt_{args.attempt:02d}.pilot.log"
    if output.exists() or log.exists():
        parser.error("Preserve previous attempts; choose a new attempt number")
    log.parent.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "M4_RUN_ID": f"{method}-dev-Mg-Sn-Sr-seed17-attempt{args.attempt:02d}",
        "M4_EPISODE_ID": "0",
        "PYTHONUNBUFFERED": "1",
    }
    history, seen, trace = [], {}, []
    with log.open("w") as stream:
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--arm",
                args.arm,
                "--attempt",
                str(args.attempt),
            ],
            cwd=MADE,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
        started = time.monotonic()
        try:
            while process.poll() is None:
                current = checkpoint_history(output, MADE / "checkpoints", seen)
                if len(current) > len(history):
                    history = current
                    print(
                        f"{args.arm}: {len(history)} official query metrics captured",
                        flush=True,
                    )
                for checkpoint in (MADE / "checkpoints").glob("**/checkpoint.json"):
                    try:
                        payload = json.loads(checkpoint.read_text())
                        configured = (
                            payload.get("config", {})
                            .get("experiment", {})
                            .get("output_dir")
                        )
                        if not configured:
                            continue
                        path = Path(configured)
                        if not path.is_absolute():
                            path = MADE / path
                        if path.resolve() != output:
                            continue
                        rows = (
                            payload.get("agent_state", {})
                            .get("planner", {})
                            .get("m3", {})
                            .get("decision_trace", [])
                        )
                        if len(rows) > len(trace):
                            trace = rows
                    except (OSError, json.JSONDecodeError):
                        continue
                if time.monotonic() - started > 1800:
                    process.terminate()
                    raise RuntimeError(
                        "Pilot exceeded 30-minute limit; preserve partial attempt"
                    )
                time.sleep(0.2)
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait()
    output.mkdir(parents=True, exist_ok=True)
    metadata_path = output / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    completed = process.returncode == 0 and metadata.get("status") == "completed"
    curve = preserve_history(history, output, completed)
    # Resolve oc.env using the exact child run identity, not parent defaults.
    previous = {key: os.environ.get(key) for key in ("M4_RUN_ID", "M4_EPISODE_ID")}
    try:
        for key in previous:
            os.environ[key] = env[key]
        config_saved = preserve_configuration(output, MADE / "results")
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    (output / "m3_decision_trace.json").write_text(
        json.dumps(trace, indent=2, allow_nan=False)
    )
    (output / "pilot_capture.json").write_text(
        json.dumps(
            {
                "development_only": True,
                "returncode": process.returncode,
                "complete_curve": curve["complete_curve"],
                "config_saved": config_saved,
                "decision_trace_count": len(trace),
                "log": log.name,
            },
            indent=2,
        )
    )
    print(
        json.dumps(
            {
                "arm": args.arm,
                "completed": completed,
                "complete_curve": curve["complete_curve"],
                "config_saved": config_saved,
                "decision_trace_count": len(trace),
            }
        ),
        flush=True,
    )
    if not completed or not curve["complete_curve"] or not config_saved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
