# Update — 26 October 2026

The current shared scoreboard, peer validation, baseline AF/EF, curves, costs and M6 assembly text are in [M2/aggregation/20261026](aggregation/20261026/README.md). It includes 126 validated real dev episodes. M3 component profiles are kept separate from Full single-switch ablations, and the missing raw m3_full comparator and remaining group inputs are explicit. This completes aggregation of the currently received results; the entire group handoff remains open. No new native PPTX is claimed by this update.

---

## Previous stage record, preserved

# M2 methods and results for M6, 25 October 2026

M2's development baselines and frozen tool-routing ablation are complete. The 36 original baseline results are reused after compatibility checks. All 18 routing-off episodes completed 20 queries. The frozen M1 Full reference comes from M1.

## Method and controlled comparison

The router chooses between checkpointed Random and Chemeleon generators from observed query feedback. It probes each tool, then uses a smoothed reward with an upper-confidence bonus. The last two queries use the reward without that bonus. The reward is a proxy for observed progress, separate from the official mSUN metric.

The frozen tag is `m1-freeze-20261025`, commit `02e0026bf450f71f4f7862228d295f5b02b49e12`. The ablation changes only `enable_tool_routing=false`. Planning, memory, self-correction and exploration remain enabled. The primary generator remains checkpointed Random. The scientific entrypoint was the frozen `M1/run_experiment.py`, with six dev systems, seeds 17/29/43, CPU ORB v3 conservative, B=20 and one episode per system and seed. No ablation ran on check or hidden systems.

## Development results

| Method | Units | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | --- | --- | --- |
| Random baseline | 18 | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon baseline | 18 | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen M1 Full | 18 | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Tool routing off | 18 | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |

Each seed mean weights the six systems equally. We then report the mean and sample SD across the three seed means. The paired difference, routing off minus Full, is −2.2778 mSUN and −17.9722 AUDC. This supports a benefit from routing in this frozen development setting. It does not establish that routing improves every system or unseen materials.

The final scores are the original official trajectory/summary values. The baseline compatibility audit checked all 36 original ZIP hashes, exact protocol equality, material-reference identity and 288 shared scientific-input hashes. No baseline was rerun.

## Curves, AF/EF and evidence

Current evidence: [verification/preserved-40204426478/report/](verification/preserved-40204426478/report/). The paired endpoint table is in [endpoint_comparison/perunit.csv](verification/preserved-40204426478/report/endpoint_comparison/perunit.csv), and seed aggregation is in [endpoint_comparison/method_summary.csv](verification/preserved-40204426478/report/endpoint_comparison/method_summary.csv).

The official runner deletes successful checkpoints before the post-exit collector reads them. The original 18 collection/audit failures remain unchanged. A separate endpoint audit accepted the completed science from original metadata, resolved configurations, trajectories, summaries, source hashes, exits and component logs.

The discovery curves are separate offline re-evaluations of the recorded structures and energies with frozen official metric functions. They passed all 720 original baseline prefix checks and all 72 original final mSUN/AUDC endpoint checks, with zero new proposals or model/oracle calls. See [recorded_curve_analysis/reevaluation_audit.json](verification/preserved-40204426478/report/recorded_curve_analysis/reevaluation_audit.json) and [paired_AF_EF.csv](verification/preserved-40204426478/report/recorded_curve_analysis/paired_AF_EF.csv). These are analysis outputs, not recovered historical checkpoints. AF/EF retain the official zero-baseline convention and EF cap; neither is a wall-time speedup.

The visible required M2 payload is verified for 18 units. The uploader omitted three raw hidden `.hydra` files per unit. Those 54 original attachments remain missing and are listed in the audit. Several M1 reference configuration/log attachments are also absent. We have not reconstructed them or claimed complete byte-for-byte original archives.

## Cost and handoff

The cost tables retain the actual machine, platform, driver time, budgeted query count and recorded fees. Known model-inference fees are USD 0. Hardware, electricity and unpriced failed attempts are excluded, and unknown token usage stays unreported. M1's reference and the cloud runs used different machines, so their times do not establish a controlled speedup.

Current [four-slide English source](report/M2_Frozen_Routing_Slide_Content_20261025.md) and [speaker notes](report/M2_SPEAKER_NOTES_20261025.md) are ready. The native PPTX remains pending; the 21 October baseline-only deck is historical. See [STAGE_ACCEPTANCE_20261025.md](STAGE_ACCEPTANCE_20261025.md).

M2 still needs the other members' frozen ablations and M6's check/hidden evaluation outputs for the group scoreboard by 27 October. M2 validates and combines those results without changing or rerunning their experiments. The final tables, curves, costs, results text and slide contribution go to M6. No message was sent and no receipt or acceptance is claimed.

---

## Historical record: 21 October baseline handoff

The text below is preserved from the earlier stage. Its pending items and counts do not describe the current result.

> **2026-10-21终态：36/36项独立dev基线验收并完成本阶段收尾。** Random18/18、Chemeleon18/18，720次成功查询；两项最终attempt均exit_code=0，官方复评issues=[]，SHA256/CRC与终态receipt核验通过。最新入口：[CURRENT_STAGE_CLOSEOUT.md](CURRENT_STAGE_CLOSEOUT.md)。仅M2范围。M1 reference、routing-off和M6 check/hidden为后续。以下旧状态保留为历史快照。

## 历史记录（下文按原日期保留）

> **保存状态补充：本次原始压缩包的手动持久上传被自动审批拒绝。** 理由是包中含运行/环境日志，审批系统认为未明确授权这份具体载荷的外部披露。30个文本成员及结束日志的凭据模式检查未发现匹配，但不能据此绕过拒绝。原始包仍在GitHub Actions artifact12283509799（90天副本）和本次本地下载中；本次只发布评分、图表、状态和交付文档。**因此Au-K-Tb/17已完成科学验收，完整原始包写入main的收尾仍待允许，不能称单项已彻底收尾。** 原有34项的持久归档不受影响。

> **2026-10-21 当前：35/36项dev基线已验收。** Random18/18、Chemeleon17/18。Au-K-Tb/17完整20/20查询，mSUN3、AUDC33.5；35项官方复评、曲线、成本及M2自己的4页PPT已更新，原始包上传受阻，证据见[CURRENT_STAGE_CLOSEOUT.md](CURRENT_STAGE_CLOSEOUT.md)。Co-Dy-W/43仍在既有run39432570527计算，不重新派发。下列旧19/34项及未启动描述均为历史快照，不是当前状态。最终36项阶段收尾和M1 reference/routing-off等后续任务尚未完成。

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

## Current independent delivery, 21 October

The independent development baseline stage is complete:36/36 units,18 for each method,720 oracle queries, official validation issues=[]. Use report/M2_Method_and_Dev_Baselines_20261021_36of36.pptx and report/M2_SPEAKER_NOTES.md for the current four-slide contribution. Earlier slides and state entries remain historical snapshots.

Official final data: verification/direct-39432570527-1/final-report/. Random mean mSUN4.0556 and AUDC40.5833; Chemeleon6.9444 and71.3056. Aggregation gives equal weights to systems within each seed, then uses the three-seed mean and sample SD. The labelled editable curves show the Mg-Sn-Sr/17 example, while all-system curves remain in the report. The official AF/EF zero-baseline convention remains unchanged. EF100 at Co-Dy-W/17 is not a measured compute speedup.

Archive checksums/CRC, uniqueness and final receipts: verification/stage-closeout-39432570527/terminal-validation.json. Original19 manifest unchanged. The current reuse manifest contains36 persistent archives. Known model feesUSD0 exclude hardware, electricity and all unpriced failures. Mean driver times16.0/234.3 minutes are separate from complete Actions job times.

M1 receives integration code and existing test evidence. M6 receives validated baseline data, curves, methods, cost caveats and M2's slides. This stage does not measure routing benefit. Same frozen M1 reference, routing-off and check/hidden remain later work. No messages were sent and no recipient acceptance is claimed.
