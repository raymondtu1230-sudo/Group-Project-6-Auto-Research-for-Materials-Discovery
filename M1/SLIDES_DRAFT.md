# M1 Slide Draft

## Slide 1 - Integrated agent architecture

- MADE state and previous queried evidence enter the M1 integration agent.
- Configurable path: planner -> self-correction -> exploration adjustment -> generator/tool router -> validity filter -> scorer -> one selected proposal.
- M2-M5 components plug into independent configuration slots and ablation switches.
- The MADE runner and oracle remain unchanged.

Speaker note: Explain that MADE owns the interaction loop and scientific feedback; M1 owns the integration boundary, configuration, checkpointing, and run artifacts.

## Slide 2 - Query budget and evidence trail

- M1 protocol v1 uses B=20; the environment is authoritative and stops at budget exhaustion.
- One runner iteration produces one oracle query; candidate batch size is capped by remaining queries to avoid excess generation.
- Checkpoints include planner/generator/filter/scorer state, memory state, and optional router/exploration state.
- Run record: commit, resolved config, system, seed, budget, trajectory, metrics, cost, wall time, and machine.

Speaker note: Keep query count separate from LLM tokens, API cost, and wall-clock time. B=20 is the M1 lead's team-selected protocol-v1 budget, not a TA-mandated value.

## Slide 3 - Results and ablations (populate after frozen runs)

| Method | mSUN@B | AUDC | AF | EF | Oracle calls | Tokens / cost | Wall time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 integrated reference (protocol v1) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Planning off | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Memory off | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Exploration off | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Tool routing off | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Speaker note: Do not present placeholder values. Replace the table with M2's official scoring output, name the evaluated systems/seeds, and disclose the number of repeats.
