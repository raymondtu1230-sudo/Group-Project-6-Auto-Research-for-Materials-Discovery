# M2 独立dev基线阶段已收尾：36/36

2026-10-21，Asia/Singapore。本轮实际核对起于03:22；终态审计03:23通过。Random18/18、Chemeleon18/18，六个dev体系、seed17/29/43、每项B=20且20次查询，共720次成功查询。官方离线复评issues=[]，无基线缺口。当前阶段完成；整个M2和课程项目仍有后续工作。

| 最后两项 | 状态 | mSUN@20 | AUDC | driver秒 | 完整job秒 |
| --- | --- | --- | --- | --- | --- |
| Au-K-Tb/17 | verified_completed，20/20，exit0 | 3 | 33.5 | 13063.939 | 13226 |
| Co-Dy-W/43 | verified_completed，20/20，exit0 | 3 | 35.5 | 19314.637 | 19455 |

Co-Dy-W/43于03:07:45完成，Au-K-Tb/17于01:23:57完成。两项均使用原run39432570527、attempt3943257052701，无再次启动科学实验。自动preserve成功，原始ZIP、receipt、环境/API及预算证据已写入[持久归档目录](verification/direct-39432570527-1/)，官方最终报告提交d890daf。

## 官方结果

| 方法 | 覆盖 | mSUN@20均值 ± 样本SD | AUDC均值 ± 样本SD | 平均driver分钟 |
| --- | --- | --- | --- | --- |
| Random | 18/18 | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 | 15.9893 |
| Chemeleon | 18/18 | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 | 234.3093 |

按每个seed内六体系等权平均，再计算三个seed的均值与样本SD。官方AF/EF及零基线约定保持原样，详见逐项与方法表。Chemeleon相对Random的官方方法均值AF=1.6876321778、EF=7.5266754850；EF包含Co-Dy-W/17零基线时的官方100约定，不能解释为运行速度或硬件加速。仅这组dev基线支持此比较，尚未测出工具路由收益。

## 证据与交付

- [官方CSV、按体系曲线、方法汇总及复用plan](verification/direct-39432570527-1/final-report/)，[终态验收](verification/stage-closeout-39432570527/terminal-validation.json)。归档全部SHA256和CRC通过、单位唯一，原19项manifest哈希仍为11c6e0dfd27c7c57d1b51d31cdd588be6475e0c804d4069e5e88d8522f4f2fee。
- [当前36份归档清单](configs/current_stage_verified_baselines.json)，独立于未修改的原19项固定清单。两项最终canonical receipts在execution_ledger，核验结果已记录于terminal-validation。
- [逐项成本](verification/stage-closeout-39432570527/cost.csv)、[时间与费用边界](verification/stage-closeout-39432570527/cost-scope.json)。成功driver时间、完整Actions job时间及安装/保存余量分别记录。已知模型费USD0不等于总计算费用0；硬件、电费和所有旧失败尝试未完整定价，token空白不补0。
- [失败与超时说明](verification/stage-closeout-39432570527/failure-records.json)。旧timeout、检查点与不安全原生恢复证据保留，无自动再次重跑。
- [版本、离线复现、测试/API与协议证据入口](verification/stage-closeout-39432570527/reproduction.json)。固定科学源63077ea、控制器e22cfb；最终两项Python3.12.15，原uv.lock。环境、数据、配置与捕获源哈希见原runtime/science-inputs.json及最终reuse-plan。两项105个科学输入文件逐一匹配固定科学源，见[协议/版本核对](verification/stage-closeout-39432570527/protocol-version-check.json)。6项收尾测试和真实34/35项历史离线复评证据保留，本次只读终态核验覆盖全部36项。
- [M2自己的4页可编辑PPT](report/M2_Method_and_Dev_Baselines_20261021_36of36.pptx)、[讲稿](report/M2_SPEAKER_NOTES.md)、[数据来源](report/current_results_data.json)。保留旧稿，完整官方曲线另存于报告目录，PPT示例曲线仍明确标注Mg-Sn-Sr/17。
- [代码/测试交M1及表格/曲线/方法/自有slides交M6](handoffs/CURRENT_STAGE_HANDOFF.md)。材料已准备，未代发、未声称成员接收。

## 保存与范围

用户02:28明确允许原始包、运行/环境日志、评分及交付材料并入main/M2。此前35项本地阶段稿保留在原工作区；主分支采用已发布的36项最终canonical归档与报告，包含这35项的全部原始科学结果。历史拦截记录保留。所有本轮新增/修改只在M2，以最新main为基底，非强推后读回核验。没有修改其他成员文件、根工作流或共享记录，没有处理PR2、购买资源、使用GPU或运行check/hidden。

M1集成冻结及reference、M2后续routing-off和成员结果接收、M6 check/hidden与全组报告分别作为后续。报告missing_units中的18项m1_full属于这些后续，不是独立基线漏项。本阶段保存与核验完成后停止本次监控。
