# Closed after the M5 evidence supplement

27 October 2026: M5 supplied the actual configuration and component evidence in b36e2a5. All18 now pass the required core checks in the [162-record development closeout](../20261027_dev_closeout/README.md). The former missing-package request below is historical and closed. Auxiliary normalization and retained configuration interpolations are disclosed in the current report; no new scientific rerun is requested.

---

## Previous intake record

# M5 exploration intake — endpoints checked, original package pending

26 October 2026. Data snapshot: `a27634d9edbf231d0c034273fa9f977f9d5e799e`.

M2 has inspected the 18 newly delivered real `exploration_off` episodes, recomputed their comparison with the correct frozen Full reference, and checked the two proposed failure cases. This closes the current offline analysis work; **it does not close M5's original-package acceptance**.

The unchanged M2 evaluator rejects all 18 new attempts because their actual `resolved_config.yaml` files are missing. Original Hydra configuration, retained per-query histories and component evidence are also absent from the attempt folders. No configuration or log has been invented to make those errors disappear. The prior **144 accepted results remain unchanged**; the new 18 have a separate **endpoint-verified, package-pending** label. A 162-row comparison table is not 162 canonical passes.

## Current material

- [Corrected M6 handoff and statistics](M6_HANDOFF.md)
- [Required M5 packaging follow-up](M5_FOLLOWUP.md)
- [Corrected failure-case notes](audits/metrics/failure_cases.md)
- [Nine-method summary with acceptance classes](results/nine_method_summary_with_acceptance.csv)
- [162 endpoint rows with acceptance classes](results/combined_162_endpoint_rows_with_acceptance.csv)
- [18 provisional Full pairs](results/m5_provisional_full_pairs.csv) and [effect summary](results/m5_provisional_effect_summary.json)
- [Curves with M5 explicitly marked pending](results/discovery_curves_with_pending_m5.svg)
- [Original per-run costs](results/m5_per_run_costs.csv)
- [Acceptance status](results/acceptance_validation.json), [strict evaluator errors](results/strict_m2_evaluator_m5_only/validation.json), [source receipts](results/m5_endpoint_evidence_receipts.json) and [provenance](results/evaluation_provenance.json)
- [Independent source audit](audits/sources/README.md), [independent metric review](audits/metrics/INDEPENDENT_REVIEW.md) and [AUDC origin check](audits/metrics/zero_origin_AUDC_proof.json)
- [Reproduction instructions](REPRODUCTION.md) and [execution checks](reproduction_validation.json)

## Corrected headline

| Arm | mSUN@20, mean ± seed SD | AUDC, mean ± seed SD | Acceptance |
| --- | ---: | ---: | --- |
| Frozen Full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 | Accepted reference |
| Exploration OFF | 9.6667 ± 1.1547 | 88.2222 ± 11.5354 | Endpoints checked; original package pending |

Full minus OFF is **+0.3333 mSUN and −0.1111 AUDC**. The report's +0.2/−1.2 headline uses a different Full reference selection; the accepted Full value stays 10.0/88.1111. The 18 successful frozen reference units include successful second attempts where applicable. No failed or earlier dry-run result is substituted for them.

The pooled population SD across 18 mSUN results is OFF 4.8305 versus Full 2.7285, so the rounded 4.8→2.7 description is numerically valid. It measures dispersion across system/seed outcomes, not the shared table's sample SD across three seed means, and does not establish a significance or risk-reduction claim. Full wins/ties/loses 8/1/9 mSUN pairs and wins/loses 9/9 AUDC pairs.

The recorded commands intend only exploration OFF; all 18×74 source fingerprints match frozen scientific source with explicit Windows newline handling. Actual resolved configurations are unavailable, so realized one-switch settings are not independently certified. M5 retains its recorded `aedf8ca...` revision. Machine and dependency differences from Full are preserved, so runtime differences are not a controlled hardware comparison.

All derived M5 histories are separate trajectory reconstructions using the unchanged M1 function and official zero-origin AUDC arithmetic. They are not original checkpoint captures or new hull/novelty calculations. Provisional AF/EF use these labelled reconstructions; the original 288 accepted baseline comparisons remain accepted separately. All original data, earlier reports and incomplete attempts remain intact. No new scientific run, model/oracle call or external message is made. All project writes stay under `M2/`.
