# Chemeleon独立基线：启动前准备已完成

记录日期：2026-10-20（Asia/Singapore）。本轮正式17项实验保持未启动。只完成M2启动准备，未代做M1集成、冻结、reference，或M6 check/hidden及组稿。

## 结论与版本

已经具备从头完整运行剩余dev Chemeleon的启动条件，目前没有必须补充权限、密钥、付费资源或其他成员成果才能解除的启动阻塞。

- 实际受检和应使用的源码提交：[`63077ea3ea612197a5ad0e71fbe015d80149ca37`](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/commit/63077ea3ea612197a5ad0e71fbe015d80149ca37)。Python固定3.12.15，uv固定0.9.18，依赖用未修改的`M1/MADE/uv.lock`和`uv sync --locked`。
- 实际执行的工作流提交：[`199b714810f9bc061315c3ca9371f16ed5118126`](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/commit/199b714810f9bc061315c3ca9371f16ed5118126)，分支`m2/tool-routing-evaluation`。
- 真实检查、17个短任务和自动保存：[run 39384607532](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39384607532)。证据已由提交`37f2124`保存到main/M2。
- `configs/chemeleon_direct_validation.json`固定已验证源码、M2文件校验和、环境、时间预算及证据。正式请求必须通过该凭证核对。
- 当前主分支上的本轮提交只涉及M2；M3/M5在本轮期间的新增提交已保留。PR #2仍为open draft，未合并、关闭或删除。

## 已有结果和17项清单

按最新正式协议、dev体系、seed和`configs/verified_baselines.json`重新导入校验：36项中19项已验收，Random18/18、Chemeleon1/18。19份原始ZIP的SHA256及CRC通过，离线重评分`validated_runs=19, issues=[]`；所有分数、成本及汇总字段与历史审计相同（本地来源路径不同）。已完成的Chemeleon Mg-Sn-Sr/17明确排除。

| 序号 | 体系 | seed | B |
| --- | --- | --- | --- |
| 1 | Au-K-Tb | 17 | 20 |
| 2 | Au-K-Tb | 29 | 20 |
| 3 | Au-K-Tb | 43 | 20 |
| 4 | Co-Dy-W | 17 | 20 |
| 5 | Co-Dy-W | 29 | 20 |
| 6 | Co-Dy-W | 43 | 20 |
| 7 | Co-Mg-Na | 17 | 20 |
| 8 | Co-Mg-Na | 29 | 20 |
| 9 | Co-Mg-Na | 43 | 20 |
| 10 | Ga-Pt-Tm | 17 | 20 |
| 11 | Ga-Pt-Tm | 29 | 20 |
| 12 | Ga-Pt-Tm | 43 | 20 |
| 13 | Hf-Ni-Zr | 17 | 20 |
| 14 | Hf-Ni-Zr | 29 | 20 |
| 15 | Hf-Ni-Zr | 43 | 20 |
| 16 | Mg-Sn-Sr | 29 | 20 |
| 17 | Mg-Sn-Sr | 43 | 20 |

快照见`configs/chemeleon_missing_dev.json`；真正启动时由`chemeleon_preflight.py plan`重新核对最新main的已验收原始归档和新成功receipt，不能直接使用旧baseline_sweep矩阵。保存、复制、评分、smoke及本轮17个短任务均不增加科学实验数量。

## 批量提交、并发与限制

配置可以一次提交17项，`fail-fast: false`，并发上限可选1至17。每项单独GitHub标准`ubuntu-latest` runner，本轮没有让用户Mac加载模型。

本轮实测：17个任务全部被调度，17个独立runner名称、17个独立目录、17份产物；45秒任务区间的并发峰值为17。整项job分别耗时50至54秒。Au-K-Tb/17故意以23退出，其余16项全部成功；失败项也上传并写回main，保存job成功。原始job metadata、带起止时间的probe和验证摘要位于`verification/preflight-39384607532-1/`；运行中的17项快照另存于本地核验目录。

**建议一次提交全部17项，并发上限设17，由GitHub按实际可用名额调度。** 这是基于本次实际观察；不能保证下次仍有17个空闲名额，也不能把它解释为账号最大并发已被测定。账号套餐、其他仓库占用和未来空闲名额无法通过当前接口完整读取，仍为未知。

[GitHub官方限制](https://docs.github.com/en/actions/reference/limits)本轮重新核对：标准Free通常20并发，Pro40；单个托管job最多6小时，矩阵最多256项。标准限制、实际可用名额和科学任务能否在6小时内完成是三项独立结论。

本轮工作流整体显示failure是有意保留一个失败任务的结果，不能把17项写成17项成功。`scheduling-validation.json`为passed=true，16项成功+1项预期失败，所有产物均保存；prepare-and-ci与preserve分别成功。

## 时间和保存安排

| 项目 | 已配置 |
| --- | --- |
| 正式实验job总上限 | 360分钟，GitHub硬上限不能通过YAML突破 |
| 计算步骤外层上限 | 340分钟 |
| 内部计算期限 | `min(20340, 21600 - 实际已耗秒数 - 1260)`秒，最长339分钟 |
| 退出与最后采集预算 | 60秒；TERM后最多等30秒，再KILL并最多等10秒 |
| 保存预算 | 留20分钟；打包步骤最多2分钟，上传步骤最多5分钟 |
| 安装/真实接入步骤 | 分别限15分钟/6分钟，实际耗时从计算预算扣除 |
| Actions产物保留 | 90天 |
| 正式持久保存 | 独立preserve job写入main/M2，避免只依赖过期下载链接 |

本轮真实环境安装39秒；从首个job计时步骤到预算核验共215秒，动态得到计算20125秒（335分25秒），另留1200秒保存和60秒退出。该核验没有启动计算。正式job会按自己的实际安装/接入时间重新计算，安装耗尽安全窗口时拒绝启动计算。最早计时步骤前的runner准备还有少量秒级开销；外层340分钟上限及20分钟保存预算用于留出实际退出、打包和上传余量。

已完成单项Chemeleon的15767.025秒约为4小时23分钟，只是一个测量。其余17项可能超时；并发不会缩短每个单项本身的计算量。保留B=20、初始候选池1024、batch256、CPU及官方推理逻辑，未缩小体系、seed、采样步数或候选池。

## 工作流和防重复

| 用途 | 可执行位置 |
| --- | --- |
| 正式缺失项完整运行 | `m2/tool-routing-evaluation`分支`.github/workflows/m2-chemeleon-direct.yml` |
| 本轮短时基础设施检查 | 同分支`.github/workflows/m2-chemeleon-preflight.yml` |
| 交付副本 | main/M2/workflows/同名文件，字节与部署副本相同 |
| 提交助手 | main/M2/submit_chemeleon.py |

正式入口由向M2分支提交`M2/requests/chemeleon-direct.json`触发；本轮没有创建该请求文件。两份新YAML经actionlint 1.7.7通过；根目录的短任务工作流已真实运行。正式路径的科学计算本轮按要求未执行。

启动前先依据最新main结果排除已完成单元；每项再以fast-forward推送建立`M2/execution_ledger/<system>-<seed>/claim_<attempt>.json`。已经登记的任务不能被普通重复请求再次启动。每个单元有独立并发组，`cancel-in-progress: false`；新提交不会取消健康的运行任务。首次claim成功后才安装并进入正式路径。

attempt为`GitHub run_id * 100 + run_attempt`；输出目录沿用M1的method/dev/system/seed/attempt。产物名包括体系、seed、run和attempt。原19项归档及失败记录不覆盖。GitHub的Re-run按钮不能作为正式重试方式；新请求须引用前次terminal receipt的attempt，并使用新的run/attempt。对同一单元的竞争claim在rebase后还会再次检查。

## 成功、失败、超时和重试

- 成功：M2捕获官方轨迹、逐次查询指标、解析配置、进程诊断和原metadata；离线官方指标核验通过后才记`verified_completed`。新receipt携带ZIP路径和SHA256，下一次missing-only计划可复用，不依赖修改或覆盖原19项清单。
- 失败或超时：保留独立attempt ZIP及receipt，124明确记timeout，其他非零退出记failed，不把部分轨迹记成完成的B=20实验。包装不改写原科学结果数字，产物检查前去除密钥值。
- 保存：`always()`上传成功和失败产物；独立preserve job在矩阵失败后仍运行，把原始ZIP、receipt和调度metadata保存到`main/M2/verification/direct-<run>-<attempt>/`，登记对应terminal receipt。提交只允许M2路径，使用fast-forward推送和有界rebase重试保留其他成员新提交。
- 新尝试：只有终态failed/timeout可以指定`retry_of`。已完成、仍运行、没有明确终态receipt的claim均拒绝重复启动。若runner硬故障导致没有可用artifact/terminal receipt，需先依据真实GitHub终态和残存产物核实并记录，不能自动声称已经恢复。上传或git发布异常会使相应保存步骤失败，Actions副本仍有90天保留窗口；异常需要复核后重新做保存，不能把失败当交付。

## 从头完整运行与可选续跑

正式入口直接调用既有`M2/run_baselines.py`和未改动的`M1/run_experiment.py`，不导入或注入`generation_cache`。本轮只为父进程增加有界运行、整进程组退出和部分证据保存，不改变官方runner、oracle、evaluator、environment、查询预算或方法。

旧run39297647516在身份检查处报`Batch model, input or execution identity mismatch`，完整比较未执行。现有缓存比较execution、request、版本、线程、源码、CPU capability、架构和权重；原缓存只存总hash，无法从旧证据确认具体不同字段。本轮未放宽身份保护、未删除旧失败，也未进行数小时采样复验。初始池中断恢复仍属未验证的可选能力，不是直接完整运行的前提。超时或中断可能损失尚未完成的初始采样；后续重试从头开始，不能承诺接着采样。

旧容量门禁采用单点263分钟乘1.5的不确定性估计，其结果超过托管期限。这是保守估算，不能证明每次完整运行都无法在期限内完成。旧恢复路径和保护保留；新入口明确采用有期限、可失败的完整尝试，以实测进度和保存余量约束运行。

## 本轮验证与证据

| 类型 | 实际结果 | 证据 |
| --- | --- | --- |
| 原始归档/离线评分 | 19份SHA256/CRC通过，19项评分零issues，全部数值一致 | verification/20261020-direct-preflight-local/；云端offline-report/ |
| 新控制测试 | 本地16项通过；包含真实子进程超时、真实本地Git提交/推送、重复保护、失败打包与密钥遮盖 | control-api-fixed.log；tests/test_chemeleon_preflight.py |
| 当前源云端测试 | M1 17/17；M2 scoped 77/77，无skip；Ruff及安装重复性通过 | m1.xml、m2.xml、ruff.log、installation-*.json |
| 当前源官方smoke | unchanged AnalyticOracle合成smoke通过，Chrome导出成功 | smoke.log |
| 真实API | 现有secret映射到MATERIALS_PROJECT_API_KEY；mp-149身份字段请求成功，约0.73秒 | api.json；admission-outcomes.json |
| 真实模型/环境 | 实际加载Chemeleon和ORB权重，无采样和oracle查询；4 CPU、Torch2线程、约82GB可用盘 | environment.json/log；dependencies.log |
| 调度/失败/保存 | 17独立runner，峰值17，16成功+1预期失败；18个Actions artifact（CI+17probe）；main保存成功 | scheduling-validation.json、github-jobs.json、probe.json、cloud-artifacts.json |
| 工作流静态检查 | 两份正式/预检YAML actionlint通过 | actionlint.log、actionlint-version.txt |

CI安装只在隔离副本运行M2/install.py，并安装已有M4接口依赖以测试最新共享配置；未将其M1/M4安装改动带回main。M2测试对象增加了Hydra运行目录上下文，以适配共享M4接口，未改其他成员的代码。正式独立基线不安装路由组件。

共享默认未设seed的单独测试，在固定源码`63077ea3ea612197a5ad0e71fbe015d80149ca37`仍出现M5的`int(None)`：单独XML保留1个失败，不属于以上77项通过；它不是独立Chemeleon使用的agent配置，不挡住本轮启动准备。本地/proc观测跳过未算通过；云端对应观测测试实际通过。首轮新增API检查因锁定客户端不接受timeout参数而失败，请求尚未发出；已修复，并保留首轮`verification/preflight-39383770866-1/`及失败摘录。没有用旧78346d6的CI替代本轮结果。

现有方法文字和幻灯片仍完整，幻灯片SHA256核对一致，覆盖数仍为19/36，Chemeleon总体汇总未伪填；未重做无关报告。四张微信原图和课程要求已核对；未代发群消息。

## 下一步准确操作（本轮未执行）

在已安装并登录GitHub CLI的仓库副本中，先预览：

```bash
python3 M2/submit_chemeleon.py --source-sha 63077ea3ea612197a5ad0e71fbe015d80149ca37 --parallel 17
```

正式启动时执行同一条命令并增加`--submit`：

```bash
python3 M2/submit_chemeleon.py --source-sha 63077ea3ea612197a5ad0e71fbe015d80149ca37 --parallel 17 --submit
```

助手通过GitHub Contents API仅向M2开发分支写请求提交，由已部署的push工作流一次展开当前剩余17项；它不会在本机进行模型计算，也不会触发旧baseline_sweep。请求必须使用`mode=formal_direct`、上述受检source_sha、`units=all_missing`、`max_parallel=17`及明确acknowledgement。如果只重试一项，增加`--units '[{"system":"Au-K-Tb","seed":17}]' --retry-of '{"Au-K-Tb-17":旧attempt整数}'`，并保留该项失败证据。

当前无真实启动阻塞。账号未来名额、各单项6小时内能否完成和可选初始池续跑能力仍有限制，不能保证科学实验全数成功。本轮不再启动任务、不新增监控或定时跟进。
