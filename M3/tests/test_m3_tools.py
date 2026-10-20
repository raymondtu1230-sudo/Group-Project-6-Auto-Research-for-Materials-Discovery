"""Tests for M3's ablation runner, summarizer and installer (synthetic files only).

cd M1/MADE
uv run pytest -q ../../M3/tests -o addopts=''
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

M3_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(M3_DIR))

import install  # noqa: E402
import run_ablations  # noqa: E402
import summarize_ablations as summ  # noqa: E402


def make_run(
    root: Path,
    method: str,
    system: str,
    seed: int,
    msun: float,
    *,
    attempt: int = 1,
    status: str = "completed",
    replans: tuple[str, ...] = (),
) -> Path:
    path = root / method / "dev" / system / f"seed_{seed}" / f"attempt_{attempt:02d}"
    (path / "summary").mkdir(parents=True)
    (path / "run_metadata.json").write_text(
        json.dumps(
            {
                "status": status,
                "wall_time_seconds": 10.0,
                "cost": {"oracle": {"queries": 20}},
            }
        )
    )
    summary = {key: {"mean": msun} for key in summ.METRICS.values()}
    (path / "summary" / "summary.json").write_text(json.dumps({"summary": summary}))
    log = "".join(f"M3 re-plan: query=5 reason={r} level=1\n" for r in replans)
    # run_ablations.py's console capture; MADE leaves run_benchmark.log empty.
    run_ablations.console_log(path).write_text(log + "M3 review: step=1\n")
    (path / "run_benchmark.log").write_text("")
    return path


def test_summarizer_pairs_runs_and_counts_replans(tmp_path: Path) -> None:
    results = tmp_path / "results"
    for seed, (base, full, p_off, s_off) in {
        17: (5, 8, 6, 7),
        29: (6, 6, 7, 5),
    }.items():
        make_run(results, "m1_baseline", "Mg-Sn-Sr", seed, base)
        make_run(results, "m3_full", "Mg-Sn-Sr", seed, full, replans=("no_progress",))
        make_run(results, "m3_planning_off", "Mg-Sn-Sr", seed, p_off)
        make_run(results, "m3_self_correction_off", "Mg-Sn-Sr", seed, s_off)
    # A failed later attempt must not replace the completed one.
    make_run(results, "m3_full", "Mg-Sn-Sr", 17, 0, attempt=2, status="failed")

    rows = summ.collect(results, tmp_path / "missing.csv")
    full = [r for r in rows if r["method"] == "m3_full"]
    assert sorted(r["msun"] for r in full) == [6, 8]
    assert all(r["replans"] == 1 and r["replans_no_progress"] == 1 for r in full)

    result = summ.paired(rows, "m3_full", "m1_baseline")
    assert result == {
        "pairs": 2,
        "mean_diff": 1.5,
        "std_diff": pytest.approx(2.1213, abs=1e-3),
        "wins": 1,
        "ties": 1,
        "losses": 0,
    }

    out, report = tmp_path / "out", tmp_path / "report" / "M3_RESULTS.md"
    summ.write_outputs(rows, out, report)
    text = report.read_text(encoding="utf-8")
    assert "no completed M3 ablation runs" not in text
    assert "contribution of M3 planning" in text
    assert "re-planned 2 times" in text
    with (out / "m3_ablation_summary.csv").open() as stream:
        methods = [r["method"] for r in csv.DictReader(stream)]
    assert methods == list(summ.METHODS)


def test_summarizer_lists_recorded_baseline_but_never_pairs_it(tmp_path: Path) -> None:
    # M1's 19 Oct CSV predates M4 memory in m1_integrated.yaml: context only.
    baseline = tmp_path / "baseline.csv"
    baseline.write_text(
        "system,seed,queries,msun_at_20,msun_fraction,audc,wall_time_seconds,"
        "known_cost_usd,result_dir\nMg-Sn-Sr,17,20,7.0,0.35,49.5,300,0.0,x\n"
    )
    make_run(tmp_path / "results", "m3_full", "Mg-Sn-Sr", 17, 9)
    rows = summ.collect(tmp_path / "results", baseline)
    assert [r["method"] for r in rows].count(summ.RECORDED) == 1
    assert summ.paired(rows, "m3_full", "m1_baseline") is None
    text = summ.render_markdown(rows, summ.summarize(rows))
    assert "context only" in text

    make_run(tmp_path / "results", "m1_baseline", "Mg-Sn-Sr", 17, 6)
    rows = summ.collect(tmp_path / "results", baseline)
    assert summ.paired(rows, "m3_full", "m1_baseline")["mean_diff"] == 3.0


def test_runner_gives_each_run_its_own_m4_run_id() -> None:
    env = run_ablations.run_env("m3_full", "Mg-Sn-Sr", 17, 2)
    assert env["M4_RUN_ID"] == "m3_full-Mg-Sn-Sr-seed17-attempt02"
    assert env["M4_EPISODE_ID"] == "0"
    other = run_ablations.run_env("m1_baseline", "Mg-Sn-Sr", 17, 2)
    assert other["M4_RUN_ID"] != env["M4_RUN_ID"]


def test_runner_requires_m4_only_when_config_uses_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "m1_integrated.yaml"
    monkeypatch.setattr(run_ablations, "AGENT_CONFIG", config)
    monkeypatch.setattr(run_ablations.importlib.util, "find_spec", lambda name: None)
    config.write_text("memory_manager: null\n")
    assert run_ablations.m4_missing() is False
    config.write_text("memory_manager:\n  _target_: m4_memory.m1_adapter.X\n")
    assert run_ablations.m4_missing() is True


def test_summarizer_reports_pending_without_runs(tmp_path: Path) -> None:
    rows = summ.collect(tmp_path / "none", tmp_path / "none.csv")
    assert rows == []
    assert "no completed M3 ablation runs yet" in summ.render_markdown(rows, [])


def test_runner_skips_completed_and_numbers_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(run_ablations, "RESULTS", tmp_path)
    make_run(tmp_path, "m3_full", "Mg-Sn-Sr", 17, 5, status="failed")
    assert run_ablations.next_attempt("m3_full", "Mg-Sn-Sr", 17) == 2
    assert not any(
        run_ablations.is_completed(p)
        for p in run_ablations.attempts("m3_full", "Mg-Sn-Sr", 17)
    )
    make_run(tmp_path, "m3_full", "Mg-Sn-Sr", 17, 5, attempt=2)
    assert any(
        run_ablations.is_completed(p)
        for p in run_ablations.attempts("m3_full", "Mg-Sn-Sr", 17)
    )
    assert run_ablations.next_attempt("m3_full", "Au-K-Tb", 17) == 1


def test_runner_rejects_placeholder_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(run_ablations.KEY_NAME, raising=False)
    monkeypatch.setattr(run_ablations, "MADE_DIR", tmp_path)
    assert run_ablations.has_api_key() is False
    (tmp_path / ".env").write_text(
        f"{run_ablations.KEY_NAME}=replace_with_your_materials_project_api_key\n"
    )
    assert run_ablations.has_api_key() is False
    (tmp_path / ".env").write_text(f"{run_ablations.KEY_NAME}=abc123\n")
    assert run_ablations.has_api_key() is True


def test_runner_defaults_cover_dev_split() -> None:
    assert run_ablations.dev_systems()[0] == "Mg-Sn-Sr"
    assert len(run_ablations.dev_systems()) == 6


def test_installed_m1_copies_match_integration() -> None:
    if not (install.REPO / install.NEW_FILES[0]).is_file():
        pytest.skip("M3 not installed in M1 (main branch); run M3/install.py --install")
    assert install.mismatches() == []


def test_m3_markers_are_in_the_integration_templates() -> None:
    for relative in install.EDITED_FILES:
        assert install.has_m3_edit(install.SOURCE / relative, relative), relative


def test_installer_accepts_m1_merge_that_keeps_m3_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # M1 integrated M3, then merged M4/M5 settings into m1_integrated.yaml.
    relative = "M1/MADE/configs/agent/m1_integrated.yaml"
    template = (install.SOURCE / relative).read_text(encoding="utf-8")
    merged = template.replace(
        "exploration_policy: null", "exploration_policy:\n  _target_: m5.Policy"
    )
    assert merged != template
    repo = tmp_path / "repo"
    (repo / relative).parent.mkdir(parents=True)
    (repo / relative).write_text(merged, encoding="utf-8")
    monkeypatch.setattr(install, "REPO", repo)

    assert install.status(relative) == "merged"
    assert relative not in install.conflicts()

    # Dropping M3's wiring is a real conflict.
    (repo / relative).write_text(
        merged.replace("  - self_correction_policy: m3_stuck_replan\n", ""),
        encoding="utf-8",
    )
    assert install.status(relative) == "changed by M1"
    assert relative in install.conflicts()


def test_installer_replaces_unchanged_m1_files_and_refuses_changed_ones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    edited = "M1/run_experiment.py"
    source, repo = tmp_path / "integration", tmp_path / "repo"
    for relative in install.FILES:
        (source / relative).parent.mkdir(parents=True, exist_ok=True)
        (source / relative).write_text(f"m3 version of {relative}\n")
    (repo / edited).parent.mkdir(parents=True)
    (repo / edited).write_text("m1 original\n")
    monkeypatch.setattr(install, "SOURCE", source)
    monkeypatch.setattr(install, "REPO", repo)
    monkeypatch.setattr(
        install, "EDITED_FILES", {edited: install._text_hash(repo / edited)}
    )
    monkeypatch.setattr(install, "FILES", (*install.NEW_FILES, edited))
    monkeypatch.setattr(sys, "argv", ["install.py", "--install"])

    install.main()
    assert install.mismatches() == []
    assert (repo / edited).read_text() == f"m3 version of {edited}\n"

    # M1 later edits its own file: the installer must not overwrite it.
    (repo / edited).write_text("m1 newer version\n")
    assert install.conflicts() == [edited]
    with pytest.raises(SystemExit, match="merge the M3 edit"):
        install.main()
    assert (repo / edited).read_text() == "m1 newer version\n"


def test_runner_refuses_non_dev_systems() -> None:
    run_ablations.check_dev_only(run_ablations.dev_systems())
    with pytest.raises(SystemExit, match="dev systems only"):
        run_ablations.check_dev_only(["Mg-Sn-Sr", "Ba-Sc-Si"])


def test_results_text_is_labelled_vs_m1_reference(tmp_path: Path) -> None:
    make_run(tmp_path, "m1_baseline", "Mg-Sn-Sr", 17, 5)
    make_run(tmp_path, "m3_full", "Mg-Sn-Sr", 17, 6)
    rows = summ.collect(tmp_path, tmp_path / "none.csv")
    text = summ.render_markdown(rows, summ.summarize(rows))
    assert "## Component vs M1 reference" in text
    assert "not the frozen agent's component ablation" in text
