> **2026-10-20 22:14 最新：用户已授权睡眠期间继续本次两项监控和阶段收尾。** 已启用有限次数的每小时复核；即时归档仍由GitHub工作流完成。所有收尾新增/修改严格限定main/M2，不改其他成员、共享记录或根目录工作流。见 [本次自动收尾要求](../OVERNIGHT_FINAL_CLOSEOUT.md) 与 [两项启动记录](../FINAL_TWO_RUN_STATUS.md)。当前已核验34/36；最终状态须等两项终止后按真实产物更新，不把定时任务启用算作科学完成。以下保留历史快照。

> 现有19项PPT、讲稿和数据保留为历史快照；本次最终数字和自己的可编辑草稿将在两项结束后的阶段收尾中同步，不把旧PPT当作当前34项或36项展示。

# M2 speaker notes

## Tool routing, about40 seconds

Our router chooses between Random and Chemeleon using feedback from completed queries. It tries each tool first, then combines observed reward with an upper-confidence bonus. Stable new observations earn one, while stable-only observations earn a quarter. This reward is a proxy, distinct from mSUN. For the final two queries, the router uses the smoothed reward alone. Routing makes no oracle call. The final routing-off comparison changes one switch in M1's frozen full system. We have not measured the router's scientific benefit yet.

## Development coverage and example curves, about40 seconds

Random is complete across all six development systems and three seeds. Chemeleon has one verified unit, so the combined baseline coverage is19 of36. These curves retain the matched Mg-Sn-Sr, seed17 example, with20 queries. Random reaches mSUN7 and AUDC55.5. Chemeleon reaches16 and161. The example does not establish an overall ranking. Across the full Random sweep, mSUN is4.06 with sample SD0.63 and AUDC is40.58 with sample SD9.46. We will complete the comparison after the remaining Chemeleon results are validated.

## Protocol and cost backups

The development protocol fixes six systems, seeds17/29/43 and20 oracle queries per unit. Random's mean driver time is16.0 minutes across the full dev sweep. Chemeleon's262.8 minutes describe only the accepted Mg-Sn-Sr/17 unit. Fees recorded for inference are zero. Hardware, electricity, failed attempts and unreported token fields are not fully priced. AF/EF are discovery-curve metrics, not wall-time speedups.

Means and sample SD are computed from equal-weight system means for each seed, followed by the three-seed summary. M6 owns check/hidden execution and final group assembly. M1 owns the frozen reference. Current main's M1/M5 unseeded initialization issue is recorded separately from M2's method. Suggested slide positions from the earlier outline need M6's confirmation.
