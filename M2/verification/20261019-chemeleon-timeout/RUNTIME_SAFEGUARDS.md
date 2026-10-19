# Runtime continuity safeguards

The user's priority is to preserve completed work and avoid preventable external interruptions. Do not cancel an active experiment merely to apply a revised timeout, refresh a conversation, or republish files.

## Current recovery

Run 39234974449 is fixed at revision 3e07d9f0. It has a 330-minute computation-step limit and a 350-minute job limit. These cannot be changed retroactively by editing the branch. Keep this run alive; do not restart it to apply configuration changes. Only the single Chemeleon unit is running. The wider sweep is excluded.

The previous gate completed three sampling batches in 52:38, 51:28 and 55:28 before entering batch four. Its 165-minute external limit was too short for this measured CPU workload. The recovery provides materially more time, but its completion time is still uncertain and is not a reported performance metric.

## Persistence that is actually available

The unchanged official MADE runner saves agent/environment state, trajectory and metric history after completed oracle steps. CachedGenerator serializes its complete candidate pool once that pool has been constructed. The official generator does not provide a restorable checkpoint midway through initial diffusion sampling. Neither failed artifact contains such a checkpoint. Do not claim that a completed sampling batch can already be resumed on another runner.

The external observer preserves diagnostic JSONL and query histories; the workflow uploads available results and failures with `always()`. This is best-effort recovery, not a guarantee against runner loss before upload. Preserve every available artifact and checkpoint and verify recovery compatibility before resuming. Never alter official scientific logic or substitute generated candidates to manufacture continuity.

## Admission rule for later experiments

Before dispatching a wider or different workload, inspect measured initialization/generation/query times, timeout limits, disk capacity and recovery support. Keep adequate time for result preservation. If the workload may exceed the host's hard limit, resolve the execution/persistence arrangement first rather than knowingly starting an unsuitable run. No wider sweep or additional retry is authorized by this note.

GitHub's official hosted-runner limit is six hours per job; raising a YAML timeout does not bypass it. Source checked 19 October 2026: https://docs.github.com/en/enterprise-cloud%40latest/actions/reference/limits and https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax . Do not promise unlimited execution on this platform. Use the existing monitor to inspect numerical progress and preserve evidence, without treating zero queries during initialization as a deadlock.
