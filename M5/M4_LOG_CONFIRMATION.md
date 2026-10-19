# M5 → M4: Evidence Log Format Confirmation

From: Chen Mingsong (M5). Re: `M4/M5_LOG_FORMAT.md`, `M4/EVIDENCE_SCHEMA.md`.
Status: **confirmed with one request** (19 Oct).

## Confirmed

- Schema v1 accepted as-is. `candidate_id` as attempt identity (not formula) is
  exactly right for trajectory analysis — multiple structures per composition
  stay distinguishable.
- Exporter requiring `--elements` for the full run system: agreed.
- ON/OFF episodes both exported from official trajectories including the final
  query: agreed — the ablation comparison depends on equal evidence availability.
- "Never invent a physical cause for an unstable structure": agreed; my failure
  write-up will classify outcomes from observed records only.

## What M5 will supply (per your request)

For over-exploitation / wasteful-exploration analysis you asked for exploration
mode, selected direction, remaining budget, candidate-tool provenance, and
policy rationale. My `ExplorationPolicy` keeps a `decision_log`; every
`adjust_plan` call appends one record:

| Field | Content |
|---|---|
| `step` / `query_count` | Campaign step |
| `m1_queries_remaining` | Budget context at decision time |
| `mode` | `explore` / `exploit` / `mixed` |
| `incoming_compositions` | Plan as received from planner/reflection |
| `outgoing_compositions` | Plan as returned |
| `composition_source` | Per composition: `planner` or `ucb_explore` |
| `ucb_mean`, `ucb_std`, `beta`, `alpha_t` | UCB statistics per pick |
| `rationale` | Short string, e.g. "alpha=0.4, 2/5 slots to unexplored stoichiometries" |

These records are JSON-serializable and ride the agent checkpoint
(`get_state()`/`load_state()`), so you can ingest them from the checkpoint or I
can dump them as a sidecar JSONL per episode — tell me which you prefer.

## One request

You noted rejected/error events are not automatically captured by the current
hook ("framework event capture remains pending"). Wasteful-exploration cases
often involve **rejected** candidates (filtered before ever costing a query).
If the hook gains a rejected/error event source before the 26 Oct ablations, I
get materially better failure trajectories. If it won't land in time, confirm
and I'll design the analysis around `evaluated`-only records.

## Next step

First real run of my policy on a practice system (target 21–23 Oct) will include
the decision_log sidecar; I'll send you one episode's output for a format
dry-run before the 24 Oct code handover.
