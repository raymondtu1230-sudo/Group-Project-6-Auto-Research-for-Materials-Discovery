# M4 adoption and acceptance

Status: preparation only. Main currently leaves `memory_manager: null`; the
planner must consume memory before any Memory-effect experiment is accepted.
Keep current M2/M3/M5 settings when integrating. Do not replace the complete
agent YAML with the older example in this directory.

## 1. Install the package (M1)

From the repository root:

```bash
cd M1/MADE
uv sync --locked
uv pip install --python .venv/bin/python --no-deps -e ../../M4
```

The editable install is local environment setup, not a change to the official
runner. Confirm the package remains importable after any later environment sync;
repeat the install if the environment manager removes it.

## 2. Merge only the memory configuration block (M1)

In `M1/MADE/configs/agent/m1_integrated.yaml`, replace `memory_manager: null`
with the following block. Preserve every other owner's configuration.

```yaml
memory_manager:
  _target_: m4_memory.m1_adapter.M4MemoryManager
  log_path: ${hydra:runtime.output_dir}/m4_evidence.jsonl
  run_id: ${oc.env:M4_RUN_ID,m4-local}
  episode_id: ${oc.env:M4_EPISODE_ID,0}
  limit: 8
  max_chars: 4000
```

Retain the existing independent `enable_memory` switch. Use a fresh manager and
unique log path per episode. Set a unique `M4_RUN_ID` for each experiment attempt;
do not treat the fallback identity as production provenance.

## 3. Consume the records (M3)

Read `context.get("m1_memory", [])` in the actual planner decision path. Records
are `list[dict]`, JSON-serializable and bounded. Include the returned observations
in the decision input; attaching unused records to context is insufficient.
Record the retrieved event IDs and the actual input supplied to the decision
policy in a separate decision trace. Do not feed that trace recursively back
into M4 retrieval. Never pass evaluation-only metrics or reference snapshots to
the planner. Do not add oracle calls.

An empty list is normal at the first decision and when memory is disabled.
The current adapter retrieves recent/contrasting observations; it does not accept
a target composition. Do not claim target-aware retrieval in the integrated
method without a separately tested interface change.

## 4. Run the contract checks (M1/M4)

Copy the component test into M1's test slot; do not overwrite the original tests.
From `M1/MADE` after configuration adoption:

```bash
cp ../../M4/integration/M1/MADE/tests/test_m4_memory.py tests/test_m4_memory.py
uv run --no-sync pytest -q tests/test_m1_integrated.py tests/test_m4_memory.py ../../M4/tests -o addopts=''
uv run --no-sync ruff check ../../M4/src/m4_memory tests/test_m4_memory.py
uv run --no-sync python ../run_smoke_test.py
```

These are instructions for the future adopted configuration, not a claim they
have already passed on that configuration. The original smoke checks framework
behavior; additionally demonstrate M3 memory consumption with fake public
observations: ON receives bounded records after feedback, OFF receives no M4
records, invalid plugin output is rejected, checkpoint restore preserves memory,
and new episodes do not leak prior records. M3 must add an assertion at its own
decision-input boundary; the existing M4 tests cannot prove future planner use.

## 5. Complete evidence and handoff

M1 invokes memory updates before the next proposal, so the online log can omit
the last evaluation. Export the official trajectory after each run, including
Memory OFF; see `../EXPERIMENT_RUNBOOK.md`. Do not change framework callback
ordering just to fill the log. Exported evidence is an analysis artifact and
must not be preloaded into either member of the comparison.

Before the frozen release, record the integrated Git revision, passing checks,
M3 consumption evidence, M5 schema confirmation and the agreed protocol. Only
then run the paired pilot and formal comparisons. Main M1 files remain unchanged
by publishing these instructions.
