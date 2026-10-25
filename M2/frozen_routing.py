"""Real M2 frozen routing ablation through existing, unchanged M2 CI infrastructure.

The legacy workflow name is transport only. Scientific execution is exclusively
the detached frozen M1/run_experiment.py, with no source/config modifications.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "M2/requests/frozen-routing-off.json"
FREEZE = "02e0026bf450f71f4f7862228d295f5b02b49e12"
TAG = "m1-freeze-20261025"
UPSTREAM = "bffda0c9a1fa1904b35c0ef67b455881c975df86"
EXPECTED_WEIGHT = "ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e"
METHOD = "tool_routing_off"
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
SEEDS = (17, 29, 43)
WORKFLOW = "M2 missing-only Chemeleon direct full runs"
NAMESPACE = "M2/frozen_20261025"
RUNTIME = ROOT / "M2/runtime"
SCIENCE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "m2-frozen-routing-science"


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args: list[str], cwd: Path | None = None, **kwargs):
    return subprocess.run(args, cwd=cwd, check=True, **kwargs)


def out(args: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def active() -> bool:
    if not TASK.is_file() or os.environ.get("GITHUB_WORKFLOW") != WORKFLOW:
        return False
    task = json.loads(TASK.read_text())
    assert task["method"] == METHOD and task["freeze_commit"] == FREEZE
    assert task["checkpoint_sha256"] == EXPECTED_WEIGHT and task["split"] == "dev"
    assert task["systems"] == list(SYSTEMS) and task["seeds"] == list(SEEDS)
    return True


def science_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SCIENCE / "M1/MADE/src"), str(SCIENCE / "M4/src")])
    env["PYTHONUNBUFFERED"] = "1"
    env["MATERIALS_PROJECT_API_KEY"] = env.get("MATERIALS_PROJECT_API_KEY", "").strip()
    return env


def prepare_science() -> Path:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if not SCIENCE.is_dir():
        run(["git", "fetch", "origin", "main", "--tags"], ROOT)
        assert out(["git", "rev-parse", f"{TAG}^{{commit}}"], ROOT) == FREEZE
        run(["git", "worktree", "add", "--detach", str(SCIENCE), FREEZE], ROOT)
    assert out(["git", "rev-parse", "HEAD"], SCIENCE) == FREEZE
    assert out(["git", "describe", "--exact-match", "--tags", "HEAD"], SCIENCE) == TAG
    assert not out(["git", "status", "--porcelain", "--untracked-files=no"], SCIENCE)
    made = SCIENCE / "M1/MADE"
    assert sha(made / "uv.lock") == sha(ROOT / "M1/MADE/uv.lock")
    if not (made / ".venv").exists():
        (made / ".venv").symlink_to(ROOT / "M1/MADE/.venv", target_is_directory=True)
    # M1's reference has an actual nested official-upstream checkout. Recreate
    # its Git boundary from genuine upstream history, leaving all frozen files.
    if not (made / ".git").exists():
        run(["git", "init"], made)
        run(["git", "fetch", "--depth", "1", "https://github.com/diffractivelabs/MADE.git", UPSTREAM], made)
        run(["git", "reset", "--mixed", "FETCH_HEAD"], made, stdout=subprocess.DEVNULL)
    assert out(["git", "rev-parse", "HEAD"], made) == UPSTREAM
    assert not out(["git", "status", "--porcelain", "--untracked-files=no"], SCIENCE)
    dump(RUNTIME / "frozen-source.json", {
        "method": METHOD, "freeze_commit": FREEZE, "freeze_tag": TAG,
        "root_tracked_clean": True, "official_upstream_head": UPSTREAM,
        "nested_git_setup": "fetch genuine official upstream then reset --mixed; no scientific file changed",
        "controller_commit": out(["git", "rev-parse", "HEAD"], ROOT),
        "uv_lock_sha256": sha(made / "uv.lock"), "python": sys.version,
        "machine": platform.node(), "platform": platform.platform(),
    })
    return made


def api_check(output: Path) -> None:
    from mp_api.client import MPRester
    key = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip()
    assert len(key) == 32, "Missing valid-format Materials Project credential"
    with MPRester(api_key=key) as client:
        docs = client.materials.summary.search(chemsys="Mg-Sn-Sr", num_chunks=1, chunk_size=1, fields=["material_id"])
        record = {"kind": "actual_authenticated_materials_project_request", "status": "accepted", "documents": len(docs), "database_version": client.get_database_version(), "material_ids": [str(x.material_id) for x in docs], "method": METHOD}
    dump(output, record)
    print(json.dumps(record), flush=True)


def model_check() -> None:
    made = prepare_science()
    archive = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "m2-frozen-chemeleon.tar.gz"
    if not archive.is_file() or sha(archive) != EXPECTED_WEIGHT:
        with urllib.request.urlopen("https://api.figshare.com/v2/file/download/54966305", timeout=90) as source, archive.open("wb") as target:
            shutil.copyfileobj(source, target, 1024 * 1024)
    measured = sha(archive)
    assert measured == EXPECTED_WEIGHT, "Actual checkpoint archive SHA-256 mismatch"
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(made, filter="data")
    checkpoint = made / "ckpts/chemeleon_csp_alex_mp_20_v0.0.2.ckpt"
    assert checkpoint.is_file()
    dump(RUNTIME / "actual-checkpoint.json", {"method": METHOD, "archive_sha256": measured, "archive_bytes": archive.stat().st_size, "expected_sha256": EXPECTED_WEIGHT, "matches": True, "extracted_csp_sha256": sha(checkpoint), "source": "official Figshare file 54966305", "checked_at_utc": datetime.now(UTC).isoformat()})
    code = """import json, pathlib
import made, made.agents.m1_integrated, made.agents.m2_tool_routing, m4_memory.capture
from made.agents.generators.chemeleon import ChemeleonGenerator
from made.oracles.orb.orb_oracle import ORBOracle
modules=[made,made.agents.m1_integrated,made.agents.m2_tool_routing,m4_memory.capture]
paths=[str(pathlib.Path(m.__file__).resolve()) for m in modules]
assert all(str(pathlib.Path.cwd().parents[1]) in p for p in paths),paths
generator=ChemeleonGenerator(task='csp',batch_size=32,device='cpu')
generator.setup()
oracle=ORBOracle(model_name='orb-v3-conservative-inf-omat',device='cpu')
print(json.dumps({'actual_cpu_model_load':True,'sampling_calls':0,'oracle_queries':0,'module_paths':paths}))
"""
    with (RUNTIME / "actual-model-load.log").open("w") as stream:
        run([str(made / ".venv/bin/python"), "-c", code], made, env=science_env(), stdout=stream, stderr=subprocess.STDOUT, timeout=150)
    print("Actual frozen Chemeleon + ORB CPU model loads passed", flush=True)


def plan(args: argparse.Namespace) -> None:
    request = json.loads(args.request.read_text())
    assert request["task"] == METHOD and request["freeze_commit"] == FREEZE
    expected = [{"system": system, "seed": seed} for system in SYSTEMS for seed in SEEDS]
    assert request["units"] == expected and request["max_parallel"] <= 4
    args.output.mkdir(parents=True, exist_ok=True)
    record = {"method": METHOD, "freeze_commit": FREEZE, "units": expected, "count": 18, "science_started": False, "old_baselines_rerun": False, "workflow_transport": WORKFLOW}
    dump(args.output / "plan.json", record)
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        print("matrix=" + json.dumps({"include": expected}), file=stream)
        print("parallel=" + str(request["max_parallel"]), file=stream)
        print("retry_of={}", file=stream)
    print(json.dumps(record), flush=True)


def git_publish(publication: Path, paths: list[str], message: str) -> None:
    assert paths and all(p.startswith(NAMESPACE + "/") for p in paths)
    run(["git", "config", "user.name", "github-actions[bot]"], publication)
    run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], publication)
    run(["git", "add", "--", *paths], publication)
    changed = out(["git", "diff", "--cached", "--name-only"], publication).splitlines()
    assert changed and all(p.startswith(NAMESPACE + "/") for p in changed), changed
    run(["git", "commit", "-m", message], publication)
    for _ in range(8):
        run(["git", "pull", "--rebase", "origin", "main"], publication)
        attempt = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=publication)
        if attempt.returncode == 0:
            return
        time.sleep(2)
    raise RuntimeError("M2-only publication push failed")


def claim(args: argparse.Namespace) -> None:
    unit = args.unit
    assert unit in {f"{s}-{seed}" for s in SYSTEMS for seed in SEEDS}
    run(["git", "pull", "--rebase", "origin", "main"], args.publication)
    relative = f"{NAMESPACE}/claims/{unit}.json"
    target = args.publication / relative
    if target.exists():
        raise RuntimeError(f"Existing claim retained; refuse duplicate scientific dispatch for {unit}")
    dump(target, {"method": METHOD, "unit": unit, "workflow_run_id": os.environ["GITHUB_RUN_ID"], "transport_attempt": args.attempt, "scientific_attempts_begin_at": 1, "freeze_commit": FREEZE, "status": "claimed", "time": datetime.now(UTC).isoformat()})
    git_publish(args.publication, [relative], f"M2: claim frozen routing-off {unit}")


def compute(args: argparse.Namespace) -> int:
    from frozen_collect import collect, validate
    assert args.split == "dev" and args.system in SYSTEMS and args.seed in SEEDS
    # Incoming method/attempt belong to unchanged legacy transport; they never
    # determine the scientific method, seed, budget, or attempt number.
    made = prepare_science()
    assert json.loads((RUNTIME / "actual-checkpoint.json").read_text())["matches"]
    deadline = time.monotonic() + min(float(args.max_seconds or 19000), 340 * 60 - 90)
    last = 1
    for scientific_attempt in (1, 2):
        attempt_dir = made / f"results/protocol_v1/{METHOD}/dev/{args.system}/seed_{args.seed}/attempt_{scientific_attempt:02d}"
        if attempt_dir.exists():
            raise RuntimeError("Never overwrite an existing scientific attempt")
        env = science_env()
        env["M4_RUN_ID"] = f"{METHOD}-{args.system}-{args.seed}-attempt{scientific_attempt:02d}-{os.environ['GITHUB_RUN_ID']}"
        env["M4_EPISODE_ID"] = "0"
        os.environ["M4_RUN_ID"] = env["M4_RUN_ID"]
        os.environ["M4_EPISODE_ID"] = "0"
        command = [str(made / ".venv/bin/python"), "../run_experiment.py", "--method", METHOD, "--split", "dev", "--system", args.system, "--seed", str(args.seed), "--attempt", str(scientific_attempt)]
        log = RUNTIME / f"{args.system}-{args.seed}-attempt_{scientific_attempt:02d}.log"
        print("REAL SCIENTIFIC COMMAND: " + " ".join(command), flush=True)
        with log.open("w") as stream:
            proc = subprocess.Popen(command, cwd=made, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                while proc.poll() is None:
                    if time.monotonic() >= deadline:
                        import signal
                        os.killpg(proc.pid, signal.SIGTERM)
                        try:
                            proc.wait(45)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid, signal.SIGKILL)
                        break
                    print(f"REAL_PROGRESS system={args.system} seed={args.seed} attempt={scientific_attempt} elapsed_running=true log_bytes={log.stat().st_size}", flush=True)
                    time.sleep(30)
                last = proc.wait()
            finally:
                collect(SCIENCE, attempt_dir, log, proc.poll() if proc.poll() is not None else -1)
        if last == 0:
            audit = validate(SCIENCE, attempt_dir)
            if audit.get("accepted"):
                return 0
            # A collection/audit finding does not justify recomputing an
            # otherwise completed scientific episode. Diagnose preserved data.
            print(json.dumps(audit), flush=True)
            return 2
        if time.monotonic() + 120 >= deadline:
            break
        print("Preserving failed attempt; next new attempt will be attempt_02", flush=True)
    return last or 1


def package(args: argparse.Namespace) -> None:
    args.output.mkdir(parents=True, exist_ok=True)
    source = SCIENCE / f"M1/MADE/results/protocol_v1/{METHOD}/dev/{args.system}/seed_{args.seed}"
    destination = args.output / f"protocol_v1/{METHOD}/dev/{args.system}/seed_{args.seed}"
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=False)
    dump(args.output / "receipt.json", {"method": METHOD, "system": args.system, "seed": args.seed, "freeze_commit": FREEZE, "exit_code": args.exit_code, "attempts": sorted(p.name for p in destination.glob("attempt_*")) if destination.exists() else [], "runtime_evidence": "../runtime", "workflow_run_id": os.environ["GITHUB_RUN_ID"]})


def publish(args: argparse.Namespace) -> None:
    run_id = args.run_id
    assert run_id.replace("-", "").isdigit()
    relative = f"{NAMESPACE}/runs/{run_id}"
    destination = args.publication / relative
    shutil.copytree(args.downloads, destination, dirs_exist_ok=False)
    secret = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip()
    if secret:
        assert not any(secret.encode() in p.read_bytes() for p in destination.rglob("*") if p.is_file())
    dump(destination / "publication.json", {"method": METHOD, "freeze_commit": FREEZE, "path": relative, "all_attempts_preserved": True, "outside_M2_changed": False, "run_id": run_id})
    git_publish(args.publication, [relative], f"M2: preserve frozen routing-off attempts from {run_id}")


def fingerprint() -> dict[str, str]:
    made = prepare_science()
    values = {str(p.relative_to(SCIENCE)): sha(p) for p in sorted((made / "src/made").rglob("*.py"))}
    values.update({str(p.relative_to(SCIENCE)): sha(p) for p in sorted((made / "configs").rglob("*.yaml"))})
    dump(RUNTIME / "frozen_science_inputs.json", values)
    return values


def main(kind: str) -> None:
    assert active(), "Frozen M2 task guard not satisfied"
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default=kind)
    for name in ("output", "request", "published", "publication", "downloads"):
        parser.add_argument("--" + name, type=Path)
    for name in ("method", "split", "system", "source", "retry-of", "unit", "kind", "run-id"):
        parser.add_argument("--" + name)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--attempt", type=int)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--max-seconds", type=float)
    parser.add_argument("--formal", action="store_true")
    args = parser.parse_args()
    if kind == "model":
        model_check()
    elif kind == "compute":
        raise SystemExit(compute(args))
    elif kind == "ledger":
        {"claim": claim, "publish": publish}[args.command](args)
    elif args.command == "plan":
        plan(args)
    elif args.command == "api":
        api_check(args.output)
    elif args.command == "budget":
        elapsed = max(0, int(time.time()) - int(os.environ["M2_JOB_EPOCH"]))
        seconds = min(340 * 60 - 90, 360 * 60 - elapsed - 330)
        assert seconds >= 120
        dump(args.output, {"method": METHOD, "compute_seconds": seconds, "job_limit_minutes": 360, "outer_compute_limit_minutes": 340, "exit_and_save_reserve_seconds": 330})
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            print(f"seconds={seconds}", file=stream)
    elif args.command == "package":
        package(args)
    else:
        raise ValueError(args.command)

