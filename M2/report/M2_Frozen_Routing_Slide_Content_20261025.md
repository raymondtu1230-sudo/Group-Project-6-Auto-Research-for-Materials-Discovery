# M2 frozen routing results: four-slide source, 25 October 2026

Ready-to-use English copy for M6. This is slide content, not a rendered PowerPoint. The existing 21 October PPTX remains a historical baseline draft. Current speaking text: [M2_SPEAKER_NOTES_20261025.md](M2_SPEAKER_NOTES_20261025.md).

## Slide 1: Routing chooses a generator from observed feedback

- Choose between Random and Chemeleon.
- Probe each tool, then use observed reward with an upper-confidence bonus.
- Use the reward alone for the final two queries.
- Routing off changes one switch. Planning, memory, self-correction and exploration stay on.
- With routing off, the primary generator remains Random.

Speaker cue: explain the controlled switch, then move to the shared protocol.

## Slide 2: All eighteen frozen routing-off episodes completed

- Six development systems and seeds 17, 29 and 43.
- One episode per system and seed, twenty queries per episode.
- CPU ORB v3 conservative, identical scientific settings and frozen source.
- All eighteen completed. Actual model weight assets and CPU loads were verified.
- Reuse the thirty-six original baseline results after compatibility checks.
- All ablations use dev only.

Source note: tag m1-freeze-20261025, commit 02e0026bf450f71f4f7862228d295f5b02b49e12. The actual scientific entrypoint was M1/run_experiment.py.

## Slide 3: Full routing has higher mean discovery scores on dev

| Method | mSUN@20 | AUDC |
| --- | --- | --- |
| Frozen M1 Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| Routing off | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |

- Routing off minus Full: −2.2778 mSUN and −17.9722 AUDC.
- Each seed weights six systems equally. The table reports mean and sample SD over three seed means.
- This supports routing in the frozen development setting. Results vary across systems and seeds.

Source note: original official trajectories and summaries, endpoint_comparison/method_summary.csv and perunit.csv.

## Slide 4: Baselines, evidence and cost complete the comparison

| Method | Dev units | Mean mSUN@20 | Mean AUDC |
| --- | --- | --- | --- |
| Random | 18 | 4.0556 | 40.5833 |
| Chemeleon | 18 | 6.9444 | 71.3056 |
| M1 Full | 18 | 10.0000 | 88.1111 |
| Routing off | 18 | 7.7222 | 70.1389 |

- Separate record-only curve analysis matched 720 original baseline prefixes and all 72 final endpoints. It made no new model/oracle calls.
- Official AF/EF use discovery curves and the original zero/cap rules.
- Missing original hidden attachments are listed in the audit. No historical checkpoint was invented.
- Known model fees are USD 0. Hardware, electricity and unpriced failures are excluded; machines differ.

Source note: ../verification/preserved-40204426478/report/baseline_compatibility/, recorded_curve_analysis/ and endpoint_comparison/costs.csv. Keep the detailed audit/cost qualifications in the report and Q&A backup.

## Assembly status

The four-slide content and the matching English script are ready. The native PPTX has not been refreshed or visually checked in this session. M6 can insert this copy in the final group deck; M2's final result-slide handoff remains due 27 October. No message has been sent and no recipient acceptance is claimed.
