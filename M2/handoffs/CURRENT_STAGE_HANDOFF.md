# M2 当前交接入口，2026-10-25

M2 自己的两种 dev 基线和 18 项冻结版工具路由消融已完成。18 项均为真实的 20-query 单次运行。旧 36 项基线通过兼容性核验后复用，没有重跑。

| 接收者 | 当前材料 | 状态 |
| --- | --- | --- |
| M1 | 原工具路由代码、配置和接口测试；冻结版已采用该组件 | 已集成。不要在冻结版上重新运行旧 installer |
| M6 | [本轮方法与结果](../METHODS_AND_M6_HANDOFF.md)、[四页英文内容](../report/M2_Frozen_Routing_Slide_Content_20261025.md)、[新英文讲稿](../report/M2_SPEAKER_NOTES_20261025.md)、四方法对比及官方 AF/EF | 结果文字、四页内容和讲稿可交。原生 PPTX 更新与视觉检查仍待 27 Oct 前完成 |
| M6 | [真实结果与分析](../verification/preserved-40204426478/report/)，包括完整可见结果、原始审计、单独的离线曲线复评与成本 | 已有 18/18 路由消融及兼容的 36 项基线。原始隐藏 Hydra 附件缺失已单列，不声称字节齐全 |
| M2 | M3 两项、M4 一项、M5 一项正式冻结版消融；M6 check/hidden 结果 | 待收齐后核验并汇总，27 Oct 前交全组表格和曲线给 M6 |

本轮 Full 的平均 mSUN/AUDC 为 10.0000/88.1111，routing-off 为 7.7222/70.1389。结论限于六个 dev 体系和三个 seed。

18 项原始 post-exit 审计没有被改成通过。官方 runner 完成后删除 checkpoint；独立终点审计及真实记录的离线复评通过，后者核对了 720 个基线前缀和 72 个原始终点。上传器漏掉的 54 个原始隐藏 Hydra 文件没有伪造或重建。

此次只准备交接材料，没有代发消息，也没有声称组员已接收。整个 M2 职责还包括 27 Oct 的全组结果汇总，不能把本轮个人实验收尾等同于全组汇总完成。

---

## Historical record: 21 October entry

The text below is preserved from the earlier stage. Its pending items and counts do not describe the current result.

# M2 当前阶段交接入口

2026-10-21。36/36独立dev基线完成，Random与Chemeleon各18项，720次查询，issues=[]。两项终态均verified_completed，原始归档和官方最终报告均持久保存。未代发消息，未获接收确认。

| 接收者与节点 | 材料（相对M2） | 状态 |
| --- | --- | --- |
| M1，24 Oct前 | integration/、configs/m2_routing.yaml、install.py、HANDOFF_LAYOUT.md、ACCEPTANCE_CHECKLIST.md | 独立组件与原版本测试可交，集成与冻结由M1完成 |
| M6，24 Oct前 | METHODS_AND_M6_HANDOFF.md、report/M2_Method_and_Dev_Baselines_20261021_36of36.pptx、report/M2_SPEAKER_NOTES.md | M2自己的4页草稿，不是全组最终PPT |
| M6，结果于27 Oct前汇总 | verification/direct-39432570527-1/final-report/、verification/stage-closeout-39432570527/cost.csv、cost-scope.json、terminal-validation.json | 全36项评分、曲线、成本与归档核验完整 |
| M2后续 | 同一冻结版M1 reference、成员消融结果包 | 接收后核验与汇总，不代跑 |

可由用户发送的短消息：M2的36项dev基线全部验收收尾了，两种方法各18项、每项20次查询，官方复评无问题。代码、测试、完整原始归档、评分表、曲线、成本及我的4页PPT均在main/M2，入口CURRENT_STAGE_CLOSEOUT.md。M1可以取接入代码和测试材料，M6可以取结果与slides。后续routing-off等同一冻结版reference后再做。
