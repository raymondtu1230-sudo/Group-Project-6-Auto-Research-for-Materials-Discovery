# Generalization: development vs held-out

Held-out split: **public check set (not the course hidden test)**. Headline values use M2's aggregation (equal-weight system mean per seed, then mean ± sample SD across seeds) and appear only when the split is complete for that method. `n/a` means incomplete; partial means are over available runs only and are not comparable. Gap = held-out − dev.

| Method | Metric | Dev | Held-out | Gap | Relative gap |
| --- | --- | --- | --- | --- | --- |
| Agent (m1_full) | mSUN@B | 9 | 14 | 5 | 55.6 % |
| Agent (m1_full) | AUDC | 77.333 | 131.25 | 53.917 | 69.7 % |
| Agent (m1_full) | AF vs Random | 1.494 | 2.538 | 1.045 | 69.9 % |
| Agent (m1_full) | EF vs Random | 18.963 | 5.199 | -13.765 | -72.6 % |
| Agent (m1_full) | AF vs Chemeleon | 1.013 | n/a (4/4 runs) | n/a | n/a |
| Agent (m1_full) | EF vs Chemeleon | 2.347 | n/a (4/4 runs) | n/a | n/a |
| Random | mSUN@B | 3.333 | 6.25 | 2.917 | 87.5 % |
| Random | AUDC | 34.833 | 60.875 | 26.042 | 74.8 % |
| Random | AF vs Random | 1 | 1 | 0 | 0.0 % |
| Random | EF vs Random | 0.833 | 1 | 0.167 | 20.0 % |
| Random | AF vs Chemeleon | 0.186 | n/a (12/4 runs) | n/a | n/a |
| Random | EF vs Chemeleon | 0.537 | n/a (12/4 runs) | n/a | n/a |
| Chemeleon | mSUN@B | 6.667 | missing (0/4 runs) | n/a | n/a |
| Chemeleon | AUDC | 69 | missing (0/4 runs) | n/a | n/a |
| Chemeleon | AF vs Random | 1.351 | missing (0/4 runs) | n/a | n/a |
| Chemeleon | EF vs Random | 18.47 | missing (0/4 runs) | n/a | n/a |
| Chemeleon | AF vs Chemeleon | 1 | missing (0/4 runs) | n/a | n/a |
| Chemeleon | EF vs Chemeleon | 1 | missing (0/4 runs) | n/a | n/a |

## Per system (mSUN@B and AUDC; seed values in brackets)

| Method | Split | System | Seeds present | mSUN@B | AUDC |
| --- | --- | --- | --- | --- | --- |
| Agent (m1_full) | dev | Mg-Sn-Sr | 17 of 17 | 12 [12] | 105 [105] |
| Agent (m1_full) | dev | Au-K-Tb | 17 of 17 | 10 [10] | 72 [72] |
| Agent (m1_full) | dev | Co-Mg-Na | 17 of 17 | 4 [4] | 18 [18] |
| Agent (m1_full) | dev | Hf-Ni-Zr | 17 of 17 | 12 [12] | 128 [128] |
| Agent (m1_full) | dev | Co-Dy-W | 17 of 17 | 6 [6] | 48 [48] |
| Agent (m1_full) | dev | Ga-Pt-Tm | 17 of 17 | 10 [10] | 93 [93] |
| Random | dev | Mg-Sn-Sr | 17 of 17 | 7 [7] | 55.5 [55.5] |
| Random | dev | Au-K-Tb | 17 of 17 | 3 [3] | 21.5 [21.5] |
| Random | dev | Co-Mg-Na | 17 of 17 | 3 [3] | 44.5 [44.5] |
| Random | dev | Hf-Ni-Zr | 17 of 17 | 5 [5] | 60.5 [60.5] |
| Random | dev | Co-Dy-W | 17 of 17 | 0 [0] | 0 [0] |
| Random | dev | Ga-Pt-Tm | 17 of 17 | 2 [2] | 27 [27] |
| Chemeleon | dev | Mg-Sn-Sr | 17 of 17 | 16 [16] | 161 [161] |
| Chemeleon | dev | Au-K-Tb | 17 of 17 | 3 [3] | 33.5 [33.5] |
| Chemeleon | dev | Co-Mg-Na | 17 of 17 | 4 [4] | 45 [45] |
| Chemeleon | dev | Hf-Ni-Zr | 17 of 17 | 6 [6] | 60 [60] |
| Chemeleon | dev | Co-Dy-W | 17 of 17 | 1 [1] | 19.5 [19.5] |
| Chemeleon | dev | Ga-Pt-Tm | 17 of 17 | 10 [10] | 95 [95] |
| Agent (m1_full) | check | Ga-Ho-Lu | 17 of 17 | 8 [8] | 78 [78] |
| Agent (m1_full) | check | Al-Li-V | 17 of 17 | 13 [13] | 112.5 [112.5] |
| Agent (m1_full) | check | Al-V-Zn | 17 of 17 | 19 [19] | 180.5 [180.5] |
| Agent (m1_full) | check | Co-Pd-Tl | 17 of 17 | 16 [16] | 154 [154] |
| Random | check | Ga-Ho-Lu | 17 of 17 | 8 [8] | 71 [71] |
| Random | check | Al-Li-V | 17 of 17 | 1 [1] | 8.5 [8.5] |
| Random | check | Al-V-Zn | 17 of 17 | 13 [13] | 128.5 [128.5] |
| Random | check | Co-Pd-Tl | 17 of 17 | 3 [3] | 35.5 [35.5] |
| Chemeleon | check | Ga-Ho-Lu | none of 17 | missing | missing |
| Chemeleon | check | Al-Li-V | none of 17 | missing | missing |
| Chemeleon | check | Al-V-Zn | none of 17 | missing | missing |
| Chemeleon | check | Co-Pd-Tl | none of 17 | missing | missing |

Zero-baseline pairs (the baseline found nothing; MADE's official convention sets the factor, see `comparison_*` in M2's per_run.csv): Agent (m1_full) AF vs Random (dev 1, held-out 0); Agent (m1_full) EF vs Random (dev 1, held-out 0); Random AF vs Random (dev 1, held-out 0); Random EF vs Random (dev 1, held-out 0); Chemeleon AF vs Random (dev 1, held-out 0); Chemeleon EF vs Random (dev 1, held-out 0).

Missing units: 4 (see `missing_units.csv`).
WARNING: agent runs from several revisions: {'m1_full': ['ae7fe81991c56dd2d77685220b74ddbef11039c7', 'bffda0c9a1fa1904b35c0ef67b455881c975df86']}
