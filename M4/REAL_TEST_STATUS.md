# M4 真实材料流程验证

2026 年 10 月 19 日，团队提交 bf141ca，M1 protocol v1，m1_baseline，dev Mg–Sn–Sr，seed 17，1 episode，20 次预算内查询。Oracle 为 CPU ORB orb-v3-conservative-inf-omat；其他策略仍为现有默认配置。

状态 completed，官方记录耗时 157.193 秒，约 2 分 37 秒。203 条 MP 数据加载后筛选为 194 条；初始化阶段重新评估 112 个稳定/近稳定结构。20 次仅指正式搜索查询，不包含初始化的额外 Oracle 计算。第一次有效运行还包含约 102 MB 模型下载，不能将耗时直接当作所有后续运行的预测。

官方 mSUN 计数为 7，AUDC 为 49.5。它们仅是本次 M1 默认 Agent 加 M4 记录模块的结果；默认 Planner 未消费 m1_memory，因此不能归因于 Memory，更不是完整团队 Agent 的最终结果。没有 ON/OFF 对照。

验收：官方 trajectory 有 20 条，M4 在线日志有 19 条（下一轮才更新观测），离线 evidence.jsonl 导出有 20 条且含最后一步。overview.csv 可供 M5 查看；proposal 结构保存在 JSONL 和官方轨迹中。策略选择理由/探索模式仍需 M5 在策略层提供，不能从当前日志推断。

本测试没有使用 LLM/OpenRouter。官方费用记录中 ORB 和 MP 的已知费用为 0；不含电脑电力及设备成本。LLM 计量字段为 not_reported，不能把该字段当作独立测得的零调用。

原始官方输出保存在本地 protocol_v1/m1_baseline/dev/Mg-Sn-Sr/seed_17/attempt_02/；未上传原始数据到此 PR。该目录中的评估指标和 ground truth 相图仅供实验后分析，禁止作为后续 Agent 的检索输入。M4 证据导出只抽取已查询观测。

下一步：M5 确认日志格式；M3 的 Planner 消费 m1_memory；之后按冻结协议做 Memory ON/OFF。当前不扩大实验数量。
