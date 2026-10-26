# M4 final handover

Owner/presenter: Zhang Yiming. Updated 26 October 2026.

M4 provides bounded observed-feedback memory, JSON checkpoint state and separate generator/filter evidence capture. The frozen full agent consumes memory through M3. The final Memory OFF ablation is complete: 18 pairs, 36 validated runs.

| Recipient | Current material | Remaining shared task |
| --- | --- | --- |
| M1 | Adopted module and [current interface](integration/ADOPTION.md) | Preserve frozen scientific source; no component reinstallation requested |
| M2 | [Raw/formal results](evidence/frozen-memory-ablation-20261026/), curves, costs and cases | Intake and shared baseline/ablation aggregation |
| M5 | [Schema](EVIDENCE_SCHEMA.md), [join rules](M5_LOG_FORMAT.md), public observations and decisions | Coordinate failure-case interpretation if needed |
| M6 | [Method, final deck and notes](report/README.md) | Assemble final group report/slides and confirm receipt |

The 18-pair mean is mSUN ON 10.0000 vs OFF 9.1111 and AUDC 88.1111 vs 86.9444. The report preserves mixed pairwise effects and seed SD. This is development evidence, not a held-out result.

Exact ON consumed-memory IDs and full initialization/LLM cost accounting remain unavailable. Reference curves carry reconstruction provenance. Supplementary OFF-vs-ON AF/EF does not replace baseline comparisons. Published artifacts do not establish personal receipt.

Earlier responsibilities, dates and work logs are preserved in [historical handover notes](archive/docs/HANDOVER_before_cleanup.md). The teacher announcement specifies group presentations 31 October / 1 November and an individual report of at most 3 pages by end 3 November. Other handoff dates are team planning, not a newly asserted teacher submission deadline.
