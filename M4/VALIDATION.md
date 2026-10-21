# Validation record

Updated 19 October 2026 for the evidence-schema revision. No new oracle run was required: saved trajectories were re-exported, and original scientific metrics were preserved.

- Current main M1 tests plus standalone M4 tests: 32 passed, three dependency warnings.
- M1 tests, standalone M4 tests and saved integration-boundary tests: 36 passed, one intentionally deselected. The saved config-construction test requires adoption into M1 and was excluded because main deliberately leaves M1 configuration unchanged.
- Ruff passed for M4 source, standalone tests and exporter.
- Added regressions cover identical online/exported elements, composition and observed classification; a queried subset within a larger system; wrong-system rejection before writing; missing-data handling; and final-step export.
- Regenerated the two committed synthetic example records with the full chemical system. The real 20-record export was also regenerated locally from the original official trajectory.

Historical evidence: temporary wiring passed 34 tests before this schema revision, completed a synthetic 2-query episode, and completed one real Mg-Sn-Sr CPU ORB episode in 157.193 seconds with 20 campaign queries. See REAL_TEST_STATUS.md. These historical counts are not the current test count.

20 October update: M1 adopted M4/M3; M5 confirmed schema v1. Real-class joint tests now check M3 consumption and optional generator/filter event capture (69 tests passed). The unchanged M1 smoke and synthetic ON/OFF episodes passed. See evidence/joint-integration. The optional capture target still needs M1 adoption, and controlled real-material Memory ON/OFF remains pending.

21 October: M1 adopted capture in `3f8d48f`. Latest joint suite: 69 passed; pilot treatment-isolation test: 1 passed. The real dev pair and complete official curves passed offline validation; see evidence/dev-pilot-20261021. Only the frozen full-agent scientific comparison remains pending.
