# 本轮接收记录与待补项

核对的 main 快照：`95f9c8e38923ac494b1117a9b212702afdc5980f`。日期：2026-10-26（新加坡）。

| 交付 | 本轮核对结果 | 汇总位置 |
| --- | --- | --- |
| M4，`9a75966b0c6e3d3fe0da41197f8e013170096110` | 18 项 Memory OFF 原始数据齐全；只关闭 memory；可以配对冻结 Full | 主基线与单开关消融表 |
| M3，`5d2efeadc19e1a6747aa4c0b6f473e8ed64c09fb` | 36 项真实冻结源码实验齐全；两组额外关闭 exploration、routing | M3 组件实验表，与 `m3_full` 对照 |
| M3 的 `m3_full` | 只有历史 18 行 CSV 和一个不含轨迹的示例，没有完整 18 项原始目录 | 标注“历史汇总，配对验收待补”，不编造 AF/EF 或曲线 |

本轮按照同学的请求，对现有原始结果使用 M2 评估代码核验，并补算相对 Random/Chemeleon 的配对 AF/EF。只做离线评分，没有重跑实验，也没有调用模型或 oracle。

M3 的 36 项不能直接记作冻结 Full 的 `planning_off` / `self_correction_off` 完成：与 Full 相比各改变三个开关。保留实际方法名，独立列出，待 M1/M3 明确是否还要交正式 Full 单开关实验。M3 自己的组件结论仍需完整 `m3_full` 基准目录才能独立复核。

本轮未发现 M5 正式冻结版 `exploration_off` 完整交付。M6 已有历史 Random check 结果，Full/Chemeleon check 与课程 hidden 输出仍待收齐。当前共享表可以交给 M6 组装，但全组收尾尚未完成。

实际执行的 M4 独立测试为 15/15 通过；联合 72 项选集因 Hydra/pymatgen 缺失而在收集时停止，不能写成 M2 已独立确认 72 项通过。原始日志和结果完整保留。

虽然用户已允许必要时备份后编辑其他成员文件，本轮没有编辑任何其他成员文件。所有新文件和交接入口更新均位于 `M2/`。没有代发消息。

可由用户转发的简短英文回执：

> Received, thanks. M4's 18 memory_off runs and M3's 36 component-study runs have been checked with M2's evaluation code and added to the shared results and baseline comparisons under M2/aggregation/20261026. M3 stays paired with m3_full, separately from the Full single-switch ablations. Please also share the complete 18-run m3_full raw package so I can finish validating that pairing.
