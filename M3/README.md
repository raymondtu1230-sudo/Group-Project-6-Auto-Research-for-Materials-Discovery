# M3: Planning and self-correction

M3 is one part of our group's materials-discovery agent. It decides **where the
agent spends its limited tries**, and it notices **when the search is stuck**
and changes course. This page explains what M3 does, how it fits into the
whole project, what it found, who receives what, and where every file is.

- **Status:** built, merged into the agent by M1; M3's assigned full-agent
  ablations and the component study are done on M1's frozen agent (90 runs),
  validated by M2's evaluator.
- **Short on time?** Read [In one minute](#in-one-minute) and
  [Results](#results).

---

## In one minute

**The project.** We are building an "auto research" agent for the MADE
benchmark. In a loop, the agent proposes a candidate material, a simulator
(the "oracle") checks whether it is stable, and the agent uses that answer to
choose its next candidate. Each run has a budget of **20 tries**. The score,
**mSUN@20**, counts the stable, unique, new materials found in those 20 tries.
The simulator and the scoring are fixed; only the agent's strategy can be
improved.

**M3's job.** Two components:

1. **Planner:** splits the search into areas and moves the remaining tries
   toward the areas that are working.
2. **Self-correction:** spots a stalled search (no new stable material for a
   while, or about to repeat itself) and changes course.

**The result.** Inside M1's full frozen agent, switching planning off halves
what the agent finds (**10.0 → 5.3** new stable materials per run, lower in 15
of 18 paired runs); switching self-correction off makes no measurable
difference (10.0 → 9.5). In the earlier component study, without M5 and M2,
M3's planning helped hard systems and hurt easy ones. Details in
[Results](#results).

---

## Where M3 fits in the whole project

Six members each own one part of the agent. M1 joins the parts into one agent;
each part can be switched on or off so its effect can be measured.

| Member | Owns |
| --- | --- |
| M1 | The agent that joins all parts, the budget, the reference run |
| M2 | Baselines to beat, scoring, choosing which generator to use (tool routing) |
| **M3** | **Planning and self-correction (this folder)** |
| M4 | Memory of past tries |
| M5 | Exploration: new areas vs. digging deeper |
| M6 | Fair testing, unseen systems, final report and slides |

**One try, step by step** (parts marked "if on" are switched off in M3's own
test runs, so they don't mix into M3's results):

1. **M3 planner** picks the area and the recipe to try next, using what it has
   seen so far and M4's memory.
2. **M3 self-correction** checks that plan; if the search looks stuck, it
   swaps in a different recipe.
3. **M5 exploration** (if on) can adjust the plan further.
4. **M2 tool routing** (if on) picks which generator builds the candidate
   structures.
5. **M1** makes sure the plan never exceeds the tries left, then the simulator
   checks the candidate.
6. **M4 memory** records the result, and the next try starts.

### Who M3 affects, and why

| Member | How M3 affects them | Why it matters |
| --- | --- | --- |
| **M1** | M3 plugs into M1's existing planner and self-correction slots. It also edits four M1 files: the agent config, the experiment script, a protocol test and the protocol notes. | M1's full agent (`m1_full`) uses the M3 planner; the frozen agent contains the current M3 code, bug fix included. |
| **M2** | Receives M3's result tables. M3's runs keep tool routing off. | M2 builds the final results table; tool routing being off means M3's numbers don't depend on M2's part. |
| **M4** | The planner reads M4's memory when it scores areas. Every M3 run gets its own memory run ID. | M4's memory test needs a planner that uses memory; M4 confirmed that M3 does. |
| **M5** | Exploration runs after M3's self-correction and receives its plan. M3's runs keep exploration off. | M3's Hf-Ni-Zr runs are a ready example of "over-exploitation", one of the two failure types M5 reports. |
| **M6** | Receives M3's method text and results text. | M3's table belongs in the "component vs M1 reference" section of the report, separate from the frozen agent's own ablation table. |

---

## How M3 works

Plain words used here: a **try** is one question to the simulator, a
**recipe** is a composition (which elements, in what amounts), and an
**area** is part of the search space (each pair of elements, or all three
together). The [glossary](#glossary) maps these to the technical terms.

### Part 1: the planner

Each test system has three elements, for example magnesium, tin and
strontium. A new material can combine any two of them or all three, so the
planner splits the search into **four areas**: the three pairs, and the
three-element mix.

1. **Split:** set up the four areas.
2. **Try:** spend 4 tries in one area. Inside that area, pick recipes not yet
   tried, choosing the ones most different from earlier tries. Skip recipes
   that fail a basic chemistry check (charge balance).
3. **Compare:** after every 4 tries, score each area by how many stable
   materials it has produced, what M4's memory says, and how much of it is
   still untried.
4. **Move:** spend the next 4 tries in the best-scoring area.

| Setting | Value | Meaning |
| --- | --- | --- |
| Tries per area visit | 4 | How long it stays before comparing areas again |
| Bonus for untried share | 0.5 | Keeps it from dropping an area too early |
| Near-miss counts as | half a find | A result within 0.1 eV/atom of stable, seen in memory |
| Skip a recipe after | 2 failures in memory | Avoids re-testing known failures |

### Part 2: self-correction

Before every try it checks the plan for two warning signs:

- **No progress:** 6 tries in a row with no new stable material.
- **Repeating:** the plan would repeat a recipe already tried twice.

When either shows up, it **changes course**: it swaps in the recipes tried
least and most different from the recent ones. If the search stays stuck, it
also generates more candidate structures per recipe; that uses no extra tries.
It waits 3 tries between changes, and any new find resets it.

### Rules M3 follows

- Uses only what the agent has actually seen; never looks at the answer key.
- Never spends a try itself; M1 enforces the 20-try budget.
- Same seed gives the same decisions, and runs can resume exactly.
- Plain rules, no AI model, so no API cost.

---

## Results

Two studies: the component study below (M3's parts with exploration and
routing off), and M3's assigned [full-agent ablations](#full-agent-ablations-m3s-assigned-ablations)
against M1's frozen agent.

### Component study

All 72 runs: 4 versions × 6 practice ("dev") systems × 3 repeats (seeds 17,
29, 43), 20 tries each, on one PC (AMD Ryzen 7 9700X, CPU only), all versions
with the same code, simulator and memory. All 72 finished on the first
attempt. The reference reproduced M1's earlier recorded numbers exactly in all
18 pairs, so the comparison is fair.

| Version | What it tests | Found per run (mSUN@20) | Discovery-curve area (AUDC) |
| --- | --- | --- | --- |
| `m1_baseline` | M1's reference: M1's own planner, self-correction off | 5.00 ± 4.41 | 39.4 |
| `m3_full` | M3 planner and self-correction on | **6.50 ± 2.60** | **62.8** |
| `m3_planning_off` | Planning off (self-correction on) | 5.11 ± 2.99 | 49.2 |
| `m3_self_correction_off` | Self-correction off (planner on) | 5.83 ± 3.13 | 58.3 |

Compared run by run (same system and seed):

| Comparison | Change per run | Better / same / worse (of 18) |
| --- | --- | --- |
| M3 vs reference | +1.50 | 9 / 3 / 6 |
| Effect of planning | +1.39 | 12 / 1 / 5 |
| Effect of self-correction | +0.67 | 7 / 10 / 1 |

**What it means**

- **Hard systems improve, easy ones get worse.** On the three systems where the
  reference finds almost nothing, M3 goes from 1.1 to 6.7 per run; on the three
  where it does well, M3 drops from 8.9 to 6.3.
- **Why:** the planner spends most tries on the pairs (3–5 of its 5 area
  visits) and at most 2 on the three-element mix. That wins when the good
  materials are in a pair (gold–potassium–terbium: 0.3 → 10.0) and loses when
  they are in the mix (hafnium–nickel–zirconium: 11.7 → 6.0).
- **Self-correction works:** it changed course 16 times, each after 6 empty
  tries. Clearest case: cobalt–magnesium–sodium, 3 → 13 materials across its
  three runs.
- **Cost:** no AI tokens, the same 20 tries; about 698 s per run against 542 s
  for the reference on this PC.
- **Limits:** 18 pairs is a small sample, and only practice systems were used,
  as the protocol requires.

Full tables and the reasoning: [report/M3_RESULTS.md](report/M3_RESULTS.md).

**On M1's frozen agent.** This component study (`m3_full`, `m3_planning_off`,
`m3_self_correction_off`, 54 runs) was re-run on the frozen tag
`m1-freeze-20261025` and reproduces the numbers above exactly, run by run.

### Full-agent ablations (M3's assigned ablations)

The project's task split gives M3 "two ablations: planning off;
self-correction off" against M1's reference, which is the frozen `m1_full`
(all five parts on). Each ablation switches off exactly one M3 part and leaves
memory, exploration and tool routing on. 36 runs, same systems, seeds, budget
and evaluator as M1's 18 reference runs:

| Version | Found per run (mSUN@20) | AUDC | `m1_full` better / same / worse | Sign test |
| --- | --- | --- | --- | --- |
| `m1_full` (M1's reference) | 10.00 | 88.1 | – | – |
| `planning_off` | 5.28 | 51.5 | 15 / 2 / 1 | p = 0.0005 |
| `self_correction_off` | 9.50 | 79.6 | 8 / 2 / 8 | p = 1.0 |

- **Planning is the larger effect.** Without it the full agent finds about half
  as many materials, and it is lower on all six systems. The weakness seen in
  the component study (losing on hafnium–nickel–zirconium) does not appear
  here: 9.3 with planning against 6.7 without.
- **Self-correction shows no measurable effect** inside the full agent. Its one
  consistent difference is cobalt–magnesium–sodium (9.0 with it, 5.7
  without), the same system where it helped in the component study.

All 90 frozen-agent result folders are in
[results/frozen_20261025/](results/frozen_20261025/).

### The bug found along the way

The first full set of runs showed **identical** results with self-correction
on and off, in all 18 pairs. The cause: the simulator marks *every* new
structure as "newly discovered", even unstable ones, and M3 had read that as
progress, so it never thought it was stuck (360 of 360 tries were marked new;
only 96 were stable). M3 now counts only **stable** new materials as progress.
All runs were redone with the fix. The summary script only accepts runs made
with the current M3 code (it checks the file's fingerprint), so old runs
cannot slip in; the old results remain in the git history (commit `e1a40d8`).

---

## Files

### Start here

| File | What it is |
| --- | --- |
| `README.md` | This page |
| [HANDOVER.md](HANDOVER.md) | What each teammate receives and needs to know |
| [DESIGN.md](DESIGN.md) | One-page design agreed with M1 |
| [EXPERIMENT_RUNBOOK.md](EXPERIMENT_RUNBOOK.md) | Step by step: set up a computer, run the 72-run component study, and run the 90 frozen-agent runs |

### The code (`integration/`)

M3's code lives here, laid out exactly where it goes in M1's folder.
`install.py` copies it in. The four M3-owned files are identical to the
versions in M1's frozen agent (tag `m1-freeze-20261025`). The four M1-owned
files are snapshots of M3's original edits; M1 has since added M4's and M5's
parts to them, so M1's own copies are the current versions. `install.py`
shows these as `merged` and never overwrites them.

| File | What it is |
| --- | --- |
| `integration/M1/MADE/src/made/agents/m3_planning.py` | **The M3 code:** the planner and self-correction |
| `integration/M1/MADE/configs/agent/planner/m3_research.yaml` | Planner settings |
| `integration/M1/MADE/configs/agent/self_correction_policy/m3_stuck_replan.yaml` | Self-correction settings |
| `integration/M1/MADE/tests/test_m3_planning.py` | 23 tests of the M3 code, no API key needed |
| `integration/M1/MADE/configs/agent/m1_integrated.yaml` | M1's agent config with M3 switched in (M1-owned; M3 edited it) |
| `integration/M1/run_experiment.py` | M1's experiment script with the three M3 test versions added (M1-owned; M3 edited it) |
| `integration/M1/tests/test_protocol.py` | M1's protocol tests, plus tests for the M3 versions (M1-owned; M3 edited it) |
| `integration/M1/EXPERIMENT_PROTOCOL.md` | M1's protocol notes, plus the M3 versions (M1-owned; M3 edited it) |

### Tools

| File | What it does |
| --- | --- |
| [install.py](install.py) | Checks that M3 is in M1's folder; `--install` puts it there. It never overwrites an M1 file that M1 has changed. |
| [run_ablations.py](run_ablations.py) | Runs the test versions (by default the 72-run component study; `--methods` picks others, such as the full-agent ablations). Safe to stop and restart; failed runs are kept and retried. |
| [summarize_ablations.py](summarize_ablations.py) | Turns finished runs into the result tables and `report/M3_RESULTS.md` |
| `examples/m3_demo.py` | Short demo with made-up results, showing the planner and course changes |
| `tests/test_m3_tools.py` | 17 tests for the three tools above |
| `ruff.toml` | Code-style rules (same as MADE's) |
| [test_results.txt](test_results.txt) | Recorded output of the checks |

### Results and report

| File | What it is | For |
| --- | --- | --- |
| [results/m3_ablation_runs.csv](results/m3_ablation_runs.csv) | One row per run (72) | M2 |
| [results/m3_ablation_summary.csv](results/m3_ablation_summary.csv) | One row per version | M2 |
| [results/frozen_20261025/](results/frozen_20261025/) | Complete result folders of all 90 frozen-agent runs (full-agent ablations and component study), plus the Chemeleon checksum receipt | M1, M2, M6 |
| [report/M3_RESULTS.md](report/M3_RESULTS.md) | Results tables and explanation | M2, M6 |
| [report/M3_METHOD.md](report/M3_METHOD.md) | Method text for the group report | M6 |

### Evidence

| Folder | What it shows |
| --- | --- |
| [evidence/20261021-dev-ablations/](evidence/20261021-dev-ablations/) | The 72 real runs: run list, every planner and course-change log line, one traced example |
| [evidence/synthetic-demo/](evidence/synthetic-demo/) | Output of the made-up-results demo |

---

## Checking and reproducing

Run from `M1/MADE`, after the setup in
[EXPERIMENT_RUNBOOK.md](EXPERIMENT_RUNBOOK.md):

```bash
uv run python ../../M3/install.py                 # every line "ok" or "merged"
PYTHONPATH="../../M4/src" uv run pytest -q tests/test_m1_integrated.py tests/test_m3_planning.py
uv run pytest -q ../../M3/tests -o addopts=''
uv run python ../../M3/run_ablations.py --dry-run  # lists the runs still to do
```

Last checked on M1's frozen tag `m1-freeze-20261025` (`ae7fe81`): M1 and M3
tests 41 passed; M3 tool tests 17 passed; M1 protocol tests 8 passed; style
checks pass; all 90 frozen-agent runs complete. One M4 test
(`test_config_constructs_real_agent`) fails because of an M5 config setting
that only works inside a real run; it is not caused by M3 (see HANDOVER.md).
Full output: [test_results.txt](test_results.txt).

---

## Glossary

| Plain word used here | Technical term | Meaning |
| --- | --- | --- |
| try | oracle query | One question to the simulator; 20 per run |
| simulator | oracle (ORB v3) | Checks whether a candidate material is stable |
| recipe | composition | Which elements, in what amounts |
| pair / three-element mix | binary edge / ternary interior | The four search areas of a three-element system |
| area | sub-goal | One of those four areas |
| stable material | on or near the convex hull | A material that could actually exist |
| found per run | mSUN@20 | Stable, unique, new materials found in 20 tries |
| discovery-curve area | AUDC | How early the finds come; higher is better |
| reference | `m1_baseline` | M1's agent without M3, used for comparison |
| test version | ablation | The agent with one part switched off |
| repeat | seed | The same test run with a different random start |
| practice systems | dev split | The six systems we may tune on |
