# M2: Tool routing and evaluation

M2 owns the Random/Chemeleon baselines, tool selection, official metric reporting,
discovery curves and cost analysis. Planning/reflection (M3), memory (M4), and
composition exploration (M5) remain their owners' components. The full reference
and its `tool_routing_off` ablation require M1's later frozen integration.

## Independent M2 delivery

This is the M2-owned delivery folder, published beside `M1/` and `M4/` on the
repository's `main` branch. M2 sources, tests, evidence and documentation belong
here. Publishing this folder does not install files into M1 or complete the
team's full integration.

See [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) for the requirement-by-
requirement audit, actual passing checks, integration boundary and branch policy.

| Contents | Location in this folder |
| --- | --- |
| Router, generator adapters and component contract tests | `integration/` |
| Hydra profile and explicit integration installer | `configs/`, `install.py` |
| Baseline driver and official metric reporting | `run_baselines.py`, `evaluate.py` |
| Reporting and process-diagnostic tests | `tests/` |
| Validated real evidence, raw results, tables and curves | `verification/` |
| Reproducible workflow definitions | `workflows/` |
| Progress, methods and presentation material | `STATUS.md`, `WORK_LOG.md`, `METHODS_AND_M6_HANDOFF.md` |

The workflow definitions are retained here with the rest of M2's work. Their
active GitHub Actions copies are under `.github/workflows/` on the
`m2/tool-routing-evaluation` development branch. Existing jobs keep their
recorded source revision. The main-branch folder publication does not start a
new experiment or merge the development branch's M1 integration changes.

## Integration

Canonical M2 sources live here. Run `install.py` explicitly to copy the
importable module, contract tests and Hydra profile into the slots required by
`M1/PLUGIN_INTERFACE.md`. The installer updates the existing
`M1/MADE/configs/agent/m1_integrated.yaml` through M1's documented fields.
The main-branch delivery itself changes only `M2/`; M1's existing contents
remain unchanged until that separate integration step is performed.

```bash
cd M1/MADE
uv sync --locked
uv run python ../../M2/install.py
uv run pytest -q tests/test_m1_integrated.py
uv run pytest -q tests/test_m2_tool_routing.py ../../M2/tests -o addopts=''
uv run ruff check src/made/agents/m2_tool_routing.py tests/test_m2_tool_routing.py
uv run python ../run_smoke_test.py
```

`agent=m2_routing` inherits the integrated configuration and enables only
`enable_tool_routing`. The base `agent=m1_integrated` keeps routing disabled.
Once M1 integrates the other members, the official ablation must use the frozen
full agent and change only that switch. This development profile is not a claim
that `m1_full` is complete.

## Router

`OutcomeAwareToolRouter.select_generator(context, generators)` returns a
configured name: `default` (MADE Random) or `chemeleon` (MADE Chemeleon CSP).
MADE still generates candidates, selects one structure and calls `env.step()`.
One such call is one query. The router never calls an oracle.

The router tries each tool once, then uses the mean observed reward plus a UCB
bonus. Stable and newly discovered feedback earns 1, stable-only feedback 0.25,
otherwise 0. These are public observation proxies, not benchmark ground truth.
For a tool used `n` times with reward sum `r`, its smoothed mean is
`(r + 0.5) / (n + 1)` and its bonus is
`0.5 * sqrt(log(total_observed + 1) / n)`. In the final two remaining queries,
only the smoothed mean is used. Ties use the configured experiment seed.

Feedback is attributed once to the preceding tool choice. Repeated calls at the
same query count are idempotent; skipped feedback is not credited to a stale
choice. Exhausted/invalid remaining budgets fail explicitly. This tool-selection
bonus does not change M5's composition exploration policy.

The router and both generator adapters support JSON `get_state`/`load_state`.
Random restores its own RNG; Chemeleon restores the seed and invocation counter
and isolates Python, NumPy and Torch random streams for each sample. The official
CPU configuration is the reproducibility target; GPU equality is not promised.
With Hydra's unspecified seed, optional M2 components use a local seed 0 so the
default disabled configuration remains loadable. Protocol experiments still use
their explicitly configured seeds.

## Real experiments and credentials

The workflow reads the repository Secret `TUWEIKANG_MATERIALS_PROJECT_API_KEY`
and exposes it to MADE as `MATERIALS_PROJECT_API_KEY`. No key belongs in source,
configuration, logs or chat. The format check does not establish API access;
only an actual Materials Project request does.

The observer now emits separate process diagnostics: process CPU seconds, log
bytes, Chemeleon's numeric generation-batch marker, latest sampling step/total,
and elapsed sampling seconds, together with completed query counts. Its child
output is unbuffered. A heartbeat is not evidence of a
completed query; CPU/log activity is not a discovery score. Unavailable or
incompatible `/proc` namespaces leave CPU counters unknown. Diagnostic JSONL
files accompany each new attempt and never enter agent state or official metrics.
Existing running workflows remain on their recorded revision; these diagnostics
do not retroactively reveal the internal progress of those older attempts.

`run_baselines.py` invokes the unchanged `M1/run_experiment.py`. It reads existing
atomic checkpoints from a separate process to preserve official per-query
evaluation history. That history is used only after evaluation and is never
passed to the agent. Missing intermediate points remain missing.

```bash
cd M1/MADE
uv run python ../../M2/run_baselines.py \
  --method random_generator_baseline --split dev \
  --system Mg-Sn-Sr --seed 17 --attempt 1
```

Use systems and seeds from `M1/protocol/`; the example is the first development
unit. Both baseline configurations, candidate pools, ORB settings and B=20 stay
as specified by M1. Repeat with `chemeleon_generative_baseline`, all six
development systems and seeds 17, 29, 43 in separate processes. Preserve every
failed attempt and choose a new attempt number when retrying.

The first development unit is an end-to-end gate, not the complete 36-unit
baseline sweep. The manual workflow now defaults to `mode=chemeleon_retry`:
one first-development Chemeleon unit, no Random rerun and no wider sweep. A
rerun of that same recovery run is blocked; there is no automatic retry loop.
The action/job limits are 330/350 minutes; these external limits do not alter
scientific settings. See the [real timeout audit](verification/20261019-chemeleon-timeout/README.md).

Only the explicitly selected `mode=baseline_sweep` reads all protocol units,
runs both gates and then the remaining 34 units with at most four concurrent
jobs. Each attempt is retained, including missing/failed units in its report.
`baseline_sweep_complete` is separate from `final_comparison_complete`, which
also requires M1's full integrated method. Code-only pushes run lightweight
integration checks. Results retain the capture source hash: wall-time claims
must also account for observer version, hardware and initial model downloads.
Official smoke tests use synthetic data and AnalyticOracle;
they verify integration and do not count as materials-discovery results.

## Offline reporting

```bash
cd M1/MADE
uv run python ../../M2/evaluate.py \
  --results-root results/protocol_v1 \
  --output ../../M2/results/dev-review --split dev --allow-partial
```

Without `--allow-partial`, all protocol-required methods/systems/seeds are
required for a final comparison. The report includes validation findings,
per-run CSV, per-system mean/sample-standard-deviation CSV, a per-method table,
and PNG/SVG curves. Method-level summaries first average systems equally for
each seed, then report the mean and sample standard deviation across seeds.
An incomplete method sweep has no claimed overall score.
Single repeats have no estimated standard deviation. Missing paired baselines,
token usage and dollar costs stay missing. Recorded model-inference prices do
not represent hardware or electricity costs; wall time and oracle queries are
reported separately.

`mSUN@B` is the official `final/novelty_stable_unique_novel_count`. AUDC, AF and EF
use MADE's official `DiscoveryCurveMetrics` and its
`num_newly_discovered_stable` curve, which is distinct from mSUN. AF/EF are paired
by system, seed and budget. Zero-baseline conventions are labelled. Counts can
decrease when the hull changes; curves are not forced to be monotonic.

The evaluator checks completed status, B queries, complete official history,
the actual saved resolved configuration, matching final metrics, identical
protocol settings and material-reference
snapshots. Only offline evaluation hashes the reference snapshot; the router
cannot inspect it. A newer failed attempt is not silently replaced by an older
success. Synthetic fixtures exist only in pytest temporary directories.

## Verification evidence

- [Complete continuation CI on b8e2c0c: passed](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39218278124):
  17 original M1 contract tests, 45 M2 tests, both Ruff checks, installation
  reproducibility and the unchanged official M1 smoke script.
- [Required M1 checks and official smoke: passed](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39211626362).
- [Actual Materials Project request and real Chemeleon continuation: passed](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39212250266).
- Small machine-readable reports with the tested revisions are in
  `verification/`; raw job artifacts contain the generated structures.

The actual model check executes three CPU sampling calls and verifies identical
continued/resumed structures, matching checkpoint state, and preservation of
external Python/NumPy/Torch random streams. It is not a discovery benchmark.
Materials performance numbers are populated only from completed protocol units.

The first actual Random development unit has now completed and passed the
offline validator: Mg-Sn-Sr, seed 17, B=20, mSUN@20=7 and AUDC=55.5. Its
[raw artifact, provenance, validation, tables and curves](verification/20261019-random-gate/README.md)
are committed together. This is one of 36 required baseline units, not an
aggregate result. See [STATUS.md](STATUS.md) for the complete handoff state.

## Handoff schedule

- By 24 October: module, configuration, tests and method note to M1; baseline
  and evaluation material to M6.
- After M1's 25 October freeze: record the reference revision and run the full
  integrated reference on 26 October, then the routing-off ablation.
- By 27 October: collect team results and deliver the validated table, discovery
  curves and cost analysis to M6. Never label a partial development run as final.
