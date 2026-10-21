# Speaker notes for the two-slide draft

Draft updated 21 October 2026. Approximately 90 seconds total. Final frozen-agent results remain pending.

## Slide 1: Memory and evidence management

M4 keeps a complete evidence log and supplies a bounded set of observations to planning. Each structure attempt has its own identity and retains public energy and stability feedback. The adapter returns recent observations with contrasting outcomes, up to eight records and 4,000 JSON characters. M1 has adopted the module, and M3 records the memory IDs used in its reviews. We export the official trajectory in both conditions to include the final query. Separate audit logs capture generator and filter events without feeding them back into decisions. Oracle exceptions remain outside this capture boundary.

## Slide 2: Memory pilot and planned evaluation

We tested one development pair on Mg-Sn-Sr with seed 17 and a budget of 20 queries per arm. Both used the M3 planner and CPU ORB, with exploration and routing off. Memory ON scored seven on mSUN and 68.5 on AUDC. OFF scored eight and 76.0, so this pair showed no benefit. ON stayed in Sn-Sr, while OFF also explored ternary compositions. The figure shows the ON run's observed phase diagram. This is a development finding from one system and seed. The formal ablation will compare the frozen full agent against Memory OFF with all other settings matched.

## Sources and presentation limits

Slide 1: M4/EVIDENCE_SCHEMA.md, M4/src/m4_memory/m1_adapter.py, M4/src/m4_memory/capture.py, M1/PLUGIN_INTERFACE.md and adopted profile commit 3f8d48f.

Slide 2: M4/evidence/dev-pilot-20261021/paired_results.csv, audit.json, m3_trace_on.json, m3_trace_off.json and raw_outputs.zip. The figure is on/trajectories/phase_diagram_episode_000.png inside the ZIP. The base team revision is e1a40d8. M6/PROTOCOL_ADOPTION.md defines the final dev-only ablation. Initialization adds oracle work beyond the 20 campaign queries. Neither the single pair nor its runtime difference establishes a general effect or isolated Memory overhead.
