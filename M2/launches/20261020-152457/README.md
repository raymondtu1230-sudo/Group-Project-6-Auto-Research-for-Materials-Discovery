# 剩余17项Chemeleon正式实验启动记录

授权：用户于2026-10-20 15:24:57（Asia/Singapore）明确要求并行启动GitHub云端。

最终启动核验：2026-10-20 15:38:22（Asia/Singapore），17个不同单元均在17个不同runner上执行正式B=20计算步骤，每项claim、锁定环境安装、真实API查询、实际模型加载与动态时间预算步骤均成功。无当前启动阻塞。完整原始步骤与runner metadata见[observed-startup.json](observed-startup.json)，main已发布的17份claim见[published-claims.json](published-claims.json)。此为启动成功，尚不能算实验成功或验收完成。

正式运行：https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39386589324

仅补启动两项：https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39387331614

请求提交：cfe27fb74394cdb76121d147272cc57f653270a4。实际代码固定63077ea3ea612197a5ad0e71fbe015d80149ca37，沿用已通过验证的启动凭证。

首个运行展开17项，其中15项通过安装、真实API和实际模型接入检查后进入计算。Ga-Pt-Tm/43与Mg-Sn-Sr/29在计算前的claim推送失败，原日志及步骤证据保存在startup-failures/。当时main没有这两项claim，API、模型检查及正式计算均跳过，因此只用新请求、新run/attempt补启动这两项；没有取消或重跑其他15项。补启动请求提交53a7f0a40ef8b89fc80801ac9447601395a0df68，实际请求见startup-retry-request.json。并发推送竞争是初步判断；helper未显示Git远端具体拒绝原因，不能视为已完整定位根因。

准备阶段的受检代码、锁定环境、真实API、模型加载、17项M1测试、77项M2测试、官方smoke及17并发短任务证据见[准备完成记录](../../CHEMELEON_PREFLIGHT_READY.md)与[原始云端证据](../../verification/preflight-39384607532-1/)。正式计算仍从头完整运行，不接入未验证的初始候选池续跑。

范围：仅dev Chemeleon缺失17项，每项B=20。原Random18项及Chemeleon Mg-Sn-Sr/17保留，不重跑。max-parallel=17，独立标准GitHub CPU runner；本机不加载17份模型。job360分钟、计算步骤340分钟，按已耗安装时间动态扣减，留出20分钟保存。

request.json是实际提交的请求；admission.json是提交前对最新main的离线重新核验。实际任务展开、claim及计算启动状态见后续保存的observed-startup.json与GitHub运行页面。已提交不等于已完成；开始时验收覆盖数仍为19/36。

各项独立失败不取消其他任务；重复启动由main/M2/execution_ledger的claim阻止。运行结束后always上传每项原始结果，独立preserve任务将成功、失败或超时证据写回main/M2/verification/direct-39386589324-1。新实验只有通过完整产物和官方指标核验后才能计为完成。

补启动的两项使用独立attempt 3938733161401，结束后保存到main/M2/verification/direct-39387331614-1；原运行的15项使用attempt 3938658932401。Actions产物保留90天，main/M2的归档独立持久保存。外层job360分钟，计算步骤340分钟，内部按安装耗时扣减并留20分钟保存与60秒退出；超时或失败保留原尝试，不保证断点续跑，也不保证所有体系在6小时内完成。

不运行check/hidden，不合并PR2，不修改M1/M3/M4/M5/M6的代码或记录。旧准备完成记录中“本轮未启动”的表述指前一准备轮；本文件记录本次新增授权后的正式启动。
