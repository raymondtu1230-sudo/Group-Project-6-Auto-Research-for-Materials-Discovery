# M4 handover and requirements check

Verified 17 October 2026 against the supplied course brief, Task Split and Step-by-Step Guide. Document contents define project requirements, not authorization to send messages or submit on the student's behalf.

## Responsibilities and dates

| Recipient | Deliverable | Due |
|---|---|---|
| M1 | One-page memory design and agreed integration contract | 19–20 Oct |
| M5 | Agree log format; provide logs from first real run | 21–23 Oct / first run |
| M1 | Tested module and integration instructions | 24 Oct |
| M6 | Method text and draft slides | 24 Oct |
| M2 | Memory-OFF results versus frozen full-agent reference, plus 2–3 discoveries | 27 Oct |
| M6 | Results interpretation and final slide material | 27 Oct |

M1 freezes the integrated agent on 25 Oct, supplies the reference by noon 26 Oct using the agreed ablation budget and seeds. Run Memory-OFF against that reference on 26–27 Oct. Do not substitute an independently configured Memory-ON run for M1's reference. M6 owns tuning/check split, seeds, budgets and repetitions. Course brief prefers three runs; one is acceptable with an explicit compute limitation.

## Design for M1

M4 stores queried candidate evidence and returns a bounded, deterministic prompt summary. Call reset at episode start, retrieve before planning, record immediately after every evaluation (including final step), and save/load state with checkpoints. New API is defined in README. Existing MADE history and filters remain fixed in the primary incremental-memory ablation. Decide with M1 whether any old history is replaced; document the precise ON/OFF treatment before experiments.

Retrieval uses composition fractions and recency with contrasting outcome examples; default maximum eight records and 4000 characters. Characters are a deterministic size guard, not model token accounting. M1 records actual tokens. Results are observations relative to the phase diagram at that evaluation step. No oracle calls, hidden labels or evaluator modifications occur inside M4.

Current implementation is an independent prototype, not integrated or scientifically validated. A real candidate structure must be preserved by the integration adapter and referenced in each record. Full setup/timed MADE run remains outstanding pending agreed environment and API access. The inspected upstream commit is a development reference, not the course's frozen commit.

## Log contract for M5

One JSON object per event. Required: run_id, episode_id, event_id, step_id, candidate_id, elements, status. Recommended: composition, reduced_formula, structure_ref, oracle_result, energy_per_atom, formation_energy_per_atom, e_above_hull, is_stable, is_newly_discovered, reason, provenance, decision_context.

M1/M5 should additionally supply policy context needed to diagnose trajectories: exploration/exploitation mode, chosen direction, remaining budget, generator/scorer identifiers, timestamps and runtime. M4 can store these as JSON fields but cannot infer them. M5 must confirm the format; agreement is pending.

Separate error (runtime failure), rejected (pre-evaluation filter failure) and evaluated with is_stable=false (scientific outcome). Do not describe an entire composition as impossible after one unsuccessful structure. Decision context should record retrieved event IDs and the exact summary supplied. Do not include credentials. An event is not evidence of actual discovery unless linked to a real oracle result and official evaluation output.

## Method text draft for M6

We implement an episodic evidence memory that records candidate identity, composition, oracle feedback and execution outcomes. Before each decision, it retrieves a bounded set of composition-related and recent observations, including contrasting outcomes, and supplies their provenance-linked summary to the agent. Memory is isolated across episodes and can be checkpointed. The planned ablation disables this additional retrieval while preserving evidence logging and the remaining frozen system. Integration and discovery-performance validation are pending.

## Draft slide outline for M6

1. Motivation: use prior oracle feedback under a fixed research budget; separate recording from reuse.
2. Method: evaluation → evidence log → bounded retrieval → next decision; distinguish compositions and structures.
3. Evaluation placeholder: official mSUN@B/AUDC/AF/EF, costs, Memory-OFF versus M1 reference, and 2–3 actual discoveries. No numbers or discovery claims until experiments complete.

## Work log

17 Oct: inspected upstream architecture and team repository; implemented JSONL storage, episode isolation, deterministic retrieval, OFF behavior, checkpoints and mock tests. Matched deliverables to original documents; added prompt-length control. Learned that MADE already includes history, so the ablation must state exactly which history channel is disabled. No real oracle/LLM runs performed. Next: M1 interface agreement, M5 format review, official setup/timed run and end-to-end validation.
