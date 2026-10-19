# M3 handover

## Scope

M3 delivers the research planner and the stuck-detection/re-planning policy.
They plug into M1's existing `planner` and `self_correction_policy` slots.
Like `M2/` and `M4/`, only `M3/` is published on `main`, and M1's files are
unchanged. `M3/integration/` holds everything M3 adds to or changes in M1.
`python M3/install.py --install` puts it into M1: the module is wired into
`m1_integrated.yaml`, and `M1/run_experiment.py` gains the M3 protocol methods.

## Deliverables

| Recipient | Deliverable | Due (Oct 2026) | Status |
| --- | --- | --- | --- |
| M1 | One-page design and slot interface (`DESIGN.md`) | 19–20 | Ready; needs M1 sign-off |
| M1 | Code, Hydra configs, tests (`M3/integration/`, installed with `M3/install.py`) | 24 | On `main`; M1 decides when to install |
| M6 | Method text (`report/M3_METHOD.md`) and draft slides (`report/M3_Method_Draft.pptx`) | 24 | Ready to send |
| M2 | Ablation results (`results/*.csv`, `report/M3_RESULTS.md`) | 27 | Waiting on Materials Project runs |
| M6 | Results text and final slides | 27 | Generated once runs finish; interpretation by hand |

## Notes for teammates

- **M1:**
  - `install.py` replaces your four edited files only if they are unchanged
    since `fcaaccc`. Otherwise it stops and names the file to merge by hand.
  - The default planner is still `diversity`, so the 18 `m1_baseline` runs stay
    valid.
  - `run_experiment.py` adds `agent/planner=m3_research` to every plug-in
    method, and adds the `m3_full`, `m3_planning_off` and
    `m3_self_correction_off` methods.
- **M4:** the M3 planner actually reads `context["m1_memory"]` in its review.
  This is the planner consumption M4's notes list as pending. M4's memory
  ablation becomes meaningful when run with the M3 planner. A test that uses
  the real `M4MemoryManager` shows memory reaching the decision when on and
  absent when off.
- **M5:** exploration runs after M3's self-correction and receives its revised
  plan. No conflicts are expected; both are capped by M1.
- **M2:** M2's `m2/tool-routing-evaluation` branch edits `m1_integrated.yaml`
  in different lines from M3; the two test-merged cleanly.

## Validation done (19 Oct, Windows, CPU)

All commands are run from `M1/MADE`; see `test_results.txt`.

- M1 and M3 tests: 37 passed, 2 skipped. With M4 on the path, the M3 tests
  pass 22/22.
- M1 protocol tests (including the new M3 methods): 7 passed. M3 tool tests:
  7 passed.
- Ruff lint and format pass.
- Smoke episodes pass: M1's standard one, and an M3 run with planner plus
  self-correction (see `evidence/synthetic-smoke/`).
- The synthetic demo shows reviews and re-plans firing (see
  `evidence/synthetic-demo/`).

## Not yet done

- No official Materials Project / ORB runs of the `m3_*` methods. These need a
  Materials Project API key in `M1/MADE/.env`; follow `EXPERIMENT_RUNBOOK.md`.
- There is no performance claim until those runs exist.
