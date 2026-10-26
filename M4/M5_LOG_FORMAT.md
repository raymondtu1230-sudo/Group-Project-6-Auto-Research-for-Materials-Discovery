# Evidence handoff for M5

M5 confirmed schema v1 in M5/M4_LOG_CONFIRMATION.md on 19 October. EVIDENCE_SCHEMA.md is the common field reference. The adapter and exporter supply the complete chemical system, candidate composition when available, and a limited observed-outcome explanation. The exporter now requires --elements for the full run system.

Export both ON/OFF episodes from official trajectories, including the final query. Do not use the online plugin log as the complete experiment record. Candidate IDs identify attempts rather than reduced formulas, so different structures at the same composition remain separate.

The committed evidence/synthetic-smoke examples contain two synthetic Li-O evaluations. They are not real discoveries or failure cases. A separate real Mg-Sn-Sr run completed 20 queries; its derived records and table are in evidence/real-workflow, while original official outputs remain preserved locally.

For over-exploitation and wasteful-exploration analysis, M1/M5 must provide exploration mode, selected direction, remaining budget, candidate-tool provenance and the actual policy rationale. These cannot be inferred from energy values. M3 must also provide the IDs/content of memory actually consumed by a decision.

Current automatic capture covers completed evaluations, including unstable outcomes. Runtime errors and rejected candidates require an explicit framework event source. The capture subclass adopted in the frozen profile provides generator/filter events; see integration/EVENT_CAPTURE.md. It does not capture oracle errors. Capture remains enabled independently of Memory. Never invent a physical cause for an unstable structure.

Prefer M5's per-episode decision_log JSONL sidecar for analysis, preserving the checkpoint as source. Join it to M4 proposal events by run/episode and completed query count; see integration/EVENT_CAPTURE.md for next-slot step semantics and filter fallback limits.

## Final evidence, 26 October

The [formal package](evidence/frozen-memory-ablation-20261026/) includes paired observations, M5 decisions and three traced cases. Join reference records by result directory, method, system, seed and attempt as well as query count: the original ON logs reuse `m4-local`, so run ID alone is insufficient. Exact formal ON review-memory IDs were not retained. Preserve this limit rather than inferring consumed IDs from available observations.
