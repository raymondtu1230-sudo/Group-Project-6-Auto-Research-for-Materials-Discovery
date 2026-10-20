"""Probe native official cached-pool restore without models or oracle calls.

This is an interface check using the actual retained query-1 checkpoint.
Generation is replaced only in this test by a sentinel: a cache miss rejects
restoration instead of silently starting another five-hour candidate pool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def inspect(published: Path, output: Path) -> dict:
    from hydra.utils import instantiate
    from omegaconf import OmegaConf

    from M2.chemeleon_preflight import fingerprint

    receipt_path = published / "M2/execution_ledger/Co-Dy-W-43/receipt_3938658932401.json"
    receipt = json.loads(receipt_path.read_text())
    assert receipt["status"] == "timeout" and receipt["exit_code"] == 124
    archive = published / receipt["archive"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == receipt["sha256"]
    with ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        names = zipped.namelist()
        cp_name = next(n for n in names if n.endswith("/checkpoint.json"))
        checkpoint = json.loads(zipped.read(cp_name))
        inputs = json.loads(zipped.read("M2/runtime/science-inputs.json"))
    assert inputs == fingerprint(), "Scientific source/data/config changed"
    assert checkpoint["query_count"] == 1
    serialized = checkpoint["agent_state"]["generator"]["cached_candidates"]
    assert sum(map(len, serialized.values())) == 1024
    cfg = OmegaConf.create(checkpoint["config"])
    agent = instantiate(cfg.agent)
    agent.load_state(checkpoint["agent_state"])
    attempted_generation = []

    class CacheMissError(RuntimeError):
        pass

    def sentinel(*_args, **_kwargs):
        attempted_generation.append(True)
        raise CacheMissError("Native restored cache would regenerate the candidate pool")

    # Test-only observer. Never installed in a formal scientific execution.
    agent.generator.base_generator.generate = sentinel
    native_error = None
    try:
        agent(checkpoint["env_state"])
    except CacheMissError:
        native_error = "native_cached_generator_miss_after_json_null_key_roundtrip"
    except Exception as error:
        native_error = type(error).__name__
    result = {
        "scope": "real_saved_checkpoint_interface_probe_no_scientific_experiment",
        "archive": receipt["archive"],
        "archive_sha256": receipt["sha256"],
        "checkpoint_member": cp_name,
        "candidate_payloads_present": 1024,
        "saved_queries": checkpoint["query_count"],
        "native_cache_keys": list(agent.generator._cached_candidates),
        "native_global_none_key_present": None in agent.generator._cached_candidates,
        "attempted_new_generation_in_probe": bool(attempted_generation),
        "native_error": native_error,
        "random_selector_state_saved": bool(checkpoint["agent_state"]["scorer"]),
        "recovery_admitted": False,
        "reason": "Native JSON cache-key restore misses the global cache; scorer RNG state is also absent. Exact continuation is not established without changing the restore path.",
        "action": "authorized_fallback_new_attempt_from_scratch_only_Co-Dy-W-43",
        "generation_sentinel_test_only": True,
        "real_models_loaded": False,
        "real_oracle_queries": 0,
        "scientific_files_modified": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    # Require the expected real failure so a changed source cannot silently
    # turn this diagnostic into an unvalidated recovery admission.
    assert attempted_generation and native_error.startswith("native_cached_generator_miss")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.published, args.output), indent=2))
