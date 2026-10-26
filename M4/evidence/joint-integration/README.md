# Joint synthetic integration evidence, 20 October 2026

Historical development evidence. The completed formal 18-pair comparison is in [the final package](../frozen-memory-ablation-20261026/). Pending-work statements below describe this earlier stage.

Main source before M4 changes: `871fa8f`. M1/M3/M4 contract and new capture tests:
**69 passed**, no skips/deselections; three existing dependency warnings.
See `../validation-history/joint_test_results.txt` for the recorded output.

The unchanged M1 smoke script passed after allowing local Chrome to launch for
plot export. A first restricted attempt failed at plot export and is not counted
as a pass. Two additional episodes used the unchanged official runner with the
M3 planner, M4 memory and optional capture subclass, seed 17, Li-O, B=2 and
AnalyticOracle. Both Memory ON and OFF completed. Their JSON and phase plots are
retained in on/ and off/. These are synthetic data, not ORB results, baseline
comparisons or evidence of a Memory performance improvement.

`validation.json` additionally preserves a real-class synthetic decision-boundary
check: M3 recorded evaluation:1 as memory input when ON, and no memory IDs when
OFF. `synthetic_event_examples.jsonl` comes from deliberate fake-filter rejection
and fake-generator exception fixtures. These events did not occur in the two
runner episodes; those episodes produced no filter/generator event sidecar.
Never describe fixture errors as observed scientific failures.

Reproduce from M1/MADE with M4 installed:

```bash
uv run --no-sync python ../../M4/examples/joint_smoke.py on
uv run --no-sync python ../../M4/examples/joint_smoke.py off
```

The script refuses existing output directories. Preserve them and choose a new
output name for repeats. See integration/EVENT_CAPTURE.md for capture coverage,
fallback interpretation and adoption. Existing main configuration does not use
the optional capture subclass until M1 applies it. Final Memory-effect evaluation
still requires the frozen full agent and matched dev runs.
