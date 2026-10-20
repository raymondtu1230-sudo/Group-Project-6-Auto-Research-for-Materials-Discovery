# Random baseline on the public check set (12/12 units)

Run by M6 on 20 Oct 2026, scored with the unchanged `M2/evaluate.py --split check`.
This is the **public check set, not the course hidden test**.

| Setting | Value |
| --- | --- |
| Method | `random_generator_baseline` (official MADE config) |
| Systems | Ga-Ho-Lu, Al-Li-V, Al-V-Zn, Co-Pd-Tl (`M1/protocol/check_systems.json`) |
| Seeds | 17, 29, 43; one episode per process |
| Budget | B = 20; every accepted unit used 20/20 queries |
| Protocol | M1 protocol v1 (ORB `orb-v3-conservative-inf-omat`, CPU) |
| Source revision | `22d0eeba26999ffa8949fe81e0310d4016dc6afa` |
| Machine | MacBook Air, Apple Silicon (arm64), macOS 26.6, CPU only |
| Command | `M6/run_check_baselines.sh --methods random_generator_baseline --execute` (wraps `M2/run_baselines.py` → `M1/run_experiment.py`) |

## Results

Method level (M2 aggregation: equal-weight system mean per seed, then mean ± sample SD over seeds):
**mSUN@20 = 5.583 ± 0.629, AUDC = 60.79 ± 0.51** (`per_method_summary.csv`).

| System | Seed values mSUN@20 | Mean mSUN@20 | Mean AUDC |
| --- | --- | --- | --- |
| Ga-Ho-Lu | 8, 9, 5 | 7.33 | 71.0 |
| Al-Li-V | 1, 3, 3 | 2.33 | 27.2 |
| Al-V-Zn | 13, 8, 9 | 10.00 | 106.7 |
| Co-Pd-Tl | 3, 2, 3 | 2.67 | 38.3 |

Wall time per unit: 147–263 s (median 203 s) on this laptop. Known model/API fees: USD 0.
Hardware and electricity are not measured.

AF/EF are blank here: they need a paired unit of the other baseline (Chemeleon) or the
agent on the same system and seed, and those check units do not exist yet.

Dev vs check comparison for Random: `../20261020-generalization-random/`
(dev 4.056 ± 0.631 → check 5.583 ± 0.629 mSUN@20, i.e. the check systems are easier for
Random by +1.53, +37.7 %).

## Failed attempts (kept, not counted)

`validation.json` lists them as `superseded_attempt`; each is inside `raw_artifact.zip`.

| Unit | Attempt | What happened |
| --- | --- | --- |
| Ga-Ho-Lu / 17 | 01 | ORB checkpoint download stalled at 56 MB for 20+ min (network). Stopped; no query had run. Checkpoint then downloaded separately (102 MB) and the unit rerun as attempt 02. |
| Co-Pd-Tl / 43 | 01, 02 | All 20 queries finished and the trajectory was written, but the run hung while the plotting library (kaleido) closed the headless browser it used for chart export (Brave, picked up from the system). The summary was never written, so the unit could not be accepted. Stopped both times. |
| Co-Pd-Tl / 43 | 03 | Accepted. Rerun with kaleido's own headless Chrome for Testing (`kaleido_get_chrome`, `BROWSER_PATH` set to it). Only chart rendering changed; the runner, oracle, evaluator and settings did not. |

## Files

- `per_run.csv`, `per_system_summary.csv`, `per_method_summary.csv`, `validation.json`,
  `discovery_curves.png/.svg`: output of `M2/evaluate.py`.
- `raw_artifact.zip`: all 15 attempt directories under
  `results/protocol_v1/random_generator_baseline/check/` (trajectories, resolved configs,
  metadata, per-query history, process logs), 267 files.
  SHA256 `6f38bdf6b30a1b47bc9d289dd44e1c4c385751c40a3867ad4b310ad8da7b4d4c`.
  The Materials Project key does not appear in any file (checked before publishing).

Reproduce the scoring (from `M1/MADE`, after unzipping into an empty folder `R`):

```bash
uv run python ../../M2/evaluate.py --results-root R/results/protocol_v1 --output NEW_DIR --split check --allow-partial
```
