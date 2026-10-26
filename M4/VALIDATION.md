# Current validation

Updated 26 October 2026.

## Interface and regression tests

All 72 relevant tests passed. The suite covers M1/M3/M4 boundaries, independent Memory switches, invalid observations, JSON bounds, checkpoint restoration, generator/filter capture isolation and pilot configuration isolation. Ruff passed for the changed reporting helper and test files. The final test-only repair supplies Hydra's output-directory context during configuration construction and restores the previous singleton afterwards. It changes no scientific code or Hydra configuration.

From the repository root, after installing M4 in the locked M1 environment:

```bash
M1/MADE/.venv/bin/python -m pytest -q -o addopts='' \
  M1/MADE/tests/test_m1_integrated.py \
  M1/MADE/tests/test_m3_planning.py \
  M1/MADE/tests/test_m4_memory.py \
  M4/tests M4/integration/test_joint_capture.py M4/integration/test_dev_pilot.py
```

This recorded count applies to the reviewed source. Future changes can change test counts. The complete scientific run evidence is separate from synthetic interface tests.

## Formal result validation

- 18 ON/OFF pairs, 36 accepted run directories, B=20 each.
- Paired protocol/material-reference snapshots match.
- All files listed in the 18 M1 reference evidence manifests pass size/SHA-256 checks.
- Offline analysis checks 720 query rows, 120 traced-case rows, 36 cost rows and all 36 published curve endpoints.
- [Validation record](evidence/frozen-memory-ablation-20261026/closeout_validation.json), [reference pairing](evidence/frozen-memory-ablation-20261026/reference_patch_validation.json) and [checksums](evidence/frozen-memory-ablation-20261026/checksums.json) preserve the evidence.

ON per-query histories have explicit trajectory-reconstruction provenance. Exact ON review-memory IDs and complete initialization/LLM cost accounting remain limitations. Individual M2 loader acceptance does not by itself establish the final group leaderboard against both required baselines.

## Historical checks

Earlier logs remain in [validation-history/](evidence/validation-history/). Their original 36/69 counts and deselections are preserved. [Earlier validation notes](archive/docs/VALIDATION_before_cleanup.md) explain schema revisions and temporary integration. Synthetic trajectories are labelled and are not real benchmark discoveries.
