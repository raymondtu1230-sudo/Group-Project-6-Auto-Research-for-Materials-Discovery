# M2 work log

## 19 October 2026: continuation after interrupted conversation

- Recovered the original user requirements and reread the five required M1
  interface/source files plus course and team deliverables. Kept the existing
  branch/PR, owner boundaries and unchanged official benchmark settings.
- Downloaded actual artifact 12169366866 from run 39213257750. Its SHA-256
  matched GitHub's digest. The Random Mg-Sn-Sr/17 trajectory has all 20 queries,
  the actual Hydra configuration and full official per-query history.
- Executed the offline evaluator on that real evidence: one accepted run and
  zero validation issues. mSUN@20 is 7 and AUDC is 55.5; these are one-unit
  development values. Produced and visually inspected both discovery curves.
- Preserved raw data/checksums, missing-unit audit and tables in the verification
  folder. No overall baseline mean/SD or missing paired metric was fabricated.
- Diagnosed why a heartbeat cannot establish scientific progress: child logs
  were redirected and buffered until completion. Added unbuffered child output
  plus CPU/log/batch diagnostics to new attempts, without changing any material
  computation, query count or selection policy.
- A real local child-process test exposed incompatible process IDs in the host
  `/proc` namespace. Added namespace validation so those counters stay unknown.
  The CPU-growth assertion is mandatory on GitHub Linux and explicitly skipped
  on the incompatible host; it is not counted as a locally passed assertion.
- Initial local test run: 61 passed, one diagnostic assertion failed because of
  that namespace limitation. After the guard, focused diagnostics: two passed,
  one explicitly skipped. Ruff passed. Keep the subsequent CI run as the source
  of truth for the complete handoff verification.
- GitHub run 39217841268 executed 17 original M1 contracts and 45 M2 tests,
  including actual live CPU-counter growth, with no failures or skips. Its next
  lint step found one import-group formatting issue under MADE's Ruff config.
  Fixed that formatting and reran the exact lint command from `M1/MADE`; it
  passed. A follow-up CI run must complete the remaining original smoke gate.
- Chemeleon's full protocol unit remains separate from the earlier three-call
  model-continuation check. A generation check does not establish discovery
  performance. Preserve the active frozen run rather than duplicate it.

Lessons: distinguish conversation connectivity, workflow status, actual process
work and completed oracle queries. Treat unknown progress as unknown. Report
unit-level scores only with their raw evidence and never as a full comparison.

## 19 October 2026: independent folder delivery on main

- Complete follow-up CI 39218278124 passed on b8e2c0c: 17 M1 contract tests,
  45 M2 tests, both Ruff checks, reproducible installation and the unchanged
  official smoke script. Updated the status to record this completed evidence.
- The user confirmed that the delivery folder is the existing `M2/`, separate
  from M1's work. Their screenshot showed `main` containing only M1 and M4;
  the earlier M2 link pointed to the development branch instead of that view.
- Prepared the independent M2 source/evidence folder for main, including copies
  of its workflow definitions. Kept main's M1, M4 and root files unchanged and
  kept PR #2's integration changes separate from this folder publication.
- No scientific run was cancelled, restarted or duplicated for packaging.

## 19 October 2026: verified timeout cause and one-unit recovery

- Read actual jobs/artifacts after the Chemeleon gate ended at 17:47 Singapore
  time. Its action log explicitly states a 165-minute timeout. Older job
  117924795008 ended with a cancelled conclusion at 17:40; its available log
  does not identify a cancellation actor.
- Downloaded artifacts 12177571578, 12177865607 and 12176904574 and verified
  all three SHA-256 digests against GitHub. Preserved untouched ZIPs, both job
  logs and source provenance in `verification/20261019-chemeleon-timeout/`.
- Model process logs show three complete batches in both attempts and progress
  in batch 4. The new gate completed its first three batches in 52:38, 51:28
  and 55:28, then reached step 3/256 in batch 4. This establishes computation,
  not a deadlock. No complete candidate-generation checkpoint was preserved.
- Kept missing final metrics/configuration/query histories explicit. The
  original partial report accepts only the existing Random unit and records
  the incomplete Chemeleon attempt. Baseline completion remains 1/36.
- Prepared one bounded Chemeleon-only retry with 330/350-minute action/job
  limits. The manual input defaults to recovery; Random and the wider sweep
  are excluded, and a rerun of the same recovery run is blocked. Model, seed,
  pool, batch size, CPU, official science code and B=20 are unchanged.
- Extended only external diagnostics to expose numeric diffusion sampling
  steps and elapsed time. New tests/checks must run before launch; the earlier
  CI is not represented as verification of this modification.

## 19 October 2026: exact M1 handoff acceptance audit

- Reconciled the user's pasted handoff requirements with all five required M1
  files and the actual M2 implementation. Recorded the requirement-to-file
  mapping and remaining gates in `ACCEPTANCE_CHECKLIST.md`.
- Synced current main into the existing M2 development branch. Resolved three
  documentation add/add conflicts using main's published M2 versions; preserved
  current M4 contents and the previously tested M1 integration code exactly.
- Local repeat: 17 M1 and 44 M2 tests passed, with the incompatible local CPU
  namespace check explicitly skipped. Ruff and installation reproducibility
  passed. No skipped local test is represented as a pass.
- GitHub run 39221672640 passed on 2b2c6753: 17 M1 and 45 M2 tests with no
  skips, both Ruff checks, reproducible installation and original smoke. Actual
  test logs and artifact 12172061499 preserve the evidence.
- Retained main and the one M2 development branch because integration review
  and scientific experiments remain open. The independent main/M2 package is
  available; full baseline and full-reference comparisons remain incomplete.

- Recovery-code CI 39234330794 passed: 17 M1 and 46 M2 tests without skips,
  Ruff, reproducible installation and unchanged official smoke. Preserved the
  actual CI source/hash/artifact identity in `recovery_ci.json`.
- The default branch does not activate M2 workflow files. A single immutable
  `retry-request.json` commit therefore requests the one authorized recovery
  on the development branch. The exact-path push trigger excludes ordinary
  changes; its empty-input fallback selects Chemeleon only and no sweep.
- Launched run 39234974449 at source 3e07d9f0. It has entered the official protocol step, not a
  completed performance result. The existing result monitor follows this run
  and is instructed not to spend the once-only retry authorization again.
