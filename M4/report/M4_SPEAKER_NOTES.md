# M4 presentation notes

Presenter: Zhang Yiming

Updated 26 October 2026. Approximately 90 seconds for two slides.

## Slide 1: Memory and evidence management

Presenter: Zhang Yiming

My contribution was the memory and evidence-management module. It records the feedback from each queried structure, including its composition, energy and observed stability. It gives the planner a bounded selection of recent stable and unstable outcomes, with up to eight records at a time. Each episode has its own memory, and the state can be restored from a checkpoint. Both Memory ON and OFF runs retain the full trajectory. Generator and filter logs stay separate from planning, so turning memory off does not remove the evidence needed for analysis.

Sources: M4/src/m4_memory/ and M1/PLUGIN_INTERFACE.md.

## Slide 2: Frozen Memory ablation

Presenter: Zhang Yiming

I ran the 18 Memory OFF experiments and compared them with the team’s 18 frozen full-agent reference runs. The comparison covers six development systems and three seeds, giving 18 pairs and 36 episodes. Each episode used the same budget of 20 campaign queries. The table shows that Memory ON averaged 10.00 mSUN, compared with 9.11 for OFF. AUDC was 88.11 versus 86.94. The average mSUN difference was positive, but the effect varied: ON did better in eight pairs, tied in three and did worse in seven. The result shows a modest average improvement, with substantial variation across pairs. These are development results. M1 reconstructed the ON curves from the saved trajectories, and the report records that provenance.

Sources: M4/evidence/frozen-memory-ablation-20261026/paired_results.csv and analysis/aggregate_curves.csv. Means average six systems within each seed, then the three seed means. The report provides seed SD and individual cases.

## Reference information for Q&A

The bounded adapter uses up to 8 records and 4,000 serialized JSON characters. Its active hook retrieves recent contrasting outcomes. Composition-distance retrieval is a separate core capability.

The detailed report records mean and sample SD across three seed means. The compact chart shows means for all 20 query points. The report also distinguishes mSUN from the new-stable count used by official AUDC. Chart values retain 10 decimal places for workbook compatibility, while the source CSV retains original precision.

Campaign queries count env.step calls. Initialization adds oracle work that is not fully instrumented. LLM costs are not reported. The reference does not retain exact ON review-memory IDs, so the case studies do not attribute a decision to a particular memory record.

Evidence and limitations: M4_FROZEN_MEMORY_RESULTS.md and ../evidence/frozen-memory-ablation-20261026/analysis/.
