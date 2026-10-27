# Reproduce the 198-run development aggregation

Use source snapshot `09c9b74300b26176ce5ade37d5192ba98caa240f` and this release's `aggregate_handoffs.py`. In a repository checkout containing the original member artifacts and prior M2 archives, run:

```bash
python M2/aggregation/20261027_m3_full_agent/aggregate_handoffs.py \
  --snapshot . \
  --prior-results M2/verification/preserved-40204426478 \
  --work M2/runtime/m3-full-agent-reproduction \
  --output M2/aggregation/20261027_m3_full_agent/results-reproduction
```

Use Python 3.13 with NumPy 2.3.5, PyYAML 6.0.3 and Matplotlib 3.10.8, as in the preceding validated analysis. Work/output directories must be new or empty. The script refuses to overwrite populated directories. This is offline evaluation and aggregation; it invokes no scientific episode, model, agent, Materials Project request or oracle.

It loads the unchanged official `DiscoveryCurveMetrics` class AST with real NumPy and executes the unchanged `M2/evaluate.py` CLI on all 198 selected views. Asserted evaluator SHA-256 is `2eacad27246a8669657c6551807cbfeb1274cf94b691840f2f196d55e3e93a89`; official metric-module SHA-256 is `f24d68a2b0a854cf7d880a97079c47e1d8160da11f7f31fa8900274067c7e3a1`. This loading method bypasses unrelated model imports without replacing metric formulas.

The existing [162-run reproduction notes](../20261027_dev_closeout/REPRODUCTION.md) explain preserved baseline/routing archives, Full selection, M4/M5 inputs and M5 auxiliary-only corrections. This script additionally accepts M3's 36 actual Full-agent records, checks concrete single-switch configs, 2,664 scientific-source fingerprints, 324 manifest members, and independently sums 720 raw AUDC prefixes. All model/source revision labels remain those recorded in the original attempts.

Line-ending conversion is verification only; original files are not edited. Published receipts contain repository-relative sources and platform labels. M5 submitted-history copies remain byte-identical to published originals. Matplotlib previews are reproducible derived plots; no original experimental phase-diagram images are copied into this release. The retained [output manifest](results/output_manifest.json) describes published result files; local PNG previews may be generated in addition.

The three public per-run CSV views omit generated source/view-directory columns (`source` and `original_source`). Scientific scores, approved runtime/cost fields and row membership are unchanged; full local evaluator exports and the original repository evidence retain the complete lineage.

M3's new histories are labelled reconstructions from the original trajectories, rather than original checkpoint captures. All 720 new discovery-count prefixes agree with the recorded stable/new-discovery flags; raw AUDC was independently summed with a zero-origin trapezoid and matched the official calculation at every prefix. This is a consistency check of recorded evidence, not a new hull, novelty or oracle evaluation.

M3 declares Chemeleon archive SHA-256 `ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e`. No run-machine archive-checksum receipt was found in the delivered 36-run artifacts. Accept the core metrics and the documented single-switch configuration comparison; retain model-archive identity as declared rather than independently established. Recovering an existing checksum receipt is a documentation follow-up, not a request to rerun.

Retain earlier qualifications: M5's 305 auxiliary normalized-AUDC discrepancies are corrected only in M2 analysis copies; M5's saved composed configurations retain interpolations; routing histories use labelled record-only reevaluation, and some original routing attachments are missing. Original member evidence and the prior 162-run release remain unchanged. Costs are partial and machines differ.
