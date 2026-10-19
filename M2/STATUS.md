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

## Current experiment status (2026-10-19 10:07 UTC)

The original run 39213257750 ended with a failed Chemeleon gate after the
external 165-minute action limit. Its model log completed three generation
batches and entered batch four; this establishes actual computation during
that attempt, rather than a deadlock. The older run 39211212095 ended with a
cancelled conclusion. Its log does not establish who or what cancelled it.

The [failure audit and original archives](verification/20261019-chemeleon-timeout/README.md)
preserve both attempts, SHA256 checksums, absent fields and the partial report.
Neither Chemeleon attempt has a completed trajectory or accepted metrics.
The report accepts one Random unit and records 35 missing baseline units.

Exactly one bounded Chemeleon retry has now started:
[run 39234974449](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39234974449),
revision `3e07d9f0`, job `118001953048`. At 10:07 UTC, environment and
Chrome installation had completed and the full-budget action step was in
progress. No sampling/query progress or completed artifact was independently
visible through the jobs API at that check; this is a launch confirmation,
not a claim of scientific progress or completion.

The retry retains the original scientific settings and raises only the
external action/job limits to 330/350 minutes with batch/CPU/log diagnostics.
It selects one Chemeleon Mg-Sn-Sr / seed 17 / B=20 unit; Random and the wider
sweep are excluded. The original launch request is preserved unchanged.
No new experiment was started by this status check. See the timestamped
[retry receipt](verification/20261019-chemeleon-timeout/retry-status.json).

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

The recovery implementation passed fresh GitHub CI 39234330794 (4284a7d8):
17 original M1 tests, 46 M2 tests without skips, Ruff, reproducible installation
and unchanged official smoke. The final launch-trigger revision ef7f8c2 also
passed complete CI 39234757674. Source details are in the timeout folder
`recovery_ci.json`. The observer now also emits numeric sampling steps, totals
and elapsed sampling seconds. No additional retry is authorized automatically.

Runtime continuity is a user requirement. Preserve the current retry instead of
restarting it for timeout edits. The current run's limits are fixed at launch;
GitHub-hosted jobs also have a six-hour hard cap. Initial generation has no
verified mid-batch restart point. See `verification/20261019-chemeleon-timeout/RUNTIME_SAFEGUARDS.md`
for admission and preservation rules before later experiments.

At the subsequent live-log check, CPU counters increased and sampling batch 1
advanced from step 4/256 to 7/256. The actual numerical observations are in
`verification/20261019-chemeleon-timeout/live-progress.json`; this establishes
sampling activity, not a completed query or final performance score.
