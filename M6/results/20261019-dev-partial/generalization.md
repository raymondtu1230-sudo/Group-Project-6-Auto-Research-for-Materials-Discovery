# Generalization: development vs held-out

Held-out split: **public check set (not the course hidden test)**. Headline values use M2's aggregation (equal-weight system mean per seed, then mean ± sample SD across seeds) and appear only when the split is complete for that method. `n/a` means incomplete; partial means are over available runs only and are not comparable. Gap = held-out − dev.

| Method | Metric | Dev | Held-out | Gap | Relative gap |
| --- | --- | --- | --- | --- | --- |
| Agent (m1_full) | mSUN@B | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AUDC | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AF vs Random | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | EF vs Random | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | AF vs Chemeleon | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Agent (m1_full) | EF vs Chemeleon | missing (0/18 runs) | missing (0/12 runs) | n/a | n/a |
| Random | mSUN@B | n/a (1/18 runs; partial mean 7) | missing (0/12 runs) | n/a | n/a |
| Random | AUDC | n/a (1/18 runs; partial mean 55.5) | missing (0/12 runs) | n/a | n/a |
| Random | AF vs Random | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |
| Random | EF vs Random | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |
| Random | AF vs Chemeleon | n/a (1/18 runs; partial mean 0) | missing (0/12 runs) | n/a | n/a |
| Random | EF vs Chemeleon | n/a (1/18 runs; partial mean 0.438) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | mSUN@B | n/a (1/18 runs; partial mean 16) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AUDC | n/a (1/18 runs; partial mean 161) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AF vs Random | n/a (1/18 runs; partial mean 2.375) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | EF vs Random | n/a (1/18 runs; partial mean 2.286) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | AF vs Chemeleon | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |
| Chemeleon | EF vs Chemeleon | n/a (1/18 runs; partial mean 1) | missing (0/12 runs) | n/a | n/a |

## Per system (mSUN@B and AUDC; seed values in brackets)

| Method | Split | System | Seeds present | mSUN@B | AUDC |
| --- | --- | --- | --- | --- | --- |
| Agent (m1_full) | dev | Mg-Sn-Sr | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Au-K-Tb | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Co-Mg-Na | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Hf-Ni-Zr | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Co-Dy-W | none of 17 29 43 | missing | missing |
| Agent (m1_full) | dev | Ga-Pt-Tm | none of 17 29 43 | missing | missing |
| Random | dev | Mg-Sn-Sr | 17 of 17 29 43 | 7 [7] | 55.5 [55.5] |
| Random | dev | Au-K-Tb | none of 17 29 43 | missing | missing |
| Random | dev | Co-Mg-Na | none of 17 29 43 | missing | missing |
| Random | dev | Hf-Ni-Zr | none of 17 29 43 | missing | missing |
| Random | dev | Co-Dy-W | none of 17 29 43 | missing | missing |
| Random | dev | Ga-Pt-Tm | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Mg-Sn-Sr | 17 of 17 29 43 | 16 [16] | 161 [161] |
| Chemeleon | dev | Au-K-Tb | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Co-Mg-Na | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Hf-Ni-Zr | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Co-Dy-W | none of 17 29 43 | missing | missing |
| Chemeleon | dev | Ga-Pt-Tm | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Ga-Ho-Lu | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Al-Li-V | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Al-V-Zn | none of 17 29 43 | missing | missing |
| Agent (m1_full) | check | Co-Pd-Tl | none of 17 29 43 | missing | missing |
| Random | check | Ga-Ho-Lu | none of 17 29 43 | missing | missing |
| Random | check | Al-Li-V | none of 17 29 43 | missing | missing |
| Random | check | Al-V-Zn | none of 17 29 43 | missing | missing |
| Random | check | Co-Pd-Tl | none of 17 29 43 | missing | missing |
| Chemeleon | check | Ga-Ho-Lu | none of 17 29 43 | missing | missing |
| Chemeleon | check | Al-Li-V | none of 17 29 43 | missing | missing |
| Chemeleon | check | Al-V-Zn | none of 17 29 43 | missing | missing |
| Chemeleon | check | Co-Pd-Tl | none of 17 29 43 | missing | missing |

Missing units: 88 (see `missing_units.csv`).
