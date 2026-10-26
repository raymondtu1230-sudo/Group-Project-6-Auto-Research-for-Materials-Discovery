# M1 frozen reference evidence

This directory contains the 18 completed `m1_full` development units and two
preserved failed attempts from the frozen reference sweep.

Each mapped attempt now includes:

- `hydra/config.yaml`, `hydra/hydra.yaml`, and `hydra/overrides.yaml`: original
  Hydra artifacts from the timestamped runner directory;
- `resolved_config.yaml`: the same Hydra configuration with interpolations
  resolved against its original runtime directory;
- `m4_evidence.jsonl` and `m5_decisions.jsonl`, when emitted by the component;
- `run_benchmark.log`: the runner-created log file (empty for these runs because
  process output was captured by `reference-sweep-20261025-tmux.log`);
- `evidence_manifest.json`: source mapping, byte sizes, and SHA-256 hashes;
- `m2_metrics_history.json` for every completed unit.

The reference launcher did not retain the successful per-query checkpoint
histories. The two discovery curves required by M2 are therefore reconstructed
losslessly from each frozen trajectory's per-query `is_stable` and
`is_newly_discovered` observations. Every reconstructed history is labelled
`reconstructed_from_frozen_official_trajectory` and checked against the final
official mSUN and AUDC. M2's canonical evaluator accepted all 18 completed
units with no missing `m1_full` unit.

M4 evidence has 19 records per successful 20-query episode by design: the last
observation has no subsequent proposal at which online memory can be updated.
The official trajectory is the complete 20-query evidence. M5 emitted 20
decision records per successful episode. The frozen implementation did not
emit separate planner or router sidecar files; no such records are inferred or
fabricated. Proposal-event capture is sparse and appears only where the capture
wrapper recorded an exceptional event.

Run `M1/package_reference_evidence.py` from the repository root to verify and
recreate this mapping from the retained timestamped directories.
