> **2026-10-21终态：36/36项独立dev基线验收并完成本阶段收尾。** Random18/18、Chemeleon18/18，720次成功查询；两项最终attempt均exit_code=0，官方复评issues=[]，SHA256/CRC与终态receipt核验通过。最新入口：[CURRENT_STAGE_CLOSEOUT.md](CURRENT_STAGE_CLOSEOUT.md)。仅M2范围。M1 reference、routing-off和M6 check/hidden为后续。以下旧状态保留为历史快照。

## 历史记录（下文按原日期保留）

# 本次两项结束后的 M2 阶段收尾

授权：2026-10-20 22:06–22:09，Asia/Singapore。用户睡觉期间继续监控已启动的两项，完成当前阶段收尾。用户再次明确：主分支所有新增/修改只能在 M2，不能干涉其他成员工作。此文件取代旧 OVERNIGHT_RUNBOOK 中“尚未开跑、暂停监控”的本次调度描述，旧证据仍原样保留。

## 范围与当前事实

- 只收尾独立 dev 基线、M2 自己的结果/代码交付入口、复现说明、成本说明、工作日志，以及自己的方法文字和幻灯片。并不代做整组交付。
- 只读完成核验必需的 M1 协议和接口；不修改 M1/M3/M4/M5/M6、共享记录或根目录工作流。不合并/关闭 PR2，不删除分支，不替别人运行科学实验，不发群消息，不声称别人接收/验收。
- 本次运行 39432570527；固定科学源 63077ea3ea612197a5ad0e71fbe015d80149ca37；控制器 e22cfb145466c056cee5ce8f4de8b75a6d15d1df。当前两项 Au-K-Tb/17、Co-Dy-W/43，attempt 3943257052701，retry_of 3938658932401。
- 已接受 34/36：Random18、Chemeleon16。此前34项的官方重新评分 issues=[]；原19项 manifest SHA256 必须保持 11c6e0dfd27c7c57d1b51d31cdd588be6475e0c804d4069e5e88d8522f4f2fee。
- 两项在 21:43 独立启动。job总上限360分钟，内部按实际安装耗时扣除，预留330秒退出/保存；上限约10月21日03:43。不要因监控或文档提交重启/取消健康任务，也不要再派新科学attempt。
- 原生恢复实测不安全，已经按用户授权从头运行；不能把恢复探测执行成功说成恢复通过。旧timeout、完整候选和检查点保留。

## 已经接好的即时保存

运行中的既定工作流在每个计算job后执行 always 打包与上传，成功/失败/超时均保留独立产物，Actions副本保留90天。独立 preserve job 先将ZIP、receipt与GitHub任务metadata提交 main/M2，再安装锁定环境并离线重评，避免评分失败损坏原始保存。

目标原始目录：`M2/verification/direct-39432570527-1/`。

目标官方报告：该目录的 `final-report/`，含 `validation.json`、`per_run.csv`、`per_method_summary.csv`、`per_system_summary.csv`、`discovery_curves.svg`/`.png`、`reuse-plan.json`；`M2/LATEST_BASELINE_RUN.json`提供入口。原始数据的保存不依赖ChatGPT保持打开或用户再次确认。

## 每次定时复核做什么

1. 用 GitHub 只读API读取该run及jobs，按实际状态判断。仍在正常执行就保留，不启动新单元。按用户00:17更新要求，每次定时检查后都汇报实际时间、状态及可核实计数；读不到计数则明确说明。运行中日志404、初始化耗时、暂时无查询不能当死锁。不猜查询计数。
2. 两项终止后先等/检查独立preserve的结果。不能把job绿色等同于科学验收。保存实际jobs时间、结论与完整结束日志，敏感信息保持GitHub掩码。主分支最新原始ZIP和receipt必须实际存在，不能只留短期链接。
3. 若只出现上传/发布/评分失败，在M2范围内修复该收尾操作，复用原ZIP离线重评，不重跑科学；不修改指标数字、官方逻辑或合理校验保护。无法自行解决的权限/产物丢失问题，保留证据、明确具体阻塞并结束，不能循环碰运气。
4. 以 main 最新提交为基底，隔离checkout，只读取共享协议；原始19项不变，新成功从 execution_ledger 的 verified_completed receipt复用，去重后生成完整36格清单。若任一新attempt失败，按实际34/35项收尾，保留缺口、退出码和失败记录，不能宣布36项完成或自动再次重跑。

## 最终数据验收与离线命令

正常工作流已生成最终报告时，先做本次只读核验：

```bash
python3 M2/verify_stage_closeout.py \
  --report M2/verification/direct-39432570527-1/final-report \
  --output M2/verification/stage-closeout-39432570527/terminal-validation.json \
  --terminal
```

此工具核对原19项manifest、每项B=20/20次查询、完整dev体系和seed、单位唯一性、报告缺失项及每份引用ZIP的SHA256/CRC、两项新attempt的持久终态receipt。它不重算指标，不调用模型、密钥、API或oracle，也不会把M1未交reference当基线漏项。输出已存在则换一个新证据文件名，不能覆盖。

若最终官方报告缺失，仅在固定63077ea的隔离科学checkout中用已有锁定环境重新导入最新published main并离线评分：

```bash
uv sync --locked --project M1/MADE
uv run --locked --project M1/MADE python M2/chemeleon_preflight.py plan \
  --published /path/to/latest-main --output M2/runtime/overnight-final-plan
uv run --locked --project M1/MADE python M2/evaluate.py \
  --results-root M2/runtime/overnight-final-plan/reused \
  --output M2/runtime/overnight-final-report --split dev --allow-partial
```

示例路径必须替换为实际隔离副本；输出目录需为空。不要调用 run_baselines、旧 baseline_sweep、batch恢复、大模型采样、check/hidden、GPU或付费资源。将最终报告和导入plan保存回最新main/M2后再执行上面的terminal audit。无需打印密钥或重新要求用户提供密钥。

## 数据通过后完成当前阶段交付

- 发布 `M2/CURRENT_STAGE_CLOSEOUT.md` 和 `M2/verification/stage-closeout-39432570527/`：本次代码与科学版本、各run/attempt、36格覆盖和缺口、原始归档入口、官方评分/曲线、终态失败记录、测试/真实API证据、运行/预算/保存证据、复现命令及验收边界。
- 保存 `M2/configs/current_stage_verified_baselines.json`，单独列出本阶段实际已验收的归档路径/校验和/单位来源；不要覆盖固定原19项的 verified_baselines.json。科学分数只从官方报告读取，完整表与曲线也保留原文件。
- 成本分开写：成功单元的20次查询、driver wall time、实际GitHub安装/完整job耗时、已知API/模型费用；失败尝试单独保留。不把known_cost_usd=0解释成硬件、电费和所有失败尝试总成本为0，不臆造token数。不把AF/EF当硬件加速比。Chemeleon未满18项时不编造整体方法分数。
- 同步 README、STATUS、DELIVERY_STATUS、ACCEPTANCE_CHECKLIST、WORK_LOG、METHODS_AND_M6_HANDOFF，以及 report/README、讲稿和当前结果数据的最新入口。历史章节清楚标为历史，保留原始证据和旧失败；最新入口中不能再把19/36或“17项未启动”当当前事实。
- 核对并更新 M2 自己的4页可编辑幻灯片，沿用其现有结构和M6草稿用途，数字/曲线来自新官方报告。使用新的dated文件，保留19项和原两项的历史版；同步讲稿、来源数据、SHA256和report入口。完整比较若仍缺结果，明确部分覆盖，不填完整Chemeleon值。用Presentations技能渲染查看实际页面，确保无溢出/错表，不制作整组PPT或编辑M6目录。
- M2自己的方法/代码交M1、结果表/曲线/方法和自己的slide材料给M6，统一在 `M2/handoffs/CURRENT_STAGE_HANDOFF.md`列路径、内容、版本和后续依赖，准备好可供用户发送的短消息。禁止代发或声称已接收。
- 核对组件文件和已有源版本测试证据一致；本次只是M2离线收尾，不因其他成员最近修改而擅自调整他们的配置。共享集成旧失败按原源码版本标注，若没有复验就不评价当前他人代码。不得借收尾合并整条开发分支。
- M1完整集成/冻结/reference，M2未来routing-off和接收成员结果，M6 check/hidden与整组报告均单独列为后续，不能说全部M2科学任务/课程项目已经结束，也不能拿这些后续条件挡独立基线验收。

## 提交、通知和停止

所有文件正式提交 main/M2，读取最新head，非强推/expected_sha提交以保留其他成员新提交；发生并行更新要重新读相应文件后重建M2-only提交。检查该次commit/compare每个路径都以M2/开头，读回关键报告和terminal-validation，确认不是只留本地或未发布草稿。不要reset/clean已有工作区。

只有实际完成保存、数据核验与上述本阶段文档/幻灯片核对，才给用户一次最终中文通知，说明34/35/36实际覆盖、两项最终结果、当前阶段是否已收尾和main/M2链接。然后将本次监控 is_enabled=false。每次检查都按用户更新要求简短汇报。若仍有健康实验运行，继续原有限次数监控；若全部实验终止且仅剩不可解决硬阻塞，说明缺什么、为什么、已保全到哪里后暂停。定时复核有次数上限，不无限轮询、不新建后续监控、不再消耗整夜额度。

## 本次要求核对

本轮实际读取新版分工PDF两页、操作指南八页，以及四张13:30微信原图；同时重新读取老师项目说明和10月16日提交要求。分工规定M2负责两种基线、评分曲线、工具路由，代码交M1，结果/材料交M6；老师要求官方mSUN@B、AUDC、AF/EF及成本、固定科学协议、可复现原始轨迹。微信要求独立文件夹、既有M1接口、真实配置环境/API、保留契约/无效输出/状态测试，禁止更改官方科学逻辑。群里通知由用户处理。附件哈希及本次只读准备核验见 `verification/stage-closeout-20261020/`。

## 2026-10-21 02:23 状态与人工保存边界

Au-K-Tb/17科学验收通过，35项官方离线评分issues=[]；Co-Dy-W/43仍在原job计算。新增项原包手动上传被自动审批拒绝，原因是运行和环境日志可能含敏感信息。本次只发布评分、曲线、成本摘要和M2自己的交付材料，不把被拒绝的包改用其他通道上传，不单独上传其运行日志，也不派发新工作流。已有自动归档仍按原配置运行；不得将配置存在等同于实际保存成功，结束后检查真实终态。当前持久原始归档覆盖仍为34项，35项评分可用。

## 2026-10-21 02:28用户已明确允许保存

用户在看到原始包含运行/环境日志、30个评分交付文件及main/M2范围后明确确认可以并入。上一节人工上传待确认状态至此结束。本次35项完整原始归档、日志、独立验收、官方评分与材料入口一并保存到verification/auktb17-closeout-20261021/；current_stage_verified_baselines.json现列35项，原19项清单未改。后续不得再用先前待确认状态阻塞已授权的同范围收尾。最后一项继续既有run，不创建canonical receipt或最终自动归档目录抢占在途工作流。最终归档仍先检查实际结果，只有全部36项验收通过才宣布36项完成。

## 最终状态：36/36，监控已停止

两项均已verified_completed，自动归档及最终官方离线评分已写入main，提交d890daf。36份原始科学归档齐全，无基线缺口，720次查询，issues=[]。本次35项手工草稿保留在原本地工作区；当前主分支入口统一指向36项canonical归档、评分和阶段交付材料。用户02:28的M2保存授权继续有效。只读终态审计和M2自己的四页PPT均已核对，监控停止，不再派发实验或持续轮询。
