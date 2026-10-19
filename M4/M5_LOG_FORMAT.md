# Evidence handoff for M5

Format confirmation by M5 is pending. EVIDENCE_SCHEMA.md is the common field reference. The adapter and exporter supply the complete chemical system, candidate composition when available, and a limited observed-outcome explanation. The exporter now requires --elements for the full run system.

Export both ON/OFF episodes from official trajectories, including the final query. Do not use the online plugin log as the complete experiment record. Candidate IDs identify attempts rather than reduced formulas, so different structures at the same composition remain separate.

The committed evidence/synthetic-smoke examples contain two synthetic Li-O evaluations. They are not real discoveries or failure cases. A separate real Mg-Sn-Sr run completed 20 queries; its derived records and table are in evidence/real-workflow, while original official outputs remain preserved locally.

For over-exploitation and wasteful-exploration analysis, M1/M5 must provide exploration mode, selected direction, remaining budget, candidate-tool provenance and the actual policy rationale. These cannot be inferred from energy values. M3 must also provide the IDs/content of memory actually consumed by a decision.

Current automatic capture covers completed evaluations, including unstable outcomes. Runtime errors and rejected candidates require an explicit framework event source. The storage API supports those statuses, but the current hook does not automatically emit them. Never invent a physical cause for an unstable structure.
