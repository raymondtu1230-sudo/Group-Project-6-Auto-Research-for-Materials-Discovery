# M4 integration validation record

20 October update: M1 adopted M4 in `9acd3c9` and M3 in `2fcc214`. Joint synthetic checks and optional rejected/error capture are documented in [integration/EVENT_CAPTURE.md](integration/EVENT_CAPTURE.md). The default Planner remains diversity. Formal full/OFF experiments are pending.

## Historical 19 October validation

Updated 19 October 2026. The main-branch handoff adds only `M4/`; existing M1 files remain unchanged. The tests below used a temporary integration configuration, retained with its integration tests in `integration/` for later adoption.

The integration review used team revision `ae10752`, which contains the previously missing M1/MADE implementation, configuration, and tests. PR #1 subsequently delivered the M4 folder to main.

## Completed validation

- `M4MemoryManager` implements M1's four memory methods, allowlists queried observations, deduplicates events, and supports JSON checkpoints.
- The temporary configuration loaded M4 through `memory_manager` and used M1's existing `enable_memory` switch.
- Tests exercised the real M1 agent's ON/OFF behavior, Planner arguments, checkpoints, invalid observations, output bounds, and Hydra construction.
- The combined M1/M4 suite passed 34 tests and Ruff checks; see test_results.txt. The folder-only handoff separately passed 12 standalone tests.
- The official synthetic smoke workflow completed one analytic-oracle episode with 2/2 queries. Both observations, including the final evaluation, were exported. Samples in evidence/synthetic-smoke are not real discoveries.
- The first smoke attempt completed its queries but failed at Chrome chart export because of execution permissions. The unchanged runner succeeded on retry after chart rendering was permitted.

No agent implementation, official runner, oracle, environment, scoring, or budget logic was modified. The temporary M1 configuration and new integration test are deferred rather than activated on main.

## Limits and remaining work

1. The default `GridSearchPlanner.propose` does not consume `previous` or `m1_memory`. Validation establishes the interface and workflow, not a change in default agent choices. M3 must consume the records and verify decision effects; M4 does not replace M3's algorithm.
2. M1 does not call the plugin when memory is OFF, and updates the last observation only on the next proposal when ON. Plugin logs therefore omit the final query and cannot provide complete OFF logs. Export the official trajectory with export_evidence.py for both groups. The exporter extracts queried observations rather than using envelope ground-truth fields for decisions.
3. Create a fresh manager per episode. Protocol v1 runs one episode per process; automatic multi-episode identity assignment is not integrated.
4. The adapter bounds returned records by serialized JSON character count using `max_chars`. This is not a model token limit; M1/M3 own the final prompt and token accounting.
5. One real Materials Project/ORB workflow has completed; see REAL_TEST_STATUS.md. There is no evidence of a Memory performance gain. Run ablations only after the Planner consumes memory.

## Reproduction

Install the locked environment from the repository root:

```bash
cd M1/MADE
uv sync --frozen
```

The commands below reproduce the earlier temporary integration after M1/M3 adopt the saved `memory_manager` configuration block and place the saved test in `M1/MADE/tests/test_m4_memory.py`. They are not claims that the current main configuration automatically enables M4. See integration/README.md; do not overwrite newer M1 configuration wholesale.

```bash
PYTHONPATH=../../M4/src uv run --no-sync pytest -q -o addopts='' tests/test_m1_integrated.py tests/test_m4_memory.py ../../M4/tests
uv run --no-sync ruff check ../../M4/src ../../M4/tests ../../M4/export_evidence.py tests/test_m4_memory.py
PYTHONPATH=../../M4/src uv run --no-sync python ../run_smoke_test.py
```

If default cache directories are unavailable, point `MPLCONFIGDIR` and `DSPY_CACHEDIR` to writable local directories. Chart export requires permission to launch Chrome. Keep the shown PYTHONPATH or install M4 into the same Python environment.

Export complete evidence for each episode from the repository root. The output file must not already exist:

```bash
python M4/export_evidence.py PATH_TO_EPISODE_JSON PATH_TO_NEW_EVIDENCE_JSONL --run-id UNIQUE_RUN --episode-id 0 --elements Mg Sn Sr
```

## Handoff scope

M4/ contains the module, documentation, tests, synthetic examples, and deferred integration references. No credentials or evaluation-only raw data are included. The derived queried-candidate evidence is available in evidence/real-workflow. M5 format confirmation and M6's final text/slides and experiment handoffs remain on the original schedule.

## Schema update

The adapter/exporter now share chemical-system, candidate-composition and observed-outcome fields. Export requires an explicit full chemical system. Existing run metrics and original trajectories remain unchanged. Updated evidence is regenerated from saved trajectories. This update does not enable M4 in M1 or capture runtime/rejection events automatically. See EVIDENCE_SCHEMA.md and VALIDATION.md.
