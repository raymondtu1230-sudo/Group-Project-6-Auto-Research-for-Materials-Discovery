# Generalization: development vs held-out

Held-out split: **public check set (not the course hidden test)**. Headline values use M2's aggregation (equal-weight system mean per seed, then mean ± sample SD across seeds) and appear only when the split is complete for that method. `n/a` means incomplete; partial means are over available runs only and are not comparable. Gap = held-out − dev.

| Method | Metric | Dev | Held-out | Gap | Relative gap |
| --- | --- | --- | --- | --- | --- |
| Random | mSUN@B | 4.056 ± 0.631 | 5.583 ± 0.629 | 1.528 | 37.7 % |
| Random | AUDC | 40.583 ± 9.459 | 60.792 ± 0.505 | 20.208 | 49.8 % |
| Random | AF vs Random | 1 ± 0 | 1 ± 0 | 0 | 0.0 % |
| Random | EF vs Random | 0.944 ± 0.096 | 1 ± 0 | 0.056 | 5.9 % |
| Random | AF vs Chemeleon | n/a (18/18 runs; partial mean 0) | n/a (12/12 runs) | n/a | n/a |
| Random | EF vs Chemeleon | n/a (18/18 runs; partial mean 0.438) | n/a (12/12 runs) | n/a | n/a |
| Chemeleon | mSUN@B | n/a (1/18 runs; partial mean 16) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AUDC | n/a (1/18 runs; partial mean 161) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AF vs Random | n/a (1/18 runs; partial mean 2.375) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | EF vs Random | n/a (1/18 runs; partial mean 2.286) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AF vs Chemeleon | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | EF vs Chemeleon | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | mSUN@B | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AUDC | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AF vs Random | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | EF vs Random | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AF vs Chemeleon | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | EF vs Chemeleon | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |

## Per system (mSUN@B and AUDC; seed values in brackets)

| Method | Split | System | Seeds present | mSUN@B | AUDC |
| --- | --- | --- | --- | --- | --- |
| Random | dev | Mg-Sn-Sr | 17 29 43 of 17 29 43 | 9.333 ± 2.517 [7 9 12] | 88.333 ± 32.75 [55.5 88.5 121] |
| Random | dev | Au-K-Tb | 17 29 43 of 17 29 43 | 2.333 ± 0.577 [3 2 2] | 18.5 ± 4.77 [21.5 13 21] |
| Random | dev | Co-Mg-Na | 17 29 43 of 17 29 43 | 2.333 ± 1.155 [3 1 3] | 34.833 ± 14.224 [44.5 18.5 41.5] |
| Random | dev | Hf-Ni-Zr | 17 29 43 of 17 29 43 | 6.333 ± 1.528 [5 8 6] | 64.167 ± 15.332 [60.5 51 81] |
| Random | dev | Co-Dy-W | 17 29 43 of 17 29 43 | 1 ± 1 [0 2 1] | 6.167 ± 6.825 [0 5 13.5] |
| Random | dev | Ga-Pt-Tm | 17 29 43 of 17 29 43 | 3 ± 1.732 [2 5 2] | 31.5 ± 4.77 [27 36.5 31] |
| Chemeleon | dev | Mg-Sn-Sr | 17 of 17 29 43 | 16 [16] | 161 [161] |
| Chemeleon | dev | Au-K-Tb | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Co-Mg-Na | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Hf-Ni-Zr | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Co-Dy-W | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Ga-Pt-Tm | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Mg-Sn-Sr | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Au-K-Tb | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Co-Mg-Na | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Hf-Ni-Zr | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Co-Dy-W | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Ga-Pt-Tm | none of 17 29 43 | missing | missing |
| Random | check | Ga-Ho-Lu | 17 29 43 of 17 29 43 | 7.333 ± 2.082 [8 9 5] | 71 ± 14.5 [71 85.5 56.5] |
| Random | check | Al-Li-V | 17 29 43 of 17 29 43 | 2.333 ± 1.155 [1 3 3] | 27.167 ± 17.243 [8.5 30.5 42.5] |
| Random | check | Al-V-Zn | 17 29 43 of 17 29 43 | 10 ± 2.646 [13 8 9] | 106.667 ± 19.496 [128.5 91 100.5] |
| Random | check | Co-Pd-Tl | 17 29 43 of 17 29 43 | 2.667 ± 0.577 [3 2 3] | 38.333 ± 3.014 [35.5 38 41.5] |
| Chemeleon | check | Ga-Ho-Lu | none of 17 29 43 | missing | missing |
| Chemeleon | check | Al-Li-V | none of 17 29 43 | missing | missing |
| Chemeleon | check | Al-V-Zn | none of 17 29 43 | missing | missing |
| Chemeleon | check | Co-Pd-Tl | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Ga-Ho-Lu | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Al-Li-V | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Al-V-Zn | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Co-Pd-Tl | none of 17 29 43 | missing | missing |

Zero-baseline pairs (the baseline found nothing; MADE's official convention sets the factor, see `comparison_*` in M2's per_run.csv): Random AF vs Random (dev 1, held-out 0); Random EF vs Random (dev 1, held-out 0).

Missing units: 59 (see `missing_units.csv`).
