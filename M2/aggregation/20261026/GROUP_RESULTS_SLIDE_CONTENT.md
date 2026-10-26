# Shared result slides for M6 — editable text

These are assembly-ready slide sources. This update does not claim that a new PPTX was exported or visually reviewed. M3 and M4's own decks remain in their report folders.

## Slide 1 — Frozen Full, baselines and one-switch ablations

**Setting:** 6 dev systems × 3 seeds; B=20; CPU ORB v3 conservative. Mean ± SD across three seed means, each equally averaging six systems.

| Method | mSUN@20 | AUDC |
| --- | ---: | ---: |
| Random | 4.06 ± 0.63 | 40.58 ± 9.46 |
| Chemeleon | 6.94 ± 1.11 | 71.31 ± 9.50 |
| Full | 10.00 ± 0.88 | 88.11 ± 9.45 |
| Routing OFF | 7.72 ± 1.18 | 70.14 ± 1.61 |
| Memory OFF | 9.11 ± 1.35 | 86.94 ± 9.03 |

**Interpretation:** Full has the highest aggregate mSUN and AUDC here. Memory effects are mixed across pairs; the aggregate difference is small. Development results do not establish significance or held-out generalization.

**Figure:** `results/discovery_curves_by_study.svg`, left panel. Its bands are sample SD across the three seed means. Curve provenance is documented in the handoff.

**Speaker text:** We compare every method on the same six development systems, three seeds and twenty-query budget. The Full reference reaches ten novel stable discoveries on average. Turning routing off reduces this to 7.72; turning memory off gives 9.11. The memory comparison is mixed across systems and seeds, so we interpret the positive aggregate difference cautiously. These are development results, not a claim of statistical significance or hidden-set performance.

## Slide 2 — M3 component study and evidence scope

**Shared setting:** exploration OFF and tool routing OFF in all three M3 profiles.

| M3 profile | mSUN@20 | AUDC | Evidence scope |
| --- | ---: | ---: | --- |
| `m3_full` | 6.50 ± 1.30 | 62.75 ± 9.03 | Historical CSV; 18-run raw comparator package pending |
| Planning OFF | 5.11 ± 0.35 | 49.22 ± 4.51 | 18 complete frozen-source runs validated |
| Self-correction OFF | 5.83 ± 0.88 | 58.31 ± 7.78 | 18 complete frozen-source runs validated |

**Interpretation:** Pair the two OFF profiles with `m3_full`. Their differences from Full cannot isolate a single module because exploration and routing also differ. Reported component mSUN gains are +1.39 for planning and +0.67 for self-correction, pending independent validation of the full comparator package.

**Figure:** `results/discovery_curves_by_study.svg`, right panel. No `m3_full` curve is drawn because its complete raw histories were not received.

**Speaker text:** M3's runs use a separate component setting in which exploration and routing are both off. Their appropriate comparator is therefore m3 full, rather than the all-enabled Full agent. The two OFF arms are validated and appear in the shared baseline comparisons. The historical comparator reports 6.50 discoveries, but its complete eighteen-run package is still needed before we can independently validate the paired component gains. We keep this evidence separate from the Full single-switch ablation table.
