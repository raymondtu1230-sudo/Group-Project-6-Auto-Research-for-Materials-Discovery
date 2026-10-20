# 最后两项重试与34项结果收尾

2026-10-20，用户21:27:24（Asia/Singapore）授权后执行。此文件记录本次启动快照，结束后的最新评分报告由工作流自动写入`M2/LATEST_BASELINE_RUN.json`，不把运行中任务记为成功。

## 已有34项均可继续使用

本轮按官方离线evaluator重新校验并评分：34项、issues=[]；Random18/18，Chemeleon16/18。全部B=20，原结果及数字未改动。原19项的固定归档清单仍保持原字节，新增成功归档通过execution_ledger的verified_completed receipt复用。

正式保存的[34项逐项表格、按体系/方法汇总及曲线](verification/final-two-preparation-20261020/closeout-34/)可用。现有两项缺口不影响其余34项的有效性；完整36项配对比较尚未完成，M1 reference与M6 check/hidden仍是各自范围。

## 恢复检查结论与本次动作

Co-Dy-W/43的1024个候选及query=1检查点完整保留。实际调用原agent.load_state后，原缓存键从None变为字符串"null"，下一次生成会缓存未命中并请求重新采样；随机选择器也没有保存随机状态。用真实保留数据、明确标注的测试sentinel在本地和本次云端都复现，未加载生成模型或调用oracle，未产生新科学成绩。

因此恢复不获准进入正式路径。按用户授权，仅Au-K-Tb/17和Co-Dy-W/43各用一个新的attempt从头运行。测试sentinel没有进入正式科学job，官方runner、oracle、evaluator、B=20、初始候选1024、batch256和seed都不改变。旧timeout、候选池和检查点不覆盖。

## 实际执行版本与证据

- 科学源码固定：`63077ea3ea612197a5ad0e71fbe015d80149ca37`，原uv.lock；云端Python3.12.15、uv0.9.18。
- 新控制器及可执行工作流提交：`e22cfb145466c056cee5ce8f4de8b75a6d15d1df`，分支`m2/tool-routing-evaluation`，路径`.github/workflows/m2-chemeleon-final-two.yml`。
- 主分支M2准备交付：`c2457fc95e80f28f4ef7a05d269446a9a0b58548`。工作流副本在`M2/workflows/m2-chemeleon-final-two.yml`，实际请求在`M2/requests/chemeleon-final-two.json`。
- 云端正式运行：[39432570527](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39432570527)。本次prepare job118661108169已成功：7项预算测试通过、真实检查点原生恢复不安全的探测执行完成、34项官方离线评分通过且零问题。
- 当前版本完整云端prepare日志及实际启动metadata见[final-two-start-39432570527](verification/final-two-start-39432570527/)。本地测试、Ruff及actionlint1.7.7通过；没有沿用旧云端通过替代本次检查。
- 新attempt：`3943257052701`，两项均显式引用旧timeout attempt`3938658932401`。main/M2/execution_ledger各保留原claim/receipt并新增claim，没有重排其余34项。

实际启动观察：两项均已完成独立claim、锁定环境安装、真实API及实际模型检查、动态预算记录，并进入正式计算。Au-K-Tb/17使用runner 1000000125，Co-Dy-W/43使用runner 1000000126；详见上述observed-startup.json。运行中不计为完成。

## 六小时内尽量多计算，并保留保存窗口

总job仍为360分钟，计算步骤外层改为360分钟。内部计算期限为`21600 - 实际已耗安装/接入秒数 - 330`秒。330秒含退出60秒、打包上限60秒、上传上限180秒、清理30秒；比原预算增加15分30秒计算窗口。时间不足则拒绝开算，不能通过YAML突破GitHub六小时硬上限，也不保证所有体系按时完成。

两项均为独立GitHub标准CPU runner，max-parallel=2、fail-fast=false、cancel-in-progress=false。每个job从本次实际启动重新计时，约21:43开始，六小时上限约为2026-10-21凌晨03:43；内部保护约03:38停止尚未完成的计算，实际边界按各自计时文件为准。

## 结束后的自动收尾

每项无论成功、失败或超时，均执行打包与上传，90天Actions保留副本。独立preserve任务将原始结果和receipt持久写入`main/M2/verification/direct-39432570527-1/`。原始证据保存完成后，独立任务再从最新main重导入成功结果，生成最新官方评分表、曲线和缺失清单，写入该目录的`final-report/`及`M2/LATEST_BASELINE_RUN.json`。

只有完整20次查询和官方离线校验通过才会登记verified_completed。失败保留新attempt，不覆盖旧记录、不把部分结果算完成。两项完成后不会启动check/hidden、GPU、付费任务或额外实验；本次没有代发群消息或改动其他成员路径。
