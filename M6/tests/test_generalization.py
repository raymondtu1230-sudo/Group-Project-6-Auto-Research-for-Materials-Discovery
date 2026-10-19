"""Tests for M6/generalization.py. All numbers here are synthetic fixtures."""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

M6 = Path(__file__).resolve().parents[1]
REPO = M6.parent
SPEC = importlib.util.spec_from_file_location(
    "generalization", M6 / "generalization.py"
)
gen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen)

FIELDS = ["method", "split", "system", "seed", "attempt", "B", "mSUN_at_B", "AUDC",
          "repository_revision", "AF_vs_random", "EF_vs_random",
          "AF_vs_chemeleon", "EF_vs_chemeleon"]  # fmt: skip


def write_runs(path: Path, rows: list[dict]) -> Path:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {"B": 20, "attempt": 1, "repository_revision": "abc", **row}
            )
    return path


def grid(split, systems, seeds, method, msun, revision="abc"):
    return [
        {"method": method, "split": split, "system": s, "seed": seed,
         "mSUN_at_B": msun(i, seed), "AUDC": 10 * msun(i, seed),
         "repository_revision": revision, "AF_vs_random": "", "EF_vs_random": ""}
        for i, s in enumerate(systems) for seed in seeds
    ]  # fmt: skip


@pytest.fixture
def systems(tmp_path):
    dev = tmp_path / "dev.json"
    held = tmp_path / "held.json"
    dev.write_text(json.dumps([["A", "B", "C"], ["D", "E", "F"]]))
    held.write_text(json.dumps([["G", "H", "I"]]))
    return dev, held


def run(tmp_path, dev_rows, held_rows, systems, *extra):
    dev = write_runs(tmp_path / "dev.csv", dev_rows)
    args = ["--dev", str(dev), "--output", str(tmp_path / "out"),
            "--dev-systems", str(systems[0]), "--heldout-systems", str(systems[1]),
            "--methods", "m1_full", *extra]  # fmt: skip
    if held_rows is not None:
        args[2:2] = ["--heldout", str(write_runs(tmp_path / "held.csv", held_rows))]
    gen.main(args)
    with (tmp_path / "out" / "generalization_summary.csv").open() as stream:
        rows = {r["metric"]: r for r in csv.DictReader(stream)}
    return rows


def test_complete_gap_uses_seed_then_system_aggregation(tmp_path, systems):
    seeds = [17, 29, 43]
    dev = grid(
        "dev",
        ["A-B-C", "D-E-F"],
        seeds,
        "m1_full",
        lambda i, s: 4 + 2 * i + seeds.index(s),
    )
    held = grid("check", ["G-H-I"], seeds, "m1_full", lambda i, s: 3 + seeds.index(s))
    rows = run(tmp_path, dev, held, systems)
    msun = rows["mSUN_at_B"]
    # dev seed means: 5, 6, 7 -> 6 ± 1; held-out 3, 4, 5 -> 4 ± 1
    assert float(msun["dev_mean"]) == 6 and float(msun["dev_sd"]) == 1
    assert float(msun["heldout_mean"]) == 4
    assert float(msun["gap_heldout_minus_dev"]) == -2
    assert msun["gap_status"] == "complete"
    # AF columns are blank in the input: they stay blank, never zero.
    assert rows["AF_vs_random"]["dev_mean"] == ""
    assert rows["AF_vs_random"]["gap_heldout_minus_dev"] == ""


def test_partial_split_has_no_headline_or_gap(tmp_path, systems):
    dev = grid("dev", ["A-B-C"], [17], "m1_full", lambda i, s: 5)
    rows = run(tmp_path, dev, None, systems)
    msun = rows["mSUN_at_B"]
    assert msun["dev_mean"] == "" and msun["gap_heldout_minus_dev"] == ""
    assert float(msun["dev_available_mean_partial"]) == 5
    assert msun["dev_runs"] == "1" and msun["dev_expected"] == "6"
    with (tmp_path / "out" / "missing_units.csv").open() as stream:
        missing = list(csv.DictReader(stream))
    assert len(missing) == 5 + 3  # 5 dev units + 3 held-out units


def test_one_seed_fallback(tmp_path, systems):
    dev = grid("dev", ["A-B-C", "D-E-F"], [17, 29, 43], "m1_full", lambda i, s: 6)
    held = grid("check", ["G-H-I"], [17], "m1_full", lambda i, s: 8)
    rows = run(tmp_path, dev, held, systems, "--heldout-seeds", "17")
    assert float(rows["mSUN_at_B"]["heldout_mean"]) == 8
    assert rows["mSUN_at_B"]["heldout_sd"] == ""  # no SD from one seed
    assert float(rows["mSUN_at_B"]["gap_heldout_minus_dev"]) == 2


def test_mixed_agent_revisions_are_refused(tmp_path, systems):
    dev = grid(
        "dev", ["A-B-C", "D-E-F"], [17, 29, 43], "m1_full", lambda i, s: 6, "rev1"
    )
    held = grid("check", ["G-H-I"], [17, 29, 43], "m1_full", lambda i, s: 6, "rev2")
    with pytest.raises(SystemExit, match="more than one revision"):
        run(tmp_path, dev, held, systems)


def test_duplicate_unit_is_refused(tmp_path, systems):
    row = grid("dev", ["A-B-C"], [17], "m1_full", lambda i, s: 5)
    with pytest.raises(SystemExit, match="Duplicate unit"):
        run(tmp_path, row + row, None, systems)


def test_output_dir_must_be_new(tmp_path, systems):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "keep.txt").write_text("x")
    with pytest.raises(SystemExit, match="already contains files"):
        run(
            tmp_path,
            grid("dev", ["A-B-C"], [17], "m1_full", lambda i, s: 5),
            None,
            systems,
        )


def test_real_recovery_package(tmp_path):
    """The accepted M2 package: 2 dev runs, every other unit reported missing."""
    source = REPO / "M2/verification/20261019-chemeleon-recovery/per_run.csv"
    gen.main(["--dev", str(source), "--output", str(tmp_path / "out")])
    with (tmp_path / "out" / "generalization_summary.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    chem = next(
        r
        for r in rows
        if r["method"] == "chemeleon_generative_baseline" and r["metric"] == "mSUN_at_B"
    )
    assert chem["dev_runs"] == "1" and chem["dev_mean"] == ""
    assert float(chem["dev_available_mean_partial"]) == 16
    assert all(r["gap_heldout_minus_dev"] == "" for r in rows)
    with (tmp_path / "out" / "missing_units.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == 88
    assert (tmp_path / "out" / "generalization.svg").read_text().startswith("<svg")


def test_check_script_dry_run_never_reuses_attempts(tmp_path):
    unit = tmp_path / "random_generator_baseline/check/Ga-Ho-Lu"
    (unit / "seed_17/attempt_01").mkdir(parents=True)
    (unit / "seed_17/attempt_01/run_metadata.json").write_text(
        '{"status": "completed"}'
    )
    (unit / "seed_29/attempt_03").mkdir(parents=True)
    (unit / "seed_29/attempt_03/run_metadata.json").write_text('{"status": "failed"}')
    out = subprocess.run(
        [str(M6 / "run_check_baselines.sh"), "--methods", "random_generator_baseline", "--systems", "Ga-Ho-Lu"],
        env={**os.environ, "M6_RESULTS_ROOT": str(tmp_path)},
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    assert "SKIP  random_generator_baseline Ga-Ho-Lu seed=17" in out.stdout
    assert "seed=29 attempt=4" in out.stdout
    assert "seed=43 attempt=1" in out.stdout
    assert "DRY RUN" in out.stdout
    assert (
        unit / "seed_29/attempt_03/run_metadata.json"
    ).read_text() == '{"status": "failed"}'


def test_check_script_refuses_ablations():
    out = subprocess.run(
        [str(M6 / "run_check_baselines.sh"), "--methods", "memory_off"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 2 and "Refusing" in out.stderr
