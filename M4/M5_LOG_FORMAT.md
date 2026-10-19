# Proposed log format and examples for M5

This format is pending M5's confirmation; it has not been sent or approved.

Export evidence.jsonl from each official episode trajectory in both ON/OFF groups, including the final query. Plugin logs are diagnostic and do not replace a complete trajectory. JSONL retains candidate proposal structures and queried energy/stability feedback. overview.csv provides a readable table example.

Fields: run_id and episode_id identify the experiment; step_id and query_count indicate query order; candidate_id identifies the evaluated structure; status is evaluated for trajectory exports; reduced_formula is the composition label. energy_per_atom, formation_energy_per_atom, and e_above_hull are in eV/atom. is_stable reflects the observed phase diagram at that step; is_newly_discovered is the official observation flag.

The two records in evidence/synthetic-smoke come entirely from a synthetic Li-O/analytic-oracle test. They are not real discovery or failure examples. Preserve commands, seeds, configurations, machine information, and complete official outputs for real experiments.

To analyze over-exploitation and wasteful exploration, M1/M5 must also record exploration mode, direction-selection rationale, remaining budget, and candidate provenance at the policy layer. M4 cannot infer these reasons from energies. Ask M5 to confirm field sufficiency before formal experiments and extend the export format if needed.
