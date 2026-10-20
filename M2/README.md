> **2026-10-20 22:14 最新：用户已授权睡眠期间继续本次两项监控和阶段收尾。** 已启用有限次数的每小时复核；即时归档仍由GitHub工作流完成。所有收尾新增/修改严格限定main/M2，不改其他成员、共享记录或根目录工作流。见 [本次自动收尾要求](OVERNIGHT_FINAL_CLOSEOUT.md) 与 [两项启动记录](FINAL_TWO_RUN_STATUS.md)。当前已核验34/36；最终状态须等两项终止后按真实产物更新，不把定时任务启用算作科学完成。以下保留历史快照。

> 2026-10-20 最新状态：已有 **34/36** 项基线，本轮官方离线重新评分34项，`issues=[]`。剩余Au-K-Tb/17、Co-Dy-W/43在原生恢复验证未通过后，按授权使用新attempt `3943257052701` 从头运行；两项均已通过本次真实API和模型检查，进入独立云端runner计算，尚未计为完成。总job 360分钟，按实际安装耗时动态预留5分30秒退出/保存窗口。见[最后两项启动及34项收尾记录](FINAL_TWO_RUN_STATUS.md)、[34项评分证据](verification/final-two-preparation-20261020/closeout-34/)和[本次云端运行](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39432570527)。以下保留历史记录。

> **最新：2026-10-20 21:16，dev基线完整覆盖34/36。** 本次17项Chemeleon中15项核验完成、2项超时；34项完整结果及2份超时归档均已保存main/M2，并重新通过SHA256、ZIP CRC及查询曲线完整性检查。保存与两项断点内容见 [运行后核验](verification/postrun-20261020-2111/README.md)：Au-K-Tb/17无生成检查点；Co-Dy-W/43保存1024候选与第1次查询检查点，恢复尚未验证。未自动重跑。以下保留此前准备轮与交付快照，历史数字以当时版本为准。

> 交付方式：本轮材料通过 PR #5 单独交付至 `main/M2/`；用户已于2026年10月20日授权合并。共享框架接入仍由M1负责，PR #2 保留草稿。下述验收数字及失败对应审计时版本；本次文件交付不包含对后续共享代码变更的复验。

# M2：当前交付入口

更新：2026年10月20日。M2 负责开发集基线、工具路由和评估。**本轮只收尾 M2 可独立完成的准备与交付，不启动新的 Chemeleon、check 或 hidden 实验。**

## 当前完成范围

| 项目 | 当前状态 | 文件 |
| --- | --- | --- |
| dev Random | 18/18 已完成并核验，每项 B=20 | `configs/verified_baselines.json`、`verification/preserved-39306348134/` |
| dev Chemeleon | 1/18 已完成并核验，剩17项未启动 | `verification/20261019-chemeleon-recovery/` |
| 原始归档和离线评分 | 19份原始 ZIP 的 SHA256/CRC 均通过；重新评分复现全部数值，零审计问题 | `verification/20261020-handoff-audit/` |
| 工具路由组件、配置和测试 | 已准备独立交付；共享配置的 M1/M5 空种子问题单独保留 | `integration/`、`configs/`、`install.py`、`ACCEPTANCE_CHECKLIST.md` |
| 方法文字和幻灯片草稿 | 已更新为19/36；原始两项结果的旧版保留作历史记录 | `METHODS_AND_M6_HANDOFF.md`、`report/` |
| 交接与后续结果接收规则 | 材料已准备，尚未发送或确认验收 | `HANDOFF_LAYOUT.md`、`handoffs/` |

## 职责与交付

- 所有 M2 新增文件保存在本目录。组件源码、配置、测试、日志、报告和实验产物均由 M2 独立维护。
- M1 在24日前接收组件代码与测试证据，负责正式安装、共享集成、冻结及完整系统 reference。我们只在隔离测试副本验证接入。
- M6 在24日前接收方法文字和幻灯片草稿，27日前接收最终表格、曲线和结果说明。check/hidden 的执行与最终组稿仍由 M6 负责。
- M2 等 M1 冻结版 reference 后运行 routing-off；收齐各成员结果后再做最终汇总。当前不能宣称整个 M2 已完成。

完整职责核对见 [DELIVERY_STATUS.md](DELIVERY_STATUS.md)。未合并的开发分支仍为 `m2/tool-routing-evaluation`，PR #2 保留草稿。发布 M2 文件夹不等于合并共享框架。

## 可复现的离线核验

```bash
cd M1/MADE
uv sync --locked
uv run python ../../M2/prepare_missing.py --results-root ../../M2/results/reused --output ../../M2/results/inventory
uv run python ../../M2/evaluate.py --results-root ../../M2/results/reused --output ../../M2/results/report --split dev --allow-partial
```

输出目录需为空。以上仅复用与评分已完成的原始记录，不调用模型或 oracle。安装组件并执行微信要求的测试，见 [HANDOFF_LAYOUT.md](HANDOFF_LAYOUT.md)。

## Chemeleon 后续

剩余17项是相互独立的 dev 单元，可并行；本轮没有开跑。六小时总时限、保存余量、未通过的恢复验证及并发安排见 [CHEMELEON_EXECUTION_PLAN.md](CHEMELEON_EXECUTION_PLAN.md)。已有19项不得重跑或重复计数。
