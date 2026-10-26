# M2 当前交接入口 — M5 端点已核对，原始包待补

2026-10-26。[本轮 M5 接收与更正](../aggregation/20261026_m5_intake/README.md)、[M6 使用说明](../aggregation/20261026_m5_intake/M6_HANDOFF.md)、[M5 补件清单](../aggregation/20261026_m5_intake/M5_FOLLOWUP.md)。

此前144项正式验收结果保持不变（M2基线与路由、M3完整54项组件研究、M4memory_off、Full参考）。新增18项exploration_off均记录完成，真实终点与来源核验通过，但原版M2评估器因缺实际resolved_config.yaml而拒收18/18；Hydra配置和组件证据也未随包提交。162行对比表明确区分144项accepted和18项package pending，不声称162项均已通过。

正确冻结Full为10.0000mSUN/88.1111AUDC，OFF为9.6667/88.2222，ON−OFF为+.3333/−.1111。已更新临时配对、重建曲线、成本和两案例更正。ON决策日志实际已存在，无需手工推断模式或重跑来补这项日志。

当前M2能做的离线接收/分析已完成；M5正式验收等待其从已有运行输出补真实配置和组件文件，不生成假配置/日志。M6剩余check/hidden和报告/原生PPT组装仍待完成；额外Fullplanning/self-correction由M1/M6决定，非M3欠交。

所有修改仅M2，旧入口已备份，原始数据和前版144项报告保留；未代发消息、未启动新实验或模型/oracle调用。
