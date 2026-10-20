# M1 Experiment Protocol v1

This is the group default protocol authored by M1. All group comparisons should use these values unless an explicit course-provided frozen setting conflicts; in that case the course setting takes precedence and M1 will issue a versioned amendment. Do not silently change settings between methods.

## Fixed benchmark settings

| Setting | M1 decision |
| --- | --- |
| MADE upstream revision | `bffda0c9a1fa1904b35c0ef67b455881c975df86` |
| Runner / evaluator | Official `scripts/run_benchmark.py`; do not change oracle, environment, validity checks, or evaluator |
| Oracle / scientific base model | ORB v3 conservative infinite model, `orb-v3-conservative-inf-omat` |
| Oracle inference | Relax structures with FIRE; `fmax=0.02`, max 500 steps, relax unit cell; `device=cpu` for the shared local protocol |
| Materials Project query | `thermo_types=[GGA_GGA+U]`; use the frozen system lists in `protocol/`; preserve each run's `phase_diagram_gt` and resolved config |
| Environment | SMACT filter on; max stoichiometry 20; stability tolerance 0.1 eV/atom; near-stable entries included; official structure matcher defaults |
| Oracle budget | `B=20` environment queries per system per seed, identical for every method |
| Repeats | Three independent process runs with seeds `17`, `29`, `43`; each process runs one episode (`experiment.num_episodes=1`) |
| Primary metric | mSUN@20: official `final/novelty_stable_unique_novel_count`; also report the fraction |
| Secondary metrics | Official AUDC, AF, EF, discovery curve, validity, and total oracle queries |
| Cost | Record model/API tokens and dollars (zero for ORB inference), Materials Project calls if available, wall time, and machine; report compute hardware separately |
| Logging | W&B off by default; raw trajectories, resolved configs, and summaries remain under `M1/MADE/results/` |

The `B=20` query budget is a team protocol choice set by the M1 lead for v1; it
is not represented as a TA-mandated value. Apply it uniformly across methods.
Any course-published requirement that conflicts with it requires a versioned
protocol amendment before affected comparisons are run.

The upstream MADE snapshot is currently at the revision above. M1's integration code is maintained in this workspace and must be included in the shared release/freeze revision before the reference run. Do not describe this upstream hash alone as the full agent revision.

## Running one protocol unit

Run from `M1/MADE` after `uv sync` and after placing the Materials Project key in the ignored local `.env`:

```bash
uv run python ../run_experiment.py --method random_generator_baseline --split dev --system Mg-Sn-Sr --seed 17
```

The same entry point accepts every method in the table, a system present in the selected split, and one of the three fixed seeds. It invokes the official benchmark runner for exactly one system and seed, initializes Python/NumPy/PyTorch random states, forces CPU inference, applies the local Modal-volume workaround in process, and writes to `results/protocol_v1/<method>/<split>/<system>/seed_<seed>/attempt_01/`. Existing attempts are never overwritten; rerun a failed seed with `--attempt 2` and retain the original failure. `m1_full` and its component ablations deliberately fail fast until all enabled plug-ins are configured; this prevents an incomplete no-op from being reported as the full method. Ablation commands use the same switch-on reference and toggle only the named component.

For local laptop execution, run systems serially. Example full development sweep (after plug-ins are installed):

```bash
for SYSTEM in Mg-Sn-Sr Au-K-Tb Co-Mg-Na Hf-Ni-Zr Co-Dy-W Ga-Pt-Tm; do
  for SEED in 17 29 43; do
    uv run python ../run_experiment.py --method m1_full --split dev --system "$SYSTEM" --seed "$SEED"
  done
done
```

Run corresponding commands for both required baselines. Run ablations on the development systems only; run the three core methods on the public check list. Do not run an ablation on the check or teaching-team held-out systems.

After a split is complete, validate it from `M1/MADE`:

```bash
uv run python ../validate_protocol_results.py --split dev
```

This checks that every required method/system/seed has one complete episode, uses all 20 queries, and has an identical serialized ground-truth snapshot for a given system across methods and repeats.

## Systems and split

The source is MADE's committed `systems_10_mp_20/systems_ternary_n10_maxatoms20_intermetallic_smact.json`, with order preserved. The first six systems are the development/tuning set; the last four are a public check set held out from policy tuning. The exact lists are in `protocol/dev_systems.json` and `protocol/check_systems.json`.

This public check set is not the course's hidden test set. If the teaching team supplies held-out systems, run the frozen reference and required baselines on them without tuning and use that result for the held-out comparison. If no held-out set is released, report the limitation; do not relabel the public check set as hidden test.

Following M6's held-out rule, only `m1_full`, Random, and Chemeleon may run on
check/hidden systems. The untuned Random and Chemeleon baselines may run before
the freeze; `m1_full` may run on check only after the 25 Oct freeze. Do not
change the agent after inspecting check results. Add a hidden split only after
the teaching team publishes its systems.

## Methods

Until M2/M3/M5 plug-ins are merged, `m1_baseline` is the runnable M1 reference:
planning and bounded memory are enabled, while reflection/self-correction,
exploration, and tool routing are disabled. It must not be reported as the
plugin-complete `m1_full` method.

Run the following methods with the same systems, oracle, evaluator, budget, and seeds:

| Method | Configuration |
| --- | --- |
| M1 full | M1 integrated agent; planning, bounded memory, M3 reflection, M5 exploration, and M2 routing on; default generator, SMACT filter, and scorer unless the routed tool set is frozen |
| Random baseline | Official `random_generator_baseline` config |
| Chemeleon baseline | Official `chemeleon_generative_baseline` config; force its inference device to CPU for this protocol |
| Planning ablation | M1 full with `enable_planning=false` |
| Memory ablation | M1 full with `enable_memory=false` |
| Self-correction ablation | M1 full with `enable_reflection=false` |
| Exploration ablation | M1 full with `enable_exploration=false` |
| Tool-routing ablation | M1 full with `enable_tool_routing=false` |
| M3 full (`m3_full`) | `m1_baseline` with the M3 planner (`agent/planner=m3_research`) and M3 self-correction on |
| M3 planning ablation (`m3_planning_off`) | `m3_full` with `enable_planning=false` |
| M3 self-correction ablation (`m3_self_correction_off`) | `m3_full` with `enable_reflection=false` |

`m1_baseline` keeps MADE's diversity planner, which its recorded runs used. Every
plug-in method above (M1 full, its ablations and the `m3_*` methods) plans with
the M3 planner. The `m3_*` methods measure M3 against `m1_baseline` on the
development systems, so they do not wait for the plugin-complete `m1_full`.
The frozen `m1_full` agent will use the M3 planner so its M4 memory records are
consumed during proposal decisions; `m1_baseline` remains the historical
diversity-planner reference.

Run the three required comparisons (M1 full and both baselines) on development and public-check systems. Run component ablations on development systems only. Each seed is a separate one-episode invocation, not three episodes under a single seed. For a defensible paired comparison, every method uses the same seed list. If a component is not delivered by its owner, mark that method unavailable; do not claim its switch-on result represents that component.

## Reporting and reproducibility

- Report mean and standard deviation over the three seeds, with the individual seed values. Do not hide failed runs; record the failure and rerun under the same seed only after recording the original failure.
- mSUN@B is the main endpoint. Report the discovery curve and official AUDC/AF/EF alongside oracle calls, LLM/API cost, wall time, and hardware.
- Save the exact command, protocol version, upstream MADE revision, M1 release revision, resolved Hydra config, seed, system, raw trajectory, final metrics, and run status for every invocation.
- Verify that the serialized ground-truth phase diagram is identical across methods for a given system. If it differs, stop aggregation and flag the data revision mismatch.
- Preserve the official evaluator and interaction boundary. The agent may only use `env.get_state()` and prior queried observations; never inspect `phase_diagram_gt`, held-out labels, or evaluator-only state for decisions.
- Do not commit Materials Project/API keys. Dataset retrieval requires `MATERIALS_PROJECT_API_KEY`; ORB evaluation itself uses no paid LLM API.

## Run-count estimate

This protocol requires 3 methods x 10 public systems x 3 seeds plus 5 ablations x 6 development systems x 3 seeds = 180 episodes, or at most 3,600 oracle queries at B=20, before failures/retries. Held-out course evaluation is additional. If compute cannot support this, reduce the number of systems uniformly for every method before starting, record a new protocol version, and never reduce only one method's budget.
