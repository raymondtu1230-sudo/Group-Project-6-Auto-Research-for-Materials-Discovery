# Evidence record schema

Schema version 1 uses additive fields. Updated exporters require the complete run chemical system explicitly; do not infer the system from the subset of candidates queried.

| Field | Meaning | Core/adapter | Trajectory export |
|---|---|---|---|
| schema_version | Record format version, currently 1 | Required | Required |
| run_id, episode_id | Experiment and episode identity | Required | Required |
| event_id | Unique event within run and episode | Required | Required |
| step_id | Campaign query step | Required | Required |
| query_count | Query count at observation | Adapter supplies it | Required |
| candidate_id | Structure attempt identity, not formula identity | Required | Required |
| elements | Sorted complete chemical system | Required | Required CLI argument |
| status | evaluated, rejected, or error | Core accepts all; adapter emits evaluated | evaluated only |
| composition | Element amounts from public proposal sites | Adapter adds mapping, or null if unavailable | Mapping, or null |
| outcome | stable, unstable, or unknown at evaluation | Adapter supplies it | Required |
| reason | Explanation of the observed classification | Adapter supplies it | Required |
| proposal | Public structure dictionary | Retained in official trajectory, not copied by adapter | Included when available |
| reduced_formula, energy fields, stability flags | Public queried feedback | Included when supplied | Included when supplied |

Energy units are eV/atom. Composition amounts include occupancies. An element outside the explicitly supplied chemical system is an error. Missing structure or stability data remain null/unknown rather than being inferred. An unstable observation explains only the observed stability classification, not a physical mechanism or a universal failure of that composition.

The generic core accepts additional JSON fields such as reason and decision_context when a caller supplies them. It does not add or validate all optional fields automatically. It validates identity, event status, JSON serialization and deduplication. The adapter and exporter intentionally construct a restricted observed-data view.

## Capture boundaries

The M1 update hook receives the last successful observation at the next proposal. It does not automatically capture generation/filter rejection or oracle exceptions. The core can store explicit rejected/error events, but framework event capture remains pending. Do not report these event types as automatically collected.

For final-step completeness and equal evidence availability under ON/OFF, use the official trajectory exporter for both groups. The online log is diagnostic. New decision-context records should include retrieved IDs and the actual supplied records once M3 consumes them. Policy rationale, exploration mode, budget context and candidate-tool provenance require M1/M5 cooperation.

## Export example

Run from the repository root. Use a new output path and the actual full system:

```bash
python M4/export_evidence.py episode_000.json evidence.jsonl --run-id RUN_ID --episode-id 0 --elements Mg Sn Sr
```

The exporter accepts an official episode object containing trajectory or a plain observation list. It ignores evaluation-only envelope fields and does not replace an existing evidence file.
