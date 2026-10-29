# M3 runs on the frozen agent

All M3 runs on M1's frozen agent (tag `m1-freeze-20261025`), returned as
complete result folders in M1's reference-evidence layout. Two studies:

1. **Full-agent ablations (M3's assigned ablations):** M1's frozen `m1_full`
   with only planning, or only self-correction, switched off. These pair with
   M1's 18-run `m1_full` reference.
2. **Component study:** `m3_full` and its two ablations, with exploration and
   tool routing off throughout. These pair with `m3_full`, not `m1_full`.

| | |
| --- | --- |
| Runs | 5 methods × 6 dev systems × seeds 17, 29, 43 = 90 runs, all `attempt_01` |
| Failures | None; no attempt overwritten |
| Frozen version | Tag `m1-freeze-20261025`; working tree had no modified tracked files |
| Machine | Windows 11 PC, AMD Ryzen 7 9700X, CPU only, up to 3 runs at a time |
| Chemeleon weights | Official Figshare file 54966305, 548,874,535 bytes, SHA-256 `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e` (same archive as M1 and M2). Loaded by all 36 full-agent runs; the component study keeps tool routing off and never loads it. Run-machine record of the archive and its four files: [chemeleon_checksum_receipt.txt](chemeleon_checksum_receipt.txt) |

**Version note.** `m3_planning_off` and `m3_self_correction_off` were run when
the tag pointed to `02e0026`; the other methods after M1 moved it to
`ae7fe81`. The move adds reference evidence only: agent code, configuration,
protocol, dependencies and runner are identical between the two commits.

## What each method switches off

Checked from every run's `resolved_config.yaml`:

| Method | Planning | Memory | Self-correction | Exploration | Tool routing | Compare with |
| --- | --- | --- | --- | --- | --- | --- |
| `m1_full` (M1's reference) | on | on | on | on | on | – |
| `planning_off` | **off** | on | on | on | on | `m1_full` |
| `self_correction_off` | on | on | **off** | on | on | `m1_full` |
| `m3_full` | on | on | on | off | off | – |
| `m3_planning_off` | **off** | on | on | off | off | `m3_full` |
| `m3_self_correction_off` | on | on | **off** | off | off | `m3_full` |

## 1. Full-agent ablations (vs `m1_full`)

| Method | mSUN@20 | AUDC | Δ mSUN vs `m1_full` | `m1_full` better / same / worse | Sign test |
| --- | --- | --- | --- | --- | --- |
| `m1_full` (reference) | 10.00 | 88.1 | – | – | – |
| `planning_off` | 5.28 | 51.5 | −4.72 | 15 / 2 / 1 | p = 0.0005 |
| `self_correction_off` | 9.50 | 79.6 | −0.50 | 8 / 2 / 8 | p = 1.0 |

Means over 18 runs; Δ and the counts are paired by system and seed.

- **Planning** is the larger effect: without it the full agent finds about
  half as many stable, unique, novel structures, and it is lower on all six
  systems (per-system means, `m1_full` → `planning_off`: Au-K-Tb 13.0 → 3.7,
  Co-Dy-W 7.3 → 3.7, Co-Mg-Na 9.0 → 3.7, Ga-Pt-Tm 10.3 → 7.3, Hf-Ni-Zr
  9.3 → 6.7, Mg-Sn-Sr 11.0 → 6.7).
- **Self-correction** shows no measurable effect inside the full agent. Its
  one consistent difference is Co-Mg-Na (9.0 with it, 5.7 without), the same
  system where it helped most in the component study.

## 2. Component study (vs `m3_full`)

| Method | mSUN@20 | AUDC |
| --- | --- | --- |
| `m3_full` | 6.50 | 62.8 |
| `m3_planning_off` | 5.11 | 49.2 |
| `m3_self_correction_off` | 5.83 | 58.3 |

All 54 runs reproduce the pre-freeze runs exactly, run by run (mSUN and AUDC).
Paired with `m3_full`, planning adds +1.39 and self-correction +0.67. Full
analysis: [../../report/M3_RESULTS.md](../../report/M3_RESULTS.md).

## Folder layout

```
protocol_v1/<method>/dev/<system>/seed_<seed>/attempt_01/
```

Each `attempt_01` folder holds the same files as M1's frozen reference runs:

| File | What it is |
| --- | --- |
| `run_metadata.json` | Status, settings, cost and input hashes |
| `trajectories/episode_000.json` | Full 20-query trajectory |
| `summary/` | Official metrics and plots |
| `hydra/` | Original Hydra configuration and overrides |
| `resolved_config.yaml` | Fully resolved configuration |
| `m4_evidence.jsonl` | M4 memory component log |
| `m5_decisions.jsonl` | M5 exploration log (full-agent ablations only; exploration is off in the component study) |
| `run_benchmark.log` | MADE's log (empty: MADE's runner resets logging) |
| `run_console.log` | Full console output, including `M3 review:` and `M3 re-plan:` lines |
| `m2_metrics_history.json` | Per-query mSUN and AUDC, rebuilt from the trajectory with M1's `curve_from_trajectory` and checked against the final metrics |
| `evidence_manifest.json` | SHA-256 and size of every added file |

Each method folder also keeps its sweep console log under `dev/`.

## Checks

- `M2/evaluate.py` validates all 90 runs with no issues; each method is
  complete (18 of 18).
- The Chemeleon archive and its four checkpoint files were re-hashed on the
  run machine and match ([receipt](chemeleon_checksum_receipt.txt)).
- Every per-query curve matches its run's final mSUN and AUDC.
- The Materials Project API key appears in none of the files.

## How they were run

From `M1/MADE` on the frozen tag, with M4 installed:

```bash
uv run python ../../M3/run_ablations.py --methods planning_off self_correction_off --no-baseline --jobs 3
uv run python ../../M3/run_ablations.py --methods m3_planning_off m3_self_correction_off --no-baseline --jobs 3
uv run python ../../M3/run_ablations.py --methods m3_full --no-baseline --jobs 3
```

`run_ablations.py` calls `M1/run_experiment.py` once per run with an explicit
`--attempt` and a unique `M4_RUN_ID`. The first `planning_off` run
(Mg-Sn-Sr, seed 17) was a single pilot made with the same command before the
sweep.
