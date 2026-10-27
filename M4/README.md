# M4: Memory and evidence management

Owner and presenter: Zhang Yiming. Updated 26 October 2026.

M4 stores public feedback from queried structures and provides bounded recent stable/unstable observations to the integrated planner. The M1 adapter returns up to 8 records and 4,000 serialized JSON characters. Separate generator/filter audit logs remain independent of the Memory switch. The frozen full agent uses M3 planning and the adopted M4 module.

## Final handoff

| Material | Location |
| --- | --- |
| Final results and limitations | [Frozen Memory results](report/M4_FROZEN_MEMORY_RESULTS.md) |
| Current presentation | [Two-slide PPTX](report/M4_Frozen_Memory_Results.pptx) |
| Presenter script | [Speaker notes](report/M4_SPEAKER_NOTES.md) |
| Method | [Memory and evidence management](report/M4_METHOD.md) |
| Raw results, validation and checksums | [Formal evidence package](evidence/frozen-memory-ablation-20261026/) |
| Curves, three cases, discovery examples and costs | [Offline analysis](evidence/frozen-memory-ablation-20261026/analysis/) |
| Setup and reproduction | [Runbook](EXPERIMENT_RUNBOOK.md) |
| Interface and validation | [M1 integration](M1_STATUS.md), [tests](VALIDATION.md) |

The completed formal comparison covers 18 ON/OFF pairs: six development systems, seeds 17/29/43 and B=20. All 36 run directories pass individual M2 validation and paired data-snapshot checks. ON averages mSUN@20=10.0000 and AUDC=88.1111; OFF averages 9.1111 and 86.9444. Pairwise effects are mixed. M1's ON curves were reconstructed from saved trajectories with explicit provenance. Exact ON review-memory IDs and full initialization/LLM cost accounting were not retained.

## Implementation

- [src/m4_memory/](src/m4_memory/): independent memory, M1 adapter, evidence contract and capture subclass.
- [tests/](tests/): standalone tests. [integration/](integration/): current interface checks and capture documentation.
- [EVIDENCE_SCHEMA.md](EVIDENCE_SCHEMA.md): versioned fields, identities and capture limits.
- [M5_LOG_FORMAT.md](M5_LOG_FORMAT.md): joining observation and policy evidence.

The core has no third-party dependencies. Integration and offline scientific reporting use the locked M1/MADE environment. The standalone core supports composition-distance retrieval, while the active argument-free M1 hook uses recent contrasting outcomes. Characters are not model tokens. Use separate per-episode identities and logs, and restore state explicitly. Concurrent writers are unsupported.

M4 preserves the official runner, oracle, evaluator and budget logic. Retrieval uses public post-query observations only. Evaluation-only reference envelopes belong to offline reporting and never enter decisions.

[Work record](WORK_LOG.md) supports the later individual report. [Three concrete discoveries](evidence/frozen-memory-ablation-20261026/analysis/DISCOVERY_EXAMPLES.md) identify source structures and query outcomes.

## Historical records

Earlier evidence remains under [evidence/](evidence/), labelled by experiment and date. [The development pilot](DEV_PILOT.md) used an earlier planner/profile and is separate from the final ablation. Old slides are in [report/archive/](report/archive/), old status documents in [archive/docs/](archive/docs/), and old test output in [evidence/validation-history/](evidence/validation-history/). The [initial memory-only YAML](integration/archive/README.md) is historical.

M2 owns shared leaderboard/baseline aggregation and M6 owns group report/slides assembly. Public files establish availability; recipient acknowledgement remains a separate handoff step.
