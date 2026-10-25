# M1 Method Draft

## System integration

We integrate the research policy with MADE's unmodified closed-loop environment. On each step, the agent receives the current observed environment state, plans compositions, generates candidate structures, filters them, and selects one structure for the official environment to evaluate. The environment remains responsible for oracle evaluation, feedback, and termination at the configured query budget.

The M1 agent exposes independent switches for planning, M4 memory, M3 self-correction, M5 exploration, and M2 tool routing so each contribution can be ablated against the same integration entry point. The standalone M1 baseline uses MADE's diversity planner and bounded observed-outcome memory. Optional M2, M3, and M5 hooks default off until supplied; enabling a missing hook fails fast. Agent and hook state are checkpointable through MADE's existing `get_state`/`load_state` mechanism.

The frozen `m1_full` configuration uses M3's research planner and self-correction, M4 memory and evidence capture, M5's UCB exploration policy (`alpha0=0.8`), and M2's outcome-aware routing between checkpointed Random and Chemeleon generators. The SMACT validity filter and random candidate scorer remain fixed. The earlier `m1_baseline` keeps MADE's diversity planner and must not be reported as the full method.

## Budget and evidence handling

The official environment enforces the query budget and each environment step evaluates exactly one selected structure. The agent mirrors the configured environment budget to expose queries used/remaining to policy hooks and caps candidate generation by the remaining budget; generated candidates do not count as oracle calls. It does not call or modify the oracle. Built-in memory stores a whitelist of post-query feedback fields exposed by MADE. Hidden ground-truth values and evaluator internals are not used for proposal selection.

## Reproducibility and current status

Each run is associated with the MADE commit, resolved configuration, system, seed, budget, raw trajectory, official metrics, runtime, machine, and available token/API-cost information. B=20 is the team protocol-v1 budget set by the M1 lead, not a TA-mandated value. The integrated release was frozen on 25 October 2026 as `m1-freeze-20261025` after the focused test suites and one official 20-query development canary passed. The canary verifies integration and is not the final leaderboard estimate. Course-provided settings, if later supplied, require a versioned protocol amendment and a new tag.
