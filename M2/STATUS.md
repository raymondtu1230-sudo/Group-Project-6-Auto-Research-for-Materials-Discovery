# M2 handoff status

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
Only one of 36 development baseline units is available here. Overall means,
standard deviations and paired Chemeleon AF/EF remain unavailable. Recorded
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

## Ended Chemeleon attempts and bounded recovery

At 17:47 Singapore time on 19 October, run 39213257750's Chemeleon gate
failed at the external 165-minute action limit. Older run 39211212095 ended
with a cancelled conclusion at 17:40, near its 180-minute job limit. Neither
remains active. The raw model logs show three complete sampling batches in
each attempt and actual progress into batch 4. These logs establish substantial
computation; the earlier zero-query heartbeat did not establish a deadlock.

The [timeout audit](verification/20261019-chemeleon-timeout/README.md) retains
both untouched artifacts, GitHub logs, checksums and the original partial report.
No complete Chemeleon trajectory, generator checkpoint, resolved configuration
or 1–20 query history was produced. The report accepts only the already verified
Random unit: one of 36 baseline units, with 35 still missing.

One Chemeleon-only recovery attempt is prepared, pending checks and actual
launch. The manual workflow defaults to that single first development unit;
it skips Random and the wider sweep and blocks a rerun of the same retry run.
Its external action limit is 330 minutes inside a 350-minute job. Numeric
sampling-step diagnostics supplement the existing CPU/log/batch observation.
M1's official scientific settings, CPU, seed, 1024-candidate pool and batch
size 256 remain unchanged. Recovery status is recorded in the audit JSON;
preparation is not a completed result. No automatic retry loop is enabled.

## Next required handovers

1. By 20 October: share the currently available development baseline evidence,
   explicitly flagging missing Chemeleon/remaining units.
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
