**2026-10-19 更新：已完成 M1 接口接入和 synthetic smoke，实际状态与复现见 [M1_STATUS.md](M1_STATUS.md)。默认 Planner 尚未使用 m1_memory，性能实验仍待 M3 接入消费。**

# PE6203 M4 Memory Module — 独立初版

这是基于已批准设计的独立模块，不修改 MADE benchmark、Oracle 或评分逻辑。Python 3.10+，运行模块及测试不需要第三方依赖、API key、GPU 或网络。

核查的上游版本：diffractivelabs/MADE `bffda0c9a1fa1904b35c0ef67b455881c975df86`。

## 本地验证

在本目录执行：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 examples/mock_demo.py
```

示例全部为 synthetic mock，不是真实材料结果。它证明模块可以记录和检索，不能证明材料发现性能提升。

## 模块做什么

- `reset(context)`：开始新的 episode，清空可检索历史，不删除日志。
- `record(event)`：向 JSONL 追加证据。同一 run/episode/event_id 的相同事件只记一次；内容冲突时报错。
- `retrieve(query=None, limit=8, max_chars=4000)`：按组成原子比例的 L1 距离排序，同距离优先近期记录；默认预留位置给最近稳定、不稳定或错误、最新记录。最多返回 limit 条，summary 不超过 max_chars 个字符；返回的 event_ids/records 只包含摘要实际容纳的记录。字符限制不等于 token 限制。
- `get_state()` / `load_state(state)`：保存与恢复历史。加载时会将缺少的事件写入当前日志。ON/OFF 由运行配置控制，不从 checkpoint 覆盖。
- `enabled=False`：返回空检索内容，仍然记录所有新证据。

第一版明确限制：单进程、单写入者，本地可信 JSONL；不支持多个进程同时写同一文件。每个 episode 建议使用独立日志路径。读取旧日志用于幂等检查，不会自动将旧实验加入检索；续跑需显式 load_state。损坏日志会报错，不静默忽略。

## 交给 M1 的接入约定

以下接口是 M4 新接口，不是声称 MADE 已有这些函数。

1. 每个 episode 开始时 reset，context 必需字段：run_id、episode_id、elements。可额外保存 seed、Oracle/Agent 配置、上游及团队代码版本。
2. 每轮决策前 retrieve，将 summary 真正加入 Planner/LLM 输入。仅将对象放入 state 而下游不读取，不算成功集成。
3. 每次 env.step 完成后立即 record，包括最后一轮。用 run/episode/step 加事件类型构成稳定 event_id。
4. 记录 decision 证据时，使用 status='evaluated' 的评估事件内附 decision_context（检索 event_ids、实际输入摘要、候选来源）。该字段是审计信息，检索摘要不会再递归展开它。
5. 随 M1 checkpoint 保存 get_state；恢复时 load_state。若评估完成而日志未写入即中断，M1 应从可信 trajectory 补记该事件。

事件必需字段：event_id、step_id、candidate_id、status。status 为 evaluated/rejected/error；error 与材料不稳定分开。推荐附 composition（元素到原子数映射）、reduced_formula、structure_ref、energy_per_atom、formation_energy_per_atom、e_above_hull、is_stable、is_newly_discovered、reason 和 provenance。

候选结构由 M1 或适配器序列化为独立文件，structure_ref 指向它；candidate_id 应区分同组成的不同结构。模块不按化学式合并结构，不把失败组成永久拉黑。当前模块不验证结构文件是否存在，需在接入时验证。

MADE 的观测字段来自 `ConvexHullEnvironment.step()`；使用返回观测而不是读取隐藏 ground truth。e_above_hull 和 is_stable 是评估时的 observed phase diagram 判断，应结合 step 解读。先保留原始证据，不回写历史稳定性。

## ON/OFF 实验

两组都有日志，基础 Agent 原有 history、UniquenessFilter 等保持一致，唯一主开关是是否向决策者传入 M4 检索内容。这测量 M4 的增量收益，不等于完全无记忆实验。

固定化学体系、初始相图、模型设置、其他模块、Oracle、预算、配对种子；每次运行和 episode 隔离。记录检索内容、实际决策输入、官方发现指标、重复率、token/耗时，以及额外 OracleScorer 和初始化计算。不要只统计 env query_count 就当作全部计算成本。

先运行一对 ON/OFF 小实验估算成本，再决定体系及种子数量。用官方结果评估 mSUN/AUDC 等，不重新定义评分。保留无提升或负面结果，案例展示历史→检索→新选择→结果。

## 待集成后验收

- 验证 M1 的真实决策输入含检索摘要，OFF 不含摘要。
- 验证最终评估被记录、重启不重复计数、不同 episode 不串历史。
- 运行小型真实 MADE episode，核对 trajectory 与日志。
- 已获得 M1 代码并安装锁定环境；真实集成与 smoke 状态见 M1_STATUS.md。真实 ORB 实验及 Planner 对记忆的实际消费仍未完成。

## 暂定交付安排（2026 年）

10/21 前确认接口，10/22–23 接入与小实验，10/24 交模块、测试和日志样例；10/25 冻结，10/26–27 完成算力允许的配对实验和 2–3 个证据案例。已核对原始文件；详细交付对象、M5 日志约定、M6 方法文字和幻灯片提纲见 HANDOVER.md。
