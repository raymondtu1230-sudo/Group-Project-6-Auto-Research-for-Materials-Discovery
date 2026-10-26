# Memory and evidence management

Updated 26 October 2026. Integrated method and preserved development evidence for M6. The final frozen-agent development ablation is complete; see M4_FROZEN_MEMORY_RESULTS.md for the authoritative results.

## Method

M4 records public feedback from evaluated candidate structures within each episode. Each record identifies the run, episode, query step and candidate attempt, with the complete chemical system, candidate composition when recoverable, and available energy and stability feedback. Separate attempt identities preserve different structures with the same reduced formula. Stability labels describe the observed phase diagram at the evaluation step.

The M1 MemoryManager adapter returns recent observations with contrasting outcomes to the Planner. It limits retrieval to eight records and 4,000 serialized JSON characters. Character limits do not define a model-token budget. The independent core also supports composition-fraction distance retrieval, but M1's argument-free get_memory() hook does not activate that mode. Each episode has isolated memory and JSON checkpoint state. Event recording detects identical retries and conflicting identities.

M1 adopted M4 memory, the M3 planner implementation and the event-capture subclass. The M3 Planner reads context["m1_memory"] and records consumed memory IDs in its review trace. The default diversity Planner ignores that field, so experiments must explicitly select the M3 Planner. Disabling Memory returns no M4 records to planning while keeping other components fixed.

M4 uses public observations and makes no oracle calls. It preserves the official MADE runner, scientific oracle, evaluator and budget logic. Its capture subclass delegates proposal execution to M1 and writes a separate generator/filter audit sidecar in both comparison arms. Capture records filter exclusions, generator/filter exceptions and empty generation batches. Oracle exceptions, planner/scorer errors and process termination remain outside this boundary. Error records contain exception classes without copying exception messages.

Filter exclusion does not establish that a structure was never evaluated: M1 falls back to the unfiltered candidates when a filter returns none. Audit records label that fallback and retain public structure identity for offline matching. An unstable evaluated structure is a scientific outcome, not automatically a runtime failure or evidence of a physical mechanism. The audit sidecar stays outside retrieval, policy rewards and decision inputs.

The official ON and OFF trajectories retain all queried observations, including the final query. The OFF package additionally includes a complete public-observation JSONL export. M1 updates online memory before the next proposal, so an online log may omit the final evaluation. Synthetic tests and the historical pilot review traces demonstrate the memory-consumption boundary; exact ON review-memory IDs were not retained in the formal reference. M5 has confirmed the evidence schema and supplies a separate decision-log interface for exploration context. The frozen agent includes the adopted M5 module and decision sidecar. The earlier development pair below did not enable exploration or use an M5 sidecar.

## Development validation

On 21 October, the historical joint suite passed 69 tests and a separate treatment-isolation test passed. The unchanged synthetic smoke and paired synthetic episodes also completed. The final 26 October relevant regression suite passed all 72 tests; see ../VALIDATION.md for its command and scope. These checks establish interface behavior, switch handling and evidence capture.

A real-material development pair used Mg-Sn-Sr, seed 17, B=20 and protocol-v1 CPU ORB. Both arms used M3 planning/reflection, Random generation and M4 capture, with composition exploration and tool routing OFF. Only the Memory switch and output identities differed. The base team revision was e1a40d8. Both runs passed M2's individual offline validation, with complete official metric histories and matching material-reference snapshots.

| Condition | Official mSUN@20 | Official AUDC |
| --- | ---: | ---: |
| Memory ON | 7 | 68.5 |
| Memory OFF | 8 | 76.0 |

ON consumed memory at four of five review points. OFF consumed none. Both offline evidence exports contain all 20 evaluated observations. Neither run produced a captured generator/filter event. These runs did not invoke LLM/OpenRouter inference.

This single development pair showed no Memory benefit. ON retained the Sn-Sr subgoal throughout, while OFF moved to the ternary subgoal after eight queries and returned after sixteen. This allocation is consistent with an over-exploitation concern, but does not establish a general effect or a sole cause. At the tested revision, M3's memory-review score counts newly discovered observations without also requiring stability, so that proxy differs from official mSUN. The original negative result remains preserved for analysis.

## Final evaluation and limitations

The completed frozen-agent comparison pairs the accepted m1_full reference with memory_off on dev, changing only enable_memory. Match systems, initial reference data, seeds, oracle settings, inference settings and other component switches. Keep capture identical in both arms, isolate episodes and retain complete evidence. M6 restricts check/hidden evaluation to the frozen full agent and baselines.

Report official mSUN@B, AUDC, paired AF/EF, discovery curves and available cost data. Use the agreed seeds 17/29/43 and disclose any reduction in repeats. Campaign-query counts exclude initialization/scorer computation. Record measured model usage where available and retain missing cost fields explicitly. Runtime differences between this single pair do not isolate Memory overhead.

The development pair remains historical. The completed final frozen-agent comparison uses all 18 development pairs, with three traced cases, discovery curves and partial cost accounting in ../evidence/frozen-memory-ablation-20261026/analysis/. Exact ON consumed-memory IDs were not retained in the formal reference, so the final cases distinguish available observations from proven consumption and avoid attributing a decision to an unrecorded memory ID.

## Sources for assembly

- M4/EVIDENCE_SCHEMA.md and M4/src/m4_memory/: implementation and capture contract.
- M4/evidence/dev-pilot-20261021/: historical paired audit, raw outputs, configurations and M3 traces.
- M4/evidence/frozen-memory-ablation-20261026/: authoritative formal paired results, raw OFF outputs, curves, cases, costs and provenance.
- M1/PLUGIN_INTERFACE.md and M1/protocol/protocol_v1.yaml: integration and experiment contract.
- M6/PROTOCOL_ADOPTION.md: dev/check/hidden roles and frozen-agent comparison.

Team settings remain subject to any teaching-team protocol amendment. The final slides and speaker notes use the completed frozen development results and identify Zhang Yiming as presenter.

## Frozen development result

ON mSUN@20=10.0000 versus OFF 9.1111, AUDC 88.1111 versus 86.9444. Effects vary by pair. See M4_FROZEN_MEMORY_RESULTS.md for aggregation, uncertainty, provenance and limitations. The final deck is M4_Frozen_Memory_Results.pptx.
