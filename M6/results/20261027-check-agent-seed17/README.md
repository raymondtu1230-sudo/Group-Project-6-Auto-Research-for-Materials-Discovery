# Frozen agent vs Random on the public check set (seed 17)

Run by M6 on 27 Oct 2026, scored with the unchanged `M2/evaluate.py --split check`.
This is the **public check set, not the course hidden test** (none was released).

## What was run

| Method | Units | Source | Notes |
| --- | --- | --- | --- |
| `m1_full` (frozen agent) | 4: Ga-Ho-Lu, Al-Li-V, Al-V-Zn, Co-Pd-Tl × seed 17 | this folder | Tag `m1-freeze-20261025` (`ae7fe81`), run from a separate worktree at the tag |
| `random_generator_baseline` | 12 (seeds 17/29/43) | `../20261020-check-random/` | Copied in for scoring; seed 17 is the paired comparison |
| `chemeleon_generative_baseline` | 0 | – | Not run: ~2.5 h per unit on this laptop (see below) |

**One seed (17) on held-out systems** for the agent, decided before the runs because of
compute, as the protocol's fallback allows (`M6/PROTOCOL_ADOPTION.md` §6). The
generalization comparison uses seed 17 on the dev side too
(`../20261027-generalization-seed17/`).

Machine: MacBook Air, Apple Silicon, CPU only. Same protocol v1 settings as dev;
the evaluator accepted all runs with matching protocol and reference snapshots.

## Results (mSUN@20 / AUDC, seed 17)

| System | Agent | Random | AF vs Random | EF vs Random |
| --- | --- | --- | --- | --- |
| Ga-Ho-Lu | 8 / 78.0 | 8 / 71.0 | 1.12 | 1.00 |
| Al-Li-V | 13 / 112.5 | 1 / 8.5 | 3.00 | 13.0 |
| Al-V-Zn | 19 / 180.5 | 13 / 128.5 | 1.29 | 1.46 |
| Co-Pd-Tl | 16 / 154.0 | 3 / 35.5 | 4.75 | 5.33 |
| **Mean** | **14.0 / 131.3** | **6.25 / 60.9** | 2.54 | – |

Dev, seed 17, same methods: agent 9.0, Random 3.33. The agent's lead over Random
grows from +5.7 (dev) to +7.8 (check); both methods score higher on the check
systems, so margins are the meaningful comparison.

## How the runs were made

- Launcher (local helper): `M2/run_baselines.py --method m1_full --split check …`,
  with `PYTHONPATH=M4/src` (how M2's frozen runs load `m4_memory`), staggered starts.
- M2's wrapper cannot resolve the frozen config's `${hydra:runtime.output_dir}`
  interpolation, so it exits with code 1 **after** the run has completed and the live
  per-query history is saved. `M6/package_check_evidence.py` then adds the Hydra
  configs, `resolved_config.yaml`, the M4/M5 component logs and an
  `evidence_manifest.json` to each completed attempt, using M1's resolver. The live
  history is not changed.
- OMP threads: Ga-Ho-Lu ran with 3 (alongside Chemeleon), the other three with 8.

## Failed and stopped attempts (kept, not counted)

| Attempt | What happened |
| --- | --- |
| `m1_full` Ga-Ho-Lu/17 attempt_01, Ga-Ho-Lu/29 attempt_01 | `m4_memory` not importable (first launch without `M4/src` on the path); stopped within a minute. Seed 29 is therefore listed as an invalid run in `validation.json`; it is not part of the seed-17 comparison. |
| `chemeleon_generative_baseline` Ga-Ho-Lu/17, Al-V-Zn/17 attempt_01 | Two runs started in the same second shared one Hydra folder and corrupted its `config.yaml`; stopped. The folder is preserved under `results/_m6_failed_attempts/`. |
| `chemeleon_generative_baseline` Ga-Ho-Lu/17, Al-V-Zn/17 attempt_02 | Stopped after ~11 min (batch 1 of 4) when held-out Chemeleon was dropped for compute. |

## Files

- `per_run.csv`, `per_system_summary.csv`, `per_method_summary.csv`, `validation.json`,
  `discovery_curves.*`: `M2/evaluate.py` output for the combined check results.
- `raw_artifact.zip`: all m1_full and Chemeleon check attempts (completed, failed and
  stopped), the preserved corrupted Hydra folder and the Hydra run folders, 216 files.
  SHA256 `c25d47ac57e550e52d77c15e6869a19534e36927b66d9594d3002893e5d13945`.
  The Materials Project key does not appear in it (checked before publishing).
