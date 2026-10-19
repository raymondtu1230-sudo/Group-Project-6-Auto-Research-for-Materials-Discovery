# Results intake for M2

M2 receives results for the final scoreboard. Each member keeps ownership of their code and experiments. This note defines what M2 needs to validate, without changing their directories or starting their work.

For each method/system/seed, provide:

- the owning folder or immutable archive link, method, split, system, seed and attempt;
- run_metadata.json with protocol, source revision, dependencies, machine and cost fields;
- resolved_config.yaml and the original trajectory, official summary and structures;
- complete per-query history at the agreed budget, including failed attempts and reasons;
- a checksum manifest and exact command;
- the frozen full-system reference revision and the single changed switch for final component ablations.

Keep dev, public check and course hidden results separate. Check and hidden evaluation belongs to M6. A component-versus-m1_baseline study is labelled separately from a frozen-m1_full component ablation. Synthetic smoke and unit-test fixtures are not scientific results.

M2 checks completeness, budget/query counts, protocol and reference consistency before scoring with the official metrics. Missing or incompatible results remain explicit. M2 does not fill missing member results, alter their experiments or describe unconfirmed delivery as received.

By27 Oct, the validated team table, curves, costs and result text go to M6. Shared system integration and freeze remain with M1.
