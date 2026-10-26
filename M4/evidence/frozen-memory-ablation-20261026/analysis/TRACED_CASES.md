# Traced development cases

These three cases describe the frozen full agent versus its Memory OFF ablation. Selection deliberately includes favourable, adverse and equal endpoint outcomes. `traced_cases.csv` preserves every query in both arms, the public observed outcome, cumulative official score, M5 incoming/outgoing compositions and policy rationale. The online record count indicates available evidence, not proof that a particular record was consumed.

## Co-Mg-Na, seed 29: positive endpoint difference

ON mSUN@20=12, AUDC=104.0. OFF mSUN@20=3, AUDC=32.5. ON queries5/6 evaluate MgNa6 and Mg4Na3, both new and stable at evaluation. Queries9–14 continue in Mg-Na, with six further new stable outcomes. OFF queries9–12 evaluate Co-Na candidates and find no stable outcomes in that block. This case illustrates a productive allocation associated with the memory-enabled full system. The candidate sequences already diverge at query2, so the later block alone cannot establish a causal explanation of the entire difference.

## Mg-Sn-Sr, seed 17: concentrated search and adverse outcome

ON mSUN@20=12, AUDC=105.0. OFF mSUN@20=14, AUDC=154.0. ON queries5–20 all stay on the Sn-Sr binary. OFF also finds early stable Mg-Sn candidates at queries2/3, followed by productive Sn-Sr queries. ON's concentrated allocation is consistent with an over-exploitation concern, but it still discovers useful structures. The paired result does not prove that a different allocation would improve the same sequence of random candidates. This is a frozen-agent adverse case, distinct from the older pre-fix pilot.

## Co-Mg-Na, seed 17: wasteful allocation and equal endpoint

Both arms finish at mSUN@20=4, but ON AUDC=18.0 and OFF AUDC=36.0. ON queries9–16 explore Co-Mg, ternary Co-Mg-Na and Co-Na compositions. None of these eight evaluations is stable at evaluation. ON then finds three new stable Mg-Na outcomes at queries18–20. OFF has already found stable candidates at queries7/8 and15/16. This is a trajectory example of diverse but unproductive budget use. It describes outcomes and allocation rather than establishing a physical failure mechanism. M5's mode and rationale fields remain available per decision.

## Evidence boundary

Each case is identified by result directory, chemical system, seed, method and attempt. M1 reference logs use `m4-local` as their run ID, so run ID alone is not a globally unique join key. Do not merge reference records from different directories by that field.

The reference upload retains online M4 observations and M5 decisions but no exact ON M3 review/consumed-memory-ID trace. Consequently these cases do not claim which exact retrieved record caused a decision. OFF review traces explicitly show no memory consumption. The earlier pilot has exact ON review traces but uses an earlier planner revision and remains labelled accordingly. Full causal attribution is a logging improvement for a future run, not grounds to fabricate a trace or silently change the frozen agent.

Sources: original `trajectories/episode_000.json`, `m2_metrics_history.json`, `m4_evidence.jsonl` (ON), `m3_decision_trace.json` (OFF), and `m5_decisions.jsonl`, addressed through `../paired_results.csv`.
