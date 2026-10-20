# 34项结果收尾及最后两项的新尝试

用户于2026-10-20 21:27:24（Asia/Singapore）授权：验证恢复并继续运行；恢复不能通过时从头运行；时间限制不要过于保守；妥善收尾已有结果。

## 现有结果可以继续使用

固定科学源码63077ea3ea612197a5ad0e71fbe015d80149ca37、未修改的锁定依赖与官方指标，重新导入原19份归档及15份新成功归档。官方离线evaluator实际重新校验并评分34项，issues=[]。Random18/18、Chemeleon16/18；缺失基线只剩Au-K-Tb/17与Co-Dy-W/43。没有重跑这些34项，也没有改动原始归档、固定19项manifest、科学预算或结果数字。

表格与曲线： [逐项结果](closeout-34/per_run.csv)、[按体系汇总](closeout-34/per_system_summary.csv)、[按方法汇总](closeout-34/per_method_summary.csv)、[曲线](closeout-34/discovery_curves.svg)、[官方校验报告](closeout-34/validation.json)。这是34/36的部分开发集结果，不能当作完整配对比较或check/hidden结果。校验报告的20个missing_units另含M1的18项reference；M2只缺2项，不把M1工作当作本次独立基线启动条件。

## 实际恢复检查：原生恢复没有通过

对Co-Dy-W/43的真实归档先核对SHA256/CRC、原科学输入指纹、1024个候选及query_count=1。随后用原Hydra配置实例化原agent，调用原load_state，并用明确标注的测试sentinel观察是否会请求新的候选生成，不加载生成模型、不调用oracle、不产生科学成绩。

实测发现：JSON把全局缓存的None键序列化为字符串"null"；原load_state没有转换回来，下一次generate查找None键时无法命中，实际触发了测试sentinel。同时RandomSelector的get_state返回空字典，没有保存随机状态。报告见[native-recovery-probe.json](native-recovery-probe.json)。不能把有1024候选文件等同于恢复正确性已通过。

本轮按用户授权选择**两个单元各用新attempt完整运行**，不向正式路径注入未验证的修复，不修改官方runner或选择逻辑。原候选池、检查点与timeout记录保留。Au-K-Tb/17本来就没有可恢复的生成检查点。

## 新时间预算及执行位置

- 每项job总上限360分钟；计算步骤外层也设360分钟，内部计算期限是21600减去实际安装/接入耗时再减330秒，不能突破平台六小时。
- 330秒包括TERM/KILL预留60秒、打包最多60秒、上传最多180秒、runner清理30秒。从实际首个job计时步骤计算，额外的runner起步开销由清理余量覆盖。安装越久，计算窗口越短；时间不足时拒绝开算。
- 相比旧20分钟保存+1分钟退出的1260秒预留，计算窗口增加930秒，即15分30秒。实测历史成功打包上传是数十秒，但仍不能保证新实验一定完成或上传永不失败。
- 每项独立CPU runner，B=20、候选1024、batch256、seed与采样设置保持原值。fail-fast=false，每单元concurrency cancel-in-progress=false；retry_of明确引用3938658932401的timeout receipt，原34项由实时复用计划排除。
- 可执行入口：m2/tool-routing-evaluation分支`.github/workflows/m2-chemeleon-final-two.yml`；本目录交付副本为`M2/workflows/m2-chemeleon-final-two.yml`。请求为`M2/requests/chemeleon-final-two.json`。
- 科学checkout固定63077ea；新M2预算控制器从工作流自身commit独立checkout，其commit和SHA256写入runtime。官方M1路径不改动。
- 云端prepare先重做7项预算测试、真实保存检查点恢复探测及34项官方离线评分，成功后才启动正式两项。恢复探测成功执行所确认的是原生恢复不安全，不能误写为恢复通过。
- 原始科学产物先独立上传、再由preserve任务写回main/M2/verification/direct-<run>-1；即使计算失败也执行保存。原始证据持久化之后，独立任务重新导入最新成功结果，生成更新的完整性报告、CSV和曲线，并写入M2/LATEST_BASELINE_RUN.json。指标不满足B=20时不计为成功。

本地已执行：Python3.12.14的锁定安装、7项预算测试、Ruff、actionlint1.7.7、实际原生恢复探测、34项官方离线评分。云端仍固定Python3.12.15和uv0.9.18；对应云端当前版本检查与正式启动另记录，不拿本地或旧云端通过冒充新云端通过。
