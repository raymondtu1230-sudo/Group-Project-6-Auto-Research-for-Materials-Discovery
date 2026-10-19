"""Protect expensive scheduling against duplicate or invalid retained evidence."""

import json
from pathlib import Path
from zipfile import ZipFile

import pytest
import yaml

from M2 import prepare_missing as scheduling
from M2.tests.test_evaluation import fixture_run, write


def protocol(tmp_path: Path):
    data = {
        "oracle": {"name": "ORBOracle"},
        "environment": {"query_budget": 4},
        "methods": {"required": list(scheduling.BASELINES)},
        "repeats": {"seeds": [17, 29, 43]},
    }
    p, s = tmp_path / "protocol.yaml", tmp_path / "systems.json"
    p.write_text(yaml.safe_dump(data))
    write(s, [["Li", "O"], ["Na", "Cl"]])
    return data, p, s


def test_completed_pair_is_never_rescheduled(tmp_path):
    data, p, s = protocol(tmp_path)
    for method in scheduling.BASELINES:
        path = fixture_run(tmp_path / "raw", method)
        m = json.loads((path / "run_metadata.json").read_text())
        m["protocol_settings"] = data
        del m["unit_test_fixture"]  # synthetic files stay in pytest's tmp_path
        write(path / "run_metadata.json", m)
    plan = scheduling.prepare(tmp_path / "raw", p, s)
    assert plan["completed_baseline_units"] == 2
    assert plan["missing_baseline_units"] == 10
    assert len(plan["hosted_random_matrix"]["include"]) == 5
    assert len(plan["capacity_blocked_chemeleon_units"]) == 5
    assert not any(
        u["system"] == "Li-O" and u["seed"] == 17 for u in plan["missing_units"]
    )


def test_invalid_or_latest_failed_evidence_blocks_scheduling(tmp_path):
    _, p, s = protocol(tmp_path)
    path = fixture_run(tmp_path / "raw", scheduling.BASELINES[0])
    m = json.loads((path / "run_metadata.json").read_text())
    m["protocol_settings"] = yaml.safe_load(p.read_text())
    write(path / "run_metadata.json", m)
    with pytest.raises(ValueError, match="Synthetic fixture"):
        scheduling.prepare(tmp_path / "raw", p, s)
    path = fixture_run(tmp_path / "raw", scheduling.BASELINES[0], attempt=2)
    write(
        path / "run_metadata.json",
        {**json.loads((path / "run_metadata.json").read_text()), "status": "failed"},
    )
    with pytest.raises(ValueError, match="explicit review"):
        scheduling.prepare(tmp_path / "raw", p, s)


def test_archive_hash_and_existing_bytes_are_protected(tmp_path, monkeypatch):
    import hashlib

    monkeypatch.setattr(scheduling, "REPO", tmp_path)
    archive = tmp_path / "raw.zip"
    with ZipFile(archive, "w") as z:
        z.writestr("result.json", '{"actual": true}')
    manifest = tmp_path / "manifest.json"
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    write(manifest, {"archives": [{"path": "raw.zip", "sha256": digest}]})
    scheduling.import_verified_archives(manifest, tmp_path / "dest")
    scheduling.import_verified_archives(manifest, tmp_path / "dest")
    (tmp_path / "dest" / digest / "result.json").write_text("changed")
    with pytest.raises(ValueError, match="refusing overwrite"):
        scheduling.import_verified_archives(manifest, tmp_path / "dest")
    write(manifest, {"archives": [{"path": "raw.zip", "sha256": "wrong"}]})
    with pytest.raises(ValueError, match="checksum mismatch"):
        scheduling.import_verified_archives(manifest, tmp_path / "dest")
