# M4 handover

## Current scope

M4 provides independent evidence storage, deterministic bounded retrieval and an adapter to M1's four-method MemoryManager interface. The main-branch handoff keeps all M4 files under M4/ and leaves M1 unchanged. Deferred configuration and integration tests are in integration/.

The adapter returns recent observations with contrasting outcomes. The standalone core additionally supports composition-targeted retrieval, but the current M1 get_memory() contract has no target-composition argument. The report must distinguish these behaviors. Main does not automatically enable M4 and the default Planner does not consume m1_memory.

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

The standalone core supports explicit rejected/error events. Current framework hooks and the trajectory exporter capture completed evaluations only. Instability is an observed outcome, not a runtime error. Use EVIDENCE_SCHEMA.md as the field contract and M5_LOG_FORMAT.md for the remaining policy-context requirements.

M5 format confirmation and M6 receipt remain pending. The report method and two-slide draft are in report/. There is no completed ablation, no improvement claim and no selection of final discovery cases yet.

## Work log

17 October: inspected MADE and developed independent storage, bounded retrieval, ON/OFF behavior, checkpointing and mock tests.

19 October: adapted to M1, validated temporary wiring, completed synthetic and real-material workflows, preserved official outputs and exported complete evidence. Delivered M4 to main, with M1 wiring deferred. Reviewed the brief and team requirements. Corrected the export schema, distinguished observed instability from uncaptured runtime failures, and prepared method text and draft slides. Effect evaluation awaits actual Planner consumption of memory.
