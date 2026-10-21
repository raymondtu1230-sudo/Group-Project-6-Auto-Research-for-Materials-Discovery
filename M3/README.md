# M3: Planning and Self-Correction

M3 decides how the agent breaks the discovery goal into steps, and detects
when the search is stuck and re-plans. It plugs into M1's existing
`M1IntegratedAgent` slots without changing MADE's runner, oracle, evaluator,
environment or budget logic.

Inspected upstream MADE revision: `bffda0c9a1fa1904b35c0ef67b455881c975df86`.

## Integration status

M1 integrated M3 into `main` on 20 Oct (`2fcc214`) and signed off the design.
M1 also merged M4's memory manager and M5's exploration policy into
`m1_integrated.yaml` alongside M3's lines. To check that M3 is in place:

```bash
cd M1/MADE
uv run python ../../M3/install.py
```

Each file shows one of three statuses:

- `ok`: the file matches `M3/integration/`.
- `merged`: an M1-owned file where M1 added other settings but kept every M3
  edit (see `M3_MARKERS` in `install.py`).
- Any other status means M3 is missing.

`--install` puts M3 into a checkout that lacks it. It never overwrites an
M1-owned file that M1 has changed.

## Folder contents

| Path | What it is |
| --- | --- |
| [DESIGN.md](DESIGN.md) | One-page design for M1 sign-off |
| [HANDOVER.md](HANDOVER.md) | Deliverables, recipients, status, notes for M1/M2/M4/M5 |
| [EXPERIMENT_RUNBOOK.md](EXPERIMENT_RUNBOOK.md) | Step-by-step ablation runs (26–27 Oct) |
| `integration/M1/...` | Everything M3 adds to or changes in M1, at M1's paths |
| [install.py](install.py) | Checks (default) or installs `integration/` into M1 |
| `ruff.toml` | MADE's lint rules for this folder |
| [run_ablations.py](run_ablations.py) | Runs all M3 ablations via `M1/run_experiment.py`; resumable |
| [summarize_ablations.py](summarize_ablations.py) | Builds result CSVs and `report/M3_RESULTS.md` |
| `examples/m3_demo.py` | Synthetic walk-through showing reviews and re-plans |
| `tests/test_m3_tools.py` | Tests for the runner, summarizer and installer |
| `report/` | Method text, results draft, slides, speaker notes (for M6) |
| `evidence/` | Synthetic smoke-run and demo outputs |
| `results/` | Ablation tables (filled by `summarize_ablations.py`) |
| [test_results.txt](test_results.txt) | Recorded test output |

Files under `integration/` (installed into M1 by `install.py`):

| File | Purpose |
| --- | --- |
| `M1/MADE/src/made/agents/m3_planning.py` | `M3ResearchPlanner` and `M3StuckReplanPolicy` |
| `M1/MADE/configs/agent/planner/m3_research.yaml` | Planner config (`agent/planner=m3_research`) |
| `M1/MADE/configs/agent/self_correction_policy/m3_stuck_replan.yaml` | Self-correction config (runs when `enable_reflection=true`) |
| `M1/MADE/tests/test_m3_planning.py` | 22 synthetic-state tests, including real `M4MemoryManager` on/off; no API key |
| `M1/MADE/configs/agent/m1_integrated.yaml` (M1-owned, edited) | Wires `self_correction_policy: m3_stuck_replan`; default planner stays `diversity` |
| `M1/run_experiment.py` (M1-owned, edited) | Uses the M3 planner for plug-in methods; adds `m3_full`, `m3_planning_off`, `m3_self_correction_off` |
| `M1/tests/test_protocol.py` (M1-owned, edited) | Tests for the new method switches |
| `M1/EXPERIMENT_PROTOCOL.md` (M1-owned, edited) | Documents the M3 methods |

## Planning (`enable_planning`)

`M3ResearchPlanner` subclasses MADE's `GridSearchPlanner`, so all the existing
planner fields still apply. It runs **plan → propose batch → review → update
plan**:

1. **Plan**: split the system into sub-goals by element subset (each binary
   edge plus the ternary interior).
2. **Propose batch**: for `batch_size` queries, target one sub-goal. Pick its
   least-attempted, most novel (by composition distance) SMACT-valid
   compositions.
3. **Review**: re-score every open sub-goal:
   `(successes + new_in_memory + 0.5·near_hull_in_memory + 1) / (attempts + 2) + coverage_weight · unexplored_share`.
4. **Update**: the top sub-goal becomes the next batch target.

Memory (M4): the planner reads `context["m1_memory"]`. These are M4's
`M4MemoryManager` records, or M1's bounded memory.

- An empty list (the first query, or `enable_memory=false`) means no evidence.
- When records exist, they feed step 3.
- Formulas that memory shows failing `memory_failure_limit` times are skipped.

Each review is written to a bounded `decision_trace` in the checkpoint, and as
an `M3 review:` line in the run log.

## Self-correction (`enable_reflection`)

`M3StuckReplanPolicy.revise_plan(plan, context)` keeps a bounded history of
observed outcomes. It flags the search as stuck when, over the last `window`
(K) queries:

- `no_progress`: no newly discovered **stable** phase was found (MADE marks
  every new structure as newly discovered, so stability is required); or
- `repetition`: the plan targets a reduced formula already tried `max_repeat`
  times.

It then re-plans to the least-visited compositions that are farthest from the
recent window.

- **Escalation:** consecutive stalls escalate. From level 2, the candidates
  per composition double. Generation is not an oracle query, and M1 still caps
  the plan.
- **Guards:** a `cooldown` stops back-to-back re-plans, and any discovery
  resets the level.
- **Logging:** each event (`query`, `reason`, `level`, `before`, `after`) is
  checkpointed and logged as an `M3 re-plan:` line.

## Safety and protocol

- Uses only `env.get_state()` fields and post-query observations. Never reads
  `phase_diagram_gt` or evaluator state, and never calls the oracle.
- Respects `context["m1_queries_remaining"]`. M1 applies the final cap.
- Deterministic: tie-breaks use an RNG seeded from `(experiment.seed, step)`.
  All state is JSON-serializable, and checkpoint/resume reproduces decisions.
- No LLM calls, so no API key or token cost.
- M1's default planner stays `diversity`, so the recorded `m1_baseline` runs
  stay reproducible.

## Status (21 Oct)

| Schedule step | Status |
| --- | --- |
| Design (19–20 Oct) | Signed off by M1 |
| Build and practice runs (21–23 Oct) | Done; tests, smoke episodes and demo pass |
| Code to M1, method text and slides to M6 (24 Oct) | Integrated by M1; method text and slides received by M6 |
| Two ablations (26–27 Oct) | First sweep done (72 runs, 21 Oct); it exposed the progress-signal bug, kept as [report/M3_RESULTS_PRE_FIX.md](report/M3_RESULTS_PRE_FIX.md). Fixed M3 arms (54 runs) re-running; the 18 baseline runs are reused |
| Results text and slides (27 Oct) | Requested by M6; generated by `summarize_ablations.py` after the runs |

## Checks

From `M1/MADE` on current `main`:

```bash
uv run python ../../M3/install.py
PYTHONPATH="../../M4/src" uv run pytest -q tests/test_m1_integrated.py tests/test_m3_planning.py
PYTHONPATH=".." uv run pytest -q ../tests -o addopts=''
uv run pytest -q ../../M3/tests -o addopts=''
uv run ruff check src/made/agents/m3_planning.py tests/test_m3_planning.py ../../M3
uv run python ../../M3/examples/m3_demo.py
```

Expected results (20 Oct, `main` at `bc97609`):

- The installer check shows seven files `ok` and `m1_integrated.yaml` as `merged`.
- M1 and M3 tests with M4 on the path: 39 passed. M1's full suite, including M4
  and M5 tests: 54 passed.
- M1 protocol tests: 7 passed.
- M3 tool tests: 12 passed.
