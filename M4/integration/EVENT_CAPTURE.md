# Proposal rejection and error capture

## Delivery status

M1 integrated M4 on main (`9acd3c9`) and M3 (`2fcc214`). The ordinary memory
manager captures evaluated feedback. On 21 October, M1 adopted the optional
capture agent in the official `m1_integrated` profile, with the same capture
configuration in both memory arms. M5 confirmed schema v1 in
`M5/M4_LOG_CONFIRMATION.md`.

## Coverage and limits

`m4_memory.capture.CapturedM1IntegratedAgent` subclasses the existing M1 agent.
Its constructor wraps the configured filter and generator objects, preserving
aliases, delegate state and M1's proposal implementation. It adds no oracle
calls and does not edit MADE's runner, environment, oracle, evaluator or budget.

- Filter candidates absent from the returned batch produce `rejected` records.
  Duplicate structures are matched by occurrence count, not collapsed by formula.
  The exact public structure is retained for matching to later observations.
- Filter/generator exceptions produce `error` records with stage and exception
  class only; the original exception is re-raised. Exception messages are omitted
  because they can contain credentials or private paths.
- An empty generator batch is recorded before M1's original failure is raised.
- No observation hook sees oracle/relaxation exceptions or process termination.
  Planner, scorer and runner errors are also outside this implementation. Do not
  call this complete runtime-failure capture. Use preserved process logs for
  offline investigation; no missing event is fabricated.

Crucially, M1 falls back to the original candidates if the filter returns none.
`rejection_scope=filter_decision`, `fallback_to_unfiltered=true`, `evaluated=null`
means a filter rejection, not proof that the candidate was never evaluated.
Even without fallback, rejection alone is not proof of wasted oracle budget.
Match the recorded public structure to the official query trajectory to assess
actual evaluation. Do not classify ordinary instability as a runtime error.
The wrapper records batch exclusion, not detailed internal filter reasons.

## M1 adoption

M1 has merged the four fields in `m4_capture_overrides.yaml` into the official
agent profile while preserving the current M3 planner, M5 policy, M2 router,
generation/filter settings and all switches. Install M4 as in `ADOPTION.md`
before running that profile.

Use an independent sidecar per episode. Enable capture identically for full and
memory_off, independent of `enable_memory`. The sidecar must never feed memory
retrieval, planner decisions or policy rewards. `get_state()`/`load_state()` save
and restore its identity, event sequence and evidence alongside the normal agent
checkpoint. Resuming requires the same run/episode identity. A new episode needs
a fresh agent. Files support one writer; disk/serialization failures propagate
rather than silently claiming complete evidence. Capture adds storage/runtime
overhead, so compare both arms with the same capture configuration.

## Field interpretation

Records retain schema v1 identities plus `stage`, optional candidate index,
`proposal`, `composition`, formula and factual rejection/error classification.
`query_count` is completed campaign queries at proposal time. `step_id` is the
next proposed query slot, not an additional charged query; repeated failed
proposals can share that slot. Event IDs include a checkpointed sequence to
separate retries and candidates. No energy, stability or physical failure reason
is invented for unevaluated candidates.

Join M5's decision-log sidecar by run, episode and completed query count/next
proposal step. Prefer M5's JSONL sidecar for analysis while preserving the agent
checkpoint as the source. Do not copy the full checkpoint into retrieval: it may
contain unrelated component state. Existing experiments retain their original
capture limitations; the new events cannot reconstruct past unobserved failures.

## Reproduce the boundary tests

From `M1/MADE`, with the local M4 package installed:

```bash
uv run --no-sync pytest -q tests/test_m1_integrated.py tests/test_m3_planning.py tests/test_m4_memory.py ../../M4/tests ../../M4/integration/test_joint_capture.py -o addopts=''
uv run --no-sync ruff check ../../M4/src/m4_memory/capture.py ../../M4/integration/test_joint_capture.py
```

Tests use real M1/M3/M4 classes and synthetic structures/public observations.
They check actual M3 decision-trace memory IDs ON/OFF, checkpoint restore,
episode isolation, partial/all filter rejection, duplicate-structure counts,
unchanged selected output including fallback, unchanged exceptions, empty
batches and safe exception logging. They are not material-discovery results.

## Local verification outcome

On 21 October, after M1 adoption, 69 combined tests passed and focused Ruff
passed. The earlier unchanged M1 smoke and two M3/M4/capture synthetic episodes
(ON/OFF, two queries each) also completed after allowing local Chrome for plot
export. See M4/evidence/joint-integration/README.md. These are integration
checks, not formal effect results.
