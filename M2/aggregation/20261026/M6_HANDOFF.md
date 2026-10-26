# Superseded by the complete M3 handoff

26 October 2026: all18 m3_full original runs have now been received and validated. [Current144-run report](../20261026_m3_complete/README.md). The complete54-run M3 component assignment is accepted. The earlier attribution of extra Full-agent planning_off/self_correction_off runs to M3 is withdrawn; M1/M6 decide that additional scope. Below is the preserved earlier intake record, not the current outstanding-work list.

---

# Shared development results for M6 — 26 October 2026

M2 has received and independently inspected M4's 18 Memory OFF results and M3's 36 component-study results. The shared table preserves their actual method names and comparison scopes. These results cover the six development systems, seeds 17/29/43, B=20 and one episode per system/seed. They are descriptive development results.

## Frozen Full reference, baselines and single-switch ablations

| Method | Units | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | ---: | ---: | ---: |
| Random | 18 | 4.0556 ± 0.6310 | 40.5833 ± 9.4586 |
| Chemeleon | 18 | 6.9444 ± 1.1097 | 71.3056 ± 9.5038 |
| Frozen M1 Full | 18 | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Tool routing OFF | 18 | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |
| Memory OFF | 18 | 9.1111 ± 1.3472 | 86.9444 ± 9.0252 |

Each seed first averages the six systems equally. The table reports the mean and sample standard deviation of the three seed means, rather than the SD of 18 pooled episodes.

Full minus routing OFF is +2.2778 mSUN and +17.9722 AUDC. Full minus memory OFF is +0.8889 mSUN and +1.1667 AUDC. The memory effect is mixed: Full wins/ties/loses 8/3/7 mSUN pairs and wins/loses 9/9 AUDC pairs. Do not infer statistical significance, uniform benefit or held-out generalization.

## M3 component study — exploration and routing OFF throughout

| Method | Evidence received | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD |
| --- | --- | ---: | ---: |
| `m3_full` | Historical 18-row CSV; full raw comparator package missing | 6.5000 ± 1.3017 | 62.7500 ± 9.0289 |
| `m3_planning_off` | 18 complete frozen-source result folders | 5.1111 ± 0.3469 | 49.2222 ± 4.5141 |
| `m3_self_correction_off` | 18 complete frozen-source result folders | 5.8333 ± 0.8819 | 58.3056 ± 7.7823 |

The appropriate comparator for these two arms is `m3_full`, as M3 requested. Their exploration and tool-routing flags are both OFF. Relative to all-enabled `m1_full`, each arm changes three switches; those differences cannot identify an isolated planning or self-correction effect. Keep this table separate from the Full single-switch table.

The historical CSV differences are +1.3889 mSUN for planning and +0.6667 for self-correction. Treat these as reported component comparisons pending the complete 18-unit `m3_full` original package and a compatibility check. Do not present them as independently validated Full-agent ablation effects. No `m3_full` AF/EF or full discovery curve has been fabricated from endpoint values.

## Analysis and provenance

The accompanying report runs the unchanged `M2/evaluate.py` validator and reporting functions on real result records. Its lightweight loader executes the unchanged official `DiscoveryCurveMetrics` class with real NumPy; unrelated model dependencies are not loaded. Source hashes and loading mode are recorded. No agent, model, oracle or Materials Project call is made during this aggregation.

AF/EF against Random and Chemeleon are recomputed from paired histories using the official rules, rather than copying the unpaired zero-valued AF/EF fields in M3's summaries. The actual frozen EF default cap is **100**, despite the older metric docstring and M4 analysis prose saying 10. Keep baseline comparisons distinct from directional OFF-versus-Full comparisons.

History provenance remains explicit: M4 OFF histories were checkpoint captured; M1 and M3 supplied reconstructed histories; M2 routing OFF curves come from the separately validated offline reevaluation of original recorded structures and energies. The latter passed 720 original baseline-prefix and 72 endpoint checks in the previous stage. Original result files, failed collection audits and missing raw Hydra attachments remain preserved and are not relabelled as complete original captures.

Costs retain the recorded machine, elapsed time, known fees and missing counters. Known model fees of USD 0 do not include hardware, electricity or all failed/initialization work. Different machines do not establish a controlled speed comparison.

M4's 72-test result is reported by M4. M2 independently ran the 15 standalone M4 tests successfully; the larger selection stopped during collection because Hydra and pymatgen are unavailable in this local evaluation environment. This limitation is separate from the raw-result validation.

## Remaining assembly inputs

- M3: all 18 original `m3_full` result directories, including trajectories, resolved configuration, histories, metadata and component logs, to validate the requested component pairing.
- M1/M3: resolve the scope of the formal frozen `planning_off` and `self_correction_off` rows. Those all-other-components-ON methods are not the two received `m3_*` profiles. If required for the shared protocol table, they remain unfilled and must use actual new runs; renaming existing results is insufficient.
- M5: the complete frozen `exploration_off` package has not been found in this snapshot.
- M6: the remaining Full/Chemeleon check results and any course hidden outputs, plus final deck assembly. Existing Random check results are historical and remain separate from these dev ablations.

M2 prepared this handoff for the user to share. It does not assert that a message was sent or that M6 has confirmed receipt. All changes in this update are under `M2/`; other members' files remain intact.
