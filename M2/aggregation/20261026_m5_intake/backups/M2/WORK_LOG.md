> **2026-10-25 当前：M2 自己的 dev 基线与冻结版 routing-off 实验已收尾。** 36 项旧基线经完整兼容性检查后复用；18 项新消融均完成 20/20 查询。全组结果接收与汇总仍待 27 Oct，新的结果 PPTX 尚待完成检查。以下保留旧工作日志，历史快照不覆盖本条当前状态。

## 25 October 2026: frozen routing ablation and evidence closeout

- Used tag `m1-freeze-20261025`, commit `02e0026bf450f71f4f7862228d295f5b02b49e12`. Scientific source/config stayed frozen. Only `enable_tool_routing` was disabled. All 18 dev system/seed units completed one B20 CPU ORB episode. No check/hidden ablation was run.
- Verified the actual Chemeleon weight archive SHA256 and CPU model loads in all 18 execution records. The archive hash is `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`.
- Rechecked all 36 original baseline ZIP hashes and paired references/protocols, plus 288 shared scientific-input hashes. All passed, so no completed baseline was rerun.
- Full averages mSUN 10.0000 / AUDC 88.1111; routing-off averages 7.7222 / 70.1389. These results support routing in this development configuration, not a universal or held-out claim.
- The official runner deletes successful checkpoints before post-exit collection. All 18 original collection audits remain unsuccessful and unchanged. Independent endpoint checks accepted the actual 20-query trajectories, summaries, settings, source hashes, component logs and exits.
- The artifact uploader excluded three hidden raw Hydra files per unit. All 54 missing attachments remain listed. They were not fabricated or replaced with reconstructed originals.
- A separate offline analysis applied frozen official logic to original recorded structures/energies. It passed all 720 original baseline prefix checks and all 72 original final endpoints. This produced analysis curves and paired AF/EF with zero new model/oracle calls or proposals. These are not recovered historical checkpoints.
- Preserved the first failed offline analysis run `40203822525`: report JSON serialization rejected a NumPy scalar. The fix changed only lossless JSON conversion; the successful retry reran analysis, not science. Earlier missing-history attempts and original failures remain evidence.
- Updated M2 handoff/method/result text, a four-slide English content source and a matching speaking script. The native frozen-results PPTX remains pending refresh and visual QA. No group message was sent and no acceptance was claimed.

What we learned: collect ephemeral checkpoints while the runner still owns them, preserve hidden attachments deliberately, and distinguish a completed scientific episode from a later collection failure. For the current outputs, original endpoint checks and separately validated record-only re-evaluation supply distinct evidence. Neither justifies inventing a missing original file.

Remaining responsibility: collect M3/M4/M5 frozen ablations and M6 check/hidden outputs, validate and send the combined table/curves/costs to M6 by 27 Oct. Review own section on 28 Oct, rehearse on 29 Oct, and prepare the individual report due 3 Nov.

---

> **2026-10-21终态：36/36项独立dev基线验收并完成本阶段收尾。** Random18/18、Chemeleon18/18，720次成功查询；两项最终attempt均exit_code=0，官方复评issues=[]，SHA256/CRC与终态receipt核验通过。最新入口：[CURRENT_STAGE_CLOSEOUT.md](CURRENT_STAGE_CLOSEOUT.md)。仅M2范围。M1 reference、routing-off和M6 check/hidden为后续。以下旧状态保留为历史快照。

## 历史记录（下文按原日期保留）

> **保存状态：** 用户于2026-10-21 02:28明确授权并入main/M2。现有35项的原始归档、日志、官方评分和M2交付材料已纳入本次保存；最后一项Co-Dy-W/43仍在原任务计算，尚不计为完成。原审批拦截作为历史记录保留。

> **2026-10-21 当前：35/36项dev基线已验收。** Random18/18、Chemeleon17/18。Au-K-Tb/17完整20/20查询，mSUN3、AUDC33.5；35项官方复评、曲线、成本及M2自己的4页PPT已更新，原始包及必要日志已纳入本次保存，证据见[CURRENT_STAGE_CLOSEOUT.md](CURRENT_STAGE_CLOSEOUT.md)。Co-Dy-W/43仍在既有run39432570527计算，不重新派发。下列旧19/34项及未启动描述均为历史快照，不是当前状态。最终36项阶段收尾和M1 reference/routing-off等后续任务尚未完成。

> **2026-10-20 22:14 最新：用户已授权睡眠期间继续本次两项监控和阶段收尾。** 已启用有限次数的每小时复核；即时归档仍由GitHub工作流完成。所有收尾新增/修改严格限定main/M2，不改其他成员、共享记录或根目录工作流。见 [本次自动收尾要求](OVERNIGHT_FINAL_CLOSEOUT.md) 与 [两项启动记录](FINAL_TWO_RUN_STATUS.md)。当前已核验34/36；最终状态须等两项终止后按真实产物更新，不把定时任务启用算作科学完成。以下保留历史快照。

> 交付方式：本轮材料通过 PR #5 单独交付至 `main/M2/`；用户已于2026年10月20日授权合并。共享框架接入仍由M1负责，PR #2 保留草稿。下述验收数字及失败对应审计时版本；本次文件交付不包含对后续共享代码变更的复验。

## 2026年10月20日：用户授权发布独立M2交付

用户明确授权将收尾草稿合入自己的M2文件夹。PR #5 的全部改动均在 M2/，与此后其他成员的提交没有文件冲突。只更新本轮发布说明；原始结果、历史验收日志、其他成员目录及 PR #2 保持原状。本次不启动实验或定时跟进，群消息仍由用户发送，未获接收确认。

# 2026年10月20日：M2职责复核和独立交付收尾

重新读取两份分工PDF、四张微信要求及M1接口文件。确认M2负责dev基线、工具路由、指标/曲线/成本和自己的方法/幻灯片材料。M1负责正式集成和reference，M6负责check/hidden及组稿。没有启动曾讨论的12项check Random；不把该项作为M2漏做。

19份固定原始ZIP逐一核对SHA256和CRC，原始字节不变。重新导入并使用原有官方指标离线评分，复现19项以及已发布数值表，issues=[]；没有新增实验或重复计数。

在全新main70e8a7e的隔离副本安装M2槽位并实际执行全部M1/M2测试：77通过、M5 seed=None失败1项、此容器/proc观测跳过1项。保存完整日志/JUnit，未修改M5或M1的共享配置来隐藏失败。当前Ruff初扫误入历史快照；M2配置仅排除verification不可变证据，当前源码仍全查，随后通过。

更新M2 README、独立交付映射、职责表、方法和讲稿、群消息草稿与结果接收规范。幻灯片更新为19/36，Random完整dev汇总和Chemeleon单项的覆盖差异明确标注，示例曲线的原始图表数据及工作簿保留。旧版本保留供追溯。恢复测试失败仍如实列明。

所有交付只写main/M2，正式M1集成和其他成员记录不动。消息不代发，PR2不合并，不声称对方收到。未开新Chemeleon、check/hidden、GPU或付费任务。完成交付即停止，不安排后续轮询。

## 以下为保留的历史工作日志

# Latest bounded closeout — 20 October 2026, 02:57 Asia/Singapore

Accepted development baseline coverage is **19/36**: Random 18 and Chemeleon 1, with zero audit issues. All 17 missing Random jobs succeeded. Their frozen-source final aggregation failed; no science was rerun. Evidence-only capture 39306348134 reused existing ZIP bytes, preserved 23 original archives with matching GitHub SHA256, executed the current offline audit and unchanged official metrics, and published to main/M2/verification/preserved-39306348134/. The original pair is counted once. The reuse manifest now pins 19 accepted archives; all paths are present on main.

Exact recovery 39297647516 failed during replay at the identity guard, before comparison. Original continuous, interrupted and failed-resume archives and the failure log are saved. Which identity field differs is not established. No retry or formal Chemeleon dispatch occurred. The remaining 17 units require diagnosed exact recovery, full-wrapper proof and cost validation, or adequate CPU runtime. Main/M1/M5, scientific parameters, check/hidden and GPU execution remain untouched. A GPU preparation guide and unsent handoff draft are saved on main/M2.

Source 78346d6 CI 39306348142 completed: 17 M1 and 62 M2 passes, no skips, both Ruff checks, installation reproducibility and official smoke. This development-configuration result is separate from the existing shared-main M1/M5 failure. PR2 was verified open, draft and unmerged; its branch is retained. Publication uses expected-head leases and all main changes stay under M2. Local disk/proxy failures did not delete user data or prevent hosted evidence publication.

Per the user's stop rule, close this bounded work and pause hourly follow-up after final verification; do not claim all M2 work is complete. See verification/20261020-overnight-closeout/README.md for blockers, tasks and links.

## Preserved historical log

# M2 work log

## Latest continuation — 20 October 2026, Singapore time

This section supersedes the older retry-only authorization and stopped-monitor
wording below. The user explicitly authorized completion of the missing 34 dev
baseline units. Preserve the already accepted Mg-Sn-Sr/17 pair and all failed
attempts. Main changes remain under M2; M1 integration and freeze stay with M1.

- Accepted scientific baseline coverage remains **2/36**, with 17 Random and
  17 Chemeleon units still unaccepted. No new scientific score is claimed.
- Previous Random workflow 39284865198 stopped in prepare at Ruff import
  sorting before any scientific unit was scheduled. Source CIs 39284459462,
  39284865097 and 39285316822 also stopped at all-M2 Ruff; their skipped smoke
  steps are not passes. Full raw job logs are retained in
  [the continuation audit](verification/20261020-preflight-and-recovery/README.md).
- The two test-import blocks were corrected under MADE's Ruff configuration.
  Revision `b3f68f274373d4599a7e026cd0f3cf5a9889e977` starts
  [missing-only Random run 39286848821](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286848821).
  Its prepare job has now passed the current checks including official smoke,
  and retained-evidence validation. The 17-unit matrix is released;
  two Random jobs were performing scientific computation and 15 were queued
  at the 16:40 UTC observation. Its matrix admits only missing Random
  units, at most four concurrently; an existing completed pair is never rerun.
- Actual small-model recovery run
  [39285316913](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39285316913)
  passed its continuous/interrupted/cross-process checks with two Li2O candidates,
  batch=1 and unchanged 256 diffusion steps. Artifact 12201404998 has GitHub
  digest `8570dbc27d6a286c60a994ccb4d704169ef4f0c58247c9a0c926ff88a65eace9`.
  This turn inspected raw logs and artifact metadata, but has not independently
  downloaded and rehashed this non-scoring artifact.
- [Batch256 cross-runner run 39286986254](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986254)
  is submitted at fixed source `e30b5bb233842797f4ad90c80732bb327d07c0bf`.
  Its two sampling jobs were queued at last inspection. It uses a 512-candidate
  Li2O validation fixture, two original batch=256 calls, an uploaded checkpoint
  and restoration on a separate runner. It requires exact structures, RNG,
  preserved first-batch bytes and distinct runner hostnames. This is **not a
  benchmark result or proof of full protocol-pool compatibility**. No formal
  Chemeleon unit has been scheduled using this experimental cache.
- Fresh isolated local checks for this turn's development source (not the
  concurrently published main prototype): 17 M1 tests and 53 M2 tests passed, no skips in
  this host invocation; focused and complete M2 Ruff passed. Local official
  smoke reached Chrome export but stalled and was terminated as an incomplete
  synthetic check. The earlier local CPU-namespace skip and Chrome socket
  failure remain historical records, not passes. Current GitHub gate is the
  source of truth for hosted smoke.
- Current-source CI [39286986328](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986328)
  at `e30b5bb` now passed all gates, including reproducible installation,
  original M1 tests, all M2 tests, both Ruff checks and unchanged official smoke.
  CI 39286848820 was still pending at its earlier inspection.
- Keep the M2 development branch and draft PR #2. Do not merge, delete branches,
  change official parameters, or edit the old retry-request.json. Routing-off
  still depends on M1's frozen full-method reference; M6 owns check/hidden tests.


## Earlier takeover snapshot (preserved)

## 19 October 2026: continuation after interrupted conversation

- Recovered the original user requirements and reread the five required M1
  interface/source files plus course and team deliverables. Kept the existing
  branch/PR, owner boundaries and unchanged official benchmark settings.
- Downloaded actual artifact 12169366866 from run 39213257750. Its SHA-256
  matched GitHub's digest. The Random Mg-Sn-Sr/17 trajectory has all 20 queries,
  the actual Hydra configuration and full official per-query history.
- Executed the offline evaluator on that real evidence: one accepted run and
  zero validation issues. mSUN@20 is 7 and AUDC is 55.5; these are one-unit
  development values. Produced and visually inspected both discovery curves.
- Preserved raw data/checksums, missing-unit audit and tables in the verification
  folder. No overall baseline mean/SD or missing paired metric was fabricated.
- Diagnosed why a heartbeat cannot establish scientific progress: child logs
  were redirected and buffered until completion. Added unbuffered child output
  plus CPU/log/batch diagnostics to new attempts, without changing any material
  computation, query count or selection policy.
- A real local child-process test exposed incompatible process IDs in the host
  `/proc` namespace. Added namespace validation so those counters stay unknown.
  The CPU-growth assertion is mandatory on GitHub Linux and explicitly skipped
  on the incompatible host; it is not counted as a locally passed assertion.
- Initial local test run: 61 passed, one diagnostic assertion failed because of
  that namespace limitation. After the guard, focused diagnostics: two passed,
  one explicitly skipped. Ruff passed. Keep the subsequent CI run as the source
  of truth for the complete handoff verification.
- GitHub run 39217841268 executed 17 original M1 contracts and 45 M2 tests,
  including actual live CPU-counter growth, with no failures or skips. Its next
  lint step found one import-group formatting issue under MADE's Ruff config.
  Fixed that formatting and reran the exact lint command from `M1/MADE`; it
  passed. A follow-up CI run must complete the remaining original smoke gate.
- Chemeleon's full protocol unit remains separate from the earlier three-call
  model-continuation check. A generation check does not establish discovery
  performance. Preserve the active frozen run rather than duplicate it.

Lessons: distinguish conversation connectivity, workflow status, actual process
work and completed oracle queries. Treat unknown progress as unknown. Report
unit-level scores only with their raw evidence and never as a full comparison.

## 19 October 2026: independent folder delivery on main

- Complete follow-up CI 39218278124 passed on b8e2c0c: 17 M1 contract tests,
  45 M2 tests, both Ruff checks, reproducible installation and the unchanged
  official smoke script. Updated the status to record this completed evidence.
- The user confirmed that the delivery folder is the existing `M2/`, separate
  from M1's work. Their screenshot showed `main` containing only M1 and M4;
  the earlier M2 link pointed to the development branch instead of that view.
- Prepared the independent M2 source/evidence folder for main, including copies
  of its workflow definitions. Kept main's M1, M4 and root files unchanged and
  kept PR #2's integration changes separate from this folder publication.
- No scientific run was cancelled, restarted or duplicated for packaging.

## 19 October 2026: verified timeout cause and one-unit recovery

- Read actual jobs/artifacts after the Chemeleon gate ended at 17:47 Singapore
  time. Its action log explicitly states a 165-minute timeout. Older job
  117924795008 ended with a cancelled conclusion at 17:40; its available log
  does not identify a cancellation actor.
- Downloaded artifacts 12177571578, 12177865607 and 12176904574 and verified
  all three SHA-256 digests against GitHub. Preserved untouched ZIPs, both job
  logs and source provenance in `verification/20261019-chemeleon-timeout/`.
- Model process logs show three complete batches in both attempts and progress
  in batch 4. The new gate completed its first three batches in 52:38, 51:28
  and 55:28, then reached step 3/256 in batch 4. This establishes computation,
  not a deadlock. No complete candidate-generation checkpoint was preserved.
- Kept missing final metrics/configuration/query histories explicit. The
  original partial report accepts only the existing Random unit and records
  the incomplete Chemeleon attempt. Baseline completion remains 1/36.
- Prepared one bounded Chemeleon-only retry with 330/350-minute action/job
  limits. The manual input defaults to recovery; Random and the wider sweep
  are excluded, and a rerun of the same recovery run is blocked. Model, seed,
  pool, batch size, CPU, official science code and B=20 are unchanged.
- Extended only external diagnostics to expose numeric diffusion sampling
  steps and elapsed time. New tests/checks must run before launch; the earlier
  CI is not represented as verification of this modification.

## 19 October 2026: exact M1 handoff acceptance audit

- Reconciled the user's pasted handoff requirements with all five required M1
  files and the actual M2 implementation. Recorded the requirement-to-file
  mapping and remaining gates in `ACCEPTANCE_CHECKLIST.md`.
- Synced current main into the existing M2 development branch. Resolved three
  documentation add/add conflicts using main's published M2 versions; preserved
  current M4 contents and the previously tested M1 integration code exactly.
- Local repeat: 17 M1 and 44 M2 tests passed, with the incompatible local CPU
  namespace check explicitly skipped. Ruff and installation reproducibility
  passed. No skipped local test is represented as a pass.
- GitHub run 39221672640 passed on 2b2c6753: 17 M1 and 45 M2 tests with no
  skips, both Ruff checks, reproducible installation and original smoke. Actual
  test logs and artifact 12172061499 preserve the evidence.
- Retained main and the one M2 development branch because integration review
  and scientific experiments remain open. The independent main/M2 package is
  available; full baseline and full-reference comparisons remain incomplete.

- Recovery-code CI 39234330794 passed: 17 M1 and 46 M2 tests without skips,
  Ruff, reproducible installation and unchanged official smoke. Preserved the
  actual CI source/hash/artifact identity in `recovery_ci.json`.
- The default branch does not activate M2 workflow files. A single immutable
  `retry-request.json` commit therefore requests the one authorized recovery
  on the development branch. The exact-path push trigger excludes ordinary
  changes; its empty-input fallback selects Chemeleon only and no sweep.
- Launched run 39234974449 at source 3e07d9f0. It has entered the official protocol step, not a
  completed performance result. The existing result monitor follows this run
  and is instructed not to spend the once-only retry authorization again.

## 19 October 2026, 22:38 Singapore: completed recovery received

- Downloaded unchanged artifacts 12194049480 and 12194876393; both SHA256
  digests match GitHub. Saved original job logs and source-CI job conclusions.
- The sole retry completed all four generation batches and 20 oracle queries.
  No new science run was launched. Random was neither rerun nor counted twice.
- Reviewed the fixed source `3e07d9f0`, all 69 recorded M1 hashes, capture hash,
  resolved Hydra configuration, raw trajectory and full query history 1..20.
- Ran the unchanged M2 evaluator and official MADE metrics offline in its
  locked environment. Two real runs accepted, zero issues; the protocol and
  material-reference snapshots match. Visually inspected the paired curves.
- Chemeleon Mg-Sn-Sr/17: mSUN=16, AUDC=161, wall=15767.025 s; the existing
  Random pair has 7 / 55.5 / 952.717 s. These are partial development results.
  AF=2.375 and EF=2.2857142857142856 refer only to the official paired curve.
- The partial package reports 34 missing baselines and 18 missing m1_full
  units; overall method means/SD stay blank. Original failed/cancelled attempts,
  null usage fields and unknown compute charges are retained. No source code,
  scientific settings, retry request or M1/M4/root files were changed.
- Published evidence/status on main/M2 and the existing development branch,
  retaining PR #2 without merging. With no active monitored science left,
  pause this result-recovery monitor after publication verification.

## 20 October 2026: current takeover and safe missing-only continuation

- Reread the five M1 contract/source files, all requested M2 records, formal protocol, course brief, task split and guide. Inspected all four M1 message screenshots and M6's newly available report/slide/compute formats.
- Preserved the M2 branch and draft PR #2. Main advanced independently through M6 publication/removal of comms files; do not overwrite those or merge the development branch.
- Rechecked original archive SHA256 values and executed official metrics again. Two accepted baseline units, zero issues, no new score, 34 missing baselines and 18 missing frozen full-method units. Current installed source matches all 69 Chemeleon M1 hashes. Random's sole differing hash is the unused M2 router from an earlier revision.
- Added checksum-pinned imports and a missing-only 36-unit inventory. Tests protect against rescheduling a completed pair, invalid/newer failed evidence, corrupted archives and overwriting existing evidence. Historical failures stay in their original package. A latest failed attempt requires explicit review, not silent fallback.
- Requested run 39284865198 at source 955bdca9: only 17 missing Random units, fresh acceptance gates, max four concurrent processes, automatic raw retention/offline reporting and M2-only publication on main. Queued is not running. Scientific configuration and run_baselines.py are unchanged.
- Local locked environment installed successfully. Original M1 tests: 17 passed. Combined current M2 tests including new recovery mechanics: 52 passed, 1 CPU-namespace skip. Focused/all-M2 Ruff passed. The original smoke failed at Chrome socket creation (Operation not permitted), despite Chrome installation and no missing shared libraries. Kept the original failed log; GitHub CI is separately queued.
- User asked how to prevent losing another long Chemeleon initialization. Implemented experimental batch-level output/RNG replay outside official source and four passing synthetic continuation/rejection tests. It refuses changed identity, RNG or corrupted bytes. Actual local model download returned upstream HTTP 403 before sampling; no bypass or fabricated real result.
- Requested actual small recovery check 39285316913 at source 639f47b3. Prepared stronger full-batch256/cross-runner artifact recovery validation. Formal Chemeleon remains blocked until admission; no reduced candidate pool, batch size, diffusion steps or query budget is used for a claimed protocol result. Small recovery fixtures are labelled integration tests.
- Produced a four-slide editable M6 draft: routing and paired discovery curves for M6 slots 7/10 (40 seconds each), protocol/cost backups and speaker notes. Native charts carry the exact official curve data and embedded workbooks. Rendered/inspected all four slides; package/layout/chart validation passed. This creates a draft deliverable, not a final team presentation.
- Corrected obsolete reference ownership and branch-count statements. M1 still integrates/freezes/supplies the full reference. M6 still owns check/hidden evaluation. No group message was sent and no receipt/acceptance was claimed.

Lesson: prevent repetition at the expensive model-batch boundary and validate exact continuation before trusting it. Preserve model outputs and RNG, not just activity logs. An execution-recovery fixture does not replace a completed 20-query scientific unit.

## Current independent verification update

Scientific coverage remains 2/36. Corrected Random run39286848821 has released 17 missing-only units; the latest observed matrix has four running job environments and 13 queued, with no new accepted result. Original Mg-Sn-Sr/17 units are excluded. Running-job log download currently returns BlobNotFound, so query/CPU counts are not inferred from workflow status.

The original small-model recovery ZIP has now been independently downloaded and SHA256-verified in verification/20261020-batch-recovery-small/. All four exact continuation checks pass on source639f47b3. Batch256 validation39286986254 has completed the continuous and deliberately interrupted stages; restoration on a separate runner is in progress. It must still pass the final exact comparison. No formal Chemeleon unit uses this cache yet.

The reviewed M6-format draft, native chart input and speaker notes are in report/. The binary draft and original small-recovery ZIP are deterministically published from checksum-verified encoded bytes by the separate assets workflow. This creates no scientific workload. M2's local Ruff configuration makes namespace import classification explicit. Current local rerun:17 M1 passes,52 M2 passes,one CPU-namespace skip. The new source still requires its own GitHub acceptance; prior source-specific checks remain historical.

M1's shared configuration advanced independently with M5 wiring during the takeover. M2 publication preserves that current tree and does not modify the shared configuration. No active scientific workflow is restarted for these source/documentation updates.


### 19 October 2026, 16:55 UTC — preserve failed large recovery validation

Accepted scientific units remain **2/36**. In missing-only Random run [39286848821](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286848821), four new jobs have succeeded, four are running and nine queued at this snapshot. The four successful jobs await artifact/protocol/official-metric verification and are not counted as accepted results.

The stronger batch256 recovery run [39286986254](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986254) **failed its final admission check**: full structure dictionaries differ and runner hostnames repeat. Final RNG, preserved batch bytes, candidate counts and no-repeat sampling checks passed. Read-only inspection found only very small numeric differences (maximum absolute difference 2.8422e-14), and distinct runner names despite the shared hostname; these observations do not override the failure. Three original artifacts were downloaded and their SHA256 digests verified. See `verification/20261020-batch256-recovery-failure/`. No production Chemeleon recovery workflow is admitted; 17 formal Chemeleon dev units remain missing.

The colleague's request for 12 Chemeleon check units is an additional evaluation request, not a launched experiment. The colleague offers to run 12 Random check units locally. M1 retains ownership of hidden-split driver support and the frozen full-system reference. No check/hidden jobs were dispatched from the screenshot alone.

Older job snapshots below are historical and superseded by this update.



## Overnight audit update — 20 October 2026, 01:22 Asia/Singapore

**Nine distinct dev baseline units have passed offline validation (9/36): eight Random and one Chemeleon.** Seven new Random ZIPs from run 39286848821 matched GitHub artifact SHA256; each has complete B=20 history, matching protocol/config and official metrics. The original verified pair is reused once. Remaining baseline units: 27 (10 Random and 17 Chemeleon). The latest job snapshot has one additional Random success awaiting audit, four running and five queued; these counts can change while the run continues.

Evidence: `verification/20261020-random-partial-audit/report-canonical/`. Initial aggregation failed on redundant floating-point derived fields, with the failure retained in `report/`. The M2-only reference hash now preserves exact independent reference values and omits only redundant lattice scalars/Cartesian positions when their basis is present. Seven regression cases and the current combined local suite passed (59 passed, one CPU-namespace skip); official metrics and scientific settings were not changed. No complete method comparison is claimed.

The latest-main isolated interface check preserves all non-M2 fields and all five switches. M1 tests: 17 passed. Combined M2 tests in that shared config: 51 passed, one failed, one skipped; failure is M5's int(None) under the unseeded default. Required focused Ruff passed; original smoke failed locally, including a retry using installed Chrome. Complete evidence is in `verification/20261020-current-main-interface/`, with an unsent M1/M5 message in `handoffs/M1_M5_CONFIGURATION_ISSUE.md`.

Read `OVERNIGHT_RUNBOOK.md` for the user-authorized continuation, evidence rules and boundaries. A preservation-only workflow is being installed on the existing development branch to publish exact original ZIPs and the failed batch256 artifacts on main/M2 independently of scoring success. It starts no scientific experiments. Check/hidden dispatch still awaits the colleague's reply and a confirmed safe setup; no formal Chemeleon recovery is admitted.

Older snapshots below are superseded by this update.



## Confirmed durable snapshot — 20 October 2026, 01:27 Asia/Singapore

**11/36 distinct dev baseline units validated, zero issues: 10 Random + 1 Chemeleon.** [Preservation run 39293506143](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39293506143) succeeded. Its exact original ZIPs are now committed under `verification/preserved-39293506143/`: nine new Random ZIPs plus all three failed batch256 recovery ZIPs, each matched to its GitHub SHA256. The original two accepted archives remain in their original folders. Official per-unit scores, curves, costs-as-recorded and audit are in that snapshot's `report/`.

All eleven accepted ZIPs are now pinned in `configs/verified_baselines.json`. The reuse planner was actually executed against these exact bytes: completed=11, missing=25. Evidence is in `verification/20261020-reuse-eleven/`. It therefore excludes all eleven accepted units from future missing-only plans. Current source sweep snapshot: four Random units running, four queued; no new Chemeleon unit dispatched. The 25 remaining baseline units comprise eight Random and 17 Chemeleon. Copies of existing artifacts add zero experiments.

The known-cost fields of the original records report zero model/API fees; compute, electricity and interruption costs have not all been priced, so do not interpret the metadata's cost_status=complete as a complete economic cost estimate. The current shared M1/M5 default failure and local smoke failures remain unresolved and explicitly logged. Latest-source cloud CI is still pending; historical passes are not used as its result. M1/M5 issue message is prepared, not sent through WeChat.

Older snapshots below are superseded by this confirmed snapshot.


## 26 October 2026 — peer handoff intake and shared aggregation

- Built: independently inspected M4's18 memory_off and M3's36 component-study OFF folders at main95f9c8e; executed the unchanged M2 evaluator on126 real dev runs, issues=[]; added252 paired Random/Chemeleon AF/EF comparisons, correct seed-first tables, separate-study curves, costs, source hashes and M6 assembly text.
- Preserved: all original peer results and previous M2 failures remain unchanged. Eighteen derivative routing history views explicitly retain the original incomplete history. Original entry-point versions are backed up under M2/aggregation/20261026/backups/. No project file outside M2 changed; no scientific rerun or message was sent.
- Checked: M4 raw archive CRC/checksums,18 one-switch configurations,74 source hashes each and paired curves; M3 all36 protocols/material snapshots and74 Windows-line-ending-aware input fingerprints. All18 new M1 reconstructed histories agree with the previous official structure-and-energy reevaluation.
- Tests: actual M4 standalone suite15/15 passed. The72-test joint selection stopped at collection due to absent Hydra/pymatgen; M4's72-pass statement is attributed, not independently certified. Offline parsing/collection failures during adapter development are retained under M2 staging and did not launch or overwrite science.
- Learned: evaluator core-completion flags cover Full and two baselines, not every group ablation. M3's current profiles also disable exploration/routing, so their causal comparator is m3_full. The historical18-row comparator CSV lacks complete raw folders; paired component gains stay provisional. Official EF default cap is100, notwithstanding older prose saying10.
- Next: request complete m3_full originals and clarify whether M1/M3 will supply formal Full planning_off/self_correction_off; collect M5 exploration_off and M6 remaining check/hidden material; update final group report/deck after receipt.


## 26 October 2026 — complete M3 comparator intake

- Built: accepted the18 original m3_full folders at dcd3481a; ran unchanged M2 evaluator on144 real dev records, issues=[]; M3-only54/54 valid; updated288 baseline comparisons,36 matched M3 component pairs, actual three-arm curves, machine-labelled costs and M6 assembly text. Earlier7-method numeric aggregates and36 Full memory/routing pair rows remain unchanged.
- Checked: all3996 M3 source fingerprints and432 manifest entries explained with explicit Windows newline handling;108 scientific files establish02/ae7 evidence-patch equivalence;36 paired configs differ only in their treatment and run paths;1080 supplied history prefixes match the unchanged M1 trajectory-history function and54 official AUDCs/endpoints agree. This verifies recorded-flag consistency, not fresh hull/novelty reevaluation.
- Results: m3_full6.50mSUN/62.75AUDC; comparator-minus-planningOFF+1.3889mSUN/+13.5278AUDC; comparator-minus-selfcorrectionOFF+.6667mSUN/+4.4444AUDC. Pairwise variation remains explicit.
- Corrected scope: latest M3/user clarification confirms extra Full-agent planning_off/self_correction_off are not M3 assignment debt. The previous M2 attribution is withdrawn. M3 assigned54-run handoff is complete; M1/M6 decide any extra Full-agent work.
- Preserved: no original metadata/history/scientific source changed; newfull keepsae7fe819 andOFFkeeps02e0026. Prior126-run release remains; outdated human-facing statements have a prominent superseding correction and byte-exact backup. No new experiment/model/oracle call or external message. All edits underM2.
- Next: M5 exploration package, M6 remaining check/hidden and final report/deck assembly; resolve extra Full-agent scope withM1/M6 if desired.
