# Development Memory pilot

## Scope

One paired development check: Mg-Sn-Sr, seed 17, B=20, protocol-v1 CPU ORB.
It uses M1's official profile with M3 planning/reflection and M4 memory/capture.
Composition exploration and tool routing are OFF in both arms. Only the Memory
switch and run/output identities differ. This is not `m1_full`, not the frozen
component ablation, and not a check/hidden run. The base team source is `e1a40d8`.

The current full method cannot yet run unchanged: its method overrides enable
tool routing while the shared profile has `tool_router: null`. This pilot does
not silently disable a component and report a full-agent score. Separate method
IDs `m4_dev_pilot_on` and `m4_dev_pilot_off` are added only to the local driver's
in-memory dev allow-list; the shared protocol and files are unchanged.

## Run and validate

From M1/MADE with the local M4 package installed and Materials Project configured:

```bash
uv run --no-sync python ../../M4/run_dev_pilot.py --arm on --attempt 1
uv run --no-sync python ../../M4/run_dev_pilot.py --arm off --attempt 1
uv run --no-sync python ../../M4/validate_dev_pilot.py --attempt 1 --output ../../M4/evidence/dev-pilot-20261021/audit.json
```

Each process calls the existing M1 metadata driver and unchanged official MADE
runner. All oracle, relaxation, dataset and budget settings come from M1. The
pair uses Random candidate generation, so no LLM/OpenRouter inference is needed.
Do not launch concurrently: upstream checkpoint names depend on launch time.
Never overwrite attempts. A 30-minute per-arm limit preserves partial attempts.

M2's existing external checkpoint-history and configuration preservation helpers
are reused. Only public M3 decision traces are copied from agent checkpoints;
evaluation history remains offline and never becomes a decision input. The
validator calls M2's canonical `load_run`, checks paired resolved settings and
material-reference hashes, requires ON/OFF decision-trace evidence, and exports
all 20 queried observations in both arms, including the final step.

The original ON configuration export was re-resolved from its saved Hydra file
using the exact child run identity; the parent now sets those identity variables
when preserving configuration. This affects logging provenance, not scientific
execution. No metric or trajectory is reconstructed or altered.

## Interpretation and remaining work

The completed paired audit and raw evidence are under `evidence/dev-pilot-20261021/`. ON scored mSUN@20=7/AUDC=68.5, versus OFF 8/76.0. The development pair did not show a Memory benefit. A single
system/seed cannot establish an aggregate effect. Keep equal and negative
outcomes. mSUN and AUDC have distinct definitions; do not interchange them.
Record campaign queries separately from initialization/scorer computation and
recorded inference fees separately from total compute cost.

Proposal-event capture is independent of Memory. A missing event file means no
captured generator/filter event occurred; do not fabricate failures. M5's new
sidecar is not part of this check: its latest module and log_path still need M1
adoption. The current main M5 policy is disabled in both arms.

After the full agent is frozen, reuse an accepted matching full reference and
run `memory_off` with only that switch changed on dev. Agree systems/repeats and
raw-output delivery with M1/M2/M6. This pilot does not replace that experiment.
