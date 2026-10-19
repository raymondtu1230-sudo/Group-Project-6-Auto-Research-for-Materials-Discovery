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
