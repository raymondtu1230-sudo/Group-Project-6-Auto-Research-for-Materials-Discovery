# Auto Research for Materials Discovery on MADE (Group Project 6)

Report template. Owner: M6. Status: skeleton, 2026-10-19.

How to use this file:

- Each section names its **owner**, its **source drafts** and its **data files**.
  Owners send text to M6 by **24 Oct**. M6 merges and edits for one voice.
- Every number comes from a file in the repo: M2 `evaluate.py` outputs, M3
  `summarize_ablations.py`, or M6 `generalization.py`. Write the source path under
  every table and figure. No number is typed in by hand.
- Missing or incomplete runs stay visible ("n/a, 4/12 runs"). Never fill them in.
- If no course hidden set is released, call the held-out split "public check set
  (not the course hidden test)" every time it appears.
- Placeholders look like `[[...]]`. Search for `[[` before submitting.

---

## Abstract (M6, last)

[[3–5 sentences: problem, our agent's main idea, headline mSUN@20 vs both baselines on
held-out systems, the component that mattered most, the main bottleneck.]]

## 1. Introduction (M6)

- Closed-loop discovery as sequential decisions under a fixed oracle budget.
- What is fixed: MADE runner, ORB oracle, evaluator, validity checks, B, tools.
- What we change: the research policy (planning, memory, exploration, routing, reflection).
- Central question (from the brief): can a better research strategy find more valid
  materials with the same tools, model and budget?
- Contributions: [[bullet list, one per component that has an ablation result]].

## 2. System (owners below; M6 edits)

Figure 1: architecture diagram. Source: `M1/SLIDES_DRAFT.md` slide 1.

| Subsection | Owner | Source drafts |
| --- | --- | --- |
| 2.1 Integration and budget handling | M1 | `M1/METHOD_DRAFT.md`, `M1/PLUGIN_INTERFACE.md`, `M1/INTEGRATION.md` |
| 2.2 Planning and self-correction | M3 | `M3/report/M3_METHOD.md`, `M3/DESIGN.md` |
| 2.3 Memory and evidence management | M4 | `M4/report/M4_METHOD.md`, `M4/EVIDENCE_SCHEMA.md` |
| 2.4 Exploration vs exploitation | M5 | `M5/DESIGN.md`, `M5/README.md` |
| 2.5 Tool routing (Random / Chemeleon) | M2 | `M2/METHODS_AND_M6_HANDOFF.md` ("Methods paragraph") |

Each subsection: what it decides, its inputs (public state only), its switch
(`enable_*`), and one sentence on why it should help. Max ~250 words each.

State clearly: the agent only uses `env.get_state()` and its own past queried
observations. It never reads `phase_diagram_gt`, held-out labels or evaluator state.

## 3. Experimental protocol (M6, with M1)

Source: `M1/EXPERIMENT_PROTOCOL.md`, `M1/protocol/protocol_v1.yaml`,
`M6/PROTOCOL_ADOPTION.md`, `M6/COMPUTE_PLAN.md`.

- MADE upstream `bffda0c9…`; frozen agent revision `[[25 Oct freeze hash]]`.
- Oracle ORB `orb-v3-conservative-inf-omat`, CPU, FIRE, fmax 0.02, 500 steps.
- B = 20 queries per system per seed; seeds 17/29/43; one episode per process.
- Splits: 6 dev (tuning + ablations), 4 public check (frozen agent + baselines only),
  [[H]] course hidden systems [[or: "not released; the check set is our only held-out
  split"]].
- Methods: frozen agent (`m1_full`), official Random baseline, official Chemeleon baseline.
- Aggregation: equal-weight mean over systems per seed, then mean ± sample SD over seeds.
- [[If used: "Held-out systems use one seed (17) for every method because of compute;
  no SD is reported for them."]]

## 4. Leaderboard (M2 data, M6 text)

Table 1. Source: `[[M2 report dir]]/per_method_summary.csv` per split
(`M2/evaluate.py --split dev|check|hidden`).

| Method | Split | Units | mSUN@20 | AUDC | AF vs Random | EF vs Random | AF vs Chemeleon | EF vs Chemeleon | Oracle calls | LLM tokens / USD | Wall time / unit | Hardware |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Agent (`m1_full`) | held-out | [[n/N]] | [[mean ± SD]] | | | | | | 20 / unit | | | |
| Random | held-out | | | | 1 (ref) | 1 (ref) | | | 20 / unit | 0 / 0 | | |
| Chemeleon | held-out | | | | | | 1 (ref) | 1 (ref) | 20 / unit | 0 / 0 | | |
| Agent (`m1_full`) | dev | | | | | | | | | | | |
| Random | dev | | | | | | | | | | | |
| Chemeleon | dev | | | | | | | | | | | |

Caption rules: name the split, systems, seeds and number of repeats. AF/EF are the
official MADE metrics on paired system/seed/budget runs, not wall-time speedups.
"USD 0" means zero recorded model/API fees, not zero total compute cost.

Appendix A holds the per-material table (from `per_system_summary.csv`), which M6 also
sends to M2 on 27 Oct.

Text: [[2–4 sentences: who wins, by how much, how consistent across systems.]]

## 5. Discovery curves (M2 data, M6 text)

Figure 2. Source: `[[M2 report dir]]/discovery_curves.png` (one panel per split).
Current partial example: `M2/verification/20261019-chemeleon-recovery/discovery_curves.png`
(1 unit per method, not a result).

- x: oracle queries used (1–20). y: cumulative newly discovered stable (the AUDC
  curve) and, separately, cumulative mSUN. Do not mix the two on one axis.
- Text: [[where curves separate (early vs late), what that says about budget use.]]

## 6. Component ablation (M3, M4, M5, M2 data; M6 combines)

Dev systems only (protocol v1). Each ablation turns off one switch in the same frozen agent.

Table 2. Sources: `M3/report/M3_RESULTS.md` (generated by `M3/summarize_ablations.py`),
M4 memory ON/OFF (`M4/VALIDATION.md` "Planned evaluation"), M5 exploration ON/OFF,
M2 routing-off (`M2/METHODS_AND_M6_HANDOFF.md`).

| Variant | Switch off | Owner | Units | mSUN@20 | Δ vs full (paired) | Better / same / worse | AUDC | Δ AUDC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full agent | none | M1 | 18 | | – | – | | – |
| Planning off | `enable_planning` | M3 | 18 | | | | | |
| Self-correction off | `enable_reflection` | M3 | 18 | | | | | |
| Memory off | `enable_memory` | M4 | 18 | | | | | |
| Exploration off | `enable_exploration` | M5 | 18 | | | | | |
| Tool routing off | `enable_tool_routing` | M2 | 18 | | | | | |

Rules: paired Δ uses the same system and seed. If a component was not delivered or not
run, write "not available" and say why. `m1_baseline` is not the full agent.

Text: [[which components matter, which do nothing measurable, any interactions.]]

## 7. Generalization: development vs held-out (M6)

Required by the brief. Table 3 and Figure 3 come from `M6/generalization.py`:

```bash
python M6/generalization.py --dev [[dev report]]/per_run.csv \
  --heldout [[check or hidden report]]/per_run.csv --heldout-split [[check|hidden]] \
  --output M6/results/[[date]]-generalization
```

- Table 3: `generalization.md` (mSUN@20, AUDC, AF, EF per method; dev, held-out, gap,
  relative gap). Per-system rows go in Appendix B.
- Figure 3: `generalization.svg`.
- Questions to answer:
  1. Does the agent's margin over each baseline hold on held-out systems?
     Compare the agent's gap with the baselines' gaps: baselines are not tuned, so
     their gap shows how much harder the held-out systems are.
  2. Is any drop driven by one system? (per-system rows)
  3. Did we tune on the check set? (No: `M6/PROTOCOL_ADOPTION.md` section 3, and the
     revision check in `generalization.py`.)
- If only 1 seed was used on held-out, say so and do not report an SD.

## 8. Failure classification (M5 + M4 data, M6 text)

At least two failure modes, one real trajectory each. Sources: M5 `decision_log` (rides
the agent checkpoint, `M5/README.md`), M4 evidence export (`M4/export_evidence.py`,
`M4/EVIDENCE_SCHEMA.md`), official trajectories under `M1/MADE/results/protocol_v1/`.

Detection rules (set before looking at results, from `M5/DESIGN.md`):

| Mode | Definition (brief) | Operational signal |
| --- | --- | --- |
| Over-exploitation | Keeps searching near known successes, misses unexplored regions | ≥ [[k]] consecutive steps with mode = exploit, compositions within [[d]] of one formula, no new stable find |
| Wasteful exploration | Spends too much budget on diverse but unproductive candidates | high α(t) with ≥ [[k]] UCB-explore picks returning unstable / not-new outcomes |
| [[Optional 3rd: generator mismatch, invalid structures, duplicates]] | | |

For each mode: Figure 4a/4b (per-query strip: query index, composition, stable?, new?,
mode), run id (`method/split/system/seed/attempt`), how many runs show the pattern
(n / total), and what the agent did (or failed to do) to recover.

## 9. Discussion (M6, with all)

- Which mechanisms contributed most to discovery efficiency (from section 6, with effect
  sizes and run counts).
- Where the remaining bottlenecks are: generator quality, oracle cost per query,
  B=20 being very small, cold start, reward proxy vs mSUN.
- Generalization lessons (section 7).
- Threats to validity: 3 seeds, 6 dev systems, CPU-only ORB, one Materials Project
  snapshot, check set ≠ hidden test.

## 10. Research cost (M2 data, M6 text)

Table 4. Source: `cost` block in each `run_metadata.json`, summarized in M2 `per_run.csv`.

| Method | Oracle calls / unit | LLM calls / tokens | Known USD | Wall time / unit (mean, range) | Hardware |
| --- | --- | --- | --- | --- | --- |
| Agent | 20 | [[if any]] | | | |
| Random | 20 | 0 | 0 | ~16 min (1 unit measured) | GitHub ubuntu-latest CPU |
| Chemeleon | 20 | 0 | 0 | ~4.4 h (1 unit measured) | GitHub ubuntu-latest CPU |

Add total compute for the project (all units, failed attempts included; see
`M2/verification/20261019-chemeleon-timeout/`). Hardware and electricity are not
measured. Say so.

## 11. Reproduction (M1, M2, M6)

- Repo and frozen revision: [[url]] @ [[hash]]; MADE upstream `bffda0c9…`.
- Environment: `cd M1/MADE && uv sync --locked` (lockfile `M1/MADE/uv.lock`), Python 3.12.
- One unit: `uv run python ../../M2/run_baselines.py --method <m> --split <s> --system <X-Y-Z> --seed <17|29|43> --attempt <n>`.
- Check baselines: `M6/run_check_baselines.sh --execute`.
- Scoring: `M2/evaluate.py`; generalization: `M6/generalization.py`.
- Raw trajectories, resolved configs, metadata and failed attempts: [[artifact location]].
- See `M1/REPRODUCE.md` and the README in each `M2/verification/*` folder.

## 12. Limitations and conclusion (M6)

[[Short. Restate the headline with its uncertainty, the most useful mechanism and the
one thing we would do next.]]

## Appendix A. Per-material results (M6 → M2, 27 Oct)

From `per_system_summary.csv` (each split): method, split, system, seeds present,
mSUN@20 (seed values), AUDC, AF/EF vs both baselines, wall time.

## Appendix B. Generalization per-system rows

From `M6/results/[[date]]-generalization/per_system.csv`.

## Appendix C. Team contributions

| Member | Role | Main files |
| --- | --- | --- |
| M1 | Integration, protocol, freeze | `M1/` |
| M2 | Tool routing, baselines, evaluation | `M2/` |
| M3 | Planning and self-correction | `M3/` |
| M4 | Memory and evidence | `M4/` |
| M5 | Exploration policy | `M5/` |
| M6 | Experiment design, generalization, report | `M6/` |
