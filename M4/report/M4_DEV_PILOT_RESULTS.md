# Real-material development Memory pair, 21 October 2026

## Controlled development scope

Team source `e1a40d8`; Mg-Sn-Sr, seed 17, B=20, protocol-v1 CPU ORB and official
M1/MADE execution. Both arms use M3 planning/reflection, Random generation and
M4 event capture; composition exploration and tool routing are OFF. These
explicit development methods are not frozen `m1_full` or its final ablation.
No check/hidden run or LLM/OpenRouter inference was performed.

## Results

| Arm | Official mSUN@20 | Official AUDC | Driver wall time (s) |
| --- | ---: | ---: | ---: |
| Memory ON | 7 | 68.5 | 191.867 |
| Memory OFF | 8 | 76.0 | 212.230 |

Both runs completed 20 queries, passed M2's canonical individual `load_run`
validation, have complete official per-query curves, and share the same
material-reference snapshot hash. Paired resolved configuration differs only
in `enable_memory` and logging/output identities/paths. See `audit.json`.
This single development pair does **not** show a Memory benefit; no aggregate
significance, general improvement or general harm is claimed. Runtime differences
are not an isolated measurement of Memory overhead. Recorded cost is partial,
and campaign-query counts exclude initialization computations.

M3 review traces contain five review points in each arm. ON uses no memory at
the initial review and records memory IDs at the next four; OFF uses no memory
at any review. ON has 19 online observations because M1 updates on the next
proposal; complete offline exports contain all 20 for both arms. OFF has no
online memory file. Neither run produced generator/filter rejection/error
events, so no proposal-event file is present; absence is not an instrumentation
failure or proof that all possible error sources are captured.

## Development failure-analysis example

Both formula sequences match for the first eight queries. At the review after
8 completed queries, ON stays in the Sn-Sr subgoal while OFF changes to Mg-Sn-Sr.
ON stays in Sn-Sr at all five reviews. OFF returns to Sn-Sr at the review after
16 queries. This is consistent with an over-exploitation concern: historical
success evidence can reinforce a productive region while delaying broader
exploration. The trace and trajectories support the observed allocation pattern,
not a claim that Memory is universally harmful or a physical cause of failure.
No event, decision rationale or counterfactual score has been invented.

M3/M5 should review the interaction between memory-weighted subgoal selection
and composition exploration before the full-agent freeze. Preserve these results
while considering any development changes; do not rewrite them as improved runs.
The formal final comparison still needs the frozen full agent, agreed dev systems
and paired repeats.

## Files and reproduction

- `paired_results.csv`: descriptive paired results.
- `audit.json`: canonical individual validation and paired setting checks.
- `m3_trace_on.json`, `m3_trace_off.json`: public decision review evidence.
- `provenance.json`: source and archive hashes.
- `raw_outputs.zip`: separate ON/OFF original metrics, trajectories, plots,
  metadata, saved Hydra configurations, capture status and complete evidence.

The ZIP includes the official evaluation-only reference envelope for offline
validation. It must never be loaded into retrieval or an agent's decision input.
Public audit source locations are expressed relative to the team repository;
underlying raw results and scientific metrics are unchanged.

See `../DEV_PILOT.md` for the driver and validation commands. Attempts are
preserved; new runs require new attempt numbers. The saved ON Hydra configuration
was resolved with its actual child run identity after correcting parent export
context; only logging provenance was affected. The driver includes this correction
for subsequent runs. M1, official runner, oracle and protocol files are unchanged.

Raw evidence and the referenced files are under `../evidence/dev-pilot-20261021/`.

## Scoring detail for M3 review

At the tested revision, M3ResearchPlanner._review adds to its memory `new`
evidence whenever `is_newly_discovered` is true, without also checking
`is_stable`. The real queried records include observations with newly-discovered
true and stable false (for example ON queries 10 and 11). Thus this review
proxy is not the official mSUN count. M3 should confirm whether that weighting
is intentional; it is a concrete development concern, not a demonstrated sole
cause of the negative pair. M4 preserved both flags and did not change M3 code.
