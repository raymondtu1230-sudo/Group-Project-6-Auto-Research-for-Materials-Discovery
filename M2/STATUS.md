# M2 status: 20 October 2026 takeover

## Accepted science: 2/36 development baseline units

| Method | System / seed | B | mSUN@B | AUDC | Driver seconds |
| --- | --- | --- | --- | --- | --- |
| Random | Mg-Sn-Sr / 17 | 20 | 7 | 55.5 | 952.717 |
| Chemeleon | Mg-Sn-Sr / 17 | 20 | 16 | 161 | 15767.025 |

The original ZIPs were checksum-verified and rescored with the unchanged official
metrics in this takeover. Two runs accepted, zero issues. Single-pair Chemeleon
AF/EF versus Random are 2.375 / 2.2857142857142856. Overall method means and SD
remain unavailable. Known inference fees are USD 0, while hardware, electricity,
interrupted-attempt charges and unreported usage remain unknown.

Original evidence is preserved in `verification/20261019-random-gate/`,
`verification/20261019-chemeleon-recovery/` and the separate timeout audit.
New read-only review, 36-unit inventory and actual local failures are in
`verification/20261020-takeover/`. These reviews do not add new scientific units.

## Missing-only work actually requested

- [Run 39284865198](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39284865198),
  fixed source `955bdca92b732c7d4fef64928df35fc15320fe85`, requests only the 17
  missing Random dev units. Four jobs at most run concurrently, one episode per
  process, unchanged official driver/configuration and B=20. Fresh M1/M2 checks
  and the original smoke must pass in `prepare` before science starts.
- At this status snapshot it is **queued**, with no new completed scientific
  result and no allocated scientific job. Queue state is not active computation.
- Reused archives are checksum-pinned. Later published result bundles can be
  imported too. Invalid/newer failed attempts stop rescheduling for explicit
  review. The completed first pair is excluded. The legacy `baseline_sweep`
  would rerun that pair and must not be launched for this continuation.
- Each job retains raw data, diagnostics, configuration, provenance and failure
  attempts. The report job uses the official metrics, uploads artifacts and
  publishes only a new `main/M2/verification/missing-<run_id>/` folder. This does
  not merge PR #2 or change main's M1 configuration.

## Chemeleon continuity: prototype, not yet admitted

Seventeen Chemeleon units remain missing. A measured unit took 263 minutes.
Other systems may be slower than a hosted six-hour job allows, and the original
initial pool has no verified mid-generation recovery. No full Chemeleon sweep
was dispatched under those conditions.

The user explicitly requested avoiding another full restart after timeout.
`generation_cache.py` therefore experiments with saving outputs of each original
`DiffusionModule.sample` batch, its exact inputs, model/source fingerprints and
Python/NumPy/Torch RNG before/after the batch. Replaying a verified batch restores
its post-call RNG and lets the original generator write/read the same CIFs in
the original order. It changes no pool size, batch size, diffusion steps, oracle
budget or official source file. A planned pause occurs before the next sampling
call. Logs alone do not establish recoverability.

Four synthetic recovery/rejection tests pass. Actual-model cross-process check
[39285316913](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39285316913),
source `639f47b301d71cc7bd7c66c7832f0ecb75bb5e9d`, is queued. This is a small
integration fixture, not a baseline score. The local actual-model check was
blocked by an upstream model-download HTTP 403; no actual sample completed locally.
A separate batch256/cross-runner workflow is prepared for the necessary stronger
admission check. Its proof must match all generated structures/order and final
RNG across actual artifact upload/download and a different runner. Until those
checks and production-wrapper integration pass, the 17 formal units remain
capacity-blocked. `cache_protocol.py` is experimental and has not been used for
accepted science. An adequately long persistent CPU host remains an alternative.

## Component verification and ownership

The delivered router, generator adapters, installer, M1 agent contract and all
five switches are preserved. The installer was executed only in our checkout,
not on shared main. It produced the documented four integration slots; no
official runner/oracle/evaluator/environment/budget or M1 contract source changed.

Current local M1 contracts: 17 passed. Current combined M2 suite: 52 passed and
one CPU-namespace skip. Focused/all-M2 Ruff passed. Original smoke failed because
this host denies Chrome socket creation, even after Chrome installation. Its
failure is retained and is not a pass. Source-specific GitHub CI is queued;
old passing CI is historical evidence only. See the actual logs/JUnit in the
current takeover package.

## Handoffs and dependencies

- By 24 October, M1 receives component/config/installer/test evidence in M2.
  M1 owns shared integration and the 25 October freeze. PR #2 remains a draft,
  unmerged, and the development branch is retained.
- M6's current format is `M6/report/SLIDES_OUTLINE.md`: M2 slide 7 (routing) and
  slide 10 (curves), 40 seconds each. `report/` contains the editable draft and
  speaker notes, plus protocol/cost backups. This is an actual draft, not the
  final group deck. Current numerical slides explicitly show one pair / 2 of 36.
- M1 supplies the frozen full-system reference by 26 October noon. M2 validates
  it and only then runs routing-off at the same revision/conditions with one
  switch changed. Do not substitute `m1_baseline` or run M1's reference for him.
- M2 collects all member results and produces final tables, curves and costs for
  M6 by 27 October. M6 owns public-check/hidden tests. No such evaluation is
  claimed here. No recipient has yet confirmed receipt or acceptance.
- The earlier recovery monitor has been updated and resumed for current runs.
  It checks at most hourly and reports meaningful new evidence. It does not
  promise an immediate notification at the exact sampling/completion instant.

## Superseded instructions, retained historical records

Old one-retry-only scope and the stopped recovery monitor describe 19 October.
The user's 20 October handoff authorizes completing missing development units.
Old CI revisions/counts in earlier checklist/log entries remain dated evidence,
not current acceptance. main now contains multiple member folders and branches;
the old statement that only two repository branches exist is obsolete. The old
README sentence assigning the full reference run to M2 has been corrected.
