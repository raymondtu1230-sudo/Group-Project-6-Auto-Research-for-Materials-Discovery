# M4 integration status

Updated 26 October 2026. The frozen full agent uses M3 planning, M4 memory and the independent capture subclass. The formal 18-pair development ablation is complete.

## Active contract

The adapter implements `update_state(state)`, `get_memory() -> list[dict]`, `get_state()` and `load_state(state)`. It allowlists public post-query feedback, deduplicates identities, bounds retrieval and supports JSON state. M1 invokes it only with Memory enabled. OFF supplies no M4 retrieval while leaving the current public environment state and other components available.

M1 updates memory before the next proposal, so online logs may omit the final evaluation. Official trajectories retain all 20 queries; OFF includes a complete offline evidence export. Generator/filter event capture remains independent of retrieval and is excluded from rewards and planner inputs. Oracle exceptions are outside its scope.

The actual OFF source was `02e0026bf450f71f4f7862228d295f5b02b49e12`. The reference evidence patch `ae7fe81991c56dd2d77685220b74ddbef11039c7` does not change the relevant scientific implementation/configuration. Later presentation and test-only changes do not relabel the original runs.

## Evidence and reproduction

- [Current validation](VALIDATION.md): final test suite and scientific result checks.
- [Final comparison](evidence/frozen-memory-ablation-20261026/): all 18 pairs, raw OFF outputs and provenance.
- [Runbook](EXPERIMENT_RUNBOOK.md): environment setup, offline reproduction and official driver.
- [Interface documentation](integration/ADOPTION.md): current installation and contract checks.
- [Historical integration notes](archive/docs/M1_STATUS_before_cleanup.md): earlier temporary wiring and adoption timeline.

The formal ON reference retains observed M4 evidence and M5 decisions, but exact ON review-memory IDs are unavailable. The earlier pilot has review traces at its own earlier revision. These two evidence sources are not interchangeable.
