# Reproduce the complete M3 comparator intake

This release adds the 18 actual `m3_full` result directories to the earlier
126-run aggregation. The earlier release is preserved; this script writes new
working files and results under `M2/` and refuses populated output directories.
It reads existing real records only and makes no model, agent, generator,
Materials Project, or oracle calls.

The source-data snapshot is main commit
`dcd3481a44f5bd9e0f9d7e58778a7f59a5a81210`. From a checkout containing that
data and this script, run:

```bash
python M2/aggregation/20261026_m3_complete/aggregate_handoffs.py \
  --snapshot . \
  --prior-results M2/verification/preserved-40204426478 \
  --work M2/runtime/group-aggregation-m3-complete-reproduction \
  --output M2/aggregation/20261026_m3_complete/results-reproduction
```

The script reads the original baseline and routing ZIPs directly from the
published repository, checks the recorded SHA-256 values and ZIP CRCs, and
extracts them into its new M2 working directory. It also checks M4's raw ZIP
against its published checksum. The old cloud runner's private or temporary
filesystem is not required.

Python 3.13 was used, with the frozen-lock NumPy 2.3.5, PyYAML 6.0.3, and
Matplotlib 3.10.8. Matplotlib's runtime cache is redirected into the M2 working
directory.

## Unchanged evaluator and official formulas

The script imports and calls the original `M2/evaluate.py` `main()` CLI function
for all 144 accepted runs, then uses its unchanged `collect`, `load_run`,
`compare`, `summarize_methods`, and `write_csv` functions. The evaluator source
SHA-256 is asserted:

`2eacad27246a8669657c6551807cbfeb1274cf94b691840f2f196d55e3e93a89`.

For offline arithmetic, the lean loader compiles the complete, unchanged
`DiscoveryCurveMetrics` class AST from the official source, with real NumPy.
It does not import unrelated model dependencies, edit metric formulas, invent
input values, or simulate experimental outcomes. The original official metric
module SHA-256 is asserted:

`f24d68a2b0a854cf7d880a97079c47e1d8160da11f7f31fa8900274067c7e3a1`.

The module hash, class AST hash, evaluator hash, aggregation-script hash, NumPy
version, and explicit lean-loading mode are saved in
`results/evaluation_provenance.json`. This execution validates the supplied
records and arithmetic; it is not a fresh independent agent/oracle or
hull/novelty calculation.

## Per-unit provenance and matching

All original metadata and result files remain unchanged. In particular, the
new `m3_full` runs record revision
`ae7fe81991c56dd2d77685220b74ddbef11039c7`, while the earlier M3 OFF runs record
`02e0026bf450f71f4f7862228d295f5b02b49e12`. The script preserves these actual
revisions in every receipt and table row. It does not relabel old runs as having
executed at the later reference-evidence revision.

For every one of the 36 M3 Full/OFF pairs, the script asserts exact equality of
all 74 recorded input hashes. It also compares the complete resolved
configurations: the assigned `enable_planning` or `enable_reflection` switch
must change, and every other difference must be one of the four listed log or
output paths. Both exploration and tool routing remain disabled in all three
M3 methods. Pair-specific configuration differences and actual source
revisions are retained in `paired_m3_component_ablations.csv`.

The M3-only validation uses the same unchanged canonical evaluator functions
on 54 raw runs, checking the six systems × seeds 17/29/43 for each of the three
methods. The 18 new `m3_full` mSUN/AUDC endpoints are additionally checked
against the earlier reported historical CSV values. Those historical values
are now corroborated by actual raw data rather than substituted for it.

History provenance is explicit:

- Baseline histories are original retained captures, matched to the earlier
  independently accepted structure-and-energy reevaluation records.
- Routing OFF original histories remain incomplete. Only separate evaluation
  views use the earlier verified record-only reevaluations; the original
  incomplete history is retained in each view under
  `original_incomplete_metrics_history.json`. Original failed collection
  audits and actual result files are untouched.
- Full reference and all three M3 methods label their histories as
  reconstructed from original trajectories. They are not presented as original
  checkpoint histories. The 360 Full reference prefixes are also matched to
  the earlier accepted structure-and-energy reevaluation, with exact original
  trajectory hashes.
- Memory OFF retains M4's externally observed checkpoint histories.

`input_receipts.json` records all 144 original metadata, trajectory and
configuration hashes, history sources, scientific profiles and actual recorded
revisions. M1's successful second attempts are used where applicable; original
failed attempts remain preserved in the source package and are excluded from
scores.

## Metrics, study scopes, and costs

All eight methods have 18 accepted runs with the same protocol and matching
canonical material reference snapshots. The 288 baseline AF/EF comparisons
pair all 144 runs against both Random and Chemeleon, including the baselines'
self-comparisons. AF/EF are calculated per matched system/seed/B unit, followed
by averaging; they are not ratios of aggregate means. Official AF defaults to
the final baseline discovery count as its target. Official EF uses denominator
at least `1e-8` and cap **100**, including the official zero-baseline convention.

Each aggregate first averages the six systems equally within each seed, then
reports the mean and sample SD across the three seed means. The M3 effect table
uses **Full minus OFF** for mSUN/AUDC deltas and explicitly **OFF versus
m3_full** for directional AF/EF. It has 36 actual matched pairs. The separate
36-pair `m1_full` memory/routing table keeps its original **OFF minus Full**
delta convention; the column names make both directions explicit.

The shared plot draws real validated histories for all three M3 arms in its
own panel. It keeps this component study separate from the Full-system
one-switch ablations. M3's assigned component delivery is complete. Whether
the team additionally wants planning/reflection ablations with exploration
and routing enabled is an M1/M6 scope decision, not missing M3 comparator
data. The M5 exploration-OFF delivery remains pending in this source snapshot.

The canonical evaluator's `final_comparison_complete` field covers its three
required core methods only. `aggregation_validation.json` separately records
M3's completion and the remaining group scope; it does not assert that all
group work or held-out evaluation is complete.

Missing cost counters retain their original status. Unknown LLM, hardware,
electricity, and failure costs are not imputed as zero. Wall times across
different machines and concurrency settings remain descriptive rather than a
controlled speed comparison. Output checksums are saved with the reports.
