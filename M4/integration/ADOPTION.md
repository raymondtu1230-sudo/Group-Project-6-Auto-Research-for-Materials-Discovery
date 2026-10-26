# M4 installation and integrated contract

Updated 26 October 2026. M1 has adopted the memory manager and independent capture wrapper. The frozen full method selects M3. No new integration or wholesale configuration replacement is requested.

## Install

From `M1/MADE` in the team checkout:

```bash
uv sync --locked
uv pip install --python .venv/bin/python --no-deps -e ../../M4
```

The editable package is local environment setup. After environment sync, verify it remains installed. Credentials stay in ignored local configuration.

## Authoritative configuration

Use the agreed frozen `M1/MADE/configs/agent/m1_integrated.yaml` and M1 method overrides. It configures the M4 manager and capture subclass with independent `enable_memory`. Preserve M2/M3/M5 components and capture when running memory_off. For original scientific provenance, see [the runbook](../EXPERIMENT_RUNBOOK.md).

The initial memory-only YAML is preserved in [archive/](archive/README.md). It disables components that belong to the final full agent. Do not copy it over the official profile. Current M4 tests already exist in `M1/MADE/tests/test_m4_memory.py`; the retained M4 test copy is a reference, not an installation step that overwrites another member's work.

## Contract and validation

The adapter returns `list[dict]` of bounded public post-query records and supports `get_state`/`load_state`. The M1 agent keeps its `(Composition, Structure)` return contract. The argument-free hook provides recent contrasting outcomes, not composition-targeted retrieval. Components never call the oracle directly or inspect hidden labels/evaluation-only state.

Use [the complete current test command](../VALIDATION.md), which passed 72 tests at the reviewed source. These include ON/OFF behavior, invalid feedback, restore, capture isolation and real M3 decision boundaries using synthetic observations. Synthetic tests are distinct from the 18-pair formal real-material comparison.

M1 updates online memory before the next proposal. Export complete trajectories in both arms when needed. The capture sidecar remains excluded from retrieval, planning inputs and rewards. See [EVENT_CAPTURE.md](EVENT_CAPTURE.md) for exact coverage and fallback semantics.
