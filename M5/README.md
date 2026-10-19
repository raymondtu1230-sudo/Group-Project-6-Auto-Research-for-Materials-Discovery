# M5 Exploration — UCBExplorationPolicy

Owner: Chen Mingsong (M5). Design: [DESIGN.md](DESIGN.md).
Contract: `M1/PLUGIN_INTERFACE.md` (`adjust_plan(plan, context) -> Plan`).

## Contents

| Path | What |
|---|---|
| `src/made/agents/m5_exploration.py` | The policy: GP surrogate + budget-annealed UCB over composition space |
| `configs/m5_exploration_block.yaml` | Hydra block to wire into `m1_integrated.yaml` |
| `tests/test_m5_exploration.py` | 10 contract tests (enabled/disabled, budget cap, annealing, cold start, no-reproposal, determinism, checkpoint round-trip, invalid output, fail-fast) |
| `install.py` | Copies module/tests/config into `M1/MADE` |
| `DESIGN.md` | One-page design |
| `M4_LOG_CONFIRMATION.md` | Evidence log format confirmation for M4 |

## Install and verify

```bash
python M5/install.py          # from repo root
cd M1/MADE
uv run pytest -q tests/test_m1_integrated.py tests/test_m5_exploration.py
uv run ruff check src/made/agents/m5_exploration.py tests/test_m5_exploration.py
uv run python ../run_smoke_test.py
```

Verified 2026-10-19 on Windows (local venv): **27 passed** (17 M1 + 10 M5),
ruff clean, official smoke run completed with `enable_exploration=true` via
Hydra overrides.

Windows note: run with `PYTHONUTF8=1` — MADE's bundled HHI data file contains
UTF-8 punctuation and the default GBK locale codec crashes
`ConvexHullEnvironment` on Chinese Windows.

## Wiring (for M1)

In `configs/agent/m1_integrated.yaml`:

```yaml
enable_exploration: true
exploration_policy:
  _target_: made.agents.m5_exploration.UCBExplorationPolicy
  seed: ${experiment.seed}
```

Ablation: `enable_exploration: false`, everything else fixed.

## What the policy does (30 seconds)

`adjust_plan` keeps the planner's compositions (exploit pool) and appends
unqueried stoichiometries ranked by UCB = -μ + β(t)·σ from a GP fit on observed
`e_above_hull` (explore pool). Exploration share α(t) = α₀·(remaining/B)^γ
anneals from aggressive to conservative as the budget drains. Every decision is
logged (mode, direction, remaining budget, UCB stats, rationale) into a
JSON-serializable `decision_log` that rides the agent checkpoint — this is also
the data source for the over-exploitation / wasteful-exploration failure
trajectories (see M4_LOG_CONFIRMATION.md).

## Guarantees

- Never calls the oracle, never reads hidden labels; inputs are only
  `context` fields documented in PLUGIN_INTERFACE.md.
- M1's budget cap runs after the hook; the policy cannot overspend.
- Deterministic under `experiment.seed`; disabled switch = exact pass-through.
- Pure numpy (no new heavy dependencies); GP fit is milliseconds at n ≤ 20.
