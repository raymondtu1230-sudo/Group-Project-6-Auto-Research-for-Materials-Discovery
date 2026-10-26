# M4 report handoff

Updated 26 October 2026. Final frozen-agent dev ablation results are in [M4_FROZEN_MEMORY_RESULTS.md](M4_FROZEN_MEMORY_RESULTS.md), with raw results and validation in [the evidence folder](../evidence/frozen-memory-ablation-20261026/). Use these results for the frozen component-ablation table.

The presentation deck below remains the earlier development-pilot draft; its single-pair numbers must not be labelled as the final ablation.

# Draft handoff for M6

Updated 21 October 2026. These English materials are ready for report and slide assembly as a draft. They do not represent the final frozen-agent ablation.

| File | Use |
| --- | --- |
| M4_METHOD.md | Report method, implementation boundaries and current dev evidence |
| M4_Method_Draft.pptx | Two editable slides with embedded speaker notes |
| M4_SPEAKER_NOTES.md | Spoken text and sources, approximately 90 seconds total |
| M4_DEV_PILOT_RESULTS.md | Detailed negative development result and evidence locations |

M1 has adopted M4 memory and capture, and M3 consumption has been verified. The Mg-Sn-Sr/seed17 development pair gave ON mSUN@20=7/AUDC=68.5 and OFF 8/76.0. Both arms used M3 planning/reflection, Random generation and capture, with exploration/routing OFF. All 20 observations per arm are preserved under ../evidence/dev-pilot-20261021/. A single pair does not establish an aggregate Memory effect.

The capture scope covers generator/filter events, including the all-filtered fallback distinction. It does not cover oracle exceptions. The shown phase diagram comes from the ON development run. Final frozen-full-agent results, representative cases and conclusions will update this draft after the controlled experiments. M6 can adapt these two slides to the group template and confirm receipt separately.
