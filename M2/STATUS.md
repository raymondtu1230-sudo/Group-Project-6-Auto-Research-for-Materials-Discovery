> 交付方式：本轮材料通过 PR #5 单独交付至 `main/M2/`；用户已于2026年10月20日授权合并。共享框架接入仍由M1负责，PR #2 保留草稿。下述验收数字及失败对应审计时版本；本次文件交付不包含对后续共享代码变更的复验。

## 本轮M2独立收尾 — 2026年10月20日

- dev基线保持19/36：Random18/18、Chemeleon1/18。19份固定原始ZIP的SHA256与CRC重新通过；独立重评分的数值表与先前发布一致，issues=[]。证据：verification/20261020-handoff-audit/。
- 当前可独立交付的组件、配置、安装映射、方法文字、讲稿、交接草稿和结果接收规范已整理。report/M2_Method_and_Partial_Results_20261020.pptx为当前草稿；旧2/36版保留为历史。
- 新增DELIVERY_STATUS.md明确M2工作范围。check Random12项属于M6，未代跑；check/hidden、正式集成、他人成员的实验和记录均不在本轮改动范围。
- 实测共享配置测试77通过、1失败、1跳过。失败为M5的seed=None初始化，跳过为本容器/proc计数不可见。该依赖交M1/M5，不用旧源码CI的通过替代当前失败。
- M2/ruff.toml只排除不可变的verification历史证据，当前源代码、integration和tests仍检查，Ruff通过。官方源码、科学参数和19份原始归档不变。
- 群消息只保存草稿，未发送、未获确认；PR2仍为草稿、未合并。M1冻结版reference、routing-off及各成员最终结果仍待后续。整个M2未完成。
- 本轮不启动Chemeleon、check、hidden、GPU或付费任务。交付后停止，不增加定时跟进。

本次本地官方合成smoke还在Chrome图片导出阶段失败，原始日志已保存；不算通过。旧源码云端smoke通过记录仅对应其源版本。

## 以下为已保留的历史状态

## Verified overnight closeout — 20 October 2026, 02:56 Asia/Singapore

**19/36 distinct dev baseline units accepted: Random 18/18; Chemeleon 1/18. Zero validation issues.** All 17 missing Random jobs in run 39286848821 succeeded. Its old-source final aggregation failed with "Protocol or material reference revision differs"; no scientific unit was rerun for that report failure. Preservation-only run [39306348134](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39306348134) reused existing ZIP bytes, checksum-verified 23 originals (17 Random plus six archives from the two failed recovery fixtures), published them to main/M2, and executed the current offline evaluator plus unchanged official metrics. The original Mg-Sn-Sr/17 pair is retained and counted once.

Evidence and score tables: [preserved-39306348134](verification/preserved-39306348134/). The actual report says validated_runs=19, issues=[], missing_baseline_units=17, baseline_sweep_complete=false, final_comparison_complete=false. Its broader missing_units=35 also includes M1's 18 unavailable full-reference units; do not misreport those as 35 missing M2 baselines. Each accepted unit has B=20 and 20 recorded queries. The checksum-pinned main/M2 reuse manifest now contains 19 archives; do not reschedule them. The development branch's older delivery snapshot must not override this main manifest.

**Chemeleon recovery admission remains blocked.** Run [39297647516](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39297647516) exited with "Batch model, input or execution identity mismatch" during replay. The exact compare and runner-identity gate did not execute. Which identity field differed is not established by the hash-only saved metadata. This is an explicit failure, not a hang and not a pass. No unchanged retry, full1024 production-wrapper run or formal missing Chemeleon unit was launched. The 17 missing Chemeleon units need a rigorously diagnosed and verified recovery path/full-wrapper cost proof, or an adequately long persistent CPU runtime. Do not remove guards, reduce scientific settings, purchase resources or assume GPU approval to proceed.

Source-specific dev CI [39297647411](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39297647411) on 053d8c3 passed 17 original M1 tests, 62 M2 tests, focused/all-M2 Ruff, reproducible installation and original synthetic smoke. This is not a pass for current shared-main M1/M5 unseeded integration: that separately recorded failure remains an owner dependency. Preservation-only source 78346d6 CI [39306348142](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39306348142) also completed successfully: 17 M1 tests, 62 M2 tests, both Ruff checks, installation reproducibility and original smoke.

Raw failure logs, job/artifact metadata and closeout cross-check are in [20261020-overnight-closeout](verification/20261020-overnight-closeout/). All source code, official science parameters and original archives remain unchanged. Known model/API fees are zero; hardware/electricity/failed-attempt costs remain incompletely priced. No overall method comparison or final slides are claimed.

[RTX4070 pilot preparation](GPU_PILOT_GUIDE_4070.md) is saved; no GPU connection or experiment was performed. Clone only the repository and create a locked environment on that machine; do not migrate all personal data or copy CPU caches. OS-specific steps and a formal GPU comparison protocol await the user's later involvement and M1/M6 alignment.

This is a bounded closeout, **not completion of all M2 work**. After evidence and final CI are recorded, pause the hourly follow-up per the user's stop rule, with no healthy science cancelled (none remains active). M1 still owns integration/freeze/full reference; routing-off awaits that reference. Check/hidden remain on hold. Prepared handoff messages are drafts for the user, not sent or accepted. Keep draft PR #2 and its branch unmerged.


## Historical snapshots (superseded)

# M2 status: 20 October 2026 takeover

## Confirmed durable snapshot — 20 October 2026, 01:27 Asia/Singapore

**11/36 distinct dev baseline units validated, zero issues: 10 Random + 1 Chemeleon.** [Preservation run 39293506143](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39293506143) succeeded. Its exact original ZIPs are now committed under `verification/preserved-39293506143/`: nine new Random ZIPs plus all three failed batch256 recovery ZIPs, each matched to its GitHub SHA256. The original two accepted archives remain in their original folders. Official per-unit scores, curves, costs-as-recorded and audit are in that snapshot's `report/`.

All eleven accepted ZIPs are now pinned in `configs/verified_baselines.json`. The reuse planner was actually executed against these exact bytes: completed=11, missing=25. Evidence is in `verification/20261020-reuse-eleven/`. It therefore excludes all eleven accepted units from future missing-only plans. Current source sweep snapshot: four Random units running, four queued; no new Chemeleon unit dispatched. The 25 remaining baseline units comprise eight Random and 17 Chemeleon. Copies of existing artifacts add zero experiments.

The known-cost fields of the original records report zero model/API fees; compute, electricity and interruption costs have not all been priced, so do not interpret the metadata's cost_status=complete as a complete economic cost estimate. The current shared M1/M5 default failure and local smoke failures remain unresolved and explicitly logged. Latest-source cloud CI is still pending; historical passes are not used as its result. M1/M5 issue message is prepared, not sent through WeChat.

Older snapshots below are superseded by this confirmed snapshot.

## Overnight audit update — 20 October 2026, 01:22 Asia/Singapore

**Nine distinct dev baseline units have passed offline validation (9/36): eight Random and one Chemeleon.** Seven new Random ZIPs from run 39286848821 matched GitHub artifact SHA256; each has complete B=20 history, matching protocol/config and official metrics. The original verified pair is reused once. Remaining baseline units: 27 (10 Random and 17 Chemeleon). The latest job snapshot has one additional Random success awaiting audit, four running and five queued; these counts can change while the run continues.

Evidence: `verification/20261020-random-partial-audit/report-canonical/`. Initial aggregation failed on redundant floating-point derived fields, with the failure retained in `report/`. The M2-only reference hash now preserves exact independent reference values and omits only redundant lattice scalars/Cartesian positions when their basis is present. Seven regression cases and the current combined local suite passed (59 passed, one CPU-namespace skip); official metrics and scientific settings were not changed. No complete method comparison is claimed.

The latest-main isolated interface check preserves all non-M2 fields and all five switches. M1 tests: 17 passed. Combined M2 tests in that shared config: 51 passed, one failed, one skipped; failure is M5's int(None) under the unseeded default. Required focused Ruff passed; original smoke failed locally, including a retry using installed Chrome. Complete evidence is in `verification/20261020-current-main-interface/`, with an unsent M1/M5 message in `handoffs/M1_M5_CONFIGURATION_ISSUE.md`.

Read `OVERNIGHT_RUNBOOK.md` for the user-authorized continuation, evidence rules and boundaries. A preservation-only workflow is being installed on the existing development branch to publish exact original ZIPs and the failed batch256 artifacts on main/M2 independently of scoring success. It starts no scientific experiments. Check/hidden dispatch still awaits the colleague's reply and a confirmed safe setup; no formal Chemeleon recovery is admitted.

Older snapshots below are superseded by this update.

## Latest verified update — 19 October 2026, 16:55 UTC

Accepted scientific units remain **2/36**. In missing-only Random run [39286848821](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286848821), four new jobs have succeeded, four are running and nine queued at this snapshot. The four successful jobs await artifact/protocol/official-metric verification and are not counted as accepted results.

The stronger batch256 recovery run [39286986254](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986254) **failed its final admission check**: full structure dictionaries differ and runner hostnames repeat. Final RNG, preserved batch bytes, candidate counts and no-repeat sampling checks passed. Read-only inspection found only very small numeric differences (maximum absolute difference 2.8422e-14), and distinct runner names despite the shared hostname; these observations do not override the failure. Three original artifacts were downloaded and their SHA256 digests verified. See `verification/20261020-batch256-recovery-failure/`. No production Chemeleon recovery workflow is admitted; 17 formal Chemeleon dev units remain missing.

The colleague's request for 12 Chemeleon check units is an additional evaluation request, not a launched experiment. The colleague offers to run 12 Random check units locally. M1 retains ownership of hidden-split driver support and the frozen full-system reference. No check/hidden jobs were dispatched from the screenshot alone.

Older job snapshots below are historical and superseded by this update.

## Current independent verification update

Scientific coverage remains 2/36. Corrected Random run39286848821 has released 17 missing-only units; the latest observed matrix has four running job environments and 13 queued, with no new accepted result. Original Mg-Sn-Sr/17 units are excluded. Running-job log download currently returns BlobNotFound, so query/CPU counts are not inferred from workflow status.

The original small-model recovery ZIP has now been independently downloaded and SHA256-verified in verification/20261020-batch-recovery-small/. All four exact continuation checks pass on source639f47b3. Batch256 validation39286986254 has completed the continuous and deliberately interrupted stages; restoration on a separate runner is in progress. It must still pass the final exact comparison. No formal Chemeleon unit uses this cache yet.

The reviewed M6-format draft, native chart input and speaker notes are in report/. The binary draft and original small-recovery ZIP are deterministically published from checksum-verified encoded bytes by the separate assets workflow. This creates no scientific workload. M2's local Ruff configuration makes namespace import classification explicit. Current local rerun:17 M1 passes,52 M2 passes,one CPU-namespace skip. The new source still requires its own GitHub acceptance; prior source-specific checks remain historical.

M1's shared configuration advanced independently with M5 wiring during the takeover. M2 publication preserves that current tree and does not modify the shared configuration. No active scientific workflow is restarted for these source/documentation updates.


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

## Accepted science: 2/36 development baseline units

| Method | System / seed | B | mSUN@B | AUDC | Driver seconds |
| --- | --- | --- | --- | --- | --- |
| Random | Mg-Sn-Sr / 17 | 20 | 7 | 55.5 | 952.717 |
| Chemeleon | Mg-Sn-Sr / 17 | 20 | 16 | 161 | 15767.025 |

The original ZIPs were checksum-verified and rescored with the unchanged official
metrics in this takeover. Two runs accepted, zero issues. Single-pair Chemeleon
AF/EF versus Random are 2.375 / 2.2857142857142856. Overall method means and SD
remain unavailable. Known inference fees are USD 0, while hardware, electricity,
interrupted-attempt charges and unreported usage remain unknown.

Original evidence is preserved in `verification/20261019-random-gate/`,
`verification/20261019-chemeleon-recovery/` and the separate timeout audit.
New read-only review, 36-unit inventory and actual local failures are in
`verification/20261020-takeover/`. These reviews do not add new scientific units.

## Missing-only work actually requested

- [Run 39284865198](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39284865198),
  fixed source `955bdca92b732c7d4fef64928df35fc15320fe85`, requests only the 17
  missing Random dev units. Four jobs at most run concurrently, one episode per
  process, unchanged official driver/configuration and B=20. Fresh M1/M2 checks
  and the original smoke must pass in `prepare` before science starts.
- At this status snapshot it is **queued**, with no new completed scientific
  result and no allocated scientific job. Queue state is not active computation.
- Reused archives are checksum-pinned. Later published result bundles can be
  imported too. Invalid/newer failed attempts stop rescheduling for explicit
  review. The completed first pair is excluded. The legacy `baseline_sweep`
  would rerun that pair and must not be launched for this continuation.
- Each job retains raw data, diagnostics, configuration, provenance and failure
  attempts. The report job uses the official metrics, uploads artifacts and
  publishes only a new `main/M2/verification/missing-<run_id>/` folder. This does
  not merge PR #2 or change main's M1 configuration.

## Chemeleon continuity: prototype, not yet admitted

Seventeen Chemeleon units remain missing. A measured unit took 263 minutes.
Other systems may be slower than a hosted six-hour job allows, and the original
initial pool has no verified mid-generation recovery. No full Chemeleon sweep
was dispatched under those conditions.

The user explicitly requested avoiding another full restart after timeout.
`generation_cache.py` therefore experiments with saving outputs of each original
`DiffusionModule.sample` batch, its exact inputs, model/source fingerprints and
Python/NumPy/Torch RNG before/after the batch. Replaying a verified batch restores
its post-call RNG and lets the original generator write/read the same CIFs in
the original order. It changes no pool size, batch size, diffusion steps, oracle
budget or official source file. A planned pause occurs before the next sampling
call. Logs alone do not establish recoverability.

Four synthetic recovery/rejection tests pass. Actual-model cross-process check
[39285316913](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39285316913),
source `639f47b301d71cc7bd7c66c7832f0ecb75bb5e9d`, is queued. This is a small
integration fixture, not a baseline score. The local actual-model check was
blocked by an upstream model-download HTTP 403; no actual sample completed locally.
A separate batch256/cross-runner workflow is prepared for the necessary stronger
admission check. Its proof must match all generated structures/order and final
RNG across actual artifact upload/download and a different runner. Until those
checks and production-wrapper integration pass, the 17 formal units remain
capacity-blocked. `cache_protocol.py` is experimental and has not been used for
accepted science. An adequately long persistent CPU host remains an alternative.

## Component verification and ownership

The delivered router, generator adapters, installer, M1 agent contract and all
five switches are preserved. The installer was executed only in our checkout,
not on shared main. It produced the documented four integration slots; no
official runner/oracle/evaluator/environment/budget or M1 contract source changed.

Current local M1 contracts: 17 passed. Current combined M2 suite: 52 passed and
one CPU-namespace skip. Focused/all-M2 Ruff passed. Original smoke failed because
this host denies Chrome socket creation, even after Chrome installation. Its
failure is retained and is not a pass. Source-specific GitHub CI is queued;
old passing CI is historical evidence only. See the actual logs/JUnit in the
current takeover package.

## Handoffs and dependencies

- By 24 October, M1 receives component/config/installer/test evidence in M2.
  M1 owns shared integration and the 25 October freeze. PR #2 remains a draft,
  unmerged, and the development branch is retained.
- M6's current format is `M6/report/SLIDES_OUTLINE.md`: M2 slide 7 (routing) and
  slide 10 (curves), 40 seconds each. `report/` contains the editable draft and
  speaker notes, plus protocol/cost backups. This is an actual draft, not the
  final group deck. Current numerical slides explicitly show one pair / 2 of 36.
- M1 supplies the frozen full-system reference by 26 October noon. M2 validates
  it and only then runs routing-off at the same revision/conditions with one
  switch changed. Do not substitute `m1_baseline` or run M1's reference for him.
- M2 collects all member results and produces final tables, curves and costs for
  M6 by 27 October. M6 owns public-check/hidden tests. No such evaluation is
  claimed here. No recipient has yet confirmed receipt or acceptance.
- The earlier recovery monitor has been updated and resumed for current runs.
  It checks at most hourly and reports meaningful new evidence. It does not
  promise an immediate notification at the exact sampling/completion instant.

## Superseded instructions, retained historical records

Old one-retry-only scope and the stopped recovery monitor describe 19 October.
The user's 20 October handoff authorizes completing missing development units.
Old CI revisions/counts in earlier checklist/log entries remain dated evidence,
not current acceptance. main now contains multiple member folders and branches;
the old statement that only two repository branches exist is obsolete. The old
README sentence assigning the full reference run to M2 has been corrected.
