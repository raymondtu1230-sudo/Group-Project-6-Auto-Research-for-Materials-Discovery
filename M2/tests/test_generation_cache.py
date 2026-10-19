"""Synthetic recovery mechanics are separate from actual-model admission."""

import json
import random

import numpy as np
import pytest
import torch
from ase import Atoms
from ase.io.jsonio import encode

from M2.generation_cache import BatchCache, GenerationPausedError, rng_state


class FakeDiffusion:
    device = "cpu"

    def state_dict(self):
        return {"weight": torch.tensor([1.0])}

    def sample(self, task, num_atoms, atom_types=None, return_trajectory=False):
        offset = random.random() + np.random.rand() + torch.rand(1).item()
        return [
            Atoms("Li2O", positions=np.full((3, 3), offset), cell=[5, 5, 5], pbc=True)
        ]


def seed():
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)


def test_exact_structures_and_rng_after_an_interruption(tmp_path):
    seed()
    model = FakeDiffusion()
    expected = [model.sample("csp", [3]) for _ in range(3)]
    expected_rng = rng_state()
    seed()
    first = BatchCache(tmp_path, {"unit": "synthetic"}, max_new_batches=1)
    with first.patch(FakeDiffusion), pytest.raises(GenerationPausedError):
        for _ in range(3):
            FakeDiffusion().sample("csp", [3])
    assert first.sampled == 1
    assert len(list(tmp_path.glob("batch_*.json"))) == 1
    seed()
    resumed = BatchCache(tmp_path, {"unit": "synthetic"})
    with resumed.patch(FakeDiffusion):
        actual = [FakeDiffusion().sample("csp", [3]) for _ in range(3)]
    assert encode(expected) == encode(actual)
    assert rng_state() == expected_rng
    assert resumed.replayed == 1 and resumed.sampled == 2


@pytest.mark.parametrize("damage", ["rng", "identity", "checksum"])
def test_resume_rejects_incompatible_or_corrupt_state(tmp_path, damage):
    seed()
    with BatchCache(tmp_path, {"unit": "synthetic"}).patch(FakeDiffusion):
        FakeDiffusion().sample("csp", [3])
    seed()
    identity = {"unit": "different"} if damage == "identity" else {"unit": "synthetic"}
    if damage == "rng":
        random.random()
    if damage == "checksum":
        path = tmp_path / "batch_0000.json"
        data = json.loads(path.read_text())
        data["payload"]["ase_atoms_json"] = "changed"
        path.write_text(json.dumps(data))
    with BatchCache(tmp_path, identity).patch(FakeDiffusion), pytest.raises(ValueError):
        FakeDiffusion().sample("csp", [3])
