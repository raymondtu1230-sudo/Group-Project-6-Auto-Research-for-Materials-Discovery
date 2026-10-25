# M2 real frozen routing-off, 25 October 2026

Authorized:18 independent real dev episodes, six systems x seeds17/29/43,
CPU ORB v3 conservative,B=20,one episode per unit. Only enable_tool_routing
is disabled. No other member's source, frozen configuration or shared workflow
is changed. Existing36 baseline results are retained, not rerun.

The existing branch-local m2-chemeleon-direct workflow is reused unchanged as
cloud transport. Its legacy Chemeleon labels/arguments are NOT scientific
parameters. Task-guarded M2 adapters select exactly tool_routing_off in a clean,
detached m1-freeze-20261025 checkout. Its sole scientific entry is the frozen
M1/run_experiment.py. Real attempts start01, failed01 is preserved before02.
Claims use M2/frozen_20261025/claims so old baseline claims are not touched.

Root freeze HEAD02e0026 and genuine nested MADE upstream HEADbffda0c are both
recorded. The genuine official upstream Git history is fetched and reset--mixed
to reproduce M1's nested checkout boundary, without changing any frozen file.
The controller and frozen scientific uv.lock are required to match. The science
process imports made and M4 from the frozen source using explicit PYTHONPATH;
actual module paths are verified. The dependency venv is shared only after that
check. No installer writes into frozen source.

The actual Figshare54966305 archive is SHA256-checked before extraction against
ccbe78df811cdf7451dbafe7c0c5fef7985b4f9502f328e0ddab44bc6896ea1e.
Actual Chemeleon CSP and ORB CPU loads plus an authenticated MaterialsProject
request gate execution. There is no synthetic data or mock science. Preflight
model loading consumes no generator sample/oracle benchmark query.

Frozen source, venv and heavy model weights live in RUNNER_TEMP outside uploads.
Only complete per-attempt scientific evidence, matching original Hydra files,
component logs, official checkpoint history, stdout/stderr and checksum receipts
are copied to M2/runtime and M2/packaged. Original metadata is never rewritten.
The preserve job copies successes and failures into main/M2/frozen_20261025
using path-restricted, non-force commits. Existing members' results are untouched.

The unchanged transport has360min job /340min compute-step limits; the controller
keeps an explicit330second exit/save reserve and honors the lower effective limit.
These are runtime bounds, not changes to B, seeds, model or generator parameters.

User requested full parallelism after first four started. A supplemental request
admits only units with no existing namespaced claim and sets max_parallel18.
The original four remain running. Account-level available concurrency determines
actual start times; no other running work is cancelled. The immutable first
workflow may later reach an already-claimed unit: its claim guard must reject
that duplicate before model setup/science. Such a transport rejection is not a
second scientific attempt and is not counted as an experimental failure.

M1 reference final metrics are available; its missing original Hydra/history/log
attachments are recorded separately and never invented. They do not block M2's
18 runs. Final-score pairing and baseline compatibility are audited afterward.
