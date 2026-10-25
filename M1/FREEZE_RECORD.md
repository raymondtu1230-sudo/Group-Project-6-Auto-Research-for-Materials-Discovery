# M1 Freeze Record

Freeze date: 2026-10-25 (Asia/Singapore)

Frozen tag: `m1-freeze-20261025`

## Frozen system

The frozen `m1_full` method uses the unmodified official MADE runner and the
team protocol v1 settings: ORB v3 conservative on CPU, `B=20`, seeds
17/29/43, the six public development systems and four public check systems.
All five component switches are enabled:

- M3 planning with `M3ResearchPlanner`
- M4 memory and evidence capture
- M3 self-correction
- M5 exploration with `alpha0=0.8`
- M2 outcome-aware routing between checkpointed Random and Chemeleon generators

The course has not supplied conflicting frozen settings or a hidden-system
list. A later course setting requires a versioned protocol amendment and a new
tag; it must not silently change this release.

## Freeze gate

The following checks passed on the frozen source:

- M1 integration and protocol tests: 89 passed
- M3 tests: 17 passed
- M4 tests: 15 passed
- M5 tests: 14 passed
- Ruff checks on the integration runner, components and focused tests: passed
- M3 installer consistency check: all M3-owned files `ok`; M1-owned merged files
  retain every required M3 marker

The gate found and fixed one stale M1 copy of M3's progress logic before the
freeze. Progress now requires a newly discovered stable phase; MADE's
`is_newly_discovered` flag alone is not treated as success. The regression
tests cover unstable records and self-correction triggering.

## Official end-to-end acceptance

Command, run from `M1/MADE`:

```bash
./.venv/bin/python ../run_experiment.py \
  --method m1_full --split dev --system Mg-Sn-Sr --seed 17 --attempt 2
```

Attempt 01 is preserved as a failed preflight: Figshare's primary download URL
returned an empty Chemeleon checkpoint archive. The official alternate Figshare
download endpoint supplied the 523 MB archive; its SHA-256 was
`ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`.
The four extracted checkpoints are local ignored dependencies.

Attempt 02 completed successfully:

| Check | Result |
| --- | --- |
| Status | `completed`, exit code 0 |
| Official queries | 20/20 |
| Episodes | 1 |
| Wall time | 380.138 s |
| All five switches | enabled |
| Planner | M3 research planner |
| Primary canary metric | mSUN@20 = 12 |
| AUDC | 105.0 |
| Input hash audit | 0 mismatches across every recorded M1/MADE input |
| M5 decisions | 20 valid JSONL records |
| M4 incremental memory evidence | 19 valid JSONL records |

The M4 count is expected: memory is updated when the next proposal begins, so
the final oracle observation has no subsequent proposal. The official
trajectory contains all 20 queries and is the complete evidence source.
Proposal-event capture remains enabled; this run produced no rejected/error
event file because no such event occurred.

Local evidence is preserved in the ignored result directories:

- `M1/MADE/results/protocol_v1/m1_full/dev/Mg-Sn-Sr/seed_17/attempt_01/`
- `M1/MADE/results/protocol_v1/m1_full/dev/Mg-Sn-Sr/seed_17/attempt_02/`
- `M1/MADE/results/20261025-185305-orb-m1_integrated/`

This is a freeze acceptance canary, not the final leaderboard estimate. The
next step is the frozen 6-system x 3-seed development reference and paired
one-switch ablations.
