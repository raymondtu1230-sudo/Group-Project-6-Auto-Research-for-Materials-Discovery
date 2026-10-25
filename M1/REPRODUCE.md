# M1 Reproduction Record

## Protocol v1 (set by M1)

| Setting | Agreed value |
| --- | --- |
| MADE upstream commit | `bffda0c9a1fa1904b35c0ef67b455881c975df86` |
| Scientific model | `orb-v3-conservative-inf-omat`, CPU, FIRE relaxation (`fmax=0.02`, 500 max steps, relax unit cell) |
| Materials Project data | `GGA_GGA+U`; frozen public systems lists in `M1/protocol/` |
| Development/check systems | First 6 / last 4 systems from the committed ternary systems file; exact lists in `M1/protocol/` |
| Course held-out systems | Use only if/when the teaching team publishes them; never tune on them |
| Oracle query budget per episode | 20 queries, same for every method |
| Seeds / repeats | `17`, `29`, `43`; one episode in a separate process per seed |
| API / compute | Materials Project API key required for data retrieval; ORB has no LLM API cost; report CPU model and wall time |
| Full protocol | `M1/EXPERIMENT_PROTOCOL.md` and machine-readable `M1/protocol/protocol_v1.yaml` |

## Local pipeline smoke test (completed; not a course result)

The smoke dataset contains synthetic Li-O entries and is evaluated by MADE's analytic Lennard-Jones oracle. It verifies the local runner/agent/environment/trajectory/summary path only. Its metrics must not be compared with course results or reported as materials discoveries.

Run from `M1/MADE` with its dependency environment installed. The wrapper verifies the working directory, selects the local synthetic dataset and analytic oracle, and applies the Modal workaround in-process without editing the upstream runner:

```bash
uv run python ../run_smoke_test.py
```

The process-local Modal patch works around the runner's unconditional volume commit in local mode; it does not modify source files. The latest wrapper run completed one episode and used exactly two of two oracle queries; its artifacts are at `M1/MADE/results/20261018-125240-analytic-m1_integrated/`. Earlier raw runs remain preserved in sibling timestamped directories. Smoke metrics are not performance evidence. The first failed attempt is preserved at `M1/MADE/checkpoints/20261018_122451/episode_000/checkpoint.json` for debugging. Do not remove it until the failure has been reviewed.

## Course benchmark

Run one system/seed unit from `M1/MADE` using the protocol driver. Obtain a free Materials Project API key in your Materials Project account's API key settings. Create the local ignored file from the checked-in template, then replace the placeholder with your real key:

```bash
cp .env.example .env
# edit .env and set MATERIALS_PROJECT_API_KEY=your_real_key
```

Do not send the key in chat or commit it. Example:

```bash
uv run python ../run_experiment.py --method random_generator_baseline --split dev --system Mg-Sn-Sr --seed 17
```

Use `--method m1_full` for the integrated agent frozen as `m1-freeze-20261025` and the corresponding `*_off` methods for paired ablations. The M1 full/ablation methods intentionally fail if a switch is on but its plug-in is absent. Outputs are grouped under `M1/MADE/results/protocol_v1/`. One official-data, 20-query freeze canary completed on 25 October 2026; see `FREEZE_RECORD.md`. Keep the Materials Project key only in the ignored `.env`. If the course later publishes conflicting frozen values, make a versioned protocol amendment and a new tag.

## Per-run record

`run_experiment.py` writes `run_metadata.json` alongside the official runner outputs, including command, UTC start, machine/OS/CPU, Python and key dependency versions, upstream MADE commit, M1 source hashes, protocol settings, seed, system, and wall time. Preserve raw outputs; do not report a score without its corresponding trajectory and resolved config. Record any additional component-level token/API cost in M2's results table.

Each new run also writes a `cost` object in `run_metadata.json`. It separates oracle queries (ORB is recorded as USD 0), Materials Project logical dataset requests (public API price is recorded as 0 with an explicit status), and optional LLM usage. LLM-enabled components can provide a usage JSON file through `M1_LLM_USAGE_FILE`, with `calls`, `input_tokens`, `output_tokens`, `cost_usd`, `provider`, and `model` fields. Alternatively, set `M1_LLM_CALLS`, `M1_LLM_INPUT_TOKENS`, `M1_LLM_OUTPUT_TOKENS`, `M1_LLM_COST_USD`, `M1_LLM_PROVIDER`, and `M1_LLM_MODEL`. Missing LLM usage is marked `not_reported`; it is never silently treated as a measured zero.
