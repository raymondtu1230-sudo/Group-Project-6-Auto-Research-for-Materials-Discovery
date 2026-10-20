"""Load official model weights and compose production config without sampling."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
from pathlib import Path

import torch
from chemeleon_dng import sample
from chemeleon_dng.download_util import get_checkpoint_path
from hydra import compose, initialize_config_dir
from orb_models.forcefield import pretrained

from made.agents.generators.chemeleon import ChemeleonGenerator


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with initialize_config_dir(
        config_dir=str(root / "M1/MADE/configs"), version_base=None
    ):
        config = compose(
            config_name="config",
            overrides=[
                "agent=chemeleon_generative_baseline",
                "experiment.seed=17",
                "agent.generator.base_generator.device=cpu",
                "oracle.device=cpu",
            ],
        )
    assert config.agent.generator.num_initial_candidates == 1024
    assert config.agent.generator.base_generator.batch_size == 256
    assert (
        config.agent.generator.base_generator._target_
        == "made.agents.generators.ChemeleonGenerator"
    )
    generator = ChemeleonGenerator(task="csp", batch_size=256, device="cpu")
    generator.setup()
    checkpoint = Path(get_checkpoint_path("csp", sample.DEFAULT_MODEL_PATH))
    # Download/load the fixed oracle; no structure evaluation or query occurs.
    oracle = pretrained.orb_v3_conservative_inf_omat(device="cpu", compile=False)
    assert oracle is not None
    record = {
        "scope": "real_weight_load_no_sampling_no_oracle_query",
        "chemeleon_loaded": generator.dm is not None,
        "chemeleon_checkpoint_sha256": hashlib.sha256(
            checkpoint.read_bytes()
        ).hexdigest(),
        "chemeleon_sample_source_sha256": hashlib.sha256(
            Path(sample.__file__).read_bytes()
        ).hexdigest(),
        "orb_loaded": True,
        "device": "cpu",
        "num_initial_candidates": 1024,
        "batch_size": 256,
        "cpu_count": os.cpu_count(),
        "torch_threads": torch.get_num_threads(),
        "disk_free_bytes": shutil.disk_usage(".").free,
        "python": platform.python_version(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in [
                "chemeleon-dng",
                "torch",
                "orb-models",
                "mp-api",
                "numpy",
                "pymatgen",
            ]
        },
    }
    if record["disk_free_bytes"] < 8 * 1024**3:
        raise RuntimeError("Less than 8 GiB free disk after environment/model setup")
    target = root / "M2/runtime/environment.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
