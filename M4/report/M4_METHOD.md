# Memory and evidence management

Draft updated 21 October 2026. Method text and development evidence for M6. Final frozen-agent results remain pending.

## Method

M4 records public feedback from evaluated candidate structures within each episode. Each record identifies the run, episode, query step and candidate attempt, with the complete chemical system, candidate composition when recoverable, and available energy and stability feedback. Separate attempt identities preserve different structures with the same reduced formula. Stability labels describe the observed phase diagram at the evaluation step.

The M1 MemoryManager adapter returns recent observations with contrasting outcomes to the Planner. It limits retrieval to eight records and 4,000 serialized JSON characters. Character limits do not define a model-token budget. The independent core also supports composition-fraction distance retrieval, but M1's argument-free get_memory() hook does not activate that mode. Each episode has isolated memory and JSON checkpoint state. Event recording detects identical retries and conflicting identities.

M1 adopted M4 memory, the M3 planner implementation and the event-capture subclass. The M3 Planner reads context["m1_memory"] and records consumed memory IDs in its review trace. The default diversity Planner ignores that field, so experiments must explicitly select the M3 Planner. Disabling Memory returns no M4 records to planning while keeping other components fixed.

M4 uses public observations and makes no oracle calls. It preserves the official MADE runner, scientific oracle, evaluator and budget logic. Its capture subclass delegates proposal execution to M1 and writes a separate generator/filter audit sidecar in both comparison arms. Capture records filter exclusions, generator/filter exceptions and empty generation batches. Oracle exceptions, planner/scorer errors and process termination remain outside this boundary. Error records contain exception classes without copying exception messages.

Filter exclusion does not establish that a structure was never evaluated: M1 falls back to the unfiltered candidates when a filter returns none. Audit records label that fallback and retain public structure identity for offline matching. An unstable evaluated structure is a scientific outcome, not automatically a runtime failure or evidence of a physical mechanism. The audit sidecar stays outside retrieval, policy rewards and decision inputs.

Both ON and OFF conditions export all evaluated observations from the official trajectory, including the final query. M1 updates online memory before the next proposal, so the online log may omit the final evaluation. M3 decision traces establish actual memory consumption. M5 has confirmed the evidence schema and supplies a separate decision-log interface for exploration context. Its updated module and log path still require adoption into M1 at the reviewed revision; the development pair below did not enable exploration or use an M5 sidecar.

## Development validation

The joint M1/M3/M4 suite passed 69 tests. A separate treatment-isolation test passed. The unchanged synthetic smoke and paired synthetic episodes also completed. These checks establish interface behavior, switch handling and evidence capture.

A real-material development pair used Mg-Sn-Sr, seed 17, B=20 and protocol-v1 CPU ORB. Both arms used M3 planning/reflection, Random generation and M4 capture, with composition exploration and tool routing OFF. Only the Memory switch and output identities differed. The base team revision was e1a40d8. Both runs passed M2's individual offline validation, with complete official metric histories and matching material-reference snapshots.

| Condition | Official mSUN@20 | Official AUDC |
| --- | ---: | ---: |
| Memory ON | 7 | 68.5 |
| Memory OFF | 8 | 76.0 |

ON consumed memory at four of five review points. OFF consumed none. Both offline evidence exports contain all 20 evaluated observations. Neither run produced a captured generator/filter event. These runs did not invoke LLM/OpenRouter inference.

This single development pair showed no Memory benefit. ON retained the Sn-Sr subgoal throughout, while OFF moved to the ternary subgoal after eight queries and returned after sixteen. This allocation is consistent with an over-exploitation concern, but does not establish a general effect or a sole cause. At the tested revision, M3's memory-review score counts newly discovered observations without also requiring stability, so that proxy differs from official mSUN. The original negative result remains preserved for analysis.

## Final evaluation and limitations

After the full-agent freeze, compare the accepted frozen m1_full reference with memory_off on dev, changing only enable_memory. Match systems, initial reference data, seeds, oracle settings, inference settings and other component switches. Keep capture identical in both arms, isolate episodes and retain complete evidence. M6 restricts check/hidden evaluation to the frozen full agent and baselines.

Report official mSUN@B, AUDC, paired AF/EF, discovery curves and available cost data. Use the agreed seeds 17/29/43 and disclose any reduction in repeats. Campaign-query counts exclude initialization/scorer computation. Record measured model usage where available and retain missing cost fields explicitly. Runtime differences between this single pair do not isolate Memory overhead.

The development pair is not the final frozen-full-agent ablation. Final results and two or three traceable cases will follow the controlled experiment. Each case should link observed evidence, memory consumed, subsequent choice and official feedback, including neutral or negative outcomes.

## Sources for assembly

- M4/EVIDENCE_SCHEMA.md and M4/src/m4_memory/: implementation and capture contract.
- M4/evidence/dev-pilot-20261021/: paired audit, raw outputs, configurations and M3 traces.
- M1/PLUGIN_INTERFACE.md and M1/protocol/protocol_v1.yaml: integration and experiment contract.
- M6/PROTOCOL_ADOPTION.md: dev/check/hidden roles and frozen-agent comparison.

Team settings remain subject to any teaching-team protocol amendment. The method slides and speaker notes use the same draft status and development results.
