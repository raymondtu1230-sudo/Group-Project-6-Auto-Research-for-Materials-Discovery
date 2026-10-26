# Closed after the M5 evidence supplement

27 October 2026: M5 supplied the actual configuration and component evidence in b36e2a5. All18 now pass the required core checks in the [162-record development closeout](../20261027_dev_closeout/README.md). The former missing-package request below is historical and closed. Auxiliary normalization and retained configuration interpolations are disclosed in the current report; no new scientific rerun is requested.

---

## Previous intake record

# M5 follow-up needed to close formal acceptance

The 18 real `exploration_off` attempts are recorded completed and their official endpoints, protocols, material reference snapshots and source fingerprints check out. M2 has finished the offline analysis possible with the received files. The remaining blocker is the original evidence package, not a request to rerun the 18 successful scientific episodes.

## Recover existing files, preserving actual provenance

For each attempt, recover the corresponding existing MADE run-output directory and supply:

- The actual `resolved_config.yaml`, together with saved Hydra configuration/overrides if retained. M2 cannot certify the realized one-switch settings from the command string alone.
- The actual M4 memory/evidence logs and other component logs that were produced. Preserve run console logs and any M3 traces. If exploration OFF legitimately produced no M5 decision log, explicitly explain that absence rather than creating one.
- Retained original per-query history if it exists. If it does not, a separate reconstruction from the real trajectory can be supplied with its source clearly labelled, following the M1 evidence-packaging approach; it must not be called an original checkpoint capture.
- A file manifest, preserving actual run metadata, attempt numbers and recorded revision `aedf8ca238d2ef56948c0eadf2c897aef67f5104`. Do not relabel an original execution as `02e0026` or synthesize runtime configurations or logs from assumptions.

Keep all original attempts and the original files. No existing attempt should be overwritten. If evidence is unavailable, state exactly what was not retained; do not invent missing bytes. The current strict evaluator errors are saved unchanged for traceability.

## Report corrections

- Use the accepted frozen Full reference: overall **10.0000 mSUN / 88.1111 AUDC**. OFF is **9.6667 / 88.2222**. ON−OFF is **+0.3333 / −0.1111**.
- Mg–Sn–Sr Full is **11.0 mSUN / 102.8333 AUDC**, so that system's ON−OFF is **−1.0 / −16.8333**.
- Keep the 4.8→2.7 pooled population-SD observation labelled separately from the shared seed-mean sample SD.
- Correct the two case descriptions using [the actual trajectories and existing ON decision log](audits/metrics/failure_cases.md). ON Ga–Pt–Tm seed17 has one ternary mixed-mode query, not six, and its same-seed OFF/ON mSUN is16/10. The ON decision sidecar is already committed.

M2's independent numerical/reference-selection audit and corrected M6 notes are available in this folder. M5's report was not edited by M2.

## Short reply for the user to send

> Thanks, M5. I checked the 18 endpoints and added a clearly marked provisional comparison. Please upload the original resolved configs, saved Hydra files and available component logs from the existing outputs so the package can be validated with M2/evaluate.py. No scientific rerun is requested. The frozen Full comparison gives +0.33 mSUN and −0.11 AUDC; I’ve also recorded corrections to the two cases under M2/aggregation/20261026_m5_intake. The ON decision log is already available.
