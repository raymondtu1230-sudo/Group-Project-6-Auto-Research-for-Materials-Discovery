# Verified real Random development unit

This is one completed development unit, not a final leaderboard or an aggregate
baseline score. The unchanged M1 protocol uses six development systems and
three seeds for each of two baselines: 36 baseline units. Only one is represented
here. The full method and paired Chemeleon comparison are unavailable.

| Field | Actual value |
| --- | --- |
| System / seed | Mg-Sn-Sr / 17 |
| Method | Official Random baseline |
| Oracle / budget | ORB / 20 queries |
| mSUN@20 | 7 |
| Official AUDC | 55.5 |
| Driver wall time | 952.717 seconds |
| Recorded inference fees | USD 0; hardware/electricity are not measured |

Source: [GitHub run 39213257750](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39213257750),
Random job 117931485324, artifact 12169366866. `provenance.json` records the exact
revision and checksums. The original ZIP is unchanged; all 20 query positions,
resolved configuration, metadata, raw trajectory and official metrics were
validated by `M2/evaluate.py`. There were no validation findings.

`validation.json` includes 53 missing units for the three-method final comparison
(18 full method, 18 Chemeleon and 17 Random). Of those, 35 are baseline units.
The method summary deliberately leaves overall means and standard deviations
blank until each complete method sweep exists. AF/EF against Chemeleon remain
missing. Random's comparison against itself is a convention, not a performance
improvement. The two plotted curves have distinct official definitions even
though their values happen to match in this particular unit.

## Reproduce this offline review

From the repository root, extract `raw_artifact.zip` into
`M2/results/upstream-run-39213257750/`. Then, from `M1/MADE`, run:

```bash
uv run python ../../M2/evaluate.py \
  --results-root ../../M2/results/upstream-run-39213257750/results/protocol_v1 \
  --output ../../M2/results/reproduced-random-gate --split dev --allow-partial
```

Choose an empty report directory. `per_run.csv` uses repository-relative source
paths in this published copy; all numeric fields are unchanged. This offline
review does not call an oracle, require a key, or expose evaluator data to agents.
