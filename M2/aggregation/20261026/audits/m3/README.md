# M3 independent intake audit, 26 October 2026

Snapshot: `95f9c8e38923ac494b1117a9b212702afdc5980f`. M3 handoff: `5d2efeadc19e1a6747aa4c0b6f473e8ed64c09fb`.

The 36 uploaded runs are complete, real frozen-source **M3 component studies**. They do not satisfy the two assigned one-switch ablations against the all-enabled `m1_full` reference.

| Condition | Planning | Memory | Self-correction | Exploration | Routing |
| --- | --- | --- | --- | --- | --- |
| Official frozen `m1_full` | on | on | on | on | on |
| Correct component comparator `m3_full` | on | on | on | off | off |
| Uploaded `m3_planning_off`, 18 runs | off | on | on | off | off |
| Uploaded `m3_self_correction_off`, 18 runs | on | on | off | off | off |
| Assigned `planning_off`, not supplied | off | on | on | on | on |
| Assigned `self_correction_off`, not supplied | on | on | off | on | on |

Relative to `m1_full`, each uploaded arm changes three switches. Its score difference cannot identify the isolated planning or self-correction contribution. Renaming directories or method labels would not repair the comparison.

## What the actual files establish

- Both uploaded methods have all six dev systems and seeds17/29/43, one completed episode and20 queries per unit:36 units,720 budgeted queries, all attempt01.
- Every original trajectory/summary agrees on final mSUN/AUDC. All36 exact protocol objects and canonical material snapshots match the paired frozen M1 reference. The current M2-style arithmetic/history checks pass.
- All36 runs record HEAD `02e0026bf450f71f4f7862228d295f5b02b49e12`. Their74 scientific-input fingerprints are identical across runs and match the frozen source after LF-to-CRLF checkout conversion. There are zero unexplained source differences. Windows line endings are not scientific edits.
- Every new mSUN/AUDC pair matches its21October CSV value. This is consistent with re-running the same deterministic M3 component profiles. Equality alone does not show old files were relabelled.
- All36 supplied histories explicitly say `reconstructed_from_frozen_official_trajectory`. They are rebuilt from at-query stable/novel flags and checked against final values. Keep this provenance; do not call them original saved checkpoint histories. Final-value agreement is not a complete independent prefix proof.
- All36 resolved configurations say memory run ID `m4-local`; their actual M4 evidence contains a unique method/system/seed/attempt run ID. This is a configuration-packaging context discrepancy. Separate files and actual unique IDs do not support a claim that memories were shared.

## Comparator evidence is incomplete

The18 `m3_full` values are in `M3/results/m3_ablation_runs.csv`. No complete18-unit `m3_full` raw result set is supplied. The only traced example is `M3/evidence/20261021-dev-ablations/traced-case-Co-Mg-Na-seed17/m3_full/`: it contains metadata, a summary and a plot, but no full trajectory. Its recorded revision is21October `81b0e36...`, not the frozen commit. Four input fingerprints differ from the frozen source: M2 routing code, M5 exploration code and two integration/routing configurations. Before independently accepting the old18-pair component comparison, obtain its complete original result folders and establish equivalence of the relevant non-treatment settings. CSV arithmetic alone does not provide that proof.

Using the common M2 convention (sample SD across three seed means, each averaging six systems), the uploaded planning-off result is5.1111±0.3469 mSUN and49.2222±4.5141 AUDC; self-correction-off is5.8333±0.8819 and58.3056±7.7823. The historical `m3_full` CSV reports6.5000±1.3017 and62.7500±9.0289 under that aggregation. These belong in a separate component-study table with their evidence scope labelled. M3's own summary uses SD over18 runs, which should not be relabelled as seed SD.

The M3 report's zero AF/EF columns are unpaired default metric outputs. They do not establish paired AF/EF against a baseline or the official zero-baseline convention. Recompute paired metrics from verified paired histories if reporting them.

## Required next handoff

Retain and file these36 results under their actual M3 method names. Ask M3 to supply the missing original `m3_full` comparator material for the component study. For the assigned frozen Full ablation table, M3 still owes18 `planning_off` and18 `self_correction_off` episodes, preserving all other components on. Those are M3-owned experiments; this audit did not launch them or change any source/result files.

Detailed per-run checks and source hashes: `m3_scientific_audit.json` and `m3_run_audit.csv`. This audit used no agent, model, oracle, dataset query or simulated experiment and made no GitHub mutation.
