"""Preserve and re-evaluate recorded real outputs, without any new experiment."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "M2/requests/frozen-offline-analysis.json"
WORKFLOW = "M2 preserve existing results without new experiments"
FREEZE = "02e0026bf450f71f4f7862228d295f5b02b49e12"


def active() -> bool:
    return REQUEST.is_file() and os.environ.get("GITHUB_WORKFLOW") == WORKFLOW


def dump(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def gh(path: str) -> dict:
    for retry in range(4):
        try:
            return json.loads(subprocess.check_output(["gh", "api", path], text=True))
        except subprocess.CalledProcessError:
            if retry == 3:
                raise
            time.sleep(2**retry)
    raise RuntimeError("Unreachable GitHub retry state")


def preserve() -> None:
    assert active()
    request = json.loads(REQUEST.read_text())
    assert request["freeze_commit"] == FREEZE and request["new_scientific_queries"] == 0
    destination = ROOT / "M2/results/preserved"
    destination.mkdir(parents=True, exist_ok=True)
    provenance = destination / "provenance.json"
    records = (
        json.loads(provenance.read_text())["artifacts"] if provenance.exists() else []
    )
    seen = {record["artifact_id"] for record in records}
    repo = os.environ["GITHUB_REPOSITORY"]
    for run_id in request["source_run_ids"]:
        page = 1
        while True:
            batch = gh(
                f"repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100&page={page}"
            )["artifacts"]
            if not batch:
                break
            for item in batch:
                if item["id"] in seen:
                    continue
                if not item["name"].startswith("m2-direct-") or item["name"].startswith(
                    "m2-direct-plan-"
                ):
                    continue
                archive = destination / f"{item['id']}-{item['name']}.zip"
                assert Path(item["name"]).name == item["name"]
                with archive.open("wb") as stream:
                    subprocess.run(
                        [
                            "gh",
                            "api",
                            f"repos/{repo}/actions/artifacts/{item['id']}/zip",
                        ],
                        stdout=stream,
                        check=True,
                    )
                digest = hashlib.sha256(archive.read_bytes()).hexdigest()
                assert item["digest"] == "sha256:" + digest
                extract = destination / "raw" / str(item["id"])
                with zipfile.ZipFile(archive) as source:
                    assert source.testzip() is None
                    for member in source.namelist():
                        path = Path(member)
                        assert not path.is_absolute() and ".." not in path.parts
                    source.extractall(extract)
                records.append(
                    {
                        "workflow_run_id": run_id,
                        "artifact_id": item["id"],
                        "artifact_name": item["name"],
                        "archive": archive.name,
                        "sha256": digest,
                        "crc_passed": True,
                    }
                )
                dump(
                    destination / "provenance.json",
                    {
                        "kind": "exact_real_routing_artifact_preservation",
                        "new_scientific_units": 0,
                        "new_oracle_queries": 0,
                        "artifacts": records,
                        "capture_complete": False,
                    },
                )
            page += 1
    if len(records) < 18:
        started = float(
            os.environ.setdefault("M2_OFFLINE_WAIT_EPOCH", str(time.time()))
        )
        if time.time() - started < request.get("wait_for_artifacts_seconds", 720):
            print(
                f"Saved{len(records)}/18 original result ZIPs; waiting20s for remaining cloud outputs",
                flush=True,
            )
            time.sleep(20)
            preserve()
            return
    assert len(records) == 18, (
        f"Expected18 unique real unit artifact ZIPs, got{len(records)}"
    )
    dump(
        destination / "provenance.json",
        {
            "kind": "exact_real_routing_artifact_preservation",
            "new_scientific_units": 0,
            "new_oracle_queries": 0,
            "artifacts": records,
            "capture_complete": True,
        },
    )
    print(
        "18 exact original real-result ZIPs preserved; no experiment was started",
        flush=True,
    )


def score() -> None:
    assert active()
    destination = ROOT / "M2/results/preserved"
    report = destination / "report"
    report.mkdir(parents=True, exist_ok=True)
    assets = []
    for receipt_path in sorted((destination / "raw").glob("*/packaged/receipt.json")):
        receipt = json.loads(receipt_path.read_text())
        runtime = receipt_path.parents[1] / "runtime"
        checkpoint = json.loads((runtime / "actual-checkpoint.json").read_text())
        source = json.loads((runtime / "frozen-source.json").read_text())
        expected_weight = (
            "ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e"
        )
        assert checkpoint["archive_sha256"] == expected_weight
        assert checkpoint["archive_bytes"] == 548874535 and checkpoint["matches"]
        assert source["freeze_commit"] == FREEZE and source["root_tracked_clean"]
        loads = [
            json.loads(line)
            for line in (runtime / "actual-model-load.log").read_text().splitlines()
            if line.startswith('{"actual_cpu_model_load"')
        ]
        assert len(loads) == 1 and loads[0]["actual_cpu_model_load"]
        assets.append(
            {
                "system": receipt["system"],
                "seed": receipt["seed"],
                "archive_sha256": checkpoint["archive_sha256"],
                "extracted_csp_sha256": checkpoint["extracted_csp_sha256"],
                "actual_cpu_model_load": True,
                "actual_frozen_source": source["freeze_commit"],
                "source_artifact": receipt_path.parts[-3],
            }
        )
    assert len(assets) == 18 and len({(x["system"], x["seed"]) for x in assets}) == 18
    assert len({x["extracted_csp_sha256"] for x in assets}) == 1
    dump(
        report / "actual_asset_verification.json",
        {"passed": True, "verified_runtime_units": 18, "records": assets},
    )
    science = Path(os.environ["RUNNER_TEMP"]) / "m2-recorded-evaluation-frozen"
    if not science.exists():
        subprocess.run(
            ["git", "fetch", "origin", "main", "--tags"], cwd=ROOT, check=True
        )
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(science), FREEZE],
            cwd=ROOT,
            check=True,
        )
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=science, text=True
    ).strip()
    assert actual == FREEZE
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(science / "M1/MADE/src"), str(science / "M4/src")]
    )
    env["PYTHONUNBUFFERED"] = "1"
    env.pop("MATERIALS_PROJECT_API_KEY", None)
    env.pop("TUWEIKANG_MATERIALS_PROJECT_API_KEY", None)
    python = str(ROOT / "M1/MADE/.venv/bin/python")
    reevaluation = report / "recorded_curve_analysis"
    command = [
        python,
        str(ROOT / "M2/reevaluate_recorded.py"),
        "--reference-repo",
        str(science),
        "--routing-root",
        str(destination / "raw"),
        "--output",
        str(reevaluation),
    ]
    print(
        "OFFLINE RECORDED-OUTPUT ANALYSIS (zero oracle/model calls): "
        + " ".join(command),
        flush=True,
    )
    subprocess.run(command, cwd=ROOT, env=env, check=True)
    endpoints = report / "endpoint_comparison"
    command = [
        python,
        str(ROOT / "M2/frozen_report.py"),
        "--results-root",
        str(destination / "raw"),
        "--reference-root",
        str(science / "M1/MADE/results/protocol_v1/m1_full/dev"),
        "--output",
        str(endpoints),
        "--curve-analysis-root",
        str(reevaluation),
    ]
    subprocess.run(command, cwd=ROOT, env=env, check=True)
    controls = report / "reproduction_code"
    controls.mkdir()
    for name in (
        "offline_frozen.py",
        "reevaluate_recorded.py",
        "frozen_report.py",
        "frozen_routing.py",
        "frozen_collect.py",
        "FROZEN_ROUTING_RUNBOOK.md",
    ):
        shutil.copyfile(ROOT / "M2" / name, controls / name)
    baseline_audit = ROOT / "M2/verification/frozen_baseline_compatibility"
    if baseline_audit.is_dir():
        shutil.copytree(baseline_audit, report / "baseline_compatibility")
    dump(
        report / "offline_execution.json",
        {
            "freeze_commit": actual,
            "new_scientific_queries": 0,
            "new_agent_proposals": 0,
            "new_model_inference": 0,
            "request": json.loads(REQUEST.read_text()),
            "controller_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "analysis": "Official metric functions applied to original recorded structures and energies; no historical checkpoint is invented",
        },
    )
    dump(
        destination / "offline_score_complete.json",
        {"passed": True, "real_units": 18, "new_oracle_queries": 0},
    )


def confirm() -> None:
    assert active()
    record = json.loads(
        (ROOT / "M2/results/preserved/offline_score_complete.json").read_text()
    )
    assert record["passed"] is True and record["real_units"] == 18
    print(
        "Recorded-output analysis and18-unit endpoint audit complete; original data unchanged",
        flush=True,
    )
