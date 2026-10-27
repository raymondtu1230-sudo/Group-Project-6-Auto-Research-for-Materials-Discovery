# Requirements Checklist (course brief → owner → status → file)

Owner: M6. Last updated: 2026-10-27 at team revision `77f1c71`; frozen agent tag `m1-freeze-20261025`.
Status: ✅ done · 🟡 partial / in progress · ⬜ not started · ⛔ blocked.

## 4.1 Codebase

| # | Deliverable (brief) | Owner | Status | File(s) / evidence |
| --- | --- | --- | --- | --- |
| C1 | Auto Research agent integrated with the official MADE interface, full closed-loop episodes | M1 | ✅ frozen 25 Oct (`m1-freeze-20261025`); 18/18 dev reference runs, mSUN@20 10.00 ± 0.88 | `M1/FREEZE_RECORD.md` |
| C2 | At least one research strategy of our own design | M2–M5 | ✅ five components integrated in the frozen agent | `M1/INTEGRATION.md` |
| C2a | Planning and decomposition | M3 | ✅ in frozen agent; ablation −4.7 mSUN when off (15/2/1 pairs) | `M3/results/frozen_20261025/` |
| C2b | Memory and evidence management | M4 | ✅ in frozen agent; ablation −0.9 when off (8/3/7) | `M4/report/M4_FROZEN_MEMORY_RESULTS.md` |
| C2c | Exploration vs exploitation | M5 | ✅ in frozen agent (α₀ = 0.8); ablation −0.3 when off (8/1/9) | `M5/report/M5_RESULTS.md` |
| C2d | Candidate proposal / tool routing | M2 | ✅ in frozen agent; ablation −2.3 when off (12/1/5) | `M2/frozen_20261025/` |
| C2e | Reflection and failure recovery | M3 | ✅ in frozen agent; ablation −0.5 when off (8/2/8) | `M3/results/frozen_20261025/` |
| C3 | Random-generator baseline (official) | M2 | ✅ dev 18/18; check 12/12 (M6, 20 Oct): mSUN@20 5.58 ± 0.63 | `M2/verification/20261020-handoff-audit/`, `M6/results/20261020-check-random/` |
| C4 | Chemeleon generative baseline (official) | M2 | 🟡 dev 18/18 ✅ (6.94 ± 1.11). Check: not run (~2.5 h per unit locally; dropped for compute, stated in report) | `M2/verification/direct-39432570527-1/final-report/` |
| C5 | Frozen configs | M1 | ✅ tag `m1-freeze-20261025` | `M1/FREEZE_RECORD.md` |
| C6 | Run commands | M1, M2, M6 | ✅ | `M1/EXPERIMENT_PROTOCOL.md`, `M1/REPRODUCE.md`, `M6/run_check_baselines.sh` |
| C7 | Random seeds | M1 | ✅ 17/29/43 | `M1/protocol/protocol_v1.yaml` |
| C8 | Dependency versions | M1 | ✅ lockfile; versions also in each `run_metadata.json` | `M1/MADE/uv.lock` |
| C9 | Raw trajectories/results behind every reported number | M2, M6 | 🟡 kept for accepted units; must cover all final units | `M2/verification/*/raw_artifact.zip` |
| C10 | Oracle/evaluator unmodified; no hidden labels read | All, M1 checks | ✅ so far (source hashes in metadata) | `M1/EXPERIMENT_PROTOCOL.md`, `M2/STATUS.md` |

## 3.2 Protocol

| # | Requirement | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| P1 | Official `scripts/run_benchmark.py` runner | M1 | ✅ | `M1/run_experiment.py` |
| P2 | Course-frozen commit, env, oracle, systems | TA → M1 | ⛔ no course hidden set or frozen settings published; protocol v1 used and stated | `M1/FREEZE_RECORD.md` |
| P3 | Optimize on dev only; final ranking on held-out systems chosen by the teaching team | M6 | 🟡 rule adopted; hidden split not in runner | `M6/PROTOCOL_ADOPTION.md` |
| P4 | Same model, oracle, budget, tools, systems, evaluator for all methods | M1, M6 | ✅ by protocol v1; checked by `M2/evaluate.py` | `M1/protocol/` |
| P5 | Three repeats preferred; one allowed if stated | M6 | 🟡 3 seeds planned; 1-seed fallback defined for held-out | `M6/COMPUTE_PLAN.md` §4, `M6/PROTOCOL_ADOPTION.md` §6 |
| P6 | Hidden-split support in runner/evaluator | M1, M2 | 🟡 M1 says the allow-list is done, but it is not on main yet (checked 20 Oct). Hidden split waits for the TA | `M6/PROTOCOL_ADOPTION.md` §4 |
| P7 | Check baselines (24 units) | M6 | 🟡 Random 12/12 ✅ (5.58 ± 0.63). Chemeleon not run (compute) | `M6/results/20261020-check-random/` |
| P8 | Frozen agent on check (12) and hidden (9·H) | M6 | ✅ check, seed 17 only (1-seed fallback): 4/4, mSUN@20 14.0 vs Random 6.25. Hidden: not released | `M6/results/20261027-check-agent-seed17/` |

## 3.1 / 4.2 Report

| # | Section (brief) | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| R1 | Leaderboard: mSUN@B, AUDC, AF, EF, research cost for our method and both baselines | M2 data, M6 | ✅ dev: Full 10.00, Chemeleon 6.94, Random 4.06. Held-out (check, seed 17): Full 14.0, Random 6.25, Chemeleon not run | `M6/results/20261027-check-agent-seed17/` |
| R2 | Discovery curves | M2 | ✅ dev curves for all 11 methods | `M2/aggregation/20261027_m3_full_agent/ (PR #6, unmerged)results/discovery_curves_by_study.svg` |
| R3 | Component ablation | M3, M4, M5, M2; M6 combines | ✅ all five single-switch ablations on dev, 198 runs validated by M2; m3_* study kept separate | `M2/aggregation/20261027_m3_full_agent/ (PR #6, unmerged)M6_HANDOFF.md` |
| R4 | Generalization: dev vs held-out | M6 | ✅ seed 17: agent 9.0 → 14.0, Random 3.3 → 6.3; lead over Random +5.7 → +7.8 | `M6/results/20261027-generalization-seed17/` |
| R5 | Failure classification: over-exploitation, one trajectory | M5, M4, M6 | ✅ exploration_off Mg-Sn-Sr/29 (16 binary queries before any ternary), audited by M2 | `M2/aggregation/20261026_m5_intake/audits/metrics/failure_cases.md` |
| R6 | Failure classification: wasteful exploration, one trajectory | M5, M4, M6 | ✅ m1_full Ga-Pt-Tm/17 (one unstable UCB ternary probe; 10 vs 16 mSUN vs off, causation not established), audited by M2 | `M2/aggregation/20261026_m5_intake/audits/metrics/failure_cases.md` |
| R7 | Discussion: which mechanisms helped, remaining bottlenecks | M6 | 🟡 drafted in the deck (planning and routing carry the gain; slow start, 1 composition/step, small sample) | deck |
| R8 | Research cost: oracle calls, tokens/USD, wall time | M2, M6 | ✅ USD 0 known fees; times on different machines | `M2/aggregation/20261027_m3_full_agent/ (PR #6, unmerged)report/COST_ANALYSIS.md` |
| R9 | Method text from each member (due 24 Oct) | M1–M5 | ✅ all received: M1 (`M1/report/A1_*`), M2 (PR #6), M3, M4 (`M4/report/`), M5 (`M5/report/`) | – |
| R10 | Per-material table to M2 (27 Oct) | M6 | 🟡 ready (`per_run.csv` in the check results); not yet sent to M2 | `M6/results/20261027-check-agent-seed17/per_run.csv` |

## 4.3 Presentation

| # | Requirement | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| S1 | 10 min talk + 5 min Q&A | M6 | ✅ 14-slide deck with speaker notes (M6's Slides artifact, private until shared) | – |
| S2 | Main idea and architecture | M1 + owners | ✅ deck slides 3–7 | – |
| S3 | How the system uses MADE and manages the budget | M1 | ✅ deck slides 2–3 | – |
| S4 | Key results vs both baselines | M6 | ✅ deck slides 9–12 | – |
| S5 | Trajectories, discoveries, failure cases | M5, M6 | ✅ deck slide 13 | – |
| S6 | Conclusions and lessons | M6 | ✅ deck slide 14 | – |
| S7 | Rehearsal 29 Oct | M6 | ⬜ | – |

## Submission

| # | Item | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
| D1 | GitHub repo or Google Drive folder with code, report, slides | M6 | ⬜ | Submit 30 Oct |
| D2 | Frozen revision tagged and named in the report | M1 | ✅ `m1-freeze-20261025` | `M1/FREEZE_RECORD.md` |
| D3 | Individual reports (≤ 3 pages, due end of 3 Nov, per `M2/STATUS.md`) | Each member | ⬜ | M6 uses `M6/WORK_LOG.md` |
| D4 | GenAI-use declaration, if the course requires one | All | ⬜ | Confirm with TA |

## Key dates

| Date | Milestone |
| --- | --- |
| 19–20 Oct | Start check baselines (Chemeleon first) |
| 24 Oct | Method text and slides from all members to M6; check baselines complete |
| 25 Oct | Agent freeze (M1) |
| 26–27 Oct | Frozen agent + baselines on check and hidden; per-material table to M2 |
| 27 Oct | M2 delivers validated tables, curves, cost, failed-run audit |
| 29 Oct | Rehearsal |
| 30 Oct | Submission |
| 31 Oct / 1 Nov | Presentations |
