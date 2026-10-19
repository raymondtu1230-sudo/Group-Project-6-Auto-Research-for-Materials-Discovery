# M2 work log

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
  and retained-evidence validation. The 17-unit matrix is released;
  two Random jobs were performing scientific computation and 15 were queued
  at the 16:40 UTC observation. Its matrix admits only missing Random
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
- Fresh isolated local checks for this turn's development source (not the
  concurrently published main prototype): 17 M1 tests and 53 M2 tests passed, no skips in
  this host invocation; focused and complete M2 Ruff passed. Local official
  smoke reached Chrome export but stalled and was terminated as an incomplete
  synthetic check. The earlier local CPU-namespace skip and Chrome socket
  failure remain historical records, not passes. Current GitHub gate is the
  source of truth for hosted smoke.
- Current-source CI [39286986328](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39286986328)
  at `e30b5bb` now passed all gates, including reproducible installation,
  original M1 tests, all M2 tests, both Ruff checks and unchanged official smoke.
  CI 39286848820 was still pending at its earlier inspection.
- Keep the M2 development branch and draft PR #2. Do not merge, delete branches,
  change official parameters, or edit the old retry-request.json. Routing-off
  still depends on M1's frozen full-method reference; M6 owns check/hidden tests.


## Earlier takeover snapshot (preserved)

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

## 19 October 2026, 22:38 Singapore: completed recovery received

- Downloaded unchanged artifacts 12194049480 and 12194876393; both SHA256
  digests match GitHub. Saved original job logs and source-CI job conclusions.
- The sole retry completed all four generation batches and 20 oracle queries.
  No new science run was launched. Random was neither rerun nor counted twice.
- Reviewed the fixed source `3e07d9f0`, all 69 recorded M1 hashes, capture hash,
  resolved Hydra configuration, raw trajectory and full query history 1..20.
- Ran the unchanged M2 evaluator and official MADE metrics offline in its
  locked environment. Two real runs accepted, zero issues; the protocol and
  material-reference snapshots match. Visually inspected the paired curves.
- Chemeleon Mg-Sn-Sr/17: mSUN=16, AUDC=161, wall=15767.025 s; the existing
  Random pair has 7 / 55.5 / 952.717 s. These are partial development results.
  AF=2.375 and EF=2.2857142857142856 refer only to the official paired curve.
- The partial package reports 34 missing baselines and 18 missing m1_full
  units; overall method means/SD stay blank. Original failed/cancelled attempts,
  null usage fields and unknown compute charges are retained. No source code,
  scientific settings, retry request or M1/M4/root files were changed.
- Published evidence/status on main/M2 and the existing development branch,
  retaining PR #2 without merging. With no active monitored science left,
  pause this result-recovery monitor after publication verification.

## 20 October 2026: current takeover and safe missing-only continuation

- Reread the five M1 contract/source files, all requested M2 records, formal protocol, course brief, task split and guide. Inspected all four M1 message screenshots and M6's newly available report/slide/compute formats.
- Preserved the M2 branch and draft PR #2. Main advanced independently through M6 publication/removal of comms files; do not overwrite those or merge the development branch.
- Rechecked original archive SHA256 values and executed official metrics again. Two accepted baseline units, zero issues, no new score, 34 missing baselines and 18 missing frozen full-method units. Current installed source matches all 69 Chemeleon M1 hashes. Random's sole differing hash is the unused M2 router from an earlier revision.
- Added checksum-pinned imports and a missing-only 36-unit inventory. Tests protect against rescheduling a completed pair, invalid/newer failed evidence, corrupted archives and overwriting existing evidence. Historical failures stay in their original package. A latest failed attempt requires explicit review, not silent fallback.
- Requested run 39284865198 at source 955bdca9: only 17 missing Random units, fresh acceptance gates, max four concurrent processes, automatic raw retention/offline reporting and M2-only publication on main. Queued is not running. Scientific configuration and run_baselines.py are unchanged.
- Local locked environment installed successfully. Original M1 tests: 17 passed. Combined current M2 tests including new recovery mechanics: 52 passed, 1 CPU-namespace skip. Focused/all-M2 Ruff passed. The original smoke failed at Chrome socket creation (Operation not permitted), despite Chrome installation and no missing shared libraries. Kept the original failed log; GitHub CI is separately queued.
- User asked how to prevent losing another long Chemeleon initialization. Implemented experimental batch-level output/RNG replay outside official source and four passing synthetic continuation/rejection tests. It refuses changed identity, RNG or corrupted bytes. Actual local model download returned upstream HTTP 403 before sampling; no bypass or fabricated real result.
- Requested actual small recovery check 39285316913 at source 639f47b3. Prepared stronger full-batch256/cross-runner artifact recovery validation. Formal Chemeleon remains blocked until admission; no reduced candidate pool, batch size, diffusion steps or query budget is used for a claimed protocol result. Small recovery fixtures are labelled integration tests.
- Produced a four-slide editable M6 draft: routing and paired discovery curves for M6 slots 7/10 (40 seconds each), protocol/cost backups and speaker notes. Native charts carry the exact official curve data and embedded workbooks. Rendered/inspected all four slides; package/layout/chart validation passed. This creates a draft deliverable, not a final team presentation.
- Corrected obsolete reference ownership and branch-count statements. M1 still integrates/freezes/supplies the full reference. M6 still owns check/hidden evaluation. No group message was sent and no receipt/acceptance was claimed.

Lesson: prevent repetition at the expensive model-batch boundary and validate exact continuation before trusting it. Preserve model outputs and RNG, not just activity logs. An execution-recovery fixture does not replace a completed 20-query scientific unit.
