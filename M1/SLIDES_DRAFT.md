# A1 Slides: System Integration and Budget Control

Visual reference: `M2/report/M2_Method_and_Dev_Baselines_20261021_36of36.pptx`.
This source keeps the same white canvas, Bitstream Charter typography, navy title treatment, blue emphasis text, sparse layout, and muted blue footer style.

## Slide 1 - Integrated agent architecture

**Key message:** Independent component slots keep ablations comparable.

### Editable flow

MADE state and A4 memory -> M1 boundary -> Planning (A3) -> Self-correction (A3) -> Exploration (A5) -> A2 routing and generation -> Validity filter -> Scorer -> One selected structure -> MADE oracle feedback -> next planning step.

### On-slide points

- A2-A5 use independent switches.
- Stateful components save and restore checkpoint state.
- Proposals use observed feedback only.
- MADE runner, oracle, and evaluator stay unchanged.

### Speaker focus

M1 provides the integration boundary inside MADE's normal agent contract. The agent receives current state and public feedback, lets enabled components shape the next plan, then generates, filters, scores, and submits one structure. MADE evaluates that structure and returns the next observed state. This keeps component ablations comparable and keeps hidden ground truth outside proposal selection.

## Slide 2 - Query budget, checkpointing, and evidence

**Key message:** The environment enforces B = 20 queries per episode.

### Editable budget flow

B = 20 queries -> Remaining budget -> Candidate cap -> One `env.step()` -> One oracle evaluation.

### On-slide points

- Candidate generation is not an oracle call.
- Checkpoint state includes the agent, planner, generator, filter, scorer, memory, evidence capture, and plug-in state.
- Each run records protocol revision, resolved config, system, seed, trajectory, metrics, cost fields, wall time, and machine.
- Keep oracle queries, model/API cost, and wall time separate.

### Frozen protocol strip

`m1-freeze-20261025` | ORB v3 conservative, CPU | seeds 17 / 29 / 43 | six public development systems | B=20

### Speaker focus

B=20 is the team's protocol-v1 setting, not a new teaching-team requirement. The environment remains authoritative, so M1 exposes remaining budget and caps candidate generation. Candidate generation does not consume oracle calls; one `env.step()` evaluates one selected structure. Checkpoint and run metadata preserve enough context to reproduce and audit results without confusing oracle calls with model/API cost or elapsed time.
