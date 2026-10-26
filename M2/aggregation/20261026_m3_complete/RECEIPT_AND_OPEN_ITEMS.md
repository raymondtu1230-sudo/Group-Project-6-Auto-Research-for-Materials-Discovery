# M3 完整交付验收与当前待办

日期：2026-10-26（新加坡）。数据快照：`dcd3481a44f5bd9e0f9d7e58778a7f59a5a81210`。

本轮新收到 `M3/results/frozen_20261025/protocol_v1/m3_full/` 的 18 项原始结果。M3 的 `m3_full`、`m3_planning_off`、`m3_self_correction_off` 三组现在各 18 项，可以完整配对；旧版汇总中“缺 m3_full 原始包”的待补项已关闭。

| 工作 | 当前状态 |
| --- | --- |
| M3 完整 54 项组件研究 | 已收齐，配对验证与共享汇总完成 |
| 相对 Random/Chemeleon 比较 | 已扩充至 144 项结果、288 个基线配对 |
| M3 规划 / 自纠正组件增益 | mSUN 分别 +1.3889 / +0.6667；AUDC 分别 +13.5278 / +4.4444，均以 m3_full 减 OFF |
| M3 曲线、AF/EF、成本 | 已使用实际记录更新，保留重建历史的来源说明 |
| Full-agent planning_off / self_correction_off | 不属于 M3 的未完成任务；是否追加及由谁执行，交 M1/M6 决定 |
| M5 正式 exploration_off | 此快照未发现完整交付，继续等待 |
| M6 其余 check/hidden 与最终报告 / PPT | 继续收集和组装；已有历史 Random check 保留独立标签 |

此前把额外 Full-agent 两项视作 M3 待补任务的表述，在本次职责澄清后已撤回。组件实验和全模块 Full 实验仍保持明确区分，不能互相改名替代。M3 当前交付可以按其实际职责验收收尾，无需为本次汇总重跑已完成实验。

所有新结果均为离线核验已有真实记录，没有模拟实验、没有新增模型或 oracle 调用。原始目录、先前汇总和失败记录均保留。只修改 M2 文件，未代发消息。

可由用户转发的简短回执：

> Received, thanks. The complete 54-run M3 package is now validated and included in the shared tables, curves and baseline comparisons under M2/aggregation/20261026_m3_complete. The paired mSUN gains are +1.39 for planning and +0.67 for self-correction. M3's assigned handoff is complete; any additional Full-agent ablations are for M1/M6 to decide.
