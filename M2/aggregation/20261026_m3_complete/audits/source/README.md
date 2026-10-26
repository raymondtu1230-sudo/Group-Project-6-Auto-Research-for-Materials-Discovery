# M3补齐m3_full后的独立验收，2026-10-26

本次读取固定快照 `dcd3481a44f5bd9e0f9d7e58778a7f59a5a81210`。新增18项 `m3_full` 已提供完整结果目录，连同原36项消融，共54项可以按 **M3组件研究** 接收。结果不是仅从旧CSV推算的。

## 分工修正

根据用户最新明确的分工，M3负责的是 `m3_full`、`m3_planning_off`、`m3_self_correction_off` 三种配置的组件研究。此前审计把全系统 `planning_off` / `self_correction_off` 的36项列为M3欠交任务，这一断言不再适用，应从M3未完成清单中撤回。是否另做全系统单开关实验，由M1/M6决定。

本次补齐也解决了此前缺少18项原始 `m3_full` comparator目录的问题。正确的组件配对是 `m3_full` 对另外两种M3配置。`m1_full` 的探索和路由均开启，属于不同配置，不能把它们之间的差值解释为只移除一个M3组件的效果。

| 配置 | 规划 | 记忆 | 自纠错 | 探索 | 路由 |
| --- | --- | --- | --- | --- | --- |
| m3_full | 开 | 开 | 开 | 关 | 关 |
| m3_planning_off | 关 | 开 | 开 | 关 | 关 |
| m3_self_correction_off | 开 | 开 | 关 | 关 | 关 |

## 实际检查结果

- 三种方法各18项，六个dev体系、seeds17/29/43覆盖精确且无重复；54项均为已完成的attempt01，单episode、20query，合计1080次预算内查询。
- 全54项原始trajectory、summary、resolved config、可见Hydra目录、M4日志、console log及重建history文件均存在。终点mSUN/AUDC、protocol及材料快照匹配检查通过。
- 36对实际resolved config逐项比较：除输出/日志路径外，只有预期的规划或自纠错开关变化，没有其他科学设置差异。
- 54×74=3996个原始源码指纹均匹配Windows CRLF checkout表示。另对108个科学源码、配置、协议、依赖锁及固定数据文件与原02e0026快照比较，规范化换行后全部一致。新m3_full记录ae7fe819、旧消融记录02e0026，不构成科学源码变化。
- 54个manifest中的432项均有解释：378个文本文件在LF转CRLF后精确匹配原hash和原bytes，54个空日志直接匹配。Git传输规范化了换行，不能把收到的LF文件称为未经任何字节变化的Windows原件。
- 全54项终点均复现之前报告值。现在有新的完整原始目录、时间戳和运行记录支持这些值，不能因数值相同就判定为旧文件改名。

## 结果及配对增益

均值与SD统一按M2口径：每个seed内六个体系等权，再对三个seed均值求均值和样本SD。

| 方法 | mSUN@20 | AUDC |
| --- | --- | --- |
| m3_full | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| m3_planning_off | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| m3_self_correction_off | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

| 比较，m3_full减去off | 平均mSUN增益 | mSUN胜/平/负 | 平均AUDC增益 | AUDC胜/平/负 |
| --- | --- | --- | --- | --- |
| 规划 | +1.3889 | 12 / 1 / 5 | +13.5278 | 10 / 0 / 8 |
| 自纠错 | +0.6667 | 7 / 10 / 1 | +4.4444 | 7 / 9 / 2 |

两项平均增益为正，但体系和seed间有差异；不能说每次都改善，也不能外推为全系统或hidden-set效果。M3旧报告中“18个运行之间的SD”不是这里的“三个seed均值SD”。

## 保留的证据说明

所有history均明确标为从原trajectory重建，终点与AUDC算术检查通过。本次没有用科学依赖重新复评每个prefix，因此不将这些文件改称原始checkpoint history。原始AF/EF零值是未配对的默认值；正式配对AF/EF应由M2评分程序在明确的曲线来源下计算。

54项resolved config中的M4运行ID为m4-local，而真实M4日志记录各自唯一的method/system/seed/attempt ID。日志记录正确，未发现共享记忆；这是后处理配置解析上下文不一致，作为证据细节保留。

详见 `m3_full_intake_audit.json`（逐文件、逐项、逐对检查）、`per_unit_endpoints.csv`、`per_method_metrics.csv` 和 `paired_gain_summary.csv`。

本次只读54项真实结果，没有启动agent、模型、oracle、数据查询或新实验，没有改动其他成员文件，也没有修改GitHub。
