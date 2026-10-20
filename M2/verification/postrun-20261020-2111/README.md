# 运行后保存核验与两项超时状态

2026-10-20 21:16（Asia/Singapore）。核验输入为main提交`df593ef41737950b47e948fa052d7d0045d1a682`，正式科学源码仍为`63077ea3ea612197a5ad0e71fbe015d80149ca37`。

## 已妥善保存的结果

本次17项独立Chemeleon dev实验中15项`verified_completed`、2项`timeout`。成功与超时ZIP均已由独立保存job写回main/M2，17份terminal receipt已发布到execution_ledger。两个保存job均成功：

- [主批39386589324](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39386589324)：13项成功和2项科学超时，保存在[direct-39386589324-1](../direct-39386589324-1/)。两项早期登记失败保留原记录，其科学工作由补启动批完成，没有重复计数。
- [补启动39387331614](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39387331614)：Ga-Pt-Tm/43和Mg-Sn-Sr/29两项成功，保存在[direct-39387331614-1](../direct-39387331614-1/)。

本次从Git主分支重新取得原始字节，独立执行[verify_preserved.py](verify_preserved.py)：19份原归档与17份本次归档共36份ZIP的SHA256全部匹配，ZIP CRC全部通过。原`configs/verified_baselines.json`保持原字节及原19项清单，没有用旧分支清单覆盖。34份完整实验均有completed metadata、B=20、dev、完整轨迹以及1至20连续查询曲线，单位身份无重复：Random18/18，Chemeleon16/18，总34/36。

完整结果见[audit.json](audit.json)。这次是离线原始字节/完整性检查和断点内容核查，没有加载模型、调用API、生成新科学实验或重新运行整套官方指标。15份新结果原有自动离线`verified_completed`校验记录保留。审计读取器两次最初的字段类型假设错误也保留在audit-first-pass.log与audit-second-pass.log；只修正读取器，没有改动实验原始数字、metadata或ZIP。

## 是否需要重新做两项

| 单元 | 超时记录 | 实际归档内容 | 当前能确定的结论 |
| --- | --- | --- | --- |
| Au-K-Tb / seed17 | 最后第4批230/256，0/20查询 | 日志、配置、输入指纹和退出信息；没有checkpoint.json或CIF候选池 | 无法用当前归档恢复初始生成；按现有证据需要重新采样，原失败attempt保留 |
| Co-Dy-W / seed43 | 候选生成完成，1/20查询 | 完整1024候选缓存、query_count=1、1条轨迹与指标历史、环境和agent状态、原配置 | 不应直接认定必须重采样；有正式查询检查点可供恢复验证，但尚未执行或通过恢复正确性验证 |

Co-Dy-W保存的是**候选生成完成后的官方查询检查点**，与旧运行39297647516未通过的初始生成batch恢复是不同情况。缓存中1024个结构的序列化payload实际存在，并非只保留数量标记。该事实不等于恢复已验证；版本、恢复接口、随机状态、查询连续性和官方指标一致性仍应在任何正式续跑前核实。未承诺直接接着完成剩余19次查询。

两项receipt均保持timeout、exit_code=124，不计入完成。未自动重试、未接入generation_cache、未修改官方科学逻辑，未运行check/hidden或付费/GPU任务。已完成34项无需因两项超时而重跑。

复验命令：在仓库中执行`python3 M2/verification/postrun-20261020-2111/verify_preserved.py`。只读取归档，重写本目录audit.json；不修改原始结果。
