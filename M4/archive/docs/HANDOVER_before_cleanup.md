# Historical documentation snapshot

Preserved before the 26 October final documentation cleanup. Statements about pending work describe earlier stages. See [the current M4 index](../../README.md) for final status and reproduction.

# M4 handover

## Current status, 26 October 2026

The frozen full agent uses M3 planning and M4 bounded observed-feedback memory. The formal Memory OFF development ablation is complete:18pairs,36validated runs. Generator/filter capture remains enabled in both arms. Final results, curves, three traced cases and cost limits are in [the formal evidence folder](../../evidence/frozen-memory-ablation-20261026). [Report materials](../../report/README.md) identify the final deck and notes. Earlier dated records below describe previous development stages and are not the current completion status.


## Current scope

M4 provides independent evidence storage, deterministic bounded retrieval and an adapter to M1's four-method MemoryManager interface. M1 adopted the M4 configuration on 20 October (`9acd3c9`) and integrated M3 (`2fcc214`). M4-owned sources and optional capture instructions stay under M4/.

The adapter returns recent observations with contrasting outcomes. The standalone core additionally supports composition-targeted retrieval, but the current M1 get_memory() contract has no target-composition argument. The report must distinguish these behaviors. The frozen full agent selects M3 and consumes m1_memory. The standalone diversity baseline does not consume that field.

## Validation completed

The earlier temporary wiring passed 34 combined M1/M4 tests and a synthetic 2-query episode. A real Mg-Sn-Sr CPU ORB episode completed 20 campaign queries in 157.193 seconds. Its complete export includes the last observation. This is workflow evidence, not evidence of a Memory performance gain. Current schema changes have focused regression tests and reuse saved trajectories without new oracle calls. See REAL_TEST_STATUS.md and VALIDATION.md.

## Required handoffs

| Recipient | Deliverable | Due in October 2026 |
|---|---|---|
| M1 | Design/interface agreement and tested implementation | Design 19-20; code 24 |
| M5 | Evidence format confirmation and logs from first real run | Format 21-23; first-run logs as available |
| M6 | Method text and draft slides | 24 |
| M2 | Memory ablation results and 2-3 discovery cases | 27 |
| M6 | Results interpretation and final slides | 27 |

M1 freezes the integrated agent on 25 October and supplies the agreed reference by noon on 26 October. M6 owns the split, seeds, budgets and repeat protocol. Compare Memory OFF to that reference under the same configuration. The brief prefers three repeats; state any compute limitation if only one is feasible.

## Integration and evidence contract

The adapter implements update_state(state), get_memory(), get_state() and load_state(state). Create a fresh manager per episode and use only public post-query observations. get_memory returns a JSON-serializable list, bounded by record count and serialized character count. M1/M3 own actual consumption and token accounting.

The standalone core supports explicit rejected/error events. The observation hook and trajectory exporter capture evaluations. The adopted capture subclass additionally records generator/filter exclusions and exceptions separately. Instability is an observed outcome, not a runtime error. Use EVIDENCE_SCHEMA.md as the field contract and M5_LOG_FORMAT.md for the remaining policy-context requirements.

M5 confirmed schema v1 in M5/M4_LOG_CONFIRMATION.md. M6 receipt of M4 method materials remains to be confirmed. The report method and two-slide draft are in report/. The final frozen development ablation and three balanced cases are complete. Its small positive aggregate difference does not establish a uniform or statistically significant benefit.

## Work log

17 October: inspected MADE and developed independent storage, bounded retrieval, ON/OFF behavior, checkpointing and mock tests.

19 October: adapted to M1, validated temporary wiring, completed synthetic and real-material workflows, preserved official outputs and exported complete evidence. Delivered M4 to main, with M1 wiring deferred. Reviewed the brief and team requirements. Corrected the export schema, distinguished observed instability from uncaptured runtime failures, and prepared method text and draft slides. Effect evaluation awaits actual Planner consumption of memory.

20 October: verified real M1/M3/M4 synthetic decision boundaries and added optional, checkpointable generator/filter audit capture. See integration/EVENT_CAPTURE.md and joint_test_results.txt. Main adoption of the optional capture target and the frozen full-agent ablation remain pending.

## 21 October development pilot

A real Mg-Sn-Sr/seed17 pair completed under the adopted M1/M3/M4 profile: ON mSUN@20=7, AUDC=68.5; OFF mSUN@20=8, AUDC=76.0. Both passed individual offline validation and paired configuration/reference checks. This is a development-only negative result, not the frozen full-agent ablation. See [DEV_PILOT.md](../../DEV_PILOT.md) and [evidence/dev-pilot-20261021/README.md](../../evidence/dev-pilot-20261021/README.md).
