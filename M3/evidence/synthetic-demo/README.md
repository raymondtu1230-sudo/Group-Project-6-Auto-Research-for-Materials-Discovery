# Synthetic M3 demo

Produced by `uv run python ../../M3/examples/m3_demo.py`, run from `M1/MADE` after
`install.py --install`.
It drives the planner and self-correction directly for 16 fake Li-Fe-O queries.
New phases are scripted at queries 3 and 13 only, so the stretch in between
should look stuck. No oracle or API key is used.

`m3_demo_trace.json` records, per query, the sub-goal, the planned and
evaluated compositions, and whether self-correction re-planned. It also holds
the planner's review scores and the three re-plan events. All three were triggered by no new phase in the
4-query window, before queries 8, 10 and 12 (`query` in the events is the
number of queries already used). The trace shows the mechanism only, not discovery
performance.

The demo uses smaller settings than the real agent so the mechanism fits in 16
queries: a 4-query stuck window (real: 6), a 2-query wait between re-plans
(real: 3) and 3 queries per sub-goal batch (real: 4). That is why its re-plans
are only 2 queries apart.
