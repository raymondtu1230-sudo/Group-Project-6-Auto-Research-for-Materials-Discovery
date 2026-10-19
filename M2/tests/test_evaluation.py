"""Synthetic records exist only in pytest tmp_path, never in reported results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from M2 import evaluate
from M2.evaluate import (
    CURVE,
    MSUN,
    collect,
    compare,
    load_run,
    summarize,
    summarize_methods,
)
from M2.run_baselines import (
    checkpoint_history,
    preserve_configuration,
    preserve_history,
)


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def fixture_run(root: Path, method: str = "m1_full", attempt: int = 1) -> Path:
    path = root / method / f"attempt_{attempt:02d}"
    write(
        path / "run_metadata.json",
        {
            "status": "completed",
            "method": method,
            "split": "dev",
            "system": ["Li", "O"],
            "seed": 17,
            "attempt": attempt,
            "query_budget": 4,
            "wall_time_seconds": 2.0,
            "protocol_settings": {
                "oracle": {"name": "ORBOracle"},
                "environment": {"query_budget": 4},
            },
            "cost": {"oracle": {"queries": 4}, "total_known_cost_usd": None},
            "unit_test_fixture": True,
        },
    )
    write(
        path / "trajectories/episode_000.json",
        {
            "trajectory": [{}, {}, {}, {}],
            "phase_diagram_gt": [{"composition": {"Li": 1}, "energy": 0}],
            "metrics": {
                "final/queries_used": 4,
                f"final/{MSUN}": 2,
                "final/discovery_curve_area_under_discovery_curve": 4.0,
            },
        },
    )
    write(path / "summary/summary.json", {"episodes": 1})
    write(
        path / "m2_metrics_history.json",
        {
            "complete_curve": True,
            "metrics_history": [
                {"queries_used": i, MSUN: count, CURVE: count}
                for i, count in enumerate([0, 1, 2, 2], start=1)
            ],
        },
    )
    (path / "resolved_config.yaml").write_text(
        "environment:\n  budget: 4\nexperiment:\n  seed: 17\n"
        "dataset:\n  elements: [Li, O]\n"
    )
    return path


def test_official_metrics_match_a_hand_calculated_example(tmp_path: Path) -> None:
    run = load_run(fixture_run(tmp_path))
    assert run.row["mSUN_at_B"] == 2
    # Trapezoids for [0,0,1,2,2] at queries [0,1,2,3,4].
    assert run.row["AUDC"] == 4.0
    assert run.row["known_cost_usd"] is None


def test_official_msun_and_official_audc_curve_are_kept_distinct(
    tmp_path: Path,
) -> None:
    path = fixture_run(tmp_path)
    history_path = path / "m2_metrics_history.json"
    history = json.loads(history_path.read_text())
    history["metrics_history"][-1][MSUN] = 1
    write(history_path, history)
    trajectory_path = path / "trajectories/episode_000.json"
    trajectory = json.loads(trajectory_path.read_text())
    trajectory["metrics"][f"final/{MSUN}"] = 1
    write(trajectory_path, trajectory)
    run = load_run(path)
    assert run.row["mSUN_at_B"] == 1
    assert run.row["AUDC"] == 4.0


def test_paired_af_ef_use_official_functions_and_the_same_seed(tmp_path: Path) -> None:
    proposal = load_run(fixture_run(tmp_path))
    baseline_path = fixture_run(tmp_path, "random_generator_baseline")
    history_path = baseline_path / "m2_metrics_history.json"
    history = json.loads(history_path.read_text())
    for point, count in zip(history["metrics_history"], [0, 0, 1, 1], strict=True):
        point[MSUN] = point[CURVE] = count
    write(history_path, history)
    trajectory_path = baseline_path / "trajectories/episode_000.json"
    trajectory = json.loads(trajectory_path.read_text())
    trajectory["metrics"][f"final/{MSUN}"] = 1
    trajectory["metrics"]["final/discovery_curve_area_under_discovery_curve"] = 1.5
    write(trajectory_path, trajectory)
    baseline = load_run(baseline_path)
    compare([proposal, baseline])
    assert proposal.row["AF_vs_random"] == 1.5
    assert proposal.row["EF_vs_random"] == 2.0
    assert proposal.row["AF_vs_chemeleon"] is None
    assert proposal.row["comparison_chemeleon"] == "missing_paired_baseline"


@pytest.mark.parametrize(
    "field",
    ["status", "budget", "protocol_budget", "config", "curve", "audc", "oracle"],
)
def test_failed_incomplete_or_synthetic_experiments_are_rejected(
    tmp_path: Path, field: str
) -> None:
    path = fixture_run(tmp_path)
    meta_path = path / "run_metadata.json"
    metadata = json.loads(meta_path.read_text())
    if field == "status":
        metadata["status"] = "failed"
    elif field == "budget":
        metadata["query_budget"] = 5
    elif field == "protocol_budget":
        metadata["protocol_settings"]["environment"]["query_budget"] = 20
    elif field == "config":
        (path / "resolved_config.yaml").write_text("environment: {budget: 999}\n")
    elif field == "oracle":
        metadata["protocol_settings"]["oracle"]["name"] = "AnalyticOracle"
    elif field == "curve":
        write(
            path / "m2_metrics_history.json",
            {"complete_curve": False, "metrics_history": []},
        )
    else:
        trajectory_path = path / "trajectories/episode_000.json"
        trajectory = json.loads(trajectory_path.read_text())
        trajectory["metrics"]["final/discovery_curve_area_under_discovery_curve"] = 999
        write(trajectory_path, trajectory)
    write(meta_path, metadata)
    with pytest.raises(ValueError):
        load_run(path)


def test_latest_failed_attempt_does_not_fall_back_to_a_success(tmp_path: Path) -> None:
    fixture_run(tmp_path, attempt=1)
    latest = fixture_run(tmp_path, attempt=2)
    meta_path = latest / "run_metadata.json"
    metadata = json.loads(meta_path.read_text())
    metadata["status"] = "failed"
    write(meta_path, metadata)
    runs, issues = collect(tmp_path, "dev")
    assert runs == []
    assert {i["kind"] for i in issues} == {
        "superseded_attempt",
        "incomplete_or_invalid_run",
    }


def test_different_reference_revisions_cannot_be_compared(tmp_path: Path) -> None:
    first = load_run(fixture_run(tmp_path))
    other = load_run(fixture_run(tmp_path, "random_generator_baseline"))
    other.reference_hash = "different-data-revision"
    with pytest.raises(ValueError, match="reference revision"):
        compare([first, other])


def test_one_repeat_has_no_invented_standard_deviation(tmp_path: Path) -> None:
    run = load_run(fixture_run(tmp_path))
    compare([run])
    summary = summarize([run])[0]
    assert summary["n"] == 1
    assert summary["mSUN_at_B_std"] is None
    assert summary["known_cost_usd_mean"] is None


def test_method_table_uses_equal_system_weights_and_variability_across_seeds(
    tmp_path: Path,
) -> None:
    runs = []
    for i, (system, seed, count) in enumerate(
        [("Li-O", 17, 0), ("Na-Cl", 17, 2), ("Li-O", 29, 1), ("Na-Cl", 29, 2)]
    ):
        run = load_run(fixture_run(tmp_path / str(i)))
        run.row.update(system=system, seed=seed, mSUN_at_B=count)
        runs.append(run)
    row = summarize_methods(runs, [["Li", "O"], ["Na", "Cl"]], [17, 29])[0]
    assert row["complete_method_sweep"] is True
    # Seed means are 1 and 1.5; do not use SD across the four heterogeneous systems.
    assert row["mSUN_at_B_mean"] == 1.25
    assert row["mSUN_at_B_std"] == pytest.approx(0.3535533905932738)
    assert row["mSUN_at_B_seed_n"] == 2
    assert row["known_cost_usd_mean"] is None
    incomplete = summarize_methods(runs[:-1], [["Li", "O"], ["Na", "Cl"]], [17, 29])[0]
    assert incomplete["complete_method_sweep"] is False
    assert incomplete["mSUN_at_B_mean"] is None


def test_checkpoint_capture_selects_only_its_own_run(tmp_path: Path) -> None:
    output, checkpoints = tmp_path / "output", tmp_path / "checkpoints"
    rows = [{"queries_used": 1, MSUN: 0, CURVE: 0}]
    write(
        checkpoints / "own/checkpoint.json",
        {
            "config": {"experiment": {"output_dir": str(output)}},
            "metrics_history": rows,
        },
    )
    write(
        checkpoints / "other/checkpoint.json",
        {
            "config": {"experiment": {"output_dir": str(tmp_path / "other")}},
            "metrics_history": rows * 9,
        },
    )
    assert checkpoint_history(output, checkpoints) == rows
    assert preserve_history(rows, output, completed=False)["complete_curve"] is True


def test_missing_intermediate_queries_are_not_fabricated(tmp_path: Path) -> None:
    record = preserve_history(
        [{"queries_used": 4, MSUN: 2, CURVE: 2}], tmp_path, completed=False
    )
    assert record["complete_curve"] is False
    assert record["query_counts"] == [4]


def test_actual_hydra_config_is_selected_resolved_and_credentials_redacted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml

    output, results = tmp_path / "output", tmp_path / "results"
    output.mkdir()
    actual = results / "actual/.hydra"
    actual.mkdir(parents=True)
    (actual / "config.yaml").write_text(
        yaml.safe_dump(
            {
                "experiment": {"output_dir": str(output), "seed": 17},
                "agent": {"seed": "${experiment.seed}"},
                "private_field": "synthetic-credential-for-redaction-test",
            }
        )
    )
    unrelated = results / "other/.hydra"
    unrelated.mkdir(parents=True)
    (unrelated / "config.yaml").write_text(
        yaml.safe_dump({"experiment": {"output_dir": str(tmp_path / "other")}})
    )
    monkeypatch.setenv(
        "MATERIALS_PROJECT_API_KEY", "synthetic-credential-for-redaction-test"
    )
    assert preserve_configuration(output, results) is True
    saved = (output / "resolved_config.yaml").read_text()
    assert yaml.safe_load(saved)["agent"]["seed"] == 17
    assert "synthetic-credential-for-redaction-test" not in saved
    assert "[REDACTED]" in saved


def test_missing_actual_hydra_config_is_not_reconstructed(tmp_path: Path) -> None:
    assert preserve_configuration(tmp_path, tmp_path / "missing") is False


def test_a_self_consistent_run_with_the_wrong_frozen_protocol_is_not_scored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml

    root = tmp_path / "runs"
    fixture_run(root)
    m1 = tmp_path / "M1"
    (m1 / "protocol").mkdir(parents=True)
    (m1 / "protocol/protocol_v1.yaml").write_text(
        yaml.safe_dump(
            {
                "oracle": {"name": "ORBOracle"},
                "environment": {"query_budget": 20},
                "methods": {"required": ["m1_full"]},
                "repeats": {"seeds": [17]},
            }
        )
    )
    write(m1 / "protocol/dev_systems.json", [["Li", "O"]])
    output = tmp_path / "report"
    monkeypatch.setattr(evaluate, "M1_DIR", m1)
    monkeypatch.setattr(
        "sys.argv",
        ["evaluate.py", "--results-root", str(root), "--output", str(output)],
    )
    with pytest.raises(SystemExit, match="No complete real-material"):
        evaluate.main()
    audit = json.loads((output / "validation.json").read_text())
    assert audit["validated_runs"] == 0
    assert audit["final_comparison_complete"] is False
    assert audit["issues"][0]["kind"] == "protocol_mismatch"
    assert not (output / "per_run.csv").exists()


def test_incomparable_references_cannot_leave_a_successful_final_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml

    root = tmp_path / "runs"
    paths = [fixture_run(root), fixture_run(root, "random_generator_baseline")]
    protocol = {
        "oracle": {"name": "ORBOracle"},
        "environment": {"query_budget": 4},
        "methods": {"required": ["m1_full", "random_generator_baseline"]},
        "repeats": {"seeds": [17]},
    }
    for path in paths:
        meta_path = path / "run_metadata.json"
        metadata = json.loads(meta_path.read_text())
        metadata["protocol_settings"] = protocol
        write(meta_path, metadata)
    trajectory_path = paths[1] / "trajectories/episode_000.json"
    payload = json.loads(trajectory_path.read_text())
    payload["phase_diagram_gt"][0]["energy"] = -1
    write(trajectory_path, payload)
    m1 = tmp_path / "M1"
    (m1 / "protocol").mkdir(parents=True)
    (m1 / "protocol/protocol_v1.yaml").write_text(yaml.safe_dump(protocol))
    write(m1 / "protocol/dev_systems.json", [["Li", "O"]])
    output = tmp_path / "report"
    monkeypatch.setattr(evaluate, "M1_DIR", m1)
    monkeypatch.setattr(
        "sys.argv",
        ["evaluate.py", "--results-root", str(root), "--output", str(output)],
    )
    with pytest.raises(SystemExit, match="reference revision"):
        evaluate.main()
    audit = json.loads((output / "validation.json").read_text())
    assert audit["missing_units"] == []
    assert audit["final_comparison_complete"] is False
    assert any(i["kind"] == "incomparable_runs" for i in audit["issues"])
    assert not (output / "per_run.csv").exists()
