# Dry-run evidence (dev system Mg-Sn-Sr, seed 17, B=20)

Raw outputs of the two pre-freeze `m1_full` integration runs used to tune
α₀. Same seed, same budget, same machine (RTX 4070 laptop, "Wander-Lust").

| Folder | α₀ | mSUN@20 | AUDC | Notes |
|---|---|---|---|---|
| `dry-run-alpha0.5/` | 0.5 | 9 | 66.5 | Explore slot opens only at step 0 |
| `dry-run-alpha0.8/` | 0.8 | 9 | 84.5 | Stable MgSr found at step 3; 7 of 9 hits in first 10 queries |

Each folder contains:
- `episode_000.json` — official MADE trajectory (20 queried observations)
- `summary.json` / `episodes.json` — evaluator summary
- `run_metadata.json` — wall time, machine, protocol hashes
- `m5_decisions.jsonl` — M5 per-step decision log (mode, direction, budget,
  UCB stats, rationale); steps 10–15 of the α₀=0.5 run are the
  wasteful-exploration example (6 diverse Sn–Sr probes, 1 stable hit)

The α₀=0.5 decision log is from the γ=2 diagnostic run, whose trajectory is
identical to the γ=1 α₀=0.5 run (both were executed with the current
sidecar-enabled code; the original γ=1 α₀=0.5 run predates the sidecar).
