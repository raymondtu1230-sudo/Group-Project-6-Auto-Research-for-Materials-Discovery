# M2 frozen development tool-routing ablation

Frozen source: `02e0026bf450f71f4f7862228d295f5b02b49e12` (`m1-freeze-20261025`). Accepted M2 units: 18/18.
Complete paired final-metric comparison: True.

Final discovery values come from actual original official trajectories and
summaries. Curve sources are labelled separately below. This reporter invokes no agent,
model, oracle, Materials Project request or simulated experiment.

| Method | mSUN@20 mean ± seed SD | AUDC mean ± seed SD |
| --- | --- | --- |
| tool_routing_off | 7.7222 ± 1.1824 | 70.1389 ± 1.6080 |
| m1_full | 10.0000 ± 0.8819 | 88.1111 ± 9.4536 |
| paired_delta_off_minus_full | -2.2778 ± 2.0571 | -17.9722 ± 9.7910 |

Each seed mean gives the six systems equal weight. The final mean and sample
standard deviation are calculated across the three seed means, not across18
independent seeds. Delta is `tool_routing_off - m1_full`; positive values favor
the routing-off condition and negative values favor full routing.

`perunit.csv` contains the paired final scores and differences. `seed_aggregate.csv`
and `method_summary.csv` expose the aggregation. `official_curves.svg` plots only
M2's verified per-query histories, when available; mSUN and the official AUDC-source count
are distinct metrics. The SHA256 manifests and preserved attempt directories
remain the evidence source; report CSV files do not replace those directories.

## Official checkpoint cleanup and independent endpoint audits

18 units were accepted for
final endpoint comparison by a NEW independent audit. Their original
`m2_validation.json` remains false and unchanged: the unchanged official runner
logged successful completion and removed its checkpoint before the post-exit
collector ran. The new audit permits only that exact three-error failure,
rechecks all frozen scientific source hashes, actual resolved settings,
component logs, process exit and completed20-query trajectory/summary, and is
saved in `independent_endpoint_audits.json`. It does not claim to recover an
original checkpoint or history.

Per-query histories available to this report: 18/18.
Separate record-only curve analysis accepted: True.
When supplied, that analysis must first validate all720 original baseline
prefixes and all72 final endpoints, then match each original trajectory hash,
material reference and frozen evaluator source hash. Such curves are labelled
offline re-evaluations of actual recorded structures/energies, never new oracle
queries or recovered checkpoint files. Without original history or a passing
separate proof, no curve is generated for that unit.

## M2 transport audit

18 accepted M2 units have missing raw hidden Hydra attachments in
the received artifact payload. Their exact missing paths and expected original
SHA256 values are recorded in `validation.json`. This is consistent with the
live artifact uploader's default exclusion of hidden files. The original raw
`.hydra/config.yaml`, `.hydra/hydra.yaml` and `.hydra/overrides.yaml` files have
not been reconstructed. The received archive is not claimed to preserve every
original byte when those files are absent.

The required visible payload is checked separately: original run metadata,
full trajectory, official summaries, `resolved_config.yaml`, component logs,
official checkpoint/history, process log and collection/exit records. Every
available file must match its recorded SHA256, and a missing file outside those
three named raw Hydra attachments remains a validation error. Scientific run
acceptance was recorded on the execution runner before artifact transport;
final-score pairing and required visible-payload integrity are distinguished
from availability of these additional original audit attachments.

## M1 reference audit attachments

18 reference units lack one or more original Hydra/resolved
configuration, component-log or per-query-history attachments in the supplied
frozen result tree. The missing-file list is in `validation.json`. Final metric
pairing uses the actual official final trajectory/summary values after checking
system, seed, B, protocol, scientific input hashes and canonical material
reference identity. Missing M1 attachments have not been invented or re-labelled
as originals. M1 discovery curves and AF/EF are consequently not reported here.
The original M1 attachments should be supplied separately for the complete audit.

The previously completed Random/Chemeleon baseline results are not re-run or
assumed compatible by this script. Their raw evidence was not an input to this
report, so no new AF/EF or baseline pairing is claimed.

## Cost and failed attempts

`costs.csv` records each method's machine, CPU/OS, elapsed driver time, query
count and known fee fields. A recorded USD0 model fee is not zero total cost.
Hardware, electricity and all unpriced failed attempts remain outside those
fees; unknown LLM calls/tokens stay blank. Different machines are not treated as
a controlled hardware-speed comparison. `failed_attempts.json` indexes preserved
failed attempts. No failed attempt was deleted or used as a completed score.

Input roots:
- M2: `/home/runner/work/Group-Project-6-Auto-Research-for-Materials-Discovery/Group-Project-6-Auto-Research-for-Materials-Discovery/M2/results/preserved/raw`
- Frozen M1 reference: `/home/runner/work/_temp/m2-recorded-evaluation-frozen/M1/MADE/results/protocol_v1/m1_full/dev`
