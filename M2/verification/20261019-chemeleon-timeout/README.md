# Chemeleon timeout audit — incomplete real experiment

The newer gate stopped at **17:47:19 Singapore time on 19 October 2026**
because its GitHub action reached its 165-minute limit. The older job ended
with a `cancelled` conclusion at 17:40:22, near its configured 180-minute job
limit. Its available log does not identify a cancellation actor. Neither
attempt is a completed materials-performance result.

## What the actual model logs establish

| Attempt | Batch 1 | Batch 2 | Batch 3 | Last recorded batch 4 step |
| --- | --- | --- | --- | --- |
| New gate, 4001 | 256/256, 52:38 | 256/256, 51:28 | 256/256, 55:28 | 3/256, elapsed 00:37 |
| Older job, 3001 | 256/256, 43:26 | 256/256, 42:53 | 256/256, 46:25 | 251/256, elapsed 43:34 |

These are diffusion sampling steps within generation batches, not oracle
queries or discovery scores. The logs prove substantial computation before
termination. They do not support the earlier suspicion of a deadlock. The
newer action's limit was shorter than the time required to finish the initial
1024-candidate generation on this CPU. There is no saved generator checkpoint
in either artifact from which this initial generation can be resumed.

## Preserved evidence

- `12177571578.zip`: untouched new-gate artifact from run 39213257750.
- `12177865607.zip`: untouched older-job artifact from run 39211212095.
- `12176904574.zip`: original partial report from the newer workflow.
- `github-job-logs.zip`: both actual GitHub job logs, without alteration.
- `audit.json`: artifact checksums, exact sources, batch observations, absent
  fields, and bounded recovery status. All ZIP checksums matched GitHub.

Each failed artifact contains only the original `run_metadata.json` and model
process log. Neither has a completed trajectory, a full 1–20 query history,
a resolved Hydra configuration, or final scientific metrics. The untouched
metadata lacks a completion status because the process was interrupted.
The GitHub outcome is recorded separately, without rewriting raw metadata.

The original report accepts only the previously verified Random unit; it flags
the incomplete Chemeleon attempt and still has **35 missing baseline units**.
Its report job succeeding does not mean that the scientific experiment passed.
The existing [Random evidence](../20261019-random-gate/README.md) remains the
only accepted baseline unit. Compute charges for the interrupted attempts are
unreported; no zero-cost claim is made.

## One bounded recovery attempt

The recovery keeps M1's official runner, oracle, evaluator, environment,
query budget, seed, CPU setting, 1024-candidate pool, batch size 256, model,
and inference settings unchanged. Only the external action limit changes to
330 minutes, within a 350-minute job. The existing observer also exposes
numeric sampling steps and elapsed sampling time alongside CPU/log/batch
diagnostics. The new fields never enter agent state or scientific metrics.

The manual workflow defaults to `mode=chemeleon_retry`, which selects only
the first development Chemeleon unit and skips the wider sweep. Random is
not rerun. A rerun of the same retry workflow attempt is blocked. This is one
retry, not an automatic retry loop. The historical `audit.json` records preparation before launch. See
[`retry-status.json`](retry-status.json) for the later observed launch and job
status; a started workflow is not a successful scientific result.

Because the active workflow exists only on the development branch, the same
recovery can be launched by one explicit `retry-request.json` commit in this
folder. Its push trigger is restricted to that exact path and the M2 branch.
Ordinary code, documentation and result updates do not trigger materials runs.
The record will be added only after fresh checks pass; a missing record means
that this explicit launch has not been requested.
