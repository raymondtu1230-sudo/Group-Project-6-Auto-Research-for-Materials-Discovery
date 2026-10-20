> **2026-10-20 最新：独立Chemeleon启动准备已完成。** 固定源63077ea：云端17项M1测试、77项M2测试、真实API、模型加载、smoke和17并发短任务已验证，产物已保存main/M2。正式17项仍未启动。完整参数、证据与后续启动命令见 [CHEMELEON_PREFLIGHT_READY.md](CHEMELEON_PREFLIGHT_READY.md)。共享默认未设seed测试的单独失败保留；整个M2、routing-off及其他成员工作未宣称完成。以下原记录按其版本保留。

> 交付方式：本轮材料通过 PR #5 单独交付至 `main/M2/`；用户已于2026年10月20日授权合并。共享框架接入仍由M1负责，PR #2 保留草稿。下述验收数字及失败对应审计时版本；本次文件交付不包含对后续共享代码变更的复验。

# M2 工作范围与交付核对

依据：本次成功读取的 Project6_Task_Split(2)(4).pdf、Project6_Step_by_Step_Guide(4).pdf；四张13:30微信截图；M1/PLUGIN_INTERFACE.md 与 M1/INTEGRATION.md。日期：2026年10月20日。

## 我们负责什么

| M2 工作 | 截至本次的情况 | 接收对象 / 时间 |
| --- | --- | --- |
| 开发集 Random、Chemeleon 基线 | Random18/18；Chemeleon1/18，余17项不在本轮启动 | M2 保存并评分；结果给 M6 |
| 工具路由设计、代码、Hydra配置、安装映射 | 已有独立组件，沿用 M1 接口和五个开关；本轮不改算法或共享接入配置 | M1，24日前 |
| 组件测试、环境与真实访问证据 | 已有源版本对应的云端通过记录；本次也实测共享配置并保留其 M1/M5 失败 | M1，随组件交付 |
| mSUN@B、AUDC、配对AF/EF、发现曲线和成本记录 | 已对19项原始记录重新核验、重算。Random可报完整 dev 汇总；Chemeleon整体值留空 | M6，阶段材料已准备，最终版27日前 |
| 方法文字、自己的幻灯片草稿与讲稿 | 更新当前覆盖数；单对示例曲线保留明确标签，未当成全方法比较 | M6，24日前 |
| routing-off 消融 | 尚未运行；等待M1冻结版与相同条件下的reference | M2执行，结果给M6 |
| 收齐各成员结果、最终对照表与曲线 | 接收规范已准备；等待各成员提供原始结果，不替他们运行 | M6，27日前 |
| 工作日志与复现说明 | 已更新，失败、跳过、依赖和未完成范围均列明 | M2保留，供个人报告与交接 |

## 微信要求如何落实

| 要求 | 对应文件 / 处理 |
| --- | --- |
| 新建自己的文件夹存新增文件和代码 | main/M2/；不写入其他成员目录 |
| 先读五份M1接口文件 | 已读取；本次测试副本的输入指纹在 verification/20261020-handoff-audit/reviewed-input-hashes.json |
| 模块、配置、测试接入既有字段 | integration/、configs/m2_routing.yaml、install.py；具体映射见 HANDOFF_LAYOUT.md |
| 保留类型、预算、五开关、JSON状态，禁止插件读隐藏状态或直接调用oracle | integration/m2_tool_routing.py及对应契约测试；不改官方 runner/oracle/evaluator/environment/预算逻辑 |
| 自己配置环境/API并实际测试 | 已有真实API/生成器证据及源版本CI，本轮只做离线原始数据复核和接口测试 |
| 开/关、非法输出、状态恢复测试，pytest/Ruff/smoke | 见 ACCEPTANCE_CHECKLIST.md 与本次审计；共享M1/M5默认配置失败不冒充通过 |
| 完成后群里通知 | handoffs/ 与 report/GROUP_HANDOFF.md 已准备草稿；由用户发送，未发送也未获接收确认 |

## 不是 M2 需要代做的工作

- M1：共享系统合并、安装其他成员组件、冻结、完整reference、官方驱动的hidden支持。
- M3/M4/M5：各自组件、消融及示例/失败分析。M2只接收并核验结果。
- M6：check/hidden执行、泛化比较、全组最终报告和幻灯片装配。dev Random18/18不覆盖check Random12项；后者不得擅自变成M2的漏项。

本次本地官方合成smoke还在Chrome图片导出阶段失败，原始日志已保存；不算通过。旧源码云端smoke通过记录仅对应其源版本。

## 本轮验收边界

19份归档的SHA256及ZIP完整性通过。离线重新评分得到19项、issues=[]，与先前发布的全部数值表一致。共享main测试实测77通过、1失败、1跳过：失败为M5的seed=None初始化，跳过为此容器不暴露子进程/proc计数。M2自身代码源版本的云端通过与本次共享配置结果分别保存，不互相替代。

Ruff最初误扫不可变历史源码快照而失败；本轮仅在M2/ruff.toml排除verification历史证据目录，当前源码、integration与tests仍检查，随后通过。没有修改历史快照来消除报错。

本轮不启动任何科学实验，不代做其他成员任务，不合并PR2，不宣称整项M2完成。接收确认、M1/M5修复、冻结版reference和成员结果仍是依赖。
