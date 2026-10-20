# M3 handover

## Scope

M3 delivers the research planner and the stuck-detection/re-planning policy.
They plug into M1's existing `planner` and `self_correction_policy` slots.
`M3/integration/` holds everything M3 adds to or changes in M1. M1 integrated
it on `main` on 20 Oct (`2fcc214`). `python M3/install.py` checks that M3 is
still in place.

## Deliverables

| Recipient | Deliverable | Due (Oct 2026) | Status |
| --- | --- | --- | --- |
| M1 | One-page design and slot interface (`DESIGN.md`) | 19–20 | Signed off by M1 (20 Oct) |
| M1 | Code, Hydra configs, tests (`M3/integration/`) | 24 | Integrated by M1 (20 Oct, `2fcc214`) |
| M6 | Method text (`report/M3_METHOD.md`) and draft slides (`report/M3_Method_Draft.pptx`) | 24 | Received by M6 (20 Oct) |
| M2, M6 | Ablation CSVs (`results/*.csv`) and results text (`report/M3_RESULTS.md`) | 27 | Requested by M6; runs scheduled 26–27 Oct |
| M6 | Final slides | 27 | After the runs |

## Notes for teammates

- **M1:**
  - Your integrated `m1_integrated.yaml` merges M4's memory manager and M5's
    exploration policy with M3's lines. `install.py` now reports this as
    `merged` (M3's edit kept) instead of a mismatch. This was a too-strict check
    on M3's side, now fixed.
  - The default planner is still `diversity`. `run_experiment.py` adds
    `agent/planner=m3_research` to every plug-in method, plus the `m3_full`,
    `m3_planning_off` and `m3_self_correction_off` methods.
- **M6:**
  - The M3 results compare `m3_full` with an `m1_baseline` re-run under the
    current configuration, with M4 memory on in both. M1's 19 Oct baseline
    predates M4 memory, so it is listed for context only and never paired.
  - Per `PROTOCOL_ADOPTION.md` §5, these go in the "component vs M1
    reference" table, not the frozen agent's ablation table. `M3_RESULTS.md`
    titles its table that way.
  - **Planner in the frozen agent (your question to M1):** on current `main`,
    `run_experiment.py` already gives `m1_full` and every `*_off` ablation,
    including `memory_off`, the M3 planner (`agent/planner=m3_research`). Only
    `m1_baseline` keeps `diversity`. The memory ablation therefore runs with a
    planner that reads `m1_memory`. M1 confirms this at the 25 Oct freeze.
  - M3 runs only on dev systems. `run_ablations.py` refuses any other system,
    and the `m3_*` methods are not part of the check/hidden allow-list.
- **M4:** the M3 planner reads `context["m1_memory"]` in its review, which is
  the planner consumption the memory ablation needs. M4 confirmed on 20 Oct
  that M3's decision trace uses memory when it is on and has none when it is
  off. Every M3 run sets its own `M4_RUN_ID`, as `M4/integration/ADOPTION.md`
  requires. If M1 applies M4's capture overrides before the runs, they apply
  equally to every M3 arm, because all arms run from the same revision.
- **M5:** exploration runs after M3's self-correction and receives its revised
  plan. M3's ablation methods keep exploration off.
- **M2:** M3's ablations keep tool routing off and use the default generator.

## Validation

All commands are run from `M1/MADE`; see `test_results.txt`.

**On 20 Oct, against `main` with M1's integration (`bc97609`):**

- `install.py` reports seven files `ok` and `m1_integrated.yaml` as `merged`.
- M1, M3, M4 and M5 tests (with M4 on the path): 54 passed.
- M1 protocol tests: 7 passed.
- M3 tool tests: 12 passed.
- Ruff passes.
- The demo runs.

**On 19 Oct:**

- Smoke episodes pass: M1's standard one, and an M3 run with planner plus
  self-correction (`evidence/synthetic-smoke/`).
- The synthetic demo shows reviews and re-plans (`evidence/synthetic-demo/`).

## Not yet done

- No official Materials Project / ORB runs yet: 72 runs (re-run baseline plus
  three M3 methods). They need a Materials Project key in `M1/MADE/.env` and M4
  installed; follow `EXPERIMENT_RUNBOOK.md`.
- There is no performance claim until those runs exist.
