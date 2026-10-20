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
records supplied by the memory component. New phases count as successes, and
results within 0.1 eV/atom of the hull count as half a success. Formulas that
memory shows failing twice are skipped. The planner thus moves its budget
toward the parts of the system that are paying off. The coverage bonus keeps
it from abandoning unexplored regions early.

The self-correction component checks every plan before it is used. It keeps a
short history of the observed outcomes. It declares the search stuck when the
last six queries produced no new phase. It also declares it stuck when the
plan would repeat a formula already tried twice in that window. When stuck,
it replaces the plan with valid compositions that have been visited least and
lie farthest from the recent queries. If the stall continues, it widens
generation by doubling the candidates per composition. Generating candidates
is not an oracle query, and the integration layer still caps the plan at the
remaining budget. A three-query cooldown prevents back-to-back re-plans, and
any discovery resets the escalation.

Both components use only public state and post-query observations. They never
read the hidden phase diagram and never call the oracle. Each oracle query
remains one environment step under MADE's budget enforcement. All randomness
is seeded from the experiment seed and step, and all state is
JSON-checkpointed, so runs are reproducible and resumable. Neither component
uses a language model, so planning adds no API cost.

## Evaluation design

M3 is measured against M1's reference agent (`m1_baseline`: diversity planner,
memory on, reflection off). The reference is re-run under the same integrated
configuration as the M3 runs, including M4's memory manager. M1's earlier
reference runs predate that memory configuration and are reported for context
only. All runs use the six protocol development systems, seeds 17, 29 and 43,
a 20-query budget and the ORB v3 oracle. Three configurations isolate M3's
parts:

- `m3_full`: planner and self-correction both on.
- `m3_planning_off`: planning off.
- `m3_self_correction_off`: self-correction off.

The primary metric is the official mSUN count. AUDC, acceleration factor and
enhancement factor are reported alongside it. Comparisons are paired by system
and seed. Self-correction events are logged, so discoveries can be linked to
the re-plans that preceded them. Following the team protocol, these results
are a component-versus-reference comparison, kept separate from the frozen
agent's component ablations. Results are in `M3_RESULTS.md`.
