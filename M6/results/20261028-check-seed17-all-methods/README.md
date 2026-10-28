# Held-out check set, seed 17: frozen agent vs Chemeleon vs Random

Scored by M6 on 28 Oct 2026 with the unchanged `M2/evaluate.py --split check`. This is
the **public check set, not the course hidden test** (none was released). This folder
supersedes `../20261027-check-agent-seed17/` for the held-out comparison; that folder
keeps the agent's raw runs.

One seed (17) per method on held-out systems, the protocol's 1-seed fallback
(`M6/PROTOCOL_ADOPTION.md` §6), decided before the runs because of compute.

## Results (mSUN@20 / AUDC)

| System | Frozen agent | Chemeleon | Random |
| --- | --- | --- | --- |
| Ga-Ho-Lu | 8 / 78.0 | 10 / 79.0 | 8 / 71.0 |
| Al-Li-V | 13 / 112.5 | 3 / 35.5 | 1 / 8.5 |
| Al-V-Zn | 19 / 180.5 | 10 / 85.0 | 13 / 128.5 |
| Co-Pd-Tl | 16 / 154.0 | 6 / 76.0 | 3 / 35.5 |
| **Mean** | **14.00 / 131.3** | **7.25 / 68.9** | **6.25 / 60.9** |

Dev, seed 17, same methods: agent 9.00, Chemeleon 6.67, Random 3.33 mSUN@20.
The agent's lead over Chemeleon grows from +2.3 (dev) to +6.8 (check); over Random
from +5.7 to +7.8. See `../20261028-generalization-seed17-all-methods/`.

## Runs

| Method | Source | Runs |
| --- | --- | --- |
| `m1_full` | `../20261027-check-agent-seed17/raw_artifact.zip` | 4, tag `m1-freeze-20261025` |
| `chemeleon_generative_baseline` | `raw_artifact_chemeleon.zip` (this folder) | 4, run 28 Oct 03:04–06:28 UTC, 4 in parallel with staggered starts, OMP 2 threads each, ~3.4 h per run |
| `random_generator_baseline` | `../20261020-check-random/raw_artifact.zip` | 12 (seed 17 is the paired one) |

Machine: MacBook Air, Apple Silicon, CPU only; same protocol v1 settings as dev.

## Kept, not counted

- Chemeleon Ga-Ho-Lu/17 and Al-V-Zn/17 attempts 01 (Hydra folder collision) and 02
  (stopped on 27 Oct when held-out Chemeleon was postponed). Their files are in the
  27 Oct raw ZIP; the new successful runs are attempt 03 for these two systems.
- `m1_full` Ga-Ho-Lu/29 attempt 01 (import failure), listed as invalid in `validation.json`.

## Files

- `per_run.csv`, `per_system_summary.csv`, `per_method_summary.csv`, `validation.json`,
  `discovery_curves.*`: evaluator output for all check runs (agent, Chemeleon, Random).
- `raw_artifact_chemeleon.zip`: all Chemeleon check attempt directories and the 28 Oct
  Hydra run folders, 141 files. SHA256
  `29e3865c90d36fc0b2e999b0b06cd3aa61e295f179f302da18040a8840173a35`. Contains no API key
  (checked).
