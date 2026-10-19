# M2 handoff status

## Latest continuation — 20 October 2026, Singapore time

This section supersedes the older retry-only authorization and stopped-monitor
wording below. The user explicitly authorized completion of the missing 34 dev
baseline units. Preserve the already accepted Mg-Sn-Sr/17 pair and all failed
attempts. Main changes remain under M2; M1 integration and freeze stay with M1.

- Accepted scientific baseline coverage remains **2/36**, with 17 Random and
  17 Chemeleon units still unaccepted. No new scientific score is claimed.
- Previous Random workflow 39284865198 stopped in prepare at Ruff import
  sorting before any scientific unit was scheduled. Source CIs 39284459462,
  39284865097 and 39285316822 also stopped at all-M2 Ruff; their skipped smoke
  steps are not passes. Full raw job logs are retained in
  [the continuation audit](verification/20261020-preflight-and-recovery/README.md).
- The two test-import blocks were corrected under MADE's Ruff configuration.
  Revision `b3f68f274373d4599a7e026cd0f3cf5a9889e977` starts
  [missing-only Random run 39286848821](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286848821).
  Its prepare job has now passed the current checks including official smoke,
  and retained-evidence validation. The 17-unit matrix is now released;
  2 Random jobs are running and 15 are queued at this observation. Its matrix admits only missing Random
  units, at most four concurrently; an existing completed pair is never rerun.
- Actual small-model recovery run
  [39285316913](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39285316913)
  passed its continuous/interrupted/cross-process checks with two Li2O candidates,
  batch=1 and unchanged 256 diffusion steps. Artifact 12201404998 has GitHub
  digest `8570dbc27d6a286c60a994ccb4d704169ef4f0c58247c9a0c926ff88a65eace9`.
  This turn inspected raw logs and artifact metadata, but has not independently
  downloaded and rehashed this non-scoring artifact.
- [Batch256 cross-runner run 39286986254](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986254)
  is submitted at fixed source `e30b5bb233842797f4ad90c80732bb327d07c0bf`.
  Its two sampling jobs were queued at last inspection. It uses a 512-candidate
  Li2O validation fixture, two original batch=256 calls, an uploaded checkpoint
  and restoration on a separate runner. It requires exact structures, RNG,
  preserved first-batch bytes and distinct runner hostnames. This is **not a
  benchmark result or proof of full protocol-pool compatibility**. No formal
  Chemeleon unit has been scheduled using this experimental cache.
- Fresh isolated local checks: 17 M1 tests and 53 M2 tests passed, no skips in
  this host invocation; focused and complete M2 Ruff passed. Local official
  smoke reached Chrome export but stalled and was terminated as an incomplete
  synthetic check. The earlier local CPU-namespace skip and Chrome socket
  failure remain historical records, not passes. Current GitHub gate is the
  source of truth for hosted smoke.
- Current-source CIs: 39286848820 (`b3f68f2`) and 39286986328 (`e30b5bb`)
  were queued at last inspection; no final success is asserted for them.
- Keep the M2 development branch and draft PR #2. Do not merge, delete branches,
  change official parameters, or edit the old retry-request.json. Routing-off
  still depends on M1's frozen full-method reference; M6 owns check/hidden tests.


## Historical record retained below

## Verified implementation and boundaries

The conversation handoff starts from repository revision `5c09abd` and preserves
the existing M2 branch and PR #2. The required five M1 documents/source files
were reread: `PLUGIN_INTERFACE.md`, `INTEGRATION.md`, `m1_integrated.py`, its
Hydra configuration, and its contract tests. The project brief, team task split,
step-by-step guide and updated submission notice were reconciled with this scope.

- The M2 router, generator checkpoint adapters, Hydra profile, installer and
  enabled/disabled tests are packaged here. The development branch also contains
  the installed copies in M1's documented slots.
- Canonical additions, evidence and English documentation stay under M2.
- The independent delivery adds `M2/` beside `M1/` and `M4/` on `main`.
  It preserves all existing main-branch files and does not merge PR #2 or apply
  the M1 integration configuration. `install.py` is the separate explicit
  integration step. Workflow definitions are included under `M2/workflows/`;
  existing experiments continue from their development-branch revisions.
- The official runner, oracle, evaluator, environment, budget, candidate-pool
  settings and M1 protocol are unchanged by this handoff.
- Process diagnostics are external to the scientific interaction. They measure
  CPU/log/generation activity and never read labels or change proposal decisions.
- Original checkpoints, failed attempts, revisions and raw results are retained.
  Secrets stay in the existing GitHub Secret and are never copied into files.

## Actual completed evidence

| Item | Evidence / scope |
| --- | --- |
| M1 contracts and original smoke | Passed on run 39213883707, revision 8fdcaaf |
| Latest upstream integration checks | Passed on run 39214658007, revision 5c09abd |
| Actual API / model continuation | Passed on run 39214657963; three real sampling calls |
| Random Mg-Sn-Sr / seed 17 / B=20 | Completed on run 39213257750, job 117931485324 |
| Offline Random result validation | One run accepted, zero issues, complete query history 1-20 |
| Random result | mSUN@20=7, AUDC=55.5, driver wall time 952.717 s |
| Actual live CPU diagnostic | Passed on GitHub Linux in run 39217841268 |
| Complete continuation CI | Passed on run 39218278124, revision b8e2c0c; 17 M1 and 45 M2 tests, both Ruff checks, reproducible installation and original smoke |
| Latest handoff acceptance CI | Passed on run 39221672640, revision 2b2c6753; 17 M1 and 45 M2 tests with no skips, Ruff, reproducible installation and original smoke |

The exact user-supplied handoff requirements and branch-retention decision are
mapped in [ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md). The M2 development
branch now includes current main's published M2 folder and M4 contents; the three
documentation conflicts were resolved using the published main versions.

The raw Random ZIP and independently generated tables/curves are in
[`verification/20261019-random-gate`](verification/20261019-random-gate/README.md).
That historical package contains one unit. The later paired recovery package
now accepts two of 36 baseline units; only single-pair AF/EF are available.
Overall method means and standard deviations remain unavailable. Recorded
zero inference fees do not establish zero total compute cost.

The local diagnostic test exposed a real namespace limitation: `/proc/self`
reports a host PID different from `os.getpid()`. CPU counters are therefore
reported as unknown on that host. The live-CPU assertion is skipped there and
is mandatory on GitHub Actions Linux. It passed on run 39217841268, which ran
17 M1 contract tests and 45 M2 tests successfully. That run then stopped on one
test-import formatting issue; the import was fixed using MADE's Ruff settings.
The subsequent complete CI run 39218278124 passed every integration acceptance
gate, including the original smoke script, on revision b8e2c0c. The namespace
limitation does not affect the completed scientific result. The independent
folder publication changes packaging and documentation, not the tested code or
scientific settings.

## Current experiment status (2026-10-19 14:38 UTC)

[Recovery run 39234974449](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39234974449)
completed successfully at 22:30 Singapore time, fixed source `3e07d9f0`.
Four batches finished and all 20 oracle queries completed. The independent
[paired report and original artifacts](verification/20261019-chemeleon-recovery/README.md)
validate Chemeleon Mg-Sn-Sr/17: mSUN@20=16, AUDC=161, wall=15767.025 s.
The existing Random unit remains mSUN@20=7, AUDC=55.5, wall=952.717 s.
Their protocol and 194-entry material reference snapshots match. Official
single-pair Chemeleon AF/EF vs Random are 2.375 / 2.2857142857142856.
No method-level aggregate score is available.

There are now **2/36 accepted baseline units**, 34 missing baseline units and
18 missing frozen full-method units (52 missing protocol-required units in
all). The original timeout/cancelled attempts remain in the
[failure audit](verification/20261019-chemeleon-timeout/README.md), excluded from
accepted results. No further experiment was launched. The one authorized retry
is consumed; the wider sweep was skipped. The monitored workflow has no active
scientific jobs. Final M2 comparison and M1 integration remain incomplete.

## Next required handovers

1. By 20 October: share the currently available development baseline evidence,
   explicitly flagging the 34 missing baseline units and the single-pair scope.
2. By 24 October: M1 reviews and integrates PR #2; M6 receives the method and
   slide material in `METHODS_AND_M6_HANDOFF.md`.
3. After M1 integrates the other owners and freezes the full agent on 25 October:
   record that release revision, receive the full reference by 26 October noon,
   and run the routing-off ablation changing only its switch.
4. By 27 October: validate the other owners' results, paired reference/baseline
   comparisons, discovery curves, costs and failed-run audit; deliver to M6.
5. M6 owns public-check and course hidden-test work. A public check split must
   never be described as a hidden test. The full report/slides remain due for
   rehearsal on 29 October; presentations are 31 October or 1 November. The
   individual report is at most three pages, due by the end of 3 November.

The full reference and routing-off comparison cannot honestly be completed
before the other owners' components and the frozen reference exist. Their
absence is a team dependency, not a reason to invent or substitute scores.

The recovery implementation passed fresh GitHub CI 39234330794 (4284a7d8):
17 original M1 tests, 46 M2 tests without skips, Ruff, reproducible installation
and unchanged official smoke. The final launch-trigger revision ef7f8c2 also
passed complete CI 39234757674. Source details are in the timeout folder
`recovery_ci.json`. The observer now also emits numeric sampling steps, totals
and elapsed sampling seconds. No additional retry is authorized automatically.

Runtime continuity is a user requirement. The completed retry was preserved
without restarting it for timeout edits. Its limits were fixed at launch;
GitHub-hosted jobs also have a six-hour hard cap. Initial generation has no
verified mid-batch restart point. See `verification/20261019-chemeleon-timeout/RUNTIME_SAFEGUARDS.md`
for admission and preservation rules before later experiments.

At the subsequent live-log check, CPU counters increased and sampling batch 1
advanced from step 4/256 to 7/256. The actual numerical observations are in
`verification/20261019-chemeleon-timeout/live-progress.json`; this establishes
sampling activity, not a completed query or final performance score.
