# Recovery admission is blocked, not a hang

At the 20 October 2026 02:51 Asia/Singapore observation, run 39297647516 has completed:
continuous and deliberately interrupted jobs succeeded; restore job 118217264688 exited 1 at 17:59:11 UTC with `ValueError: Batch model, input or execution identity mismatch`. It failed before second-batch generation and before the exact comparison or runner-metadata step. No pass is claimed. The older run 39286986254's comparison failure remains preserved separately.

The cache deliberately compares execution identity, request, library/source/weight fingerprints, threads, CPU capability and architecture. The exception does not disclose which field differed; the saved cache stores only an identity hash. This observation cannot establish a CPU mismatch or a serialization fix. A future diagnostic must expose the relevant non-secret identities and isolate the actual difference before any changed run; do not remove the guard, round output, relax scientific settings, or retry unchanged.

All current jobs are exited, not stuck. No cancellation was necessary or claimed. The 60-minute two-observation no-progress condition was not invoked. Formal Chemeleon remains 1/18 accepted; 17 missing units have NOT been launched. Neither batch256 fixture nor the unverified full1024 production wrapper is a benchmark score.

Preservation-only run 39306348134 at source 78346d6d92fcfb18fa44447d650b9e6f77e43adc includes both recovery run IDs and all final Random archives, and reuses previously saved ZIP bytes. It does no science. Raw evidence must reach main/M2 before closing this turn.

The local scratch disk also reports no available space and shell clone cannot connect to its configured proxy. No user's files, environments or running processes were deleted to make space. GitHub connector reads/writes and hosted evidence-only processing remain usable.

Next viable paths: rigorously diagnose exact recovery with identity evidence and then validate the full protocol wrapper/costs, or arrange adequately long persistent CPU execution. No new paid runtime or unconfirmed GPU execution is authorized. The separate GPU guide is preparation only. Shared-main M1/M5 default integration and frozen full-method reference remain owner dependencies. Do not mark all M2 work complete.
