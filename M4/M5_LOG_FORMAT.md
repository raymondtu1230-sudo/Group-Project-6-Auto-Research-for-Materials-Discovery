# M5 日志格式与样例

这是待 M5 确认的格式，尚未发送或获得同意。

两组都从官方 episode trajectory 导出 evidence.jsonl；包含最后一次查询。Memory 插件日志只用于调试，不能替代完整 trajectory。JSONL 保留每次候选的 proposal 结构和已查询的能量/稳定性结果；overview.csv 是方便阅读的表格样例。

字段：run_id/episode_id 区分实验；step_id/query_count 表示查询次序；candidate_id 区分本次结构；status 为 evaluated；reduced_formula 是组成标签；energy_per_atom、formation_energy_per_atom、e_above_hull 单位为 eV/atom；is_stable 为当时 observed phase diagram 判断；is_newly_discovered 是官方观测标记。

当前目录 evidence/synthetic-smoke 的两条记录全部来自 synthetic Li-O/analytic oracle 测试，不可当作真实发现或失败案例。真实实验需同时保留命令、种子、配置、机器和完整官方输出。

M5 要分析 over-exploitation / wasteful exploration，还需 M1/M5 在策略层记录探索模式、方向选择理由、剩余预算和候选来源。M4 不能从能量记录推断这些理由。正式运行前请 M5 确认字段够用，必要时扩展导出格式。
