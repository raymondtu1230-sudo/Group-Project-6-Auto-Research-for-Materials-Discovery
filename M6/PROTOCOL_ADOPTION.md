# M6 Protocol Adoption

Status: adopted 2026-10-19 at team revision `73dc953`; updated 2026-10-20 for M3's
added methods and the ablation reference (sections 3 and 5). Owner: M6.

## 1. Adoption

M6 adopts **M1 protocol v1** (`M1/EXPERIMENT_PROTOCOL.md`, `M1/protocol/protocol_v1.yaml`)
unchanged for every result in the report:

| Setting | Value (from M1, not changed here) |
| --- | --- |
| MADE upstream | `bffda0c9a1fa1904b35c0ef67b455881c975df86` |
| Oracle | ORB `orb-v3-conservative-inf-omat`, CPU, FIRE, fmax 0.02, 500 steps, cell relaxation |
| Budget | B = 20 oracle queries per system per seed, same for every method |
| Seeds | 17, 29, 43; one process and one episode per seed |
| Dev (tuning) split | `M1/protocol/dev_systems.json`: Mg-Sn-Sr, Au-K-Tb, Co-Mg-Na, Hf-Ni-Zr, Co-Dy-W, Ga-Pt-Tm |
| Check split | `M1/protocol/check_systems.json`: Ga-Ho-Lu, Al-Li-V, Al-V-Zn, Co-Pd-Tl |
| Primary metric | mSUN@20 = `final/novelty_stable_unique_novel_count` |
| Secondary | official AUDC, AF, EF (MADE implementation), discovery curve, validity, cost |
| Aggregation | `M2/evaluate.py`: equal-weight system mean per seed, then mean and sample SD across seeds |

If the course team publishes frozen settings that differ (commit, base model, B,
systems), the course setting wins. M1 issues a versioned amendment and M6 updates this
file. Results from different protocol versions are never pooled.

## 2. Split roles

| Split | Who runs what | Purpose |
| --- | --- | --- |
| dev | All methods and all ablations, any time | Tuning and component ablation |
| check | **Only** the frozen `m1_full` agent, Random and Chemeleon | Overfitting check before the hidden test |
| hidden | **Only** the frozen `m1_full` agent, Random and Chemeleon | Final held-out ranking (course systems) |

## 3. Rule added by M6: check set = frozen agent only

Protocol v1 already forbids ablations on check/hidden systems. M6 adds:

1. **No agent run on the check set before the freeze.** Only three methods ever run on
   check or hidden systems: the frozen `m1_full`, Random and Chemeleon. `m1_full` runs
   there only at the frozen release revision (planned 25 Oct). Every other method stays on
   dev, including `m1_baseline`, the `*_off` ablations and M3's `m3_full`,
   `m3_planning_off` and `m3_self_correction_off`. Before the freeze, nobody runs the
   agent on check systems or looks at per-system check results for it.
2. **Baselines may run on the check set now.** Random and Chemeleon have nothing to
   tune, so running them early leaks no information into the agent and saves time.
3. **No changes after seeing check results.** If the agent is changed after its check
   run, that is a new freeze with a new revision. The report keeps the first check
   result and the later one. Nothing is cherry-picked.
4. **Check numbers are not tuning signals.** Check results go into the generalization
   section, not into hyperparameter choice, prompts, routing rewards or thresholds.
5. **The check set is never called the hidden test.** If the course does not release
   held-out systems, the report says "public check set (not the course hidden test)"
   everywhere it appears.
6. Every check/hidden run records the frozen revision (`m2_capture.shared_repository_commit`
   in `run_metadata.json`). `generalization.py` refuses to compare dev and held-out
   `m1_full` runs that come from different revisions unless told otherwise.

## 4. How the hidden split will be added (proposal to M1)

M6 does not edit M1's or M2's code. This is the proposed change for M1 (runner) and
M2 (wrapper/evaluator) once the TA releases the systems:

1. **New file, not a YAML edit.** Add `M1/protocol/hidden_systems.json` in the same
   format as `check_systems.json` (list of element lists, TA order preserved). Do **not**
   add a key to `protocol_v1.yaml`: `M2/evaluate.py` rejects any run whose recorded
   `protocol_settings` differ from the current YAML, so editing it would invalidate
   every accepted run.
2. **Accept the split.** Change `choices=("dev", "check")` to
   `("dev", "check", "hidden")` in `M1/run_experiment.py`, `M2/run_baselines.py` and
   `M2/evaluate.py`. Each already resolves systems from `protocol/<split>_systems.json`,
   so nothing else changes. The output path becomes
   `results/protocol_v1/<method>/hidden/<system>/seed_<seed>/attempt_NN/`.
3. **Guard the methods.** In `run_experiment.py`, accept `--split check` and
   `--split hidden` only for `m1_full`, `random_generator_baseline` and
   `chemeleon_generative_baseline`. Use an allow-list, not a deny-list, so that methods
   added later (such as M3's `m3_*`) are blocked automatically. This makes rule 3.1 and
   protocol v1's no-ablation rule enforceable in code.
4. **Record the source.** Commit the TA email or announcement date and the exact
   system list in a short `M1/protocol/HIDDEN_SOURCE.md`. No hidden system is ever
   hard-coded in agent code or config.
5. **Shape check.** `run_experiment.py` currently requires ternary systems. If the TA
   releases non-ternary systems, M1 relaxes that check in the same change and states
   it in the amendment.
6. **If B or other settings change for the hidden test,** that is protocol v2. Dev and
   check runs under v1 are reported separately; the hidden comparison uses only v2 runs.

Until then: `run_check_baselines.sh` has `--split` and `generalization.py` has
`--heldout-split` so both work with `hidden` as soon as the runner accepts it.

## 5. Ablation reference (added 2026-10-20)

Protocol v1 defines a component ablation as the frozen `m1_full` with one switch turned
off, run on dev at the same seeds. Some owners compare their component with
`m1_baseline` instead (M3: `m3_full` vs `m1_baseline`). The report keeps the two apart:

- **Component ablation (report Table 2):** `m1_full` vs `m1_full` with one switch off,
  same frozen revision, paired by system and seed. This answers "what does each
  component add to our final agent?"
- **Component vs M1 reference (separate table, labelled as such):** for example,
  `m3_full` vs `m1_baseline`. This answers "does the component help on top of the plain
  M1 agent?" It is useful evidence, but it is not the final agent's ablation.
- `m1_baseline` results are never reported as "our method" on the leaderboard.

Memory only matters if the planner reads `m1_memory`. M3's planner does, and the default
diversity planner does not. So the memory ablation is only meaningful if the frozen agent
uses M3's planner. M1 decides this at the freeze, and the report says which planner the
frozen agent uses.

## 6. Seeds and repeats on held-out systems

- Default: 3 seeds (17, 29, 43) on check and hidden, like dev.
- Fallback if compute runs out: seed 17 only, for **every** method on that split, decided
  before the run starts and stated in the report and the leaderboard caption. The brief
  allows one run if compute is limited and this is stated. The TA is asked to confirm. With one seed there is no SD; `generalization.py` leaves it blank.
