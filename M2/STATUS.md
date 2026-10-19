# M2 handoff status

## Verified implementation and boundaries

The conversation handoff starts from repository revision `5c09abd` and preserves
the existing M2 branch and PR #2. The required five M1 documents/source files
were reread: `PLUGIN_INTERFACE.md`, `INTEGRATION.md`, `m1_integrated.py`, its
Hydra configuration, and its contract tests. The project brief, team task split,
step-by-step guide and updated submission notice were reconciled with this scope.

- The M2 router, generator checkpoint adapters, Hydra profile, installer and
  enabled/disabled tests are already present in the documented M1 slots.
- Canonical additions, evidence and English documentation stay under M2.
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

The raw Random ZIP and independently generated tables/curves are in
[`verification/20261019-random-gate`](verification/20261019-random-gate/README.md).
Only one of 36 development baseline units is available here. Overall means,
standard deviations and paired Chemeleon AF/EF remain unavailable. Recorded
zero inference fees do not establish zero total compute cost.

The local diagnostic test exposed a real namespace limitation: `/proc/self`
reports a host PID different from `os.getpid()`. CPU counters are therefore
reported as unknown on that host. The live-CPU assertion is skipped there and
is mandatory on GitHub Actions Linux; it must pass in CI before this feature is
claimed verified. This limitation does not affect the generation-marker and
log-preservation checks or the completed scientific result.

## Still active / not yet verified

At the handoff, run 39213257750's Chemeleon gate is still executing. Its older
observer reports heartbeats with zero completed oracle queries, which cannot
distinguish slow initial generation from a stall. The official configuration
first generates a cached pool and the M1 protocol forces CPU; no pool, seed,
batch-size or scientific setting has been reduced to obtain a faster score.
The older run 39211212095 also remains part of the failed/completed-run audit.

The active workflow is pinned to `bf62711`; new code commits do not update its
running jobs. Its remaining 34 baseline units depend on both initial gates.
Do not launch a duplicate sweep or label an active run completed. Inspect real
query/checkpoint output and the final artifacts before accepting each result.

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
