# M1 Method Draft

## System integration

We integrate the research policy with MADE's unmodified closed-loop environment. On each step, the agent receives the current observed environment state, plans compositions, generates candidate structures, filters them, and selects one structure for the official environment to evaluate. The environment remains responsible for oracle evaluation, feedback, and termination at the configured query budget.

The M1 agent exposes independent switches for planning, M4 memory, M3 self-correction, M5 exploration, and M2 tool routing so each contribution can be ablated against the same integration entry point. The standalone M1 baseline uses MADE's diversity planner and bounded observed-outcome memory. Optional M2, M3, and M5 hooks default off until supplied; enabling a missing hook fails fast. Agent and hook state are checkpointable through MADE's existing `get_state`/`load_state` mechanism.

The current provisional Hydra configuration uses MADE's diversity composition planner, the random structure generator, the SMACT validity filter, and a random candidate scorer. This is an integration baseline, not a claim that the final team strategy or course settings have been selected. The final planner, generator set, tool router, and exploration policy will be frozen after M2-M5 hand over their tested components.

## Budget and evidence handling

The official environment enforces the query budget and each environment step evaluates exactly one selected structure. The agent mirrors the configured environment budget to expose queries used/remaining to policy hooks and caps candidate generation by the remaining budget; generated candidates do not count as oracle calls. It does not call or modify the oracle. Built-in memory stores a whitelist of post-query feedback fields exposed by MADE. Hidden ground-truth values and evaluator internals are not used for proposal selection.

## Reproducibility and current status

Each run will be associated with the MADE commit, resolved configuration, system, seed, budget, raw trajectory, official metrics, runtime, machine, and available token/API-cost information. The frozen course commit, base model/settings, systems, budget, seeds, and repeat count remain to be confirmed with the teaching team. No benchmark result is reported in this draft.
