# M4 setup and reproduction

Updated 26 October 2026. The formal experiments are complete. Prefer offline reproduction of the published results before considering new oracle runs.

## 1. Environment

From the repository root:

```bash
cd M1/MADE
uv sync --locked
uv pip install --python .venv/bin/python --no-deps -e ../../M4
```

Keep API credentials in ignored local configuration. M4 adds no API keys or network requirement to the independent core. Real MADE runs require the team's configured dependencies, scientific assets and API access.

## 2. Reproduce saved results offline

The [formal package](evidence/frozen-memory-ablation-20261026/) contains `memory_off_raw_results.zip`. Extract its repository-relative paths into a suitable checkout without overwriting an existing different attempt. ON reference originals are committed under `M1/MADE/results/protocol_v1/m1_full/dev/` at evidence patch `ae7fe81991c56dd2d77685220b74ddbef11039c7`.

From the repository root:

```bash
M1/MADE/.venv/bin/python M4/build_frozen_report.py \
  --results-root M1/MADE/results/protocol_v1 \
  --output /tmp/m4-analysis-reproduction
```

This helper uses saved artifacts, M2 validation and official MADE metric functions. It does not invoke the oracle. See [analysis documentation](evidence/frozen-memory-ablation-20261026/analysis/README.md) for curve definitions, seed aggregation, costs and directional OFF-vs-ON AF/EF. Required Random/Chemeleon comparisons remain with the shared M2 report.

## 3. Original scientific execution

The actual Memory OFF runs used frozen source `02e0026bf450f71f4f7862228d295f5b02b49e12`. Scientific code/configuration match the later reference evidence patch; preserve the actual metadata revision. Use full commit hashes to distinguish this from later documentation/test changes. Do not silently rerun at today's main and label it as the original freeze.

The official entry point, from `M1/MADE`, is:

```bash
uv run --no-sync python ../run_experiment.py \
  --method memory_off --split dev --system Mg-Sn-Sr --seed 17 --attempt N
```

Replace `N` with a new unused positive attempt number. This is an execution reference, not a request to duplicate completed experiments. The accepted sweep used six dev systems and seeds 17/29/43, B=20, CPU ORB and one episode per process. Only `enable_memory` differs from the full method. Planning, reflection, exploration, routing and independent capture remain enabled. Ablations never run on check/hidden.

Set unique `M4_RUN_ID` and `M4_EPISODE_ID` per attempt before launch. Preserve failed attempts and all original output paths. Official successful-run checkpoints may be removed by the runner: capture their histories externally during execution, or explicitly document any later official reconstruction. Do not label reconstruction as original checkpoint data. The published OFF package already retains histories, saved Hydra configuration, resolved configuration, M5 logs, M3 OFF traces and complete trajectory exports.

## 4. Full evidence

M1's online memory update occurs before the next proposal, so the final evaluation may be absent from its online log. OFF retrieval may produce no online memory log. Export public queried observations from each official trajectory when a complete evidence file is needed:

```bash
M1/MADE/.venv/bin/python M4/export_evidence.py \
  PATH_TO_EPISODE_JSON PATH_TO_NEW_EVIDENCE_JSONL \
  --run-id UNIQUE_RUN --episode-id 0 --elements Mg Sn Sr
```

Run this from the repository root. The output must be new. Keep the full chemical system and explicit run identity. Generator/filter sidecars occur only when captured events exist. Absence alone does not demonstrate that all possible failures were monitored. Evaluation-only reference envelopes remain offline and never enter agent memory.

## 5. Acceptance and handoff

Use [current validation](VALIDATION.md), the final paired table and checksums. Reuse accepted matching ON references rather than rerunning them. Retain neutral/negative cases. Distinguish observed allocation from proven memory-record causality: exact formal ON review IDs were not retained. Record campaign queries separately from total oracle work and retain missing cost values explicitly.

M2 owns shared baseline AF/EF and final aggregation. M6 owns final group assembly. Earlier wrapper/pilot instructions are preserved in [historical runbook notes](archive/docs/EXPERIMENT_RUNBOOK_before_cleanup.md) and [the dated pilot document](DEV_PILOT.md).
