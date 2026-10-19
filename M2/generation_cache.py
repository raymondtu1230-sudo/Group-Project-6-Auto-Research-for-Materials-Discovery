"""Experimental, lossless batch replay outside the unchanged scientific source.

This is execution recovery, not a generator policy. It caches only public model
inputs, generated ASE atoms and RNG states. Never pass oracle/evaluator state.
Admission to protocol experiments requires a real interrupted-vs-continuous check.
"""

from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import os
import platform
import random
from pathlib import Path

import numpy as np
import torch
from ase.io.jsonio import decode, encode


class GenerationPausedError(RuntimeError):
    """A deliberate stop before a new batch, after previous batches were saved."""


def rng_state() -> dict:
    numpy = np.random.get_state()
    return {
        "python": json.loads(json.dumps(random.getstate())),
        "numpy": [numpy[0], numpy[1].tolist(), *numpy[2:]],
        "torch_cpu": torch.get_rng_state().tolist(),
    }


def restore_rng(state: dict) -> None:
    def tuples(value):
        return tuple(tuples(x) for x in value) if isinstance(value, list) else value

    random.setstate(tuples(state["python"]))
    value = state["numpy"]
    np.random.set_state((value[0], np.array(value[1], dtype=np.uint32), *value[2:]))
    torch.set_rng_state(torch.tensor(state["torch_cpu"], dtype=torch.uint8))


def digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


def model_digest(model) -> str:
    value = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        value.update(name.encode())
        array = tensor.detach().cpu().contiguous().numpy()
        value.update(str(array.dtype).encode())
        value.update(str(array.shape).encode())
        value.update(array.tobytes())
    return value.hexdigest()


class BatchCache:
    def __init__(
        self, directory: Path, identity: dict, max_new_batches: int | None = None
    ):
        self.directory = directory
        self.identity = identity
        self.max_new_batches = max_new_batches
        self.cursor = 0
        self.sampled = 0
        self.replayed = 0
        self.directory.mkdir(parents=True, exist_ok=True)

    @contextlib.contextmanager
    def patch(self, model_class):
        original = model_class.sample
        signature = inspect.signature(original)
        source_hash = hashlib.sha256(inspect.getsource(original).encode()).hexdigest()
        cache = self

        def sample(model, *args, **kwargs):
            if str(model.device) != "cpu":
                raise ValueError("Batch recovery is verified for CPU only")
            arguments = signature.bind(model, *args, **kwargs)
            arguments.apply_defaults()
            request = {k: v for k, v in arguments.arguments.items() if k != "self"}
            if request.get("return_trajectory") or request.get("task") != "csp":
                raise ValueError("Recovery supports the official CSP atoms output only")
            identity = {
                "execution": cache.identity,
                "request": request,
                "torch": torch.__version__,
                "numpy": np.__version__,
                "threads": torch.get_num_threads(),
                "source": source_hash,
                "module_source": hashlib.sha256(
                    Path(inspect.getfile(model_class)).read_bytes()
                ).hexdigest(),
                "cpu_capability": torch.backends.cpu.get_cpu_capability(),
                "architecture": platform.machine(),
                "weights": model_digest(model),
            }
            key = digest(identity)
            path = cache.directory / f"batch_{cache.cursor:04d}.json"
            before = rng_state()
            if path.exists():
                envelope = json.loads(path.read_text())
                payload = envelope["payload"]
                if digest(payload) != envelope["sha256"]:
                    raise ValueError("Batch checkpoint checksum mismatch")
                if payload["identity_sha256"] != key:
                    raise ValueError(
                        "Batch model, input or execution identity mismatch"
                    )
                if payload["rng_before"] != before:
                    raise ValueError(
                        "RNG state differs before replay. Stop rather than change samples"
                    )
                result = decode(payload["ase_atoms_json"])
                restore_rng(payload["rng_after"])
                cache.replayed += 1
                print(
                    f"M2 replayed verified generation batch {cache.cursor + 1}",
                    flush=True,
                )
            else:
                if (
                    cache.max_new_batches is not None
                    and cache.sampled >= cache.max_new_batches
                ):
                    raise GenerationPausedError(
                        "Saved batches retained. Pause before the next sampling call"
                    )
                result = original(model, *args, **kwargs)
                after = rng_state()
                if model_digest(model) != identity["weights"]:
                    raise ValueError(
                        "Sampling mutated model state. Recovery is not safe"
                    )
                encoded = encode(result)
                # Exercise the actual lossless serializer before accepting a cache.
                if encode(decode(encoded)) != encoded:
                    raise ValueError("ASE serialization is not lossless")
                payload = {
                    "version": 1,
                    "identity_sha256": key,
                    "rng_before": before,
                    "rng_after": after,
                    "ase_atoms_json": encoded,
                }
                temporary = path.with_suffix(".tmp")
                with temporary.open("w") as stream:
                    json.dump(
                        {"payload": payload, "sha256": digest(payload)},
                        stream,
                        allow_nan=False,
                    )
                    stream.flush()
                    os.fsync(stream.fileno())
                temporary.replace(path)
                cache.sampled += 1
                print(
                    f"M2 atomically saved generation batch {cache.cursor + 1}",
                    flush=True,
                )
            cache.cursor += 1
            return result

        model_class.sample = sample
        try:
            yield self
        finally:
            model_class.sample = original
