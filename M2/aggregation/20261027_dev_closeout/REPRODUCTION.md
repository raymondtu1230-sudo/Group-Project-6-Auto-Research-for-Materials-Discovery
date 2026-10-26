# Reproduce the development closeout evaluation

This release evaluates nine methods × six development systems × seeds
17/29/43: 162 real completed units at B=20. It preserves all earlier releases,
including M5's prior strict rejection and conditional endpoint analysis. This
release adds packaging evidence and corrects an auxiliary field only in
separate analysis views; it runs no new scientific episodes, models, agents,
Materials Project requests, generators, or oracles.

The source-data snapshot is main commit
`b36e2a50d9d3e31fc941d827addab94db2c5d3cc`. From a checkout containing those
data and this script, run:

```bash
python M2/aggregation/20261027_dev_closeout/aggregate_handoffs.py \
  --snapshot . \
  --prior-results M2/verification/preserved-40204426478 \
  --work M2/runtime/dev-closeout-reproduction \
  --output M2/aggregation/20261027_dev_closeout/results-reproduction
```

Python 3.13 was used with the frozen-lock versions NumPy 2.3.5, PyYAML 6.0.3,
and Matplotlib 3.10.8. The script refuses populated work/output directories.
All new work, derivative views, plots and runtime cache stay under M2. Original
member result files, metadata and previous reports are not edited.

## Unchanged canonical evaluation and official arithmetic

The unchanged `M2/evaluate.py` `main()` CLI function is run on all 162 selected
evaluation views. It also uses the same unchanged `load_run`, `collect`,
`compare`, `summarize_methods` and `write_csv` functions. The evaluator SHA-256
is asserted:

`2eacad27246a8669657c6551807cbfeb1274cf94b691840f2f196d55e3e93a89`.

The transparent lean loader compiles the complete, unchanged
`DiscoveryCurveMetrics` class AST from the actual official module with real
NumPy, avoiding imports of unrelated model dependencies. It does not replace
formulas, simulate outcomes or supply invented inputs. The official module
SHA-256 is asserted:

`f24d68a2b0a854cf7d880a97079c47e1d8160da11f7f31fa8900274067c7e3a1`.

The module and class AST hashes, evaluator and analysis-script hashes, NumPy
version, and explicit lean-loading mode are saved in
`results/evaluation_provenance.json`.

## Exact selection and original evidence

The Full reference is selected by the previous accepted metadata, trajectory,
and configuration hashes, not by choosing the largest attempt number. The
approved Mg–Sn–Sr seeds 17 and 29 use `attempt_02`; the other 16 units use
`attempt_01`. Every observed nonreference metadata record is listed in
`excluded_nonreference_full_attempts.json`. Descriptions of other historical
pilot attempts are not treated as evidence that their actual bytes were
published or inspected.

Original baseline and routing ZIPs are read from the existing published M2
package, checked against their recorded SHA-256 values and ZIP CRCs, and
extracted under the new M2 working directory. M4's ZIP is checked against its
published checksum. No temporary cloud-runner filesystem is required.

Each of the 18 newly packaged M5 units retains the exact metadata and
trajectory hashes from the prior endpoint-only intake. All nine methods'
aggregate means, sample SDs and baseline comparison statistics are checked
against the preceding nine-method table. This upgrade changes acceptance and
packaging, not the experimental outcomes.

For M3, every one of the 36 Full/OFF pairs has all 74 recorded scientific
input hashes identical. Complete resolved configurations may differ only in
the assigned planning/reflection flag and four recorded output/log paths. The
actual source revisions remain intact: the new `m3_full` runs record
`ae7fe81991c56dd2d77685220b74ddbef11039c7`, while their earlier OFF runs record
`02e0026bf450f71f4f7862228d295f5b02b49e12`.

M5's actual recorded revision remains
`aedf8ca238d2ef56948c0eadf2c897aef67f5104`. All 74 recorded source hashes per
unit are checked against the scientific source, allowing deterministic
LF/CRLF checkout conversion only. No historical run is relabelled as having
executed at a later commit.

## M5 manifest transport and configuration qualifications

M5's evidence manifest was created from Windows checkout bytes. Of its 144
members in this source snapshot, 18 empty run logs match published bytes
exactly; 126 text files are published with LF while their manifest records
CRLF. For every such file, restoring only LF to CRLF must reproduce both the
exact recorded size and SHA-256. No other difference is accepted. Actual
published hashes, recorded hashes, sizes, and verification modes are retained
in `m5_evidence_manifest_verification.csv` and its JSON summary. Published
source bytes are not changed. The first exact-byte preflight failure is kept
as analysis history; it is not a failed scientific run.

The delivered `resolved_config.yaml` is the run's saved composed configuration.
Some static/runtime interpolation strings remain in that artifact. Their paths
are listed per unit in `input_receipts.json`; the report does not claim that
every interpolation was expanded. The actual M2 validator's concrete budget,
seed and system checks pass, and the analysis asserts the required feature
switches. This is distinct from claiming that the supplied artifact is a fully
expanded Hydra runtime snapshot. The original configuration is preserved, and
no replacement configuration is fabricated.

## Auxiliary normalized-AUDC correction in separate views

The newly supplied M5 histories pass the canonical validator's core checks:
query counts, discovery counts, mSUN and raw AUDC. All 360 raw-prefix AUDC
values additionally match the unchanged official formula. However, the
auxiliary `discovery_curve_area_under_discovery_curve_normalized` field is
incorrect in **305 of 360** submitted prefixes. These values do not enter
the shared mSUN, raw AUDC, AF or EF results.

For each M5 unit the program first validates the as-submitted record with
`load_run`, then preserves its original bytes as
`as_submitted_metrics_history.json` in the separate M2 evaluation view. Only
the incorrect auxiliary normalized values are replaced in the analysis view,
using unchanged
`DiscoveryCurveMetrics.area_under_discovery_curve(normalize=True)` for the
actual prefix. This is raw area divided by `queries²/2`. A deep comparison
asserts that every other parsed history field is unchanged.

Both the byte-exact submitted history and corrected analysis history are also
retained under `results/m5_history_analysis_views/`. The 305 before/after
changes, original history hashes, query indices, function and unchanged-core
flags are recorded in `m5_normalized_AUDC_corrections.csv`. The separate
`m5_auxiliary_normalization_audit.json` explicitly distinguishes submitted core
acceptance from this auxiliary discrepancy. The original member attempts and
their manifests are never edited. Do not interpret the canonical evaluator's
empty issue list as a claim that every field in every submitted document was
already correct.

## Other history provenance

- Random/Chemeleon use original retained histories checked against the earlier
  accepted structure-and-energy reevaluations.
- Routing OFF original histories remain incomplete. Its 18 evaluation views
  preserve those original files and use separately labelled, previously
  accepted record-only reevaluations. They are not recovered checkpoint bytes.
- Full reference and all three M3 histories are labelled as reconstructed from
  original trajectories. Full's 360 discovery-count prefixes also match the
  earlier accepted structure-and-energy reevaluation with exact original
  trajectory hashes.
- Memory OFF uses M4's externally observed checkpoint histories.
- M5 histories are likewise trajectory reconstructions, with the auxiliary
  correction described above. Their 360 discovery-count prefixes match the
  earlier independent intake reconstruction.

No new hull/novelty or oracle calculation is implied by this offline evaluator
execution. `input_receipts.json` records every selected source, original hash,
view hash, actual revision, feature profile and history source.

## Metrics and completion scope

There are 324 official AF/EF comparisons against the two generator baselines,
54 matched Full-system pairs for memory/routing/exploration, and 36 matched M3
component pairs. All AF/EF values are computed per system/seed/B pair before
aggregation. Official AF defaults to the final baseline discovery count as
its target; official EF uses denominator minimum `1e-8` and cap 100, including
the official zero-baseline conventions.

Each aggregate equally averages the six systems within each seed, followed
by mean and sample SD across the three seed means. Full-system delta columns
use **OFF minus Full**; M3 component delta columns use **Full minus OFF**.
Directional AF/EF columns are explicitly labelled **OFF versus Full**.
They are not ratios of aggregate means.

The three Full-system one-switch ablations and the valid three-arm M3 component
study complete the received assigned development packages. Extra planning or
self-correction ablations with exploration and routing enabled would be an
optional M1/M6 scope decision, not a missing M3 delivery or a development
closeout blocker. This does not assert that held-out evaluation, group report
assembly or every later project duty is complete.

Missing cost counters retain their original status. Unknown LLM, hardware,
electricity and failure costs are not imputed as zero. Cross-machine wall times
remain descriptive, not a controlled speed comparison. Output checksums and
separate validation scopes are saved with the tables and plots.
