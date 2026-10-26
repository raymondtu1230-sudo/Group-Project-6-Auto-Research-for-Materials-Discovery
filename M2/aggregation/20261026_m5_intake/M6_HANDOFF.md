# M6: corrected exploration comparison and acceptance status

Use this supplement with the [accepted 144-run report](../20261026_m3_complete/README.md). M3's assigned component study remains complete. M5's new 18 endpoints are checked, but their original configuration/evidence package is pending; mark that qualification in any draft table or figure. Do not state that all 162 directories pass the M2 evaluator.

## Shared statistical convention

Each seed equally averages six dev systems, followed by mean and sample SD across seeds 17/29/43. All records use B=20 and one episode.

| Arm | mSUN@20 | AUDC | Status |
| --- | ---: | ---: | --- |
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 | Accepted |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 | Endpoint-verified; package pending |
| Full minus OFF | +0.3333 ± 1.8559 | −0.1111 ± 18.8947 | Provisional matched endpoint effect |

Both aggregate effects are close to zero in this dev sample. Full mSUN is better/equal/worse in 8/1/9 pairs; AUDC is better/worse in 9/9. Do not imply a uniform advantage or statistical significance.

Per-system Full-minus-OFF mSUN remains +5.6667 for Co–Mg–Na, +2.6667 for Hf–Ni–Zr, +1.0000 for Au–K–Tb, −1.0000 for Mg–Sn–Sr, −1.0000 for Co–Dy–W and −5.3333 for Ga–Pt–Tm. Mg–Sn–Sr Full is **11.0**, not 10.0. Its AUDC is **102.8333**, not 96.0. The other five system rows agree with M5's report to its displayed precision.

The rounded pooled mSUN population SD decreases from OFF 4.8 to Full 2.7, using all 18 outcomes. This is a different statistic from the seed-level SD in the shared table. The corresponding Full pooled AUDC SD is 28.8177, not the report's 28.5. No variance significance test is implied.

## Two cases: retain only the observed facts

1. **Delayed ternary sampling, OFF Mg–Sn–Sr seed29.** Queries 1–16 are Sn–Sr binaries with six stable hits. The first Sn9Sr1 stable observation is query 2, not query1. Queries 17–20 are ternaries; queries 19/20 are stable Mg2Sn5Sr2 and Mg8Sn7Sr3. Final mSUN is 8. This shows late region coverage, without proving what would have happened if the ternaries were queried earlier. The recorded structures are unique; the evidence does not establish duplicate-structure mode collapse.
2. **One unsuccessful mixed/UCB ternary query, Full Ga–Pt–Tm seed17.** Only query6 is ternary, Ga1Pt4Tm3 with e_hull≈0.4170 eV/atom. Its actual decision mode is `mixed`. The other five steps called ternary exploration in the report are binary `exploit` decisions from the planner. The Full `m5_decisions.jsonl` exists and contains all 20 decisions; no manual mode labels or scientific rerun are needed. Same-seed OFF/ON endpoints are **16/10 mSUN and 168/93 AUDC**; 15.7/10.3 are system means. One unsuccessful query does not account for the whole six-discovery difference.

Full per-query evidence and hashes are preserved in [failure_cases.json](audits/metrics/failure_cases.json). Stability follows the recorded protocol tolerance of 0.1 eV/atom; it does not mean exactly zero hull distance. The report's causal rescue/easy-system explanation should be framed as a hypothesis rather than observed attribution of every step.

## Acceptance and presentation wording

The recorded command and 74 source fingerprints per run support intended exploration-only removal. Without original resolved configurations, actual realized settings cannot receive canonical certification. Full and OFF also have different recorded machines and package versions; costs remain machine-labelled descriptive records.

Suggested draft statement: “Exploration's aggregate dev effect is small, with mixed system-level differences. Provisional endpoints give +0.33 mSUN and −0.11 AUDC for ON minus OFF. The OFF package awaits original configuration and component-evidence files.”

Use the dashed `[package pending]` M5 curve in the shared figure. Its source is a labelled reconstruction from real trajectory observations; no new model or oracle call occurs. Keep pending labels until the original package passes the unchanged evaluator. Additional Full planning/self-correction remains an M1/M6 scope decision, and M6's final check/hidden/report/PPT assembly is separate.
