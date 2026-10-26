# M5 supplemental package audit — 27 October 2026

Snapshot `b36e2a50d9d3e31fc941d827addab94db2c5d3cc`; original science freeze `02e0026bf450f71f4f7862228d295f5b02b49e12`.

**18 项探索关闭实验的核心结果、实际保存的 Hydra 配置和组件证据现已可接收。** 上次“配置及日志缺失”的核心包缺口已补齐；仍须保留下面的配置来源、历史重建和错误辅助字段边界。

## 独立核对结果

| 检查 | 结果 |
|---|---|
| 六 dev 系统 × seeds17/29/43 | 18项，全部completed、attempt_01、20queries，共360queries |
| 上次已交144个原始文件 | 全部与上次快照逐字节相同，包括metadata、trajectory、summary、图和console |
| metadata源码指纹 | 18×74=1,332项，全部匹配原始冻结文件的CRLF表示 |
| 扩展科学源码/配置/数据/依赖文件 | 108项，LF规范化后全部仍与原始冻结版一致 |
| 补充manifest | 18份、144项，全部hash与bytes一致；126项需按Windows CRLF表示核验，18个空日志直接一致 |
| 实际保存的Hydra配置对 | 18对，除experiment.output_dir外，唯一差异均为enable_exploration=true→false |
| 开关组合 | 18项均为planning/memory/reflection/tool_routing=true、exploration=false |
| saved overrides 与 metadata命令 | 18/18完全相同 |
| 协议与材料参考 | 与各自已完成Full参照18/18一致 |
| M4 evaluated日志 | 每项19条，queries1..19；共342条，实际run_id均独立且与system/seed/attempt匹配 |
| 重建核心曲线 | 360个前缀的累计发现数、mSUN及零原点梯形AUDC与记录观测一致，18项终点匹配原始指标 |

文件相同支持这次为证据补交而非替换原实验；我们没有访问运行机器，不能将此扩展为证明机器上从未做过其他尝试。当前提交树没有新增attempt_02，也未改写旧metadata/trajectory。

Full参照仅选择每个system-seed的已完成正式attempt：Mg-Sn-Sr seeds17/29使用attempt_02，其他使用attempt_01。21Oct的M5 dry-runs保留作历史证据，未进入本次配对。原始指标仍为Full10.0000/88.1111，OFF9.6667/88.2222；Full−OFF为mSUN+0.3333、AUDC−0.1111。

## 必须保留的来源边界

1. **文件名resolved_config.yaml不代表完全解析。** 全部18项中，该文件与保存的hydra/config.yaml逐字节相同，各自保留17处插值。除了Hydra路径和环境变量，seed、query_budget、planner参数和device等可静态解析的引用也仍保留。这来自package_evidence.py在完整解析失败后整体退回resolve=False；manifest准确说明是saved composed config。我们已直接比较两臂原始saved Hydra配置，因此单开关比较成立；不要再称这些文件为完整运行时resolved dump。
2. **m2_metrics_history.json是明确标记的重建历史。** source为reconstructed_from_frozen_official_trajectory，不能称原checkpoint恢复。核心计数和原始AUDC均通过，但其中normalized AUDC字段有305/360处使用错误分母：package脚本为area/(B*mSUN)，官方为area/(queries_used²/2)。例如Au-K-Tb seed17 query3记录0.025，官方定义应为0.111111…。这不改变原始mSUN/AUDC或本次原始配对结果；汇总时排除这个错误辅助字段，或另存使用冻结官方函数的分析结果，不改写原件。
3. **OFF没有m5_decisions.jsonl有合理解释。** enable_exploration=false不会调用M5 hook，不应制造空日志充数。M4实际evaluated-outcome日志已补齐；optional m4_proposal_events日志仍未收到。冻结capture代码仅在拒绝/错误事件时写文件，单凭其缺失不能断言缺少科学查询结果。
4. **运行平台及metadata版本标签保持原样。** M5的Windows AMD/torch2.14.1+cu126与正式Full的macOS ARM/torch2.9.1不同，虽然都指定CPU。不得把时间差当受控加速结论。metadata的aedf8ca仍是共享仓库文档提交标签，不能重写为原始freeze HEAD或MADE upstream；科学输入同一性由源码指纹和保存配置支持。

## 报告核对

新的M5_RESULTS.md已修正Full参照、正式attempt选择、dry-run排除、总体差值和重建/配置来源说明。仍有文字残留需要报告整合时更正：Ga-Pt-Tm seed17案例最后一句称其他所有步均为exploit，但原始20条sidecar实际为8条mixed、12条exploit；不能仅凭二元/三元成分推断模式。WORK_LOG等历史文档仍有旧参照差值、缺sidecar和pending实验的描述，应以最新结果报告为当前状态并保留日期背景。

结论为**核心实验与证据接收，附明确来源限制**。normalized AUDC辅助字段和上述报告文字不应进入最终结果；没有发现要求重跑18项科学实验的理由。

完整逐项审计见m5_supplement_audit.json，端点与配置检查见m5_supplement_units.csv；audit_m5_supplement.py只使用标准库与Ruby YAML读取器，不导入或调用科学运行时。
