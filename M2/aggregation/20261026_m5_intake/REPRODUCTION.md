# Reproduce the conditional M5 intake

This release does not claim that all 162 result directories pass the canonical
evaluator. It reuses the accepted 144-run report unchanged and separately
reviews 18 newly delivered real `exploration_off` runs. Their official
endpoints can be checked, but every new attempt is missing its original
resolved configuration and other required packaging evidence.

From a checkout containing the source-data snapshot
`a27634d9edbf231d0c034273fa9f977f9d5e799e` and this script, run:

```bash
python M2/aggregation/20261026_m5_intake/intake_exploration.py \
  --snapshot . \
  --work M2/runtime/m5-intake-reproduction \
  --output M2/aggregation/20261026_m5_intake/results-reproduction
```

Python 3.13 with frozen-lock NumPy 2.3.5, PyYAML 6.0.3, and Matplotlib 3.10.8
was used. All new working files, output, and Matplotlib cache stay under M2.
The program refuses populated work/output directories and does not modify an
original attempt or prior accepted report.

## Strict evaluation and the accepted 144-run carryover

The unmodified `M2/evaluate.py` `main()` CLI function is first executed on the
18 original M5 attempts. It accepts **zero** of them: all 18 fail while opening
`resolved_config.yaml`. The original errors and CLI exit text are saved under
`strict_m2_evaluator_m5_only/` and `strict_m2_evaluator_stdout.log`.

These errors apply to the new M5 package; they do not invalidate the previously
accepted 144 runs. The old 144-run report's 21 manifest entries are checked
before its tables, accepted unit hashes, and aggregate curves are reused. This
incremental script does not rerun its agent, oracle, or complete plotting job.
`canonical_144_carryover.json` records the exact source manifest and validation
hashes.

The original evaluator's expected core-method missing-unit list in this
M5-only strict invocation is not a new failure of those already delivered
methods. The relevant strict finding is the 18 actual M5 configuration errors.

## Separate endpoint-only analysis

Each M5 unit is independently checked for completed status, dev split, one
episode, B=20, 20 trajectory entries, official query count, exact protocol,
unique system/seed, and canonical material reference agreement with the latest
completed frozen `m1_full` run. M1's two successful second attempts are selected
where applicable. The Full metadata and trajectory hashes must also match the
prior accepted report.

All 74 recorded source-file hashes per M5 run are checked against the frozen
source snapshot, allowing only deterministic LF/CRLF checkout line endings.
The recorded command must contain exactly the five intended feature switches:
planning, memory, reflection, and routing on; exploration off. This verifies
the recorded intention and source identity. It does **not** replace inspection
of the actual resolved configuration, which is missing.

The program compiles the complete, unchanged `curve_from_trajectory` function
AST from `M1/package_reference_evidence.py`, using its real JSON, math, and Path
dependencies. That official function reconstructs the discovery counts from
the original per-query `is_stable` and `is_newly_discovered` observations and
checks the final mSUN/AUDC against the original official endpoints. Source and
function AST hashes are recorded. No metric formula or experimental value is
invented, and no new hull, novelty, generator, model, or oracle calculation is
performed.

The reconstructed records are saved only in the separate
`derived_endpoint_analysis/` directory and explicitly labelled as derivative
analysis. They are not inserted into the original attempt as
`m2_metrics_history.json`, and they are not described as original checkpoint
captures. No `resolved_config.yaml`, Hydra configuration, or component log is
fabricated.

Official `DiscoveryCurveMetrics` arithmetic is loaded by the same transparent
unchanged-class AST loader used by the accepted report. The evaluator and
official metric-module hashes remain asserted. AF/EF versus Full and both
generator baselines are therefore provisional comparisons using the derived
M5 curves. Baseline curves are taken from the earlier accepted recorded
structure-and-energy analysis, matched to the accepted unit trajectory and
reference hashes and checked against its reported endpoints.

The 18 Full comparisons and 36 baseline comparisons are **provisional**, while
the prior 288 baseline comparisons remain accepted. EF uses the official
denominator minimum `1e-8` and cap 100; AF uses the final baseline discovery
count as its default target. The official zero-baseline conventions are
preserved. Each reported mean/SD first equally averages six systems per seed,
then computes the mean and sample SD across seeds 17/29/43. Full−OFF is the
explicit delta direction in the M5 pair table.

## Reading the outputs

- `acceptance_validation.json`: 144 prior accepted, zero newly strict accepted,
  18 endpoint-only verified, and the missing-package status.
- `nine_method_summary_with_acceptance.csv`: eight accepted methods plus the
  pending M5 endpoint row, each with an explicit acceptance class.
- `combined_162_endpoint_rows_with_acceptance.csv`: per-unit scores with the
  same distinction. 162 table rows do not mean 162 canonical passes.
- `m5_endpoint_only_per_run.csv`, `m5_provisional_full_pairs.csv`, and
  `m5_provisional_effect_summary.json`: the newly checked endpoints and
  conditional comparisons.
- `m5_endpoint_evidence_receipts.json`: every original file's size/hash, actual
  recorded revision, command flags, verified source count, and missing evidence.
- `discovery_curves_with_pending_m5.*`: accepted curves plus a dashed M5 curve
  explicitly marked `[package pending]`.

M5's recorded revision is retained as
`aedf8ca238d2ef56948c0eadf2c897aef67f5104`; it is not relabelled as an earlier
commit. Original cost values and unknown counters retain their recorded
statuses. Unknown LLM, machine, electricity, or failure costs are not imputed as
zero, and wall times across machines are not a controlled speed comparison.

## Evidence still needed for canonical acceptance

The definitive file inventory in every M5 receipt identifies the absent
`resolved_config.yaml`, original Hydra files, original retained per-query
history, and component logs. A console log stored one level above the attempt
does not supply these files. Recover and package the existing original output
and retained capture evidence if they are available. Do not synthesize a
resolved configuration from the command and present it as the run's actual
configuration; do not fabricate missing log or checkpoint bytes. Any separate
trajectory reconstruction must keep its explicit provenance, as this report
does. A corrected package should then be submitted to the canonical evaluator
as a new intake, preserving this strict rejection and all original attempts.
