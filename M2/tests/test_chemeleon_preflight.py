"""Synthetic control tests plus real subprocess timeout; no benchmark sampling."""

import json
import subprocess

import pytest

from M2 import chemeleon_preflight as preflight
from M2 import execution_ledger, run_baselines


@pytest.mark.parametrize("elapsed", [0, 300, 1800, 20000])
def test_budget_preserves_real_save_time(elapsed):
    result = preflight.budget(100, 100 + elapsed)
    assert result["compute_seconds"] <= 340 * 60 - 60
    assert (
        elapsed + result["compute_seconds"] + result["save_reserve_seconds"] + 60
        <= 360 * 60
    )


def test_exhausted_setup_refuses_compute():
    with pytest.raises(ValueError, match="No safe compute"):
        preflight.budget(0, 360 * 60)


def plan():
    return {
        "source_sha": "a" * 40,
        "validated_direct_source": True,
        "matrix": {
            "include": [
                {"method": preflight.METHOD, "system": "Mg-Sn-Sr", "seed": 29, "B": 20},
                {"method": preflight.METHOD, "system": "Co-Dy-W", "seed": 17, "B": 20},
            ]
        },
    }


def request():
    return {"source_sha": "a" * 40, "max_parallel": 17, "mode": "infrastructure_only"}


def test_matrix_and_already_completed_unit_protection():
    assert len(preflight.validate_request(request(), plan())) == 2
    for units in [
        [{"system": "Mg-Sn-Sr", "seed": 17}],
        [{"system": "Co-Dy-W", "seed": 17}] * 2,
    ]:
        with pytest.raises(ValueError):
            preflight.validate_request({**request(), "units": units}, plan())


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_sha", "b" * 40),
        ("max_parallel", 18),
        ("max_parallel", True),
        ("mode", "formal_direct"),
    ],
)
def test_bad_request_fails_before_science(field, value):
    with pytest.raises(ValueError):
        preflight.validate_request({**request(), field: value}, plan())


def test_formal_requires_exact_acknowledgement():
    formal = {**request(), "mode": "formal_direct"}
    with pytest.raises(ValueError):
        preflight.validate_request(formal, plan(), True)
    formal["acknowledgement"] = "RUN_ONLY_MISSING_DEV_CHEMELEON_B20_NO_RESUME"
    assert len(preflight.validate_request(formal, plan(), True)) == 2


def test_real_subprocess_timeout_preserves_failure_evidence(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    made = root / "M1/MADE"
    made.mkdir(parents=True)
    (root / "M1/run_experiment.py").write_text(
        "import time\nprint('TEST PROCESS ONLY, NO SCIENCE', flush=True)\ntime.sleep(60)\n"
    )
    monkeypatch.setattr(run_baselines, "REPO", root)
    monkeypatch.setattr(run_baselines, "MADE", made)
    assert (
        run_baselines.run_unit(
            preflight.METHOD, "dev", "Mg-Sn-Sr", 29, 1, max_seconds=1
        )
        == 124
    )
    folder = (
        made
        / "results/protocol_v1"
        / preflight.METHOD
        / "dev/Mg-Sn-Sr/seed_29/attempt_01"
    )
    assert (
        json.loads((folder / "m2_exit.json").read_text())["termination"]
        == "compute_time_limit"
    )
    assert "TEST PROCESS ONLY" in (folder / "m2_process.log").read_text()
    assert not json.loads((folder / "m2_metrics_history.json").read_text())[
        "complete_curve"
    ]
    with pytest.raises(ValueError, match="use a new attempt"):
        run_baselines.run_unit(preflight.METHOD, "dev", "Mg-Sn-Sr", 29, 1, 1)


def local_publication(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(remote)],
        check=True,
        capture_output=True,
    )
    checkout = tmp_path / "publication"
    subprocess.run(
        ["git", "clone", str(remote), str(checkout)], check=True, capture_output=True
    )
    execution_ledger.git(checkout, "config", "user.name", "Test")
    execution_ledger.git(checkout, "config", "user.email", "test@example.invalid")
    (checkout / "M2").mkdir()
    (checkout / "M2/test.txt").write_text("synthetic ledger test")
    execution_ledger.git(checkout, "add", "M2")
    execution_ledger.git(checkout, "commit", "-m", "test fixture")
    execution_ledger.git(checkout, "push", "origin", "main")
    return checkout


def test_real_git_claim_blocks_duplicate_and_requires_new_attempt(tmp_path):
    checkout = local_publication(tmp_path)
    unit = "Mg-Sn-Sr-29"
    execution_ledger.claim(checkout, unit, 1, "a" * 40, None)
    with pytest.raises(ValueError, match="Duplicate"):
        execution_ledger.claim(checkout, unit, 2, "a" * 40, None)
    folder = checkout / "M2/execution_ledger" / unit
    (folder / "receipt_1.json").write_text(json.dumps({"status": "failed"}))
    execution_ledger.commit(
        checkout,
        [str((folder / "receipt_1.json").relative_to(checkout))],
        "synthetic failure",
    )
    execution_ledger.claim(checkout, unit, 2, "a" * 40, 1)
    assert (folder / "claim_1.json").is_file() and (folder / "claim_2.json").is_file()
    (folder / "receipt_2.json").write_text(json.dumps({"status": "verified_completed"}))
    with pytest.raises(ValueError, match="Completed"):
        execution_ledger.claim(checkout, unit, 3, "a" * 40, 2)


def test_publication_rejects_non_m2_paths(tmp_path):
    with pytest.raises(ValueError, match="confined"):
        execution_ledger.commit(tmp_path, ["M1/bad.txt"], "refused")


def test_failed_archive_masks_secret_and_preserves_attempt(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    folder = root / "M2/runtime"
    folder.mkdir(parents=True)
    (folder / "log.txt").write_text("synthetic-secret")
    monkeypatch.setattr(preflight, "REPO", root)
    monkeypatch.setenv("MATERIALS_PROJECT_API_KEY", "synthetic-secret")
    monkeypatch.setattr(preflight.subprocess, "check_output", lambda *a, **kw: "a" * 40)
    result = preflight.package(tmp_path / "package", "Mg-Sn-Sr-29", 1, 124)
    from zipfile import ZipFile

    with ZipFile(tmp_path / "package" / result["archive"]) as archive:
        assert archive.read("M2/runtime/log.txt") == b"[REDACTED]"
    assert result["status"] == "timeout"
    with pytest.raises(ValueError, match="overwrite"):
        preflight.package(tmp_path / "package", "Mg-Sn-Sr-29", 1, 1)


def test_locked_mp_api_constructor_contract():
    import inspect

    from mp_api.client import MPRester

    # The client version is fixed by uv.lock. Bind the real public constructor
    # before any authenticated cloud request; no API call occurs here.
    inspect.signature(MPRester).bind(
        api_key="synthetic-not-a-key", mute_progress_bars=True
    )
