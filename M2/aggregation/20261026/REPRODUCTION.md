# Reproduce the M2 handoff aggregation

This program scores existing real experimental records. It starts no scientific
episodes and makes no agent, generator, Materials Project, or oracle calls. It
does not modify the evaluator, the original results, or another member's files.
Every working directory and output must be under `M2/`; existing populated
outputs are refused.

The data snapshot used for this release is main commit
`95f9c8e38923ac494b1117a9b212702afdc5980f`. Actual frozen experimental source
remains `02e0026bf450f71f4f7862228d295f5b02b49e12`; the later reference-evidence
patch must not be substituted into original run metadata.

From a checkout containing the same source data, with this aggregation script
available, run:

```bash
python M2/aggregation/20261026/aggregate_handoffs.py \
  --snapshot . \
  --prior-results M2/verification/preserved-40204426478 \
  --work M2/runtime/group-aggregation-20261026-reproduction \
  --output M2/aggregation/20261026/results-reproduction
```

The script reads all original baseline and routing artifact ZIPs directly from
the published repository package, verifies their recorded SHA-256 values and
ZIP CRCs, then extracts them under the requested working directory. It does not
require the earlier cloud runner's private or temporary filesystem. M4's ZIP is
also hash-checked against M4's published checksum file before extraction.

Python 3.13 was used for the validation. Direct numerical and plotting packages
are frozen-lock versions NumPy 2.3.5, PyYAML 6.0.3, and Matplotlib 3.10.8.
Matplotlib's runtime cache is directed into the M2 working directory.

## Exact evaluator and metric source

The script imports and calls the unchanged `M2/evaluate.py` `main()` CLI function,
then uses its unchanged `collect`, `compare`, `summarize_methods`, and `write_csv`
functions for the expanded report. The evaluator source hash is asserted:

`2eacad27246a8669657c6551807cbfeb1274cf94b691840f2f196d55e3e93a89`.

To avoid importing the unrelated model stack for offline arithmetic, the loader
compiles only the complete, unchanged `DiscoveryCurveMetrics` class AST from
the official `made/evaluation/metrics.py`, using real NumPy. It does not replace
metric formulas or generate input values. The official module hash is asserted:

`f24d68a2b0a854cf7d880a97079c47e1d8160da11f7f31fa8900274067c7e3a1`.

The full module hash, class AST hash, evaluator hash, analysis-script hash,
NumPy version, and explicit lean-loading mode are recorded in
`evaluation_provenance.json`. This is an offline evaluator execution, not a
fresh independent run of the agent, oracle, hull, or novelty calculations.

## Provenance of the per-query histories

- Random/Chemeleon: original retained histories, checked against the earlier
  independently validated structure-and-energy reevaluations.
- Tool routing OFF: all 18 original collection histories are incomplete. The
  evaluation views preserve those original records as
  `original_incomplete_metrics_history.json` and use separately labelled
  derivative histories from the earlier accepted official structure-and-energy
  reevaluations. This does not recover original checkpoint bytes or change the
  original failed collection audits.
- Full reference: the newly published histories explicitly say reconstructed
  from the original trajectory. All 360 discovery-count prefixes are additionally
  matched against the earlier accepted structure-and-energy reevaluations, with
  exact original trajectory SHA-256 checks.
- M3: the submitted histories are explicitly reconstructed from the trajectory.
  The canonical evaluator checks query coverage, mSUN endpoints and official
  AUDC arithmetic. This must not be described as original checkpoint capture or
  a new independent hull/novelty prefix reevaluation.
- Memory OFF: the submitted histories were retained by M4's external checkpoint
  observation. Their provenance is retained unchanged.

`input_receipts.json` maps every accepted evaluation view to its original
metadata, trajectory, configuration hashes, history source, scientific profile,
and appropriate causal comparator. No metadata in an original result is edited.
The M1 reference includes successful second attempts where applicable; original
failed attempts remain in the source package and are excluded from scores.

## Metric and comparison conventions

The official evaluator accepts 126 unique completed runs: seven methods, each
with six development systems and three seeds at B=20. All protocol settings and
canonical material reference snapshots must agree before comparison. The 252
baseline comparisons are 126 runs paired against each of Random and Chemeleon,
including each baseline's self-comparison.

For every method and metric, the six systems are equally averaged within each
seed, followed by a mean and sample standard deviation across the three seed
means. AF/EF are computed per matched system/seed/B unit and then aggregated;
they are not ratios of aggregate means. Official AF defaults to the final
baseline discovery count as its target; it is zero when a required target is
not reached. Official EF uses a baseline denominator of at least `1e-8` and caps
the result at **100**. This includes the official zero-baseline convention,
including zero-vs-zero EF equal to zero.

`m2_evaluator/validation.json`'s `final_comparison_complete` field covers the
three protocol-required core methods only. It does **not** certify that every
assigned group ablation or held-out task is complete. The separate
`aggregation_validation.json` records that limitation.

Memory OFF and routing OFF are matched to frozen `m1_full` as one-switch
ablations. M3's two OFF methods have exploration and routing disabled as well,
so their causal comparator is `m3_full`, not `m1_full`. Only an historical CSV
with 18 `m3_full` endpoints is available. That comparator is labelled reported,
not independently validated; its curve and paired AF/EF are not fabricated.
M3's OFF arms can nevertheless be compared descriptively with both generator
baselines, with this different scientific profile kept explicit.

Known costs and missing counters retain their original statuses. Unknown LLM,
hardware, electricity, and failure costs are not imputed as zero. Wall times on
different machines and concurrency settings are descriptive, not a controlled
hardware-speed benchmark.

The analysis checks and checksum manifest are preserved with the tables and
curves. The canonical shared curve plot separates the Full study from the M3
component study; no missing `m3_full` curve is drawn.
