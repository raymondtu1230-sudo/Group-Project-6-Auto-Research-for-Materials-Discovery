# 当前验收状态 — 2026年10月20日02:57（新加坡）

- 科学基线核验 **19/36**，零审计问题：Random 18/18、Chemeleon 1/18。没有排队、运行或待验收的Random。原始首轮两项只计一次。
- main/M2/verification/preserved-39306348134/ 保存23份SHA256核对通过的原始ZIP，包括17份补跑Random和两次恢复验证的6份归档。恢复验证本身不算基线成绩。
- 开发源78346d6、CI 39306348142：17项原M1测试、62项M2测试均通过，无跳过；focused/all-M2 Ruff、安装复现、官方合成smoke通过。日志在 verification/20261020-overnight-closeout/。这不是对共享main M1/M5默认配置的重新验收，该项已知失败仍待其负责人处理。
- 恢复验证39297647516在身份保护检查失败，最终比较未执行；完整候选池生产入口及剩余17项Chemeleon均未获准开跑。不得把失败说成通过、原样重试或降低科学设置。
- main的 verified_baselines.json 已固定19份归档；旧开发分支清单不能覆盖它或导致重复派发。现有幻灯片仍是原始两项结果的历史草稿。
- M1负责正式集成、冻结和完整reference；M6负责check/hidden。新进度消息仅保存于 handoffs/20261020_PROGRESS_FOR_M1_M6_ZH.md，尚未发送/确认。PR2保留草稿、未合并。
- 本轮可独立完成的原始归档和CI已核验。按照用户停止规则暂停后续轮询，保留恢复、运行时限和成员/用户依赖；这不代表整个M2完成。

## 历史清单（与上文不一致时以上文为准）

# Current acceptance update: 20 October 2026

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

The source revision `2b2c6753` and CI counts below are historical evidence.
Current reruns, skipped checks and the local smoke failure are recorded in
`verification/20261020-takeover/`. Current GitHub CI must be checked by revision.
Do not treat any old CI as proof of the newly added scheduler or recovery prototype.
The router itself and all five M1 switches are unchanged. Experimental batch
replay is a separate admission gate, not an accepted scientific result.

# M2 handoff acceptance checklist

Reviewed on 19 October 2026 against the user's supplied M1 handoff instructions.
This checklist covers the M2 component handoff. Completion of the team's full
scientific comparison is a separate gate.

## Ownership and reviewed source

- Canonical sources, tests, workflow definitions, evidence and notes are in
  `M2/` on `main`, beside the other members' folders.
- The integration candidate is `m2/tool-routing-evaluation`, revision
  `2b2c675317b3530963c27f69d8d88490d7b31dd4`, in
  [PR #2](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/pull/2).
- All five required M1 files were read: `M1/PLUGIN_INTERFACE.md`,
  `M1/INTEGRATION.md`, the M1 integrated agent, its Hydra configuration, and
  `tests/test_m1_integrated.py`.
- M2 implements tool routing and checkpointable generator adapters. M3's
  planning/reflection, M4's memory and M5's composition exploration stay with
  their respective owners.

## Requirement mapping

| Requirement | Implementation and verified evidence |
| --- | --- |
| Importable component | `integration/m2_tool_routing.py`; `install.py` copies it to `M1/MADE/src/made/agents/m2_tool_routing.py`. |
| Hydra configuration and existing field names | `configs/m2_routing.yaml` is installed into M1's agent config directory. The installer connects `tool_router` and `generators` in `m1_integrated.yaml`. |
| Preserve `agent(state) -> (Composition, Structure)` | The existing M1 agent is unchanged. Contract tests verify the returned composition and structure. |
| Preserve all five independent switches | The M2 profile inherits the existing configuration and changes only `enable_tool_routing`. Tests compare the other four switches. |
| Correct router/generator types | The router returns a configured generator name. Its adapters return `list[Structure]`. M1's existing Plan and memory contracts are unchanged. |
| Respect remaining queries | The router checks `m1_queries_remaining` and rejects exhausted/invalid budgets. M1's original budget caps remain in force. |
| One environment step per oracle query | No runner, environment or budget code is changed. The router only selects a generator and never evaluates a structure. |
| No oracle calls or hidden-state access in the plug-in | The reviewed plug-in reads query count, remaining budget and the previous public observation. It does not import oracle/evaluator/environment code or read hidden labels. |
| JSON checkpoint state | Router and both generator adapters implement `get_state` and `load_state`. JSON round-trip and resumed-decision/structure checks pass. |
| Seeded reproducibility | Router checks cover seeds 17/29/43. Random generation restores its RNG. A separate real CPU Chemeleon check verified equal continuous/resumed structures and preservation of external random streams. |
| Enabled and disabled behavior | `integration/test_m2_tool_routing.py` checks routed selection and primary-generator fallback. |
| Invalid outputs and checkpoints | Tests reject unknown names/unrelated objects, corrupt state, changed configuration and invalid budgets. |
| Required test inputs | Contract/unit tests use fake MADE state and synthetic structures as requested. They are actually executed and are not reported as materials benchmark results. |
| Environment and API setup | CI installs the frozen environment using `uv sync --locked`. Actual Materials Project access and real Chemeleon generation passed separately; see the JSON evidence under `verification/`. |
| No embedded credentials or machine-specific source paths | Credentials use the existing repository Secret, mapped to `MATERIALS_PROJECT_API_KEY`. Plug-in source contains no key values or hard-coded workspace paths. |
| Independent folder | The published `main/M2` directory contains the canonical package and validated evidence. Installing its integration copies is a separate, explicit operation. |

Against current `main`, the integration candidate changes only four M1 slots:
the new module, new component test, new M2 Hydra profile, and the existing
`m1_integrated.yaml` configuration. The official runner, oracle, evaluator,
environment, budget logic, M1 agent implementation and original M1 tests are
unchanged. Current M4 contents are preserved exactly.

## Executed checks

[GitHub run 39221672640](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39221672640)
passed on revision `2b2c6753`:

- 17 original M1 contract tests and 45 M2 tests passed, with no skips.
- Focused Ruff and the complete M2 Ruff check passed.
- Re-running the installer produced no tracked changes.
- The unchanged official `M1/run_smoke_test.py` passed.
- Artifact `12172061499`, `m2-integration-verification`, preserves JUnit and
  smoke evidence. The job logs preserve the actual command output.

The local continuation also ran the checks: 17 M1 and 44 M2 tests passed, and
one process-CPU test was explicitly skipped because the local `/proc` namespace
does not match the process IDs. That same CPU test passed in GitHub Linux;
the skipped local assertion is not counted as a local pass.

Reproduce from the repository root:

```bash
cd M1/MADE
uv sync --locked
uv run python ../../M2/install.py
uv run pytest -q tests/test_m1_integrated.py
uv run pytest -q tests/test_m2_tool_routing.py ../../M2/tests -o addopts=''
uv run ruff check src/made/agents/m2_tool_routing.py tests/test_m2_tool_routing.py
uv run ruff check ../../M2
uv run python ../run_smoke_test.py
```

Unit tests and the AnalyticOracle smoke establish integration behavior. Actual
API/model checks establish real access and model continuation. Scientific
performance is accepted only from completed, validated protocol experiments.

## Remaining acceptance gates and branch policy

- The component implementation and its checks are ready for M1 review. PR #2
  contains the separately prepared M1 integration slots and active GitHub
  workflow files; these have not been merged into `main` by this handoff.
- Two of 36 development baseline units are accepted: Random Mg-Sn-Sr/17
  (B=20, mSUN=7, AUDC=55.5) and Chemeleon on the same unit (mSUN=16,
  AUDC=161). The [paired recovery package](verification/20261019-chemeleon-recovery/README.md)
  validates the identical protocol and material-reference snapshot. No overall
  method score exists. Another 34 baseline units, the full integrated reference
  and routing-off comparison remain incomplete.
- Keep `main`: it is the shared delivery branch. Keep the single M2 development
  branch while PR review/integration and experiment work remain active. Other members also have their own branches; retain them.
- Retire the M2 branch only after its required changes are accepted into the
  shared branch, checks pass, and experiment evidence and remaining workflow
  needs are accounted for. Folder delivery alone is not a reason to delete it.
- Do not announce that the whole M2 scientific task is finished while those
  experiment gates are pending. A group-chat completion notice remains a
  separate communication step.
