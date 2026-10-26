# M2 material for M6, 25 October 2026

The current scientific contribution covers 36 original dev baselines and 18 frozen routing-off episodes, compared with M1's 18-unit Full reference. All four methods use the six dev systems and seeds 17/29/43, B=20 and one episode per system/seed.

| Method | Units | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | --- | --- | --- |
| Random baseline | 18 | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon baseline | 18 | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen M1 Full | 18 | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Tool routing off | 18 | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |

Means and sample SDs are across the three seed means, each weighting the six systems equally. Routing off minus Full is −2.2778 mSUN and −17.9722 AUDC. These are development-set results, with variation across systems and seeds.

Current result sources are in [verification/preserved-40204426478/report](../verification/preserved-40204426478/report/). Use its `endpoint_comparison/` for original final metrics and costs, `baseline_compatibility/` for the old 36-unit reuse proof, and `recorded_curve_analysis/` for separately labelled offline curves and official paired AF/EF.

The curve analysis uses actual recorded structures and energies. It passed 720 original baseline prefix checks and all 72 original endpoints, with no scientific rerun. The original unsuccessful post-exit checkpoint collection records remain unchanged. The 54 raw hidden `.hydra` attachments omitted by transport remain explicitly missing. Visible resolved configurations and component evidence are checked separately.

Current [four-slide English source](M2_Frozen_Routing_Slide_Content_20261025.md) and [speaking text](M2_SPEAKER_NOTES_20261025.md) are ready. The native PPTX has not been refreshed or visually checked; this remains part of the 27 October handoff. The existing [21 October four-slide deck](M2_Method_and_Dev_Baselines_20261021_36of36.pptx) and [21 October notes](M2_SPEAKER_NOTES.md) are historical baseline-stage drafts.

Known USD 0 model fees exclude hardware, electricity and unpriced failures. Keep machine labels and elapsed times. Different machines do not support a controlled speed comparison. AF/EF are official discovery metrics, with their original zero/cap rules.

Machine-readable current data: [frozen_results_data_20261025.json](frozen_results_data_20261025.json).

M6 owns the final group deck. M2 still collects the other members' final results for the 27 October group scoreboard. See [stage acceptance](../STAGE_ACCEPTANCE_20261025.md).
