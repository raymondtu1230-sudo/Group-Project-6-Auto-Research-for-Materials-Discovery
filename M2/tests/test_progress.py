"""Execute real child processes to verify observability before the first query.

These are process-diagnostic tests, not materials experiments or benchmark scores.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from M2.run_baselines import process_progress, run_unit


@pytest.mark.skipif(sys.platform != "linux", reason="Linux CPU counters")
def test_real_cpu_work_and_generation_marker_are_visible_before_first_query(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "child.log"
    code = (
        "import time\n"
        "print('Generating batch #2 with 256 samples.', flush=True)\n"
        "stop = time.monotonic() + 3\n"
        "while time.monotonic() < stop:\n"
        "    sum(i*i for i in range(10000))\n"
    )
    with log_path.open("w") as log:
        child = subprocess.Popen([sys.executable, "-c", code], stdout=log)
        try:
            first = process_progress(child.pid, log_path)
            if first["process_cpu_seconds"] is None:
                if os.environ.get("GITHUB_ACTIONS") == "true":
                    pytest.fail("GitHub Linux runner did not expose process CPU counters")
                pytest.skip("This execution host does not expose child /proc counters")
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                last = process_progress(child.pid, log_path)
                if last["generation_batch"] == 2 and (
                    last["process_cpu_seconds"] or 0
                ) > (first["process_cpu_seconds"] or 0):
                    break
                time.sleep(0.02)
            assert last["generation_batch"] == 2
            assert last["generation_batch_size"] == 256
            assert last["process_log_bytes"] > 0
            assert last["process_cpu_seconds"] > first["process_cpu_seconds"]
            assert "queries_used" not in last
        finally:
            child.terminate()
            child.wait(timeout=5)


def test_unavailable_counters_stay_unknown_and_log_content_is_not_disclosed(
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "child.log"
    log_path.write_text(
        "private synthetic credential: NEVER_PRINT_THIS\n"
        "Generating batch #3 with 32 samples.\n"
    )
    snapshot = process_progress(999999999, log_path)
    assert snapshot["process_cpu_seconds"] is None
    assert snapshot["generation_batch"] == 3
    assert "NEVER_PRINT_THIS" not in json.dumps(snapshot)
    assert process_progress(999999999, tmp_path / "absent")["process_log_bytes"] == 0


def test_an_orphaned_live_log_cannot_be_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from M2 import run_baselines

    monkeypatch.setattr(run_baselines, "MADE", tmp_path)
    parent = tmp_path / "results/protocol_v1/random_generator_baseline/dev/Mg-Sn-Sr/seed_17"
    parent.mkdir(parents=True)
    log_path = parent / "attempt_01.process.log"
    log_path.write_text("original failed attempt evidence")
    with pytest.raises(ValueError, match="preserve it"):
        run_unit("random_generator_baseline", "dev", "Mg-Sn-Sr", 17, 1)
    assert log_path.read_text() == "original failed attempt evidence"
