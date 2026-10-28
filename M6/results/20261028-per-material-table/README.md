# Per-material results (M6 → M2)

mSUN@20 and AUDC per chemical system and method. Development: seeds 17/29/43 (values listed, mean shown). Public check set (not the course hidden test): seed 17 only.

| Split | System | Frozen agent mSUN (seeds) | Chemeleon mSUN (seeds) | Random mSUN (seeds) | Agent AUDC | Chemeleon AUDC | Random AUDC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | Au-K-Tb | 13 (10 14 15) | 4.67 (3 6 5) | 2.33 (3 2 2) | 106.5 | 47.67 | 18.5 |
| dev | Co-Dy-W | 7.33 (6 8 8) | 2 (1 2 3) | 1 (0 2 1) | 57.67 | 25.33 | 6.17 |
| dev | Co-Mg-Na | 9 (4 12 11) | 2.67 (4 2 2) | 2.33 (3 1 3) | 68.17 | 25.67 | 34.83 |
| dev | Ga-Pt-Tm | 10.33 (10 12 9) | 11.33 (10 14 10) | 3 (2 5 2) | 101.83 | 111.33 | 31.5 |
| dev | Hf-Ni-Zr | 9.33 (12 7 9) | 7.67 (6 12 5) | 6.33 (5 8 6) | 91.67 | 81.83 | 64.17 |
| dev | Mg-Sn-Sr | 11 (12 9 12) | 13.33 (16 13 11) | 9.33 (7 9 12) | 102.83 | 136 | 88.33 |
| check | Al-Li-V | 13 (13) | 3 (3) | 1 (1) | 112.5 | 35.5 | 8.5 |
| check | Al-V-Zn | 19 (19) | 10 (10) | 13 (13) | 180.5 | 85 | 128.5 |
| check | Co-Pd-Tl | 16 (16) | 6 (6) | 3 (3) | 154 | 76 | 35.5 |
| check | Ga-Ho-Lu | 8 (8) | 10 (10) | 8 (8) | 78 | 79 | 71 |

Sources: development, M2 aggregation `M2/aggregation/20261027_m3_full_agent/results/m2_evaluator/per_run.csv` (merged in PR #6); check, `M6/results/20261028-check-seed17-all-methods/per_run.csv`. All values from the unchanged `M2/evaluate.py`. Machine-readable copy: `per_material.csv`.
