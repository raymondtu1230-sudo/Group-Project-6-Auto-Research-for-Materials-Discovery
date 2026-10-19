# M2 bounded closeout — 20 October 2026, 02:57 Asia/Singapore

| Item | Actual state |
| --- | --- |
| Accepted dev baselines | 19/36, zero audit issues |
| Random | 18/18 complete and accepted |
| Chemeleon | 1/18 accepted, 17 unlaunched |
| Active scientific jobs | 0 |
| Pending/unverified Random jobs | 0 |
| Exact recovery fixture | Failed identity guard; no final comparison pass |
| Evidence-only publication | 39306348134 succeeded, 23 original ZIPs SHA256-verified |
| Current development CI | 39306348142 succeeded: 17 M1 + 62 M2, Ruff, reproducible install, original smoke |
| Main/M1 modifications this turn | None |
| PR #2 | Open, draft, unmerged; branch retained |
| Check/hidden / GPU / paid compute | Not launched |

All accepted trajectories retain B20 and official per-query evidence. Copies and fixtures are not extra scores. Source-run final report failure is preserved, and current offline evaluation accepts all 18 Random units plus the original Chemeleon unit. The 35 missing units in the report comprise 17 missing baselines and 18 M1-owned full-reference units.

## Resume requirements

1. Read main/M2/STATUS.md and use configs/verified_baselines.json (19 checksum-pinned archives). If using the older development checkout, bring in the correct main evidence/manifest before scheduling. Do not dispatch legacy sweep, rerun an accepted unit, rerun science because aggregation failed, or automatically rerun the failed recovery.
2. Diagnose the actual identity component that blocked replay with non-secret input/source/weight/runtime evidence. The saved exception/hash alone is insufficient to identify it. Preserve all guardrails and raw outputs. Recovery still needs the exact atom/CIF/RNG/cross-runner proof, full1024 production wrapper and stage-cost validation before the 17 formal Chemeleon units can be admitted. Alternatively, establish adequate persistent CPU runtime within existing authority.
3. Shared-main unseeded M1/M5 integration remains separately failed; development-source CI does not override it. Let M1/M5 resolve their component/config issue. M1 owns full integration, release freeze and full-method reference. Only then run routing-off under the same release.
4. User follow-up can establish the 4070 OS/access and agree M1/M6 GPU measurement protocol. The guide is preparation only, no remote access or scientific GPU execution. No paid resources or check/hidden dispatch without the reserved decisions.
5. Code/config/test handoff to M1 and method/draft slides to M6 by 24 October; final validated results/curves/costs to M6 by 27 October. The existing four-slide draft depicts the historical original pair, not all19 or a completed comparison. Draft notices have not been sent or acknowledged.
6. Per the user's sleep/stop rule, end this bounded run and pause hourly polling after final evidence verification. No science needs cancellation. This pause is due to failed recovery admission and remaining runtime/owner/user dependencies, not successful completion of all M2 work.

## Evidence

- Raw archives and audit: ../preserved-39306348134/
- source-ci-job-118244318256.log and preservation-job-118244318678.log
- observed-jobs.json, observed-artifacts.json, coverage-crosscheck.json
- RECOVERY_BLOCKER.md and recovery-job-118217264688.log
- ../../GPU_PILOT_GUIDE_4070.md

The local scratch disk was full and its shell network proxy was unavailable; no user environment/data was deleted. Hosted processing and repository publication succeeded. Existing original files remain recoverable from Git history; no material deletion occurred.
