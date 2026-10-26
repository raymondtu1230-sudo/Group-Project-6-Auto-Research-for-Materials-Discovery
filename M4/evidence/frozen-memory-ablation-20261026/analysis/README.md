# Offline analysis and reproduction

These artifacts use saved data only. The scientific runner, oracle, environment and evaluator remain unchanged.

- `per_query_curves.csv`: all 720 query points across 36 runs. mSUN and cumulative new-stable counts are distinct measures.
- `aggregate_curves.csv`, `discovery_curves.png` and `.svg`: equal-weight system averages within each seed, then mean across 3 seeds. Shading shows sample SD across the three seed means, not a confidence interval. AUDC uses MADE's `num_newly_discovered_stable` curve.
- `paired_AF_EF_OFF_vs_ON.csv`: official MADE AF/EF with proposal=Memory OFF and reference=frozen full ON, using `num_newly_discovered_stable`. This is an explicitly directional supplementary ablation comparison. It does not replace the required Random/Chemeleon comparisons in M2's group leaderboard. AF uses the final ON new-stable count as target. Failure to reach it produces 0 under the official convention. EF retains the official zero-baseline handling and cap 10.
- `per_run_cost.csv`, `cost_summary.json`: original launcher wall times and partial cost fields, not the external coordinator's elapsed times. Each arm has 360 campaign queries. Initialization/scorer oracle work is not fully instrumented. LLM tokens/cost remain `not_reported`, and known model price 0 does not imply zero total resource cost. ON and OFF ran on different named machines, so their wall times do not isolate memory overhead or establish speedup.
- `TRACED_CASES.md`, `traced_cases.csv`: three balanced case studies with 120 query rows. Missing exact ON review IDs remain explicit.

## Reproduce

Use the M1/MADE locked environment with the local M4 package installed, as described in the team setup. From the repository root, first extract [the preserved OFF archive](../memory_off_raw_results.zip) into the repository root without overwriting a different existing attempt. The archive retains paths starting `M1/MADE/results/protocol_v1/memory_off/`. The ON originals are committed under `M1/MADE/results/protocol_v1/m1_full/dev/` at evidence revision `ae7fe81`.

```bash
M1/MADE/.venv/bin/python M4/build_frozen_report.py \
  --results-root M1/MADE/results/protocol_v1 \
  --output /tmp/m4-analysis-reproduction
```

The reporting helper invokes M2 `load_run` and official MADE metric functions. It never queries the oracle or supplies evaluator data to the agent. ON histories retain M1's trajectory-reconstruction provenance. OFF histories come from checkpoint observation. See the parent report for the actual run revision and the evidence-only patch distinction.
