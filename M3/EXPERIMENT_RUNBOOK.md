# M3 experiment runbook (26–27 Oct)

Runs M3's two ablations against M1's reference on your own laptop.

## 1. One-time setup

```bash
cd M1/MADE
uv sync --locked
cp .env.example .env          # then edit .env: MATERIALS_PROJECT_API_KEY=<your key>
```

Get the key from your Materials Project dashboard (materialsproject.org, API
section). Never commit `.env` or paste the key into chat or logs.

Check the code before spending compute:

```bash
uv run python ../../M3/install.py --install            # put M3 into this M1 checkout
uv run python ../../M3/install.py                      # all lines should say "ok"
uv run pytest -q tests/test_m1_integrated.py tests/test_m3_planning.py
uv run pytest -q ../../M3/tests -o addopts=''
```

## 2. Pilot (one run, ~3–5 min)

```bash
uv run python ../run_experiment.py --method m3_full --split dev --system Mg-Sn-Sr --seed 17
```

Output: `results/protocol_v1/m3_full/dev/Mg-Sn-Sr/seed_17/attempt_01/`. It
contains:

- `trajectories/episode_000.json`, with per-query metrics;
- a phase-diagram plot;
- `summary/summary.json`;
- `run_metadata.json`, with status and cost.

`M3 review:` and `M3 re-plan:` lines appear in the console. MADE's runner
resets logging, so its `run_benchmark.log` stays empty. `run_ablations.py`
therefore saves each run's console as `console_attempt_XX.log` beside the
attempt folder.

Check that `run_metadata.json` says `"status": "completed"` and 20 queries.

This pilot creates `attempt_01`, which `run_ablations.py` then counts as
completed. To keep its M3 log lines for the summary, run the pilot through the
script instead:

```bash
uv run python ../../M3/run_ablations.py --methods m3_full --systems Mg-Sn-Sr --seeds 17
```

## 3. All ablations

```bash
uv run python ../../M3/run_ablations.py --dry-run   # lists what will run
uv run python ../../M3/run_ablations.py
```

This runs:

- **Methods:** `m3_full`, `m3_planning_off` and `m3_self_correction_off`.
- **Systems:** the six dev systems.
- **Seeds:** 17, 29 and 43.

That is 54 one-episode runs, a few hours on CPU (M1's baseline runs took
140–300 s each).

The script is safe to stop and restart. Completed runs are skipped. A failed
run is retried under the next attempt number, and the failure stays on disk.

M1's 18 `m1_baseline` runs are the reference. If their result folders are not
on your laptop, the summary uses `M1/m1_baseline_dev_summary.csv`. To recompute
the baseline locally, add `--with-baseline`.

## 4. Summarize and hand off

```bash
uv run python ../../M3/summarize_ablations.py
```

This writes:

- `M3/results/m3_ablation_runs.csv` (per run);
- `M3/results/m3_ablation_summary.csv` (per method);
- `M3/report/M3_RESULTS.md`: tables plus generated "what changed" sentences.

Edit the "Why" section by hand.

Send to M2 by 27 Oct: the two CSVs and `M3_RESULTS.md`. Send to M6 by 27 Oct:
`M3_RESULTS.md` and the updated slides.

## Fairness checklist

- Same systems, seeds, budget, oracle and protocol version for every method.
- Do not tune M3 settings on the check split; the ablations use dev only.
- Report every run, including failed attempts and neutral or negative
  differences.
