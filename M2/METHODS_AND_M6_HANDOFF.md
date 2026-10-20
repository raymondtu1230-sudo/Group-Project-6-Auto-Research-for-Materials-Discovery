> **2026-10-20 22:14 最新：用户已授权睡眠期间继续本次两项监控和阶段收尾。** 已启用有限次数的每小时复核；即时归档仍由GitHub工作流完成。所有收尾新增/修改严格限定main/M2，不改其他成员、共享记录或根目录工作流。见 [本次自动收尾要求](OVERNIGHT_FINAL_CLOSEOUT.md) 与 [两项启动记录](FINAL_TWO_RUN_STATUS.md)。当前已核验34/36；最终状态须等两项终止后按真实产物更新，不把定时任务启用算作科学完成。以下保留历史快照。

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

## Current independent delivery, 20 October

The current editable draft is report/M2_Method_and_Partial_Results_20261020.pptx, with four slides and speaker notes. Dev coverage is19/36: Random18/18 and Chemeleon1/18. Random has a complete dev aggregate, while Chemeleon has only a labelled Mg-Sn-Sr/17 example. The initial matching-pair curves are retained and explicitly labelled as a single pair. No overall Chemeleon, full-method ranking or routing-effect claim is made.

Latest verified tables and curves are in verification/20261020-handoff-audit/report/. The19 checksum-pinned originals remain unchanged. The earlier two-unit presentation is historical. Suggested M6 insertion positions7/10 come from the prior outline and need confirmation against M6's current deck, which is not present in this repository.

Checkpointable adapter state does not prove resumability during initial baseline pool generation. Full-pool recovery has not passed admission. No new Chemeleon or check/hidden scientific job was launched in this closeout. Check/hidden execution remains with M6, shared integration and the frozen full reference with M1. M2's final routing-off comparison waits for that reference.
