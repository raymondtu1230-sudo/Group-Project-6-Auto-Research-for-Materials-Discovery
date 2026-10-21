# Memory experiment preparation and result handoff

Prepared against main revision `b361659` on 19 October 2026. This document does
not activate M4 or start experiments. Recheck the frozen team protocol before
using it. The existing Mg-Sn-Sr workflow run is development evidence, not an
accepted full-agent ablation or a replacement for the following runs.

## Readiness gate

- M1 adopts `integration/ADOPTION.md`, preserves all independent switches and
  supplies the frozen full-agent revision.
- M3 demonstrates that retrieved records reach the actual decision input when
  ON and are absent when OFF. Existing baseline history remains unchanged.
- M2 confirms its capture wrapper is the agreed entry point for both `m1_full`
  and `memory_off`, and confirms the result destination and required artifacts.
- Use the protocol development systems, B=20, seeds 17/29/43, one episode per
  process, and the same oracle/model/relaxation/candidate settings in both arms.
  M6 confirms any protocol changes or reduced-repeat exception.
- Both runs use the same frozen scientific implementation and material-reference
  snapshot. No intermediate source edits, cross-run memory import or hidden-data
  decision inputs. Preserve the resolved configuration and reference revision.

## Paired pilot commands (after the readiness gate)

From the repository root, use the prepared environment and M2's existing external
capture wrapper. No alternate benchmark runner or metric implementation is added.
The example is one development pair, not the full sweep:

```bash
cd M1/MADE
M4_RUN_ID=m1_full-dev-Mg-Sn-Sr-seed17-attempt01 M4_EPISODE_ID=0 \
  uv run --no-sync python ../../M2/run_baselines.py \
  --method m1_full --split dev --system Mg-Sn-Sr --seed 17 --attempt 1
M4_RUN_ID=memory_off-dev-Mg-Sn-Sr-seed17-attempt01 M4_EPISODE_ID=0 \
  uv run --no-sync python ../../M2/run_baselines.py \
  --method memory_off --split dev --system Mg-Sn-Sr --seed 17 --attempt 1
```

M2's wrapper accepts a method name and invokes M1's protocol driver, which
recognizes both methods. Compatibility of the capture mechanism with the final
integrated agent still needs the pilot; these commands are not completed-run
claims. Do not run them against today's unintegrated default and call it a
Memory experiment. Do not rerun an existing attempt directory; increment the
attempt number and preserve failures. If M1 supplies the full reference, reuse
that accepted matching run instead of duplicating it. Record the new run ID for
every retry. Keep credentials in local environment configuration, never commands
or committed artifacts.

Check the paired resolved configurations: only `enable_memory` should differ in
scientific settings. Output paths, attempt identities and logging provenance may
differ. In particular, Memory OFF must retain the same M2 routing, M3 planning
and M5 exploration settings as the full reference. Inspect both decision traces,
not only the switch value, before accepting the treatment.

## Required result files per run

Under `M1/MADE/results/protocol_v1/<method>/dev/<system>/seed_<seed>/attempt_<NN>/`:

| Artifact | Acceptance purpose |
| --- | --- |
| `run_metadata.json` | completed status, protocol, seed, revision and cost provenance |
| `resolved_config.yaml` | actual saved settings, not a reconstructed config |
| `trajectories/episode_000.json` | B queried observations and official final metrics |
| `trajectories/phase_diagram_episode_000.png` | post-run visualization |
| `summary/summary.json` | exactly one completed episode |
| `m2_metrics_history.json` | `complete_curve: true`, official query history 1 through B |
| M2 capture log and available progress diagnostics | timing, failures and capture audit |
| M4 complete evidence export and M3 decision trace | observed candidates and demonstrable memory use |

The online M4 log is in Hydra's runtime output directory, which may differ from
the protocol result directory. Record its location; do not assume it is already
bundled with the protocol results. Memory OFF may have no online plugin log
because M1 skips the plugin. Export the official queried trajectory for both
arms, including the final observation, from `M1/MADE`:

```bash
uv run --no-sync python ../../M4/export_evidence.py \
  results/protocol_v1/m1_full/dev/Mg-Sn-Sr/seed_17/attempt_01/trajectories/episode_000.json \
  results/protocol_v1/m1_full/dev/Mg-Sn-Sr/seed_17/attempt_01/m4_evidence_complete.jsonl \
  --run-id m1_full-dev-Mg-Sn-Sr-seed17-attempt01 --episode-id 0 --elements Mg Sn Sr
```

Use the corresponding method/path/run ID for OFF and other units. The exporter
refuses to overwrite a file. See `EVIDENCE_SCHEMA.md`; it extracts public queried
observations, not the evaluation-only envelope. Full official outputs retained
for offline validation must never become retrieval inputs.

## Offline acceptance and reporting

From `M1/MADE`, run M2's canonical evaluator:

```bash
uv run --no-sync python ../../M2/evaluate.py \
  --results-root results/protocol_v1 \
  --output ../../M4/results/pilot-review --split dev --allow-partial
```

Inspect the generated validation findings and per-run table. `--allow-partial`
permits an incomplete report; it does not make invalid runs valid or establish
a complete scientific comparison. Preserve every rejected run and its reason.
M2 verifies complete curves, matching final metrics/configuration/protocol and
material-reference consistency. The old M4 workflow run was not captured with
this wrapper and must not be relabelled as accepted; do not invent intermediate
metrics to fill a missing history.

After a valid pair, estimate runtime/storage and agree the remaining systems and
seeds with M1/M2/M6. M2 owns the aggregate scoreboard and paired AF/EF calculations.
Report official mSUN and AUDC separately; their source curves differ. Do not
compare our development m1_baseline AUDC=49.5 to M2's Random AUDC=55.5 as a Memory
effect. They are different methods and neither is the required full/OFF pair.

## M4 delivery to M2 and M6

Send a manifest listing each method/system/seed/attempt, frozen revision, raw
result location, validation status, decision trace and complete evidence export.
Include failures and missing units. Supply official metrics, runtime, recorded
costs/token usage where available, and 2-3 cases tracing earlier observation to
retrieval, subsequent decision and outcome. Include neutral/negative cases and
do not infer a physical failure mechanism from instability alone.

Evidence files are not a substitute for the official scoreboard. Do not equate
B campaign queries with all initialization/scorer computation, or zero recorded
inference fees with zero total computing cost. Do not upload `.env`, credentials
or full local debug logs without inspection.

Target schedule remains code/method handoff by 24 October, team freeze on 25,
reference by noon on 26, and accepted M4 results/cases plus final interpretation
by 27, subject to team confirmation and measured compute availability.

## 20 October integration update

M1 has adopted M4 and M3. Joint synthetic tests exercise the real M3 decision
trace with Memory ON/OFF. Select the M3 planner explicitly while the default
remains diversity. M5 confirmed schema v1; the optional generator/filter event
capture is described in integration/EVENT_CAPTURE.md and needs M1 adoption.
Capture must be identical in both arms and remain outside decision inputs.
M6 confirms ablations on dev only; check/hidden are restricted to the frozen
full agent and baselines. Formal experiments still require the frozen reference.

## 21 October development-pair outcome

M1 adopted capture in `3f8d48f`. The explicit M3/M4 development pair completed and is documented in DEV_PILOT.md; it is not a frozen full-agent ablation. Current m1_full enables unconfigured tool routing, so do not run the final commands above until the full-agent readiness gate is met. Negative development results and raw outputs are retained under evidence/dev-pilot-20261021/.
