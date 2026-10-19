# PE6203 M4 Memory Module

The main-branch handoff adds only `M4/`. M1 configuration and integration-test examples are retained in `integration/` for later adoption by M1/M3; M4 is not automatically enabled in the main-branch agent.

As of 19 October 2026, a temporary M1 integration passed interface tests and a synthetic smoke run. One real-material ORB workflow was also validated. The default Planner does not consume `m1_memory`, so a Memory performance ablation remains pending. See [M1_STATUS.md](M1_STATUS.md) and [REAL_TEST_STATUS.md](REAL_TEST_STATUS.md).

This standalone module implements the approved memory design without changing the MADE benchmark, oracle, or scoring logic. The core module and standalone tests require Python 3.10+ and no third-party packages, API keys, GPU, or network access. M1 integration uses the separate MADE dependency environment.

Inspected upstream MADE revision: `bffda0c9a1fa1904b35c0ef67b455881c975df86`.

## Local validation

Run from this directory:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 examples/mock_demo.py
```

The example uses synthetic mock data, not real material outcomes. It demonstrates recording and retrieval, not improved discovery performance.

## Core module behavior

- `reset(context)`: start an episode and clear retrievable history without deleting the log.
- `record(event)`: append evidence to JSONL. Identical retries with the same run/episode/event ID are recorded once; conflicting content raises an error.
- `retrieve(query=None, limit=8, max_chars=4000)`: rank observations by L1 distance between composition fractions, breaking ties in favor of recent records. With the default limit, reserve slots for recent stable, unsuccessful/error, and latest outcomes. Return at most `limit` records and a summary of at most `max_chars` characters. Returned event IDs and records match the evidence included in the summary. Characters are not model tokens.
- `get_state()` / `load_state(state)`: save and restore history. Loading appends missing events to the current log. Runtime ON/OFF configuration is not overwritten by the checkpoint.
- `enabled=False`: return empty retrieval while continuing to record new evidence in the standalone core. The M1 adapter has different invocation behavior; see M1_STATUS.md.

The first version supports one process and one writer per trusted local JSONL file. Concurrent writes are unsupported. Use a separate path per episode. Existing logs are read for idempotency checks, not automatically imported into retrieval; resume explicitly with `load_state`. Corrupted logs raise errors rather than being silently skipped.

## Core integration design for M1

The following is the proposed standalone M4 API, not an existing MADE API. The adapter to M1's four-method contract is documented in M1_STATUS.md.

1. Call `reset` at episode start with `run_id`, `episode_id`, and `elements`. Optional provenance includes seeds, oracle/agent configuration, and upstream/team revisions.
2. Retrieve before each decision and actually pass the summary to the Planner/LLM. Adding unused data to state does not demonstrate memory use.
3. Ideally record immediately after each `env.step`, including the final evaluation. Build stable event IDs from run, episode, step, and event type. M1's existing hook updates on the next proposal, so export the official trajectory for complete evidence.
4. An evaluated event may include `decision_context`: retrieved event IDs, the exact input summary, and candidate provenance. This is audit information and is not recursively expanded into the retrieval summary.
5. Save M4 state with M1 checkpoints. If interrupted after evaluation but before logging, recover the event from a trusted official trajectory.

Required core event fields are `event_id`, `step_id`, `candidate_id`, and `status`. Allowed statuses are `evaluated`, `rejected`, and `error`; runtime errors are distinct from scientific instability. Recommended fields include `composition` (element-to-amount mapping), `reduced_formula`, `structure_ref`, energy fields, `is_stable`, `is_newly_discovered`, `reason`, and `provenance`.

M1 or its adapter should preserve candidate structures separately and reference them through `structure_ref`, or retain them in the official trajectory. Candidate IDs must distinguish structures with the same composition. M4 does not merge candidates by formula or permanently exclude a composition after one failure. The core does not verify referenced structure files; integration must validate them.

Use observations returned by `ConvexHullEnvironment.step()`, never hidden ground truth. `e_above_hull` and `is_stable` refer to the observed phase diagram at evaluation time. Preserve original evidence and its step rather than rewriting historical stability labels.

## Memory ON/OFF experiment

Keep evidence logs in both groups and hold the base agent's existing history, filters, and other settings fixed. The treatment is whether M4 retrieval reaches the decision-maker. This measures the incremental contribution of M4, not the effect of removing every history mechanism.

Match chemical systems, initial phase diagrams, model settings, other components, oracle, budget, paired seeds, and stopping rules. Isolate runs and episodes. Record retrieved content, actual decision input, official metrics, duplicates, tokens, runtime, and extra OracleScorer/initialization computations. Environment query_count alone is not the total number of oracle evaluations.

Start with a paired pilot to estimate cost before scaling. Use official mSUN/AUDC and other metrics without redefining scoring. Retain neutral and negative outcomes. Cases should connect prior evidence, retrieval, the next selection, and its outcome.

## Remaining integration acceptance checks

- Verify retrieval is consumed in the actual decision input and omitted when OFF.
- Confirm complete final-step evidence, idempotent resume, and episode isolation.
- Compare real episode trajectories with exported logs.
- The locked MADE environment and a real ORB workflow have been validated; Planner consumption and a causal Memory ablation remain pending.

## Delivery schedule for October 2026

Confirm the interface by 21 October; complete integration and pilot checks on 22-23 October; hand off code and log examples to M1 and method text/draft slides to M6 by 24 October. Freeze on 25 October. Run the agreed ablations and prepare 2-3 evidence-backed cases on 26-27 October, subject to compute availability. Original task documents have been checked. See HANDOVER.md for recipients and report/ for method text and the editable two-slide draft.

## Evidence schema and reporting

See [EVIDENCE_SCHEMA.md](EVIDENCE_SCHEMA.md) for required fields and capture limits. The trajectory exporter requires `--elements` for the full chemical system. The adapter now records candidate composition and a factual observed-outcome explanation; it still does not perform target-composition retrieval through M1. See report/M4_METHOD.md for the current report text and the slide draft in report/.
