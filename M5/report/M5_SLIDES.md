# M5 Slides — Content Draft

Owner: Chen Mingsong (M5). For M6 to drop into the shared deck.
3 slides, ~1.5–2 min speaking time. Text is kept short for slides; speaker
notes carry the detail.

---

## Slide 1 — Exploration vs exploitation (the problem & the idea)

**Title:** Exploration policy: budget-annealed UCB

**On-slide bullets:**
- 20 oracle queries per episode — fixed budget, must split explore vs exploit
- Explore = try unfamiliar compositions; exploit = refine near known successes
- Our hook: `adjust_plan(plan, context)` — re-composes the plan's composition
  list (the only steering lever the generators honour)

**One-line takeaway (bottom of slide):**
"Buy information early, spend it late."

**Speaker notes:**
We get exactly 20 oracle calls. The agent has to decide every step whether to
probe a new region of the composition space or dig deeper where it already
found stable materials. My module sits in the M1 pipeline between planning
and generation; its only lever is which compositions the plan asks the
generator to build — M1 confirmed the generators ignore `plan.constraints`,
so composition choice is the whole decision surface.

---

## Slide 2 — Algorithm + decision log

**Title:** GP surrogate + UCB, annealed by remaining budget

**On-slide bullets:**
- Fit a Gaussian process on observed `(composition → e_above_hull)` — ms per fit
- Rank unqueried stoichiometries by `UCB = −μ + β(t)·σ`
- Anneal exploration share and β with remaining budget:
  `α(t) = 0.8 · (remaining / 20)` (early explore, late exploit)
- Every decision → one JSON line: mode, direction, remaining budget, UCB
  stats, rationale → feeds M4's evidence log

**Speaker notes:**
The GP is the cheap oracle: with at most 20 observations it predicts both the
expected energy-above-hull of an unseen composition and how uncertain that
prediction is. UCB balances the two. Both the exploration share and the UCB
weight shrink as the budget drains, so the first half of the episode buys
information and the second half exploits. Every step is logged to a JSONL
sidecar — that log is what M4 uses for the failure trajectories.

---

## Slide 3 — Results + failure modes

**Title:** Exploration rescues hard systems, costs easy ones

**On-slide bullets:**
- Overall wash: +0.2 mSUN, but variance 4.8 → 2.7 (more consistent)
- Rescues hard systems: Co-Mg-Na +5.7 mSUN, Hf-Ni-Zr +2.7
- Costs easy systems: Ga-Pt-Tm −5.3, Mg-Sn-Sr −2.0
- Two failure modes, one trajectory each:
  - **Over-exploitation** (off): 14 straight Sn–Sr binaries, ternary space
    reached only at query 16 → 2 more stable found immediately
  - **Wasteful exploration** (on): ternary Ga–Pt–Tm probes all unstable while
    the Ga–Tm binary stayed rich

**Speaker notes:**
The honest headline is not "exploration wins" — it's that exploration is a
stabiliser and a rescue mechanism. Where the base agent gets stuck, like
Co-Mg-Na, UCB-driven probes pull it out and roughly triple mSUN. Where the
random generator is already productive, like Ga-Pt-Tm, the same probes spend
budget and cost about five mSUN. Both failure modes are visible in single
trajectories: turning exploration off leads to over-exploitation — the agent
locks onto one binary line and misses a whole ternary region — while leaving
it on spends queries on diverse but unproductive probes. Under the current
single-composition planner, exploration is capped at about one slot per step,
which is the main limitation and goes into Future Plans.

---

## Notes for M6

- Use these bullets as-is or tighten to fit the template.
- Slide 3 has two small figures available in `M5/evidence/`: the two failure
  trajectories (episode JSON) — or I can render discovery-curve PNGs if the
  template wants one chart per slide.
- Timing: 3 slides ≈ 1.5–2 min. If the deck needs me down to 2 slides, merge
  1+2 (the algorithm is the interesting part).
