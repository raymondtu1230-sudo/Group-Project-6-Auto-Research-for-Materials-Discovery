# M5 Work Log — Chen Mingsong

Raw material for the individual report (due 3 Nov). Rule from the task split:
log what you built, what failed, what you learned. Negative results are fine —
explain why and what you'd change.

## 2026-10-19

**Setup & environment**
- Read the task split PDF and the step-by-step guide end-to-end; mapped my role
  (M5 exploration) against the handover deadlines. Pulled the Group C sheet to
  confirm the team roster and presentation constraints.
- Cloned the group repo and audited every member's progress. Found M1/M2/M3/M4
  ahead of schedule; M4 was blocked waiting on my log-format confirmation;
  M6 had not started.
- Got the MP API key installed locally (`.env` + user env var). Diagnosed why
  `mp-api` didn't read it natively (it honors `MP_API_KEY`; MADE reads
  `MATERIALS_PROJECT_API_KEY` and passes it explicitly). Verified with an
  `mp-149` query, then with MADE's own `PhaseDiagramDataset` on Mg-Sn-Sr (203
  entries — matches M1's official number).
- **Pitfall fixed**: older MP records fail Monty decoding on new pymatgen
  (`No module named pymatgen.core.entries`). Applied M1's patch pattern:
  register a `sys.modules` alias `pymatgen.core.entries →
  pymatgen.entries.computed_entries`. Worked immediately.

**Design**
- Drafted the one-page design: budget-annealed UCB over composition space.
  Key early decision: the hook only controls `Plan.compositions` /
  `num_candidates` / `constraints`, so "exploration vs exploitation" became
  "how many fresh stoichiometries to append to the planner's list", with α(t)
  and β(t) annealing as a function of remaining budget.

**Delivery (code)**
- Implemented `UCBExplorationPolicy` in pure numpy (GP surrogate via RBF
  kernel + Cholesky; UCB = -μ + β·σ; stoichiometry enumeration with reduced-
  formula dedup). No new dependencies — GP fit is milliseconds at n ≤ 20.
- Wrote 10 contract tests mirroring M1's style. **Bug found while testing**:
  Python's `round()` uses banker's rounding, so `round(0.5) = 0` silently
  swallowed the exploration slot for single-composition plans. Fixed with
  `int(x + 0.5)`.
- Verified: 27 tests pass (17 M1 contract + 10 M5), ruff clean, official
  smoke run completes with `enable_exploration=true`.
- Confirmed M4's evidence log schema v1 and sent back the fields my policy
  will emit (`decision_log` with mode / direction / remaining budget /
  UCB stats / rationale). Asked M4 whether rejected/error events can be
  captured before 26 Oct — they materially improve the wasteful-exploration
  failure case.

## 2026-10-20

**Integration & hardening**
- Wired the component into `m1_integrated.yaml` (switch defaults off so M1's
  reference behavior is unchanged). Verified a full smoke run with only the
  switch flipped — no extra Hydra overrides needed. Pushed to main.
- Overheard M1's reply to M6 in the group chat: `m1_full` will use M3's
  planner + M4's memory; held-out runs will only execute `m1_full`, Random,
  Chemeleon. Freeze date is **25 Oct**. No action needed from me, but it
  confirmed which memory format my policy must handle.

**Real bug found by reading teammate code (Lesson #1)**
- Verified whether M4's `memory_manager` output includes `e_above_hull` (it
  does — good). But reading `M4MemoryManager.get_memory()` revealed the
  returned records are bounded by `limit` (default **8**). My original logic
  only excluded already-queried formulas based on `m1_memory`; once a record
  aged out of that window, the corresponding stoichiometry became re-proposable
  and the UCB pool could waste queries re-testing it.
- **Fix**: the policy now accumulates its own episode-level
  `_queried_history` (every formula ever observed, regardless of the memory
  window) and excludes that set from the explore pool. History rides the
  checkpoint via `queried_formulas`. Added a regression test simulating an
  aged-out record.
- 28 tests pass, ruff clean, pushed as commit `bc97609`.

**Lessons learned (raw notes for the individual report)**
- Component boundaries matter more than algorithm cleverness. Reading the
  interface contract (`adjust_plan` sees only `Plan` + context dict)
  immediately told me which levers I had — and that my original "I'll pick
  the generator" idea was out of scope. Design inside the sandbox first.
- Contract tests caught a subtle Python semantics bug (`round`) before it
  silently degraded the ablation. Banker's rounding is easy to forget.
- Reading teammates' code (`M4MemoryManager`) surfaced a correctness issue my
  own tests couldn't see — my fake memory fixtures were unbounded. Test with
  realistic constraints from the start.
- Windows-specific: MADE crashes on Chinese-locale machines unless
  `PYTHONUTF8=1` is set (GBK codec fails on the bundled HHI data file).
  Documented in SETUP_NOTES_小组.md.

## Pending / next

- [x] ~~Align with M1 on B=20 and `plan.constraints` semantics~~ — done 20 Oct:
      B=20 is the team's protocol-v1 choice (consistent across methods);
      constraints are ignored by the built-in generators, so composition
      steering via `plan.compositions` is confirmed as the only effective lever.
- [ ] First real-system run of the policy (target 21–23 Oct); watch for
      over-exploitation / wasteful-exploration candidates
- [ ] Send M4 a decision_log sidecar for a format dry-run
- [ ] Run the exploration ablation (26–27 Oct) on own laptop

## 2026-10-26

**Ablation run (exploration_off)**
- Ran the full exploration_off sweep: 18 episodes (6 dev systems × seeds
  17/29/43), frozen protocol v1, via M3's resume-friendly `run_ablations.py`
  at `--jobs 4` (32-thread laptop). All completed clean; results committed to
  `M1/MADE/results/protocol_v1/exploration_off/`.
- Paired against M1's frozen `m1_full` (same systems/seeds). Result: overall
  wash (+0.2 mSUN, −1.2 AUDC) but variance drops 4.8→2.7. Exploration rescues
  hard systems (Co-Mg-Na +5.7, Hf-Ni-Zr +2.7) and costs easy ones
  (Ga-Pt-Tm −5.3). Analysis in `M5/report/M5_RESULTS.md`.
- Two failure trajectories chosen: over-exploitation = OFF Mg-Sn-Sr seed 29
  (14 consecutive Sn-Sr binaries, ternary region only reached at queries 16+
  where it immediately yields 2 stable); wasteful exploration = ON Ga-Pt-Tm
  seed 17 (ternary Ga-Pt-Tm probes all unstable while the Ga-Tm binary was
  rich).

**Lessons (raw notes)**
- An ablation can be a wash overall yet still worth writing up: the mechanism
  (risk reduction on hard systems vs budget cost on easy ones) is the result.
- Parallel runs on a laptop with ORB-on-CPU means per-episode wall time grows
  ~3-4×; total throughput is flat. 4 jobs saturated 32 threads.
- M1's frozen reference runs lack the `m5_decisions.jsonl` sidecar — likely
  the install.py re-run I flagged on 21 Oct was not done on their side. Flagged
  to M2/M6 in M5_RESULTS.md with a manual-annotation fallback.

## Pending / next

- [x] Run exploration_off ablation (26 Oct) — DONE
- [x] Pick 2 failure trajectories — DONE (see M5_RESULTS.md)
- [ ] Send results + failure section to M2/M6 (commit `d6d4e88` is the
      handover; message drafts ready)
- [ ] Finish M5 slides; review own report section (28–29 Oct)
- [ ] Individual report (3 Nov)
