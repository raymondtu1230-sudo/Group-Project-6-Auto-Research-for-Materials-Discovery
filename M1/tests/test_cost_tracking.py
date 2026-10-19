import json

from cost_tracking import build_cost_record


def test_cost_record_counts_trajectory_and_marks_zero_oracle_cost(tmp_path, monkeypatch):
    trajectory_dir = tmp_path / "trajectories"
    trajectory_dir.mkdir()
    (trajectory_dir / "episode_000.json").write_text(
        json.dumps({"steps": [{"query": 1}, {"query": 2}]})
    )

    record = build_cost_record(
        output_dir=tmp_path,
        method="random_generator_baseline",
        status="completed",
        query_budget=20,
        wall_time_seconds=12.5,
    )

    assert record["oracle"]["queries"] == 2
    assert record["oracle"]["cost_usd"] == 0.0
    assert record["materials_project"]["logical_dataset_requests"] == 1
    assert record["llm"]["cost_status"] == "not_reported"
    assert record["total_known_cost_usd"] == 0.0
    assert record["wall_time_seconds"] == 12.5


def test_cost_record_accepts_llm_usage_file(tmp_path, monkeypatch):
    usage = tmp_path / "usage.json"
    usage.write_text(
        json.dumps(
            {
                "provider": "test-provider",
                "model": "test-model",
                "calls": 3,
                "input_tokens": 100,
                "output_tokens": 40,
                "cost_usd": 0.012,
            }
        )
    )
    monkeypatch.setenv("M1_LLM_USAGE_FILE", str(usage))

    record = build_cost_record(
        output_dir=tmp_path,
        method="m1_full",
        status="completed",
        query_budget=20,
        wall_time_seconds=1.0,
    )

    assert record["llm"]["input_tokens"] == 100
    assert record["llm"]["output_tokens"] == 40
    assert record["llm"]["cost_usd"] == 0.012
    assert record["total_known_cost_usd"] == 0.012
    assert record["total_cost_status"] == "complete"
