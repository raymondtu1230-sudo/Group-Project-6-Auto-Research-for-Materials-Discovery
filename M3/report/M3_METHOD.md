# Planning and self-correction

## Method

The planning component decides which composition the agent queries next. It
treats discovery in a chemical system as a set of sub-goals, one for each
subset of the system's elements. A ternary system therefore has three binary
edges and one ternary interior. The planner works in short batches. During a
batch of four queries it stays on one sub-goal. There it chooses the
composition that has been attempted least and lies farthest, in composition
space, from everything already tried. Candidates must pass the SMACT
charge-balance check. After each batch the planner reviews all sub-goals that
still have untried compositions. It scores each one by its smoothed success
rate, `(successes + 1) / (attempts + 2)`, plus a bonus for the share of
compositions not yet tried. The highest-scoring sub-goal becomes the next
target. When memory is enabled, the review also counts the bounded memory
records supplied by the memory component. New stable phases count as
successes, and other results within 0.1 eV/atom of the hull count as half a
success. Formulas that memory shows as unstable twice are skipped. The planner
thus moves its budget toward the parts of the system that are producing stable
phases. The coverage bonus keeps it from abandoning unexplored regions early.

The self-correction component checks every plan before it is used. It keeps a
short history of the observed outcomes. It declares the search stuck when the
last six queries produced no new stable phase. MADE marks every structure not
seen before as newly discovered, stable or not, so that mark alone is not
counted as progress. It also declares the search stuck when the
plan would repeat a formula already tried twice in that window. When stuck,
it replaces the plan with valid compositions that have been visited least and
lie farthest from the recent queries. If the stall continues, it widens
generation by doubling the candidates per composition. Generating candidates
is not an oracle query, and the integration layer still caps the plan at the
remaining budget. A three-query cooldown prevents back-to-back re-plans, and
any new stable phase resets the escalation.

Both components use only public state and post-query observations. They never
read the hidden phase diagram and never call the oracle. Each oracle query
remains one environment step under MADE's budget enforcement. All randomness
is seeded from the experiment seed and step, and all state is
JSON-checkpointed, so runs are reproducible and resumable. Neither component
uses a language model, so planning adds no API cost.

## Evaluation design

All runs use the six protocol development systems, seeds 17, 29 and 43, a
20-query budget, the ORB v3 oracle and one episode per run. Comparisons are
paired by system and seed, and tested with a two-sided sign test over the
pairs that differ. The primary metric is the official mSUN count; AUDC is
reported alongside it. M3 is evaluated in two studies.

**Full-agent ablations.** M3's assigned ablations start from M1's frozen agent
(`m1_full`, tag `m1-freeze-20261025`), with all five components on. Each
ablation switches off exactly one M3 component and keeps memory, exploration
and tool routing on:

- `planning_off`: planning off, so the agent proposes the full chemical system
  at every query instead of following the planner's sub-goals.
- `self_correction_off`: self-correction off.

Each has 18 runs, paired with M1's 18 `m1_full` reference runs and using the
same Chemeleon checkpoint archive and evaluator. These results belong in the
frozen agent's component-ablation table.

**Component study.** This study isolates M3's parts with exploration and tool
routing off:

- `m3_full`: planner and self-correction both on.
- `m3_planning_off`: planning off.
- `m3_self_correction_off`: self-correction off.

These are compared with M1's reference agent (`m1_baseline`: diversity
planner, memory on, self-correction off), re-run under the same configuration,
including M4's memory manager. M1's earlier reference runs predate that memory
configuration and are reported for context only. The three `m3_*` versions
were re-run on the frozen tag and reproduce the development runs exactly.
Following the team protocol, these results are a component-versus-reference
comparison, kept separate from the frozen agent's ablations.

Self-correction events are logged in both studies, so discoveries can be
linked to the re-plans that preceded them. Results are in `M3_RESULTS.md`.
