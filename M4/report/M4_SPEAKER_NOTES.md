# M4 presentation notes

Updated 26 October 2026. Approximately 90 seconds for two slides. Use `M4_Frozen_Memory_Results.pptx` for final assembly. The older 21 October draft remains historical.

## Slide 1: Memory and evidence management

M4 stores the public feedback from each evaluated structure and supplies bounded observations to planning. Each attempt keeps its own identity and observed stability. The M1 adapter returns recent observations with contrasting outcomes, up to eight records and 4,000 JSON characters. The independent core also supports composition-distance retrieval, but the active argument-free hook uses bounded recent feedback. M3 consumes this memory. We export every official trajectory, including the final query. Separate generator and filter audit logs remain outside decision inputs and stay enabled when memory is off. Oracle exceptions are outside that capture boundary.

## Slide 2: Frozen Memory ablation

We compared the frozen full agent with memory disabled across six development systems and three seeds, using 20 campaign queries per episode. All 36 runs passed individual validation, and reference snapshots match. Memory ON averaged 10.00 mSUN versus 9.11 OFF. AUDC averaged 88.11 versus 86.94. The effect is mixed: ON is better in eight mSUN pairs, equal in three and worse in seven. For example, it helps on Co-Mg-Na seed 29, but concentrated Sn-Sr search loses against OFF on Mg-Sn-Sr seed 17. Memory helps some allocations but does not guarantee improvement. These results use the development split. M1 reconstructed the ON curves from frozen trajectories with documented provenance.

## Sources and Q&A

Source table: M4/evidence/frozen-memory-ablation-20261026/paired_results.csv. Chart: analysis/aggregate_curves.csv, arithmetic mean of six systems within seed, then three seeds. Slide table rounds means to two decimals; report includes seed SD. Official AUDC uses new-stable discovery counts, a definition distinct from mSUN. Cases: analysis/TRACED_CASES.md and traced_cases.csv. Costs: analysis/per_run_cost.csv. A budgeted campaign query is one env.step; initialization adds uninstrumented oracle work. LLM cost is not reported. Exact ON consumed-memory IDs are unavailable for the formal reference. Avoid causal attribution to a specific record. All source code and evidence remain separately versioned.
