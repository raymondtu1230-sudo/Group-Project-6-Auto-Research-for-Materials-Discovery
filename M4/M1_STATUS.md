# M4 接入验证记录 2026 年 10 月 19 日

基于团队仓库 `ae10752`。此前缺少的 M1/MADE 已上传，已读取真实 Agent、配置和测试。

## 本地已完成

- M4MemoryManager 实现 M1 的四个 Memory 方法，白名单保存已查询观测，支持去重与 JSON checkpoint。
- 配置通过现有 memory_manager 字段加载 M4；enable_memory 沿用 M1 独立开关。
- 使用真实 M1 Agent 测试 ON/OFF、Planner 参数传递、checkpoint、无效观测、长度上限和 Hydra 构造。
- M1 原有测试与 M4 全部测试、Ruff 代码检查通过，详情见 test_results.txt。
- 官方 synthetic smoke 运行成功，analytic oracle，1 episode，2/2 queries。轨迹导出为两条证据，包含最后一次评估。样例见 evidence/synthetic-smoke；不是真实材料发现证据。
- 首次 smoke 在两次查询结束后的 Chrome 出图阶段因执行权限失败；未改 runner，放行本地出图后重跑成功。

没有修改 Agent、官方 runner、Oracle、环境、评分或预算逻辑。发布状态以 GitHub 的 m4-memory 分支和 Pull Request 为准。

## 必须明确的限制

1. 默认 GridSearchPlanner.propose 不读取 previous 或 m1_memory。因此本次证明接口通路及流程可运行，不证明 Memory 已影响默认 Agent 的选择。需 M3 的 Planner 消费该字段并验证实际决策差异。M4 不替换 M3 算法。
2. M1 OFF 时不调用 Memory 插件，且 ON 时在下一次 proposal 才更新上一次结果。插件日志不含最后一次查询，也不能作为 OFF 的完整日志。两组统一使用 export_evidence.py 从官方 trajectory 导出；此工具只抽取查询观测，不读取 envelope 的 ground truth 字段用于决策。
3. 为避免混用历史，每 episode 创建新实例；协议 v1 每进程仅一个 episode。多 episode 自动身份分配尚未接入。
4. max_chars 约束返回记录序列化后的 JSON 字符长度，不等于模型 token 上限；M1/M3 负责最终 prompt 和 token 计量。
5. 已完成一组 Materials Project/ORB 真实流程验证，详见 REAL_TEST_STATUS.md；尚无 Memory 性能提升证据。待 Planner 消费 Memory 后再做消融。

## 复现

从仓库根目录：

```bash
cd M1/MADE
uv sync --frozen
PYTHONPATH=../../M4/src uv run --no-sync pytest -q -o addopts='' tests/test_m1_integrated.py tests/test_m4_memory.py ../../M4/tests
uv run --no-sync ruff check ../../M4/src ../../M4/tests ../../M4/export_evidence.py tests/test_m4_memory.py
PYTHONPATH=../../M4/src uv run --no-sync python ../run_smoke_test.py
```

若系统不允许默认缓存目录，可将 MPLCONFIGDIR 和 DSPY_CACHEDIR 设为本地可写缓存目录；图表导出需要系统允许启动 Chrome。配置文件仍通过原字段加载 M4，运行时须保留上述 PYTHONPATH，或先将 M4 安装到同一 Python 环境。

导出两组共同日志（每个 episode 单独运行，目标文件必须尚不存在）：

```bash
python M4/export_evidence.py PATH_TO_EPISODE_JSON PATH_TO_NEW_EVIDENCE_JSONL --run-id UNIQUE_RUN --episode-id 0
```

## 交付范围

M4/ 为模块、说明、测试与合成样例。M1 的改动仅有配置中的 memory_manager 配置块和新增 tests/test_m4_memory.py。不包含密钥或真实实验结果。M5 格式确认、M6 最终文稿与实验结果仍按原计划交付。
