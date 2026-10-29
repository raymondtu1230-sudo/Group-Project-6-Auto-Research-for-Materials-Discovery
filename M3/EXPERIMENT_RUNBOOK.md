# M3 experiment runbook

How to reproduce M3's runs on your own computer. Sections 1–4 cover the
component study (72 runs against `m1_baseline`). Section 5 covers the runs on
M1's frozen agent: M3's assigned full-agent ablations (`planning_off`,
`self_correction_off`) and the component study re-run (90 runs in total).

M1 integrated M3 on `main` (`2fcc214`). M1 also made M4's memory
manager the default memory in `m1_integrated.yaml` (`9acd3c9`). Every run with
memory on, including `m1_baseline`, therefore needs the M4 package installed.

## 1. One-time setup

Needs git and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery.git
cd Group-Project-6-Auto-Research-for-Materials-Discovery/M1/MADE
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
uv run python ../../M3/run_ablations.py --dry-run --jobs 3   # should say 72 to run
uv run python ../../M3/run_ablations.py --jobs 3
```

`--jobs` runs several at once: use about one per 4–5 CPU cores (3 on 16
threads). Keep the machine awake and online; the first run downloads the
~100 MB ORB model.

This runs:

- **Methods:** `m1_baseline`, `m3_full`, `m3_planning_off` and
  `m3_self_correction_off`.
- **Systems:** the six dev systems.
- **Seeds:** 17, 29 and 43.

That is 72 one-episode runs, several hours on CPU (M1's baseline runs took
140–300 s each).

`m1_baseline` is re-run because M1's 18 recorded runs were made
before M4's memory became the default. Pairing M3 against them would mix M3's
effect with the memory change. The recorded runs still appear in the summary
as `m1_baseline_recorded`, for context only. `--no-baseline` skips the re-run.

The script is safe to stop and restart. Completed runs are skipped. A failed
run is retried under the next attempt number, and the failure stays on disk.

## 4. Summarize and share

```bash
uv run python ../../M3/summarize_ablations.py
```

This writes:

- `M3/results/m3_ablation_runs.csv` (per run);
- `M3/results/m3_ablation_summary.csv` (per method);
- `M3/report/M3_RESULTS.md`: tables plus generated "what changed" sentences.

Edit the "Why" section by hand.

Share with M2: the two CSVs and `M3_RESULTS.md`. Share with M6:
`M3_RESULTS.md`.

Following M6's `PROTOCOL_ADOPTION.md`, label these results "component vs M1
reference" (`m3_full` vs `m1_baseline`), separate from the frozen agent's
component ablation table.

## 5. Runs on M1's frozen agent

These runs use M1's frozen agent as it is, so skip `install.py --install` (the
tag already contains the current M3 code). Setup as in section 1, then:

1. **Check out the tag and confirm it is clean.**

   ```bash
   git fetch --tags --force
   git checkout m1-freeze-20261025      # commit ae7fe81
   git status --porcelain --untracked-files=no   # must print nothing
   ```

2. **Put the Chemeleon weights in place.** The full agent's tool routing can
   use the Chemeleon generator. Download the official archive (Figshare file
   54966305), check it, and extract it from `M1/MADE`. It unpacks into
   `ckpts/`, which git ignores:

   ```bash
   curl -L --fail -o ../../../checkpoints.tar.gz https://api.figshare.com/v2/file/download/54966305
   sha256sum ../../../checkpoints.tar.gz   # must be ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e
   tar -xzf ../../../checkpoints.tar.gz    # creates ckpts/ with four .ckpt files
   ```

   The archive is 548,874,535 bytes, the same one M1 and M2 used. Keep it
   outside the repository. M3's record of the archive and the four files is
   `results/frozen_20261025/chemeleon_checksum_receipt.txt`.

3. **Run.** From `M1/MADE`:

   ```bash
   uv run python ../../M3/run_ablations.py --methods planning_off self_correction_off --no-baseline --jobs 3
   uv run python ../../M3/run_ablations.py --methods m3_full m3_planning_off m3_self_correction_off --no-baseline --jobs 3
   ```

   `--no-baseline` is needed: the reference for the full-agent ablations is
   M1's own 18 `m1_full` runs, which are already in the repository.

4. **Check.** `uv run python ../../M3/run_ablations.py --methods planning_off
   self_correction_off m3_full m3_planning_off m3_self_correction_off
   --no-baseline --dry-run` should report 90 of 90 completed. Validate with
   M2's evaluator, also from `M1/MADE`:
   `uv run python ../../M2/evaluate.py --results-root results/protocol_v1 --output <new folder> --split dev`.

Result folders, layout and numbers: `results/frozen_20261025/README.md`.

## Fairness checklist

- Same systems, seeds, budget, oracle, memory configuration and protocol
  version for every method.
- Do not tune M3 settings on the check split; the ablations use dev only.
- Report every run, including failed attempts and neutral or negative
  differences.
