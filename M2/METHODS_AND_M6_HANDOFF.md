# M2 methods and slides material for M6

Status: implementation handoff and presentation draft. Populate performance
numbers only from the workflow's validated real-material report. Full-reference
and routing-off experiments follow the team's frozen M1 integration.

## Methods paragraph

We integrate tool selection through the existing M1 agent interface. The router
chooses between MADE's Random generator and Chemeleon CSP using only completed
query feedback and remaining query budget. Each tool is tried once. Subsequent
choices maximize a smoothed reward plus an upper-confidence bonus, with seeded
tie-breaking; the final two queries use the observed reward without that bonus.
The reward is 1 for stable newly discovered observations, 0.25 for stable-only
observations, and 0 otherwise. This reward is a public feedback proxy and does
not replace the benchmark's mSUN definition. Candidate generation is followed by
the existing M1 filtering and scoring workflow. MADE evaluates one selected
structure per environment step. Generator adapters preserve checkpoint state
without changing the upstream generation algorithms. The plug-in does not
access oracle internals, evaluator state, or hidden ground truth.

## Slide 1: Controlled tool choice

- Fixed components: official runner, oracle, evaluator, environment and B=20.
- New component: select the configured Random or Chemeleon generator.
- Input: public last-query observation and remaining budget.
- Policy: initial tool probes, observed-reward UCB, final-budget greedy choice.
- Control: `enable_tool_routing=false` uses the primary generator. The final
  ablation changes only this flag in the same frozen full agent.

Speaker note: choosing a generator does not make an oracle call. The independent
planning, memory, reflection and composition-exploration switches remain intact.
M2's local development profile is not the team's completed full method.

## Slide 2: Evaluation protocol

- Official Random and Chemeleon baselines; six development systems and seeds
  17/29/43, each in its own process: 36 baseline units.
- ORB `orb-v3-conservative-inf-omat`, CPU, FIRE, fmax=0.02, 500 maximum steps,
  cell relaxation enabled; all settings read from `M1/protocol/protocol_v1.yaml`.
- Primary: official mSUN@B. Secondary: official AUDC, paired AF and EF.
- Plot mSUN and the official AUDC-source curve separately.
- Keep raw trajectories, query history, resolved configuration, revision,
  dependencies, cost metadata and failed attempts.

Speaker note: the official AUDC curve uses `num_newly_discovered_stable`, while
mSUN is `novelty_stable_unique_novel_count`. We call MADE's metric functions and
do not substitute a different definition. Match system, seed and budget when
forming paired comparisons; retain the official zero-baseline convention.

## Slide 3: Results and cost (fill after validation)

Use `per_method_summary.csv` for the comparison table and
`discovery_curves.png`/`.svg` for the curves. Method summaries use equal-weight
system means within each seed, followed by mean/sample SD across the three
seeds. Keep per-system results available to show heterogeneity. An incomplete
method sweep has no overall score. Show AF/EF against both baselines and retain
missing values when a pair is unavailable.

Show oracle query counts and wall time separately from recorded dollar prices.
Hardware/electricity prices are not measured by the current M1 cost recorder.
Do not describe zero recorded model-inference fees as zero total computing cost.
Do not invent token usage for methods that do not report it.

## Evidence already available

- Original M1 contract tests, focused Ruff, and the unchanged official smoke
  script passed on GitHub run `39211626362`.
- Real Materials Project access and three actual Chemeleon sampling calls passed
  on run `39212250266`; resumed and continuous structures matched exactly.
- These verify integration and access, not mSUN/AUDC performance.

## Remaining team dependencies

M1 integrates M3/M4/M5 and freezes the full agent on 25 October. Record that
reference revision for the 26 October full-reference and routing-off runs.
Collect the other owners' ablations and deliver the complete validated table,
curves, cost analysis, failed-run audit and reproducibility details by 27 October.
M6 owns check/hidden-test handling. No hidden test system is encoded in M2 code.
