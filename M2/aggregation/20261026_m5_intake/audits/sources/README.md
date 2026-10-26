# M5 development intake audit — 26 October 2026

Snapshot: `a27634d9edbf231d0c034273fa9f977f9d5e799e`.
This audit reads existing files only. No science was rerun, no models/oracles were called, and no original artifacts or GitHub files were changed.

**18 项真实完成结果可收为带明确限制的端点证据；完整交付包尚未通过。**

## 已核实的结果

- `exploration_off` 有且仅有六个 dev 系统 × seeds 17/29/43，共18项，全部 attempt_01、completed、一次 episode、20次查询，总计360次。没有 check/hidden 结果或已有失败尝试出现在这次交付树中；这不能证明其他位置从未存在失败尝试。
- 全部18项的原始 trajectory、summary、episodes 表中的 mSUN/AUDC 相同，协议和精确独立材料参考数据均与各自选中的已完成 frozen M1 Full 一致。参考比较采用既有 M2 canonicalization，不舍入能量、晶格矩阵或分数坐标。
- 18×74=1,332 个 metadata 指纹全部吻合原始02e002冻结源码的 Windows CRLF 表示。另对108个科学代码、配置、协议、数据及依赖文件核对，当前快照与原始冻结版在 LF 规范化后全部相同。
- 与各自 Full metadata 命令相比，排除运行输出路径后，唯一设置变化均为 `agent.enable_exploration=true → false`。其余四项开关全部启用，seed/B/CPU ORB 等命令设置相同。

源码中的固定生成配置保持不变：主生成器为 checkpointed Random；路由的 Chemeleon 为 CSP、batch_size32、device 跟随 CPU oracle。探索参数为 alpha0=0.8、gamma=1.0、beta0=2.0。这里核实的是被冻结文件和记录命令，不能取代缺失的实际 resolved config、模型二进制哈希或环境安装证据。

## 完整包缺口

每个 attempt 只有7个文件：metadata、原始 trajectory JSON/图、summary JSON、episodes JSON/CSV、参考图；另有一个 console 文件放在 seed 父目录，共144个接收文件。

**全部18项均缺少实际 resolved configuration、原始 Hydra 配置和组件日志**，包括 M4 evidence/proposal capture 和运行组件日志。缺失的原始每查询 history/checkpoint 也未收到；官方成功运行会删除 checkpoint，不能因此反推运行失败，但不能宣称历史文件已恢复。关闭探索时是否本应生成 M5 decisions 文件需按官方组件行为区分，核心缺口是配置和已启用组件日志。

应从 M5 的原运行目录补交这些原始文件，保留原路径对应关系和现有 attempt_01。**不要拿源码默认配置重新生成文件并称为实际原配置，也不要为补附件而重跑科学实验或覆盖 attempt。** 补齐前，`complete_required_original_packages=false`、`actual_resolved_one_switch_configurations_certified=false`。

metadata 的 `made_upstream_commit` 记为 `aedf8ca238d2ef56948c0eadf2c897aef67f5104`，而 protocol 的 upstream 是 `bffda0c…`。GitHub 已确认 aedf8ca 是本组仓库的 M2 文档更新提交，不能把它解释为 MADE upstream 或原始冻结 HEAD。1332个指纹和108文件等同性支持冻结科学输入一致，但这次没有收到准确 detached HEAD/clean-status 记录。

M5 记录的运行平台是 Windows AMD、Python3.12.10、torch2.14.1+cu126；选中 Full 是 macOS ARM、Python3.12.13、torch2.9.1。尽管命令指定 CPU，报告“same machine family”仍不成立。不能将时间差当作受控效率实验，也应保留跨平台/依赖差异的因果解释限制。

## 应使用的配对数值

均值与样本 SD 的单位是三项 seed mean，每项等权平均六系统；胜/平/负统计18个 system-seed 配对。

| 项目 | mSUN | AUDC |
|---|---:|---:|
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Exploration off | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 |
| Full − off | +0.3333 ± 1.8559 | −0.1111 ± 18.8947 |
| Full 胜/平/负 | 8 / 1 / 9 | 9 / 0 / 9 |

因此目前只支持整体均值接近、效果随系统和种子变化；不能把总体差值说成统一改善。

M5 表中的 ON **9.8 /87.0** 不应直接汇总。仅把 frozen `Mg-Sn-Sr/seed_17/attempt_02` 的 **12 /105** 换成21Oct `M5/evidence/dry-run-alpha0.8` attempt08 的 **9 /84.5**，就精确重现报告的 Mg **10.0 /96.0** 和整体 **9.8±2.7 /87.0±28.5**。没有收到选择脚本或 manifest，因此此处表述为“与旧 dry-run 替换精确吻合”，不声称已经证明作者如何操作，更不声称是所有失败 attempt 被平均。

## 曲线与失败案例限制

`M5/src/m5_analysis.py` 用累计稳定发现数的逐点求和计算名为 AUDC 的值；该算法与官方梯形面积不同，18项均不相同，均值93.0556对官方88.2222。不要把 helper 输出当官方指标。

累计 trajectory 的 `is_stable && is_newly_discovered`，并按照官方 `_extract_discovery_curve` 加入 `(query0, discoveries0)` 原点后，全部18项的最终 mSUN 与梯形 AUDC 都精确匹配原记录。注意 Ga-Pt-Tm seed43 第一次查询即发现稳定新材料；若漏掉原点，会少算0.5并误报126.0对126.5差异。这是审计算法的问题，已在脚本和输出中纠正。端点算术一致仍不能称为原 checkpoint 已恢复；保存的曲线应明确标为 recorded-trajectory reconstruction，配对 AF/EF 使用冻结官方指标函数。

报告 Ga-Pt-Tm seed17 的“15.7 vs10.3”实际是三 seed 的系统均值；真实 seed17 是16 vs10。报告所称 Full 缺少 M5 sidecar 已过时：本快照全部18项选中的完整 Full 都有真实 `m5_decisions.jsonl`。探索模式应据这些原日志核对，不能单凭三元成分推断。

明细在 `m5_input_audit.json`，端点表在 `m5_per_unit_endpoints.csv`；`audit_m5_inputs.py` 是仅使用标准库的可重复审计脚本。
