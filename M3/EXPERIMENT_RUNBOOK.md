# M3 experiment runbook (26–27 Oct)

Runs M3's two ablations against M1's reference on your own laptop.

M1 integrated M3 on `main` on 20 Oct (`2fcc214`). M1 also made M4's memory
manager the default memory in `m1_integrated.yaml` (`9acd3c9`). Every run with
memory on, including `m1_baseline`, therefore needs the M4 package installed.

## 0. Fresh computer (fastest path)

Run **all 72** runs on one machine (baseline included), so every arm uses the
same hardware and code; no results need copying in. In PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex      # uv (once); git must be installed
git clone https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery.git
cd Group-Project-6-Auto-Research-for-Materials-Discovery\M1\MADE
uv sync --locked
uv pip install --no-deps -e ..\..\M4
uv run python ..\..\M3\install.py --install    # puts the fixed M3 module into M1 (local only)
copy .env.example .env                           # then put your Materials Project key in .env
uv run python ..\..\M3\run_ablations.py --dry-run --jobs 3   # should say 72 to run
uv run python ..\..\M3\run_ablations.py --jobs 3
```

`--jobs`: use about one run per 4–5 CPU cores (e.g. 3 on 16 threads, 5 on 24).
Keep the machine awake, plugged in and online. The first run also downloads the
~100 MB ORB model. When it finishes: `uv run python ..\..\M3\summarize_ablations.py`.

## 1. One-time setup

```bash
cd M1/MADE
uv sync --locked
uv pip install --no-deps -e ../../M4   # M4 memory manager (repeat after any uv sync)
cp .env.example .env                   # then edit .env: MATERIALS_PROJECT_API_KEY=<your key>
```

Get the key from your Materials Project dashboard (materialsproject.org, API
section). Never commit `.env` or paste the key into chat or logs.

Check the code before spending compute:

```bash
uv run python ../../M3/install.py   # each line "ok" or "merged"
PYTHONPATH="../../M4/src" uv run pytest -q tests/test_m1_integrated.py tests/test_m3_planning.py
uv run pytest -q ../../M3/tests -o addopts=''
```

`install.py` shows `merged` for `m1_integrated.yaml`. That means M1 merged
M4's and M5's settings into the file and kept M3's lines, which is expected.

## 2. Pilot (one run, ~3–5 min)

```bash
uv run python ../../M3/run_ablations.py --methods m3_full --systems Mg-Sn-Sr --seeds 17 --no-baseline
```

Output: `results/protocol_v1/m3_full/dev/Mg-Sn-Sr/seed_17/attempt_01/`. It
contains:

- `trajectories/episode_000.json`, with per-query metrics;
- a phase-diagram plot;
- `summary/summary.json`;
- `run_metadata.json`, with status and cost;
- M4's `m4_evidence.jsonl`.

The console, with the `M3 review:` and `M3 re-plan:` lines, is saved beside it
as `console_attempt_01.log`. MADE's runner resets logging, so its
`run_benchmark.log` stays empty. Check that `run_metadata.json` says
`"status": "completed"` and 20 queries.

Use the script rather than calling `run_experiment.py` directly. The script
saves the console and gives each run its own `M4_RUN_ID`, which M4 requires.

## 3. All runs

```bash
uv run python ../../M3/run_ablations.py --dry-run   # lists what will run
uv run python ../../M3/run_ablations.py
```

This runs:

- **Methods:** `m1_baseline`, `m3_full`, `m3_planning_off` and
  `m3_self_correction_off`.
- **Systems:** the six dev systems.
- **Seeds:** 17, 29 and 43.

That is 72 one-episode runs, several hours on CPU (M1's baseline runs took
140–300 s each).

`m1_baseline` is re-run because M1's 18 recorded runs (19 Oct) were made
before M4's memory became the default. Pairing M3 against them would mix M3's
effect with the memory change. The recorded runs still appear in the summary
as `m1_baseline_recorded`, for context only. `--no-baseline` skips the re-run.

The script is safe to stop and restart. Completed runs are skipped. A failed
run is retried under the next attempt number, and the failure stays on disk.

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

Following M6's `PROTOCOL_ADOPTION.md`, label these results "component vs M1
reference" (`m3_full` vs `m1_baseline`), separate from the frozen agent's
component ablation table.

## Fairness checklist

- Same systems, seeds, budget, oracle, memory configuration and protocol
  version for every method.
- Do not tune M3 settings on the check split; the ablations use dev only.
- Report every run, including failed attempts and neutral or negative
  differences.
