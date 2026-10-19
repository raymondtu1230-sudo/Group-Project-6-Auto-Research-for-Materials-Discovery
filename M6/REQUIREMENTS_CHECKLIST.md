# Requirements Checklist (course brief → owner → status → file)

Owner: M6. Last updated: 2026-10-20 at team revision `221e159`.
Status: ✅ done · 🟡 partial / in progress · ⬜ not started · ⛔ blocked.

## 4.1 Codebase

| # | Deliverable (brief) | Owner | Status | File(s) / evidence |
| --- | --- | --- | --- | --- |
| C1 | Auto Research agent integrated with the official MADE interface, full closed-loop episodes | M1 | 🟡 `m1_baseline` runs end to end; `m1_full` waits for plug-in integration and the 25 Oct freeze | `M1/MADE/src/made/agents/`, `M1/INTEGRATION.md`, `M1/run_experiment.py` |
| C2 | At least one research strategy of our own design | M2–M5 | 🟡 components delivered as separate folders, not yet wired into one frozen agent | `M2/integration/`, `M3/`, `M4/src/`, `M5/src/` |
| C2a | Planning and decomposition | M3 | 🟡 code + tests on main; M1 still has to run `M3/install.py`; ablation runs (vs `m1_baseline`) due to M2 by 27 Oct | `M3/README.md`, `M3/HANDOVER.md` |
| C2b | Memory and evidence management | M4 | 🟡 code + tests; M3's planner reads `m1_memory` (default planner does not), so the memory ablation needs M3's planner in the frozen agent | `M4/M1_STATUS.md`, `M4/VALIDATION.md` |
| C2c | Exploration vs exploitation | M5 | 🟡 code + 10 tests; not integrated | `M5/README.md` |
| C2d | Candidate proposal / tool routing | M2 | 🟡 code + tests; PR #2 unmerged | `M2/STATUS.md` |
| C2e | Reflection and failure recovery | M3 | 🟡 as C2a | `M3/README.md` |
| C3 | Random-generator baseline (official) | M2 | 🟡 dev 1/18 units; check 0/12 | `M2/verification/20261019-random-gate/` |
| C4 | Chemeleon generative baseline (official) | M2 | 🟡 dev 1/18 units; check 0/12 | `M2/verification/20261019-chemeleon-recovery/` |
| C5 | Frozen configs | M1 | 🟡 protocol frozen; agent freeze 25 Oct | `M1/protocol/protocol_v1.yaml`, `M1/MADE/configs/` |
| C6 | Run commands | M1, M2, M6 | ✅ | `M1/EXPERIMENT_PROTOCOL.md`, `M1/REPRODUCE.md`, `M6/run_check_baselines.sh` |
| C7 | Random seeds | M1 | ✅ 17/29/43 | `M1/protocol/protocol_v1.yaml` |
| C8 | Dependency versions | M1 | ✅ lockfile; versions also in each `run_metadata.json` | `M1/MADE/uv.lock` |
| C9 | Raw trajectories/results behind every reported number | M2, M6 | 🟡 kept for accepted units; must cover all final units | `M2/verification/*/raw_artifact.zip` |
| C10 | Oracle/evaluator unmodified; no hidden labels read | All, M1 checks | ✅ so far (source hashes in metadata) | `M1/EXPERIMENT_PROTOCOL.md`, `M2/STATUS.md` |

## 3.2 Protocol

| # | Requirement | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| P1 | Official `scripts/run_benchmark.py` runner | M1 | ✅ | `M1/run_experiment.py` |
| P2 | Course-frozen commit, env, oracle, systems | TA → M1 | ⛔ not yet announced; asked the TA (M6) | – |
| P3 | Optimize on dev only; final ranking on held-out systems chosen by the teaching team | M6 | 🟡 rule adopted; hidden split not in runner | `M6/PROTOCOL_ADOPTION.md` |
| P4 | Same model, oracle, budget, tools, systems, evaluator for all methods | M1, M6 | ✅ by protocol v1; checked by `M2/evaluate.py` | `M1/protocol/` |
| P5 | Three repeats preferred; one allowed if stated | M6 | 🟡 3 seeds planned; 1-seed fallback defined for held-out | `M6/COMPUTE_PLAN.md` §4, `M6/PROTOCOL_ADOPTION.md` §6 |
| P6 | Hidden-split support in runner/evaluator | M1, M2 | ⬜ proposed, including an allow-list so only `m1_full` and the two baselines run on check/hidden | `M6/PROTOCOL_ADOPTION.md` §4 |
| P7 | Check baselines (24 units) | M6 (+M2 GitHub) | ⬜ ready to launch; needs go-ahead | `M6/run_check_baselines.sh`, `M6/COMPUTE_PLAN.md` |
| P8 | Frozen agent on check (12) and hidden (9·H) | M6 | ⬜ after 25 Oct | `M6/COMPUTE_PLAN.md` |

## 3.1 / 4.2 Report

| # | Section (brief) | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| R1 | Leaderboard: mSUN@B, AUDC, AF, EF, research cost for our method and both baselines | M2 data, M6 | ⬜ M6 has a local template | – |
| R2 | Discovery curves | M2 | 🟡 plotting works (`evaluate.py`); partial curve only | `M2/verification/20261019-chemeleon-recovery/discovery_curves.png` |
| R3 | Component ablation | M3, M4, M5, M2; M6 combines | ⬜ after freeze; dev only. M3's results compare with `m1_baseline`, so they go in a separate table, not Table 2 (`M6/PROTOCOL_ADOPTION.md` §5) | `M3/report/M3_RESULTS.md` |
| R4 | Generalization: dev vs held-out | M6 | 🟡 tool ready and tested; no held-out data yet | `M6/generalization.py` (tested on `M2/verification/20261019-chemeleon-recovery/`) |
| R5 | Failure classification: over-exploitation, one trajectory | M5, M4, M6 | ⬜ logging exists (`decision_log`) | – |
| R6 | Failure classification: wasteful exploration, one trajectory | M5, M4, M6 | ⬜ needs rejected/error events from M4 (M5 asked for them before 26 Oct); otherwise built from evaluated queries only | – |
| R7 | Discussion: which mechanisms helped, remaining bottlenecks | M6 | ⬜ | – |
| R8 | Research cost: oracle calls, tokens/USD, wall time | M2, M6 | 🟡 recorded per run | `M1/cost_tracking.py` |
| R9 | Method text from each member (due 24 Oct) | M1–M5 | 🟡 M3 ✅ received 20 Oct (`M3/report/M3_METHOD.md`, `M3_Method_Draft.pptx`); M2 and M4 drafts exist; M1 short draft; M5 design doc only | sent to M6 |
| R10 | Per-material table to M2 (27 Oct) | M6 | ⬜ | – |

## 4.3 Presentation

| # | Requirement | Owner | Status | File(s) |
| --- | --- | --- | --- | --- |
| S1 | 10 min talk + 5 min Q&A | M6 | 🟡 M6 has a local outline, 9:55 budget | – |
| S2 | Main idea and architecture | M1 + owners | 🟡 drafts exist | `M1/SLIDES_DRAFT.md`, `M3/report/*.pptx`, `M4/report/*.pptx` |
| S3 | How the system uses MADE and manages the budget | M1 | 🟡 | `M1/SLIDES_DRAFT.md` slide 2 |
| S4 | Key results vs both baselines | M6 | ⬜ | – |
| S5 | Trajectories, discoveries, failure cases | M5, M6 | ⬜ | – |
| S6 | Conclusions and lessons | M6 | ⬜ | – |
| S7 | Rehearsal 29 Oct | M6 | ⬜ | – |

## Submission

| # | Item | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
| D1 | GitHub repo or Google Drive folder with code, report, slides | M6 | ⬜ | Submit 30 Oct |
| D2 | Frozen revision tagged and named in the report | M1 | ⬜ | 25 Oct |
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
