# M6 Work Log

Member 6: experiment design, generalization and report lead.
Entries are dated (Singapore time) and record what was done, what was verified and
what is still open. Used for the individual report.

## 2026-10-19

- Read the course brief, `README.md`, `M1/EXPERIMENT_PROTOCOL.md`, `M1/protocol/`,
  `M1/run_experiment.py`, `M2/STATUS.md`, `M2/METHODS_AND_M6_HANDOFF.md`,
  `M2/evaluate.py`, `M2/run_baselines.py`, `M4/M1_STATUS.md`, `M5/README.md` and
  `M5/DESIGN.md` at team revision `73dc953`.
- Repo state at that revision:
  - Protocol v1 (M1): 6 dev systems, 4 check systems, seeds 17/29/43, B=20, ORB v3
    conservative oracle on CPU.
  - `M1/run_experiment.py`, `M2/run_baselines.py` and `M2/evaluate.py` accept only
    `--split dev|check`. There is no hidden-test split.
  - Accepted baseline units: 2 of 36 dev units (Random and Chemeleon, Mg-Sn-Sr, seed
    17). No check-set units exist.
  - M5 has more than a design doc now: `M5/` has the UCB exploration policy, 10
    tests and an installer (commit `73dc953`). It is not integrated into M1 yet.
- Decided to adopt M1 protocol v1 unchanged instead of writing a new protocol. Added
  the "check set = frozen agent only" rule and a proposal for the hidden split
  (`PROTOCOL_ADOPTION.md`).
- Found that `M2/evaluate.py` only accepts runs that have `m2_metrics_history.json`.
  Only `M2/run_baselines.py` writes that file; it wraps `M1/run_experiment.py`
  without changing it. So check/hidden runs must go through that wrapper, or they
  cannot be scored. `run_check_baselines.sh` uses it.
- Found that `M2/evaluate.py` rejects any run whose recorded `protocol_settings`
  differ from the current `protocol_v1.yaml`. Adding the hidden split must not edit
  that YAML, or all 2 accepted units (and every later one) become `protocol_mismatch`.
  Proposed a separate `hidden_systems.json` instead.
- Wrote the compute plan. The 12 Chemeleon check units are about 53 h of CPU and
  must start now, on GitHub Actions, in parallel.
- Wrote `run_check_baselines.sh` (dry-run by default, next free attempt only, skips
  completed units) and `generalization.py` (dev vs held-out table + chart, missing
  runs explicit). Tested `generalization.py` on
  `M2/verification/20261019-chemeleon-recovery/`.
- Drafted the report template, the 10-minute slide outline, the requirements
  checklist, the TA email and the group message.
- No benchmark job was launched.

### Open

- TA: frozen commit, base model, B, hidden-test release date, whether 1 seed is
  acceptable on held-out systems.
- M1: hidden split in the runner; freeze revision on 25 Oct.
- M2: check-split workflow run for the 24 check baseline units.
- M5: integration ETA into `m1_integrated.yaml`.

## 2026-10-20

- PR #3 (M6 folder) and PR #4 (repo cleanup) are merged into `main`. Personal drafts
  (messages, report and slide templates, sample outputs) are kept out of the repo.
  Only project files are committed.
- Checked M6 on `main` (`221e159`): 9 tests pass, Ruff is clean, and the
  `run_check_baselines.sh` dry run lists all 24 check units (0 completed).
- Read the team updates from M3, M4 and M5 and changed the protocol docs to match:
  - M3 adds `m3_full`, `m3_planning_off` and `m3_self_correction_off` to
    `run_experiment.py` through `M3/install.py`. The check/hidden rule now names the
    three allowed methods, and the runner proposal uses an allow-list
    (`PROTOCOL_ADOPTION.md` §3, §4).
  - M3's ablations compare with `m1_baseline`, not `m1_full`. Added an
    ablation-reference rule: those results go in a separate table from the
    component ablation (`PROTOCOL_ADOPTION.md` §5).
  - M3's planner reads `m1_memory` and the default planner does not, so the memory
    ablation depends on which planner M1 freezes.
  - M5 asked M4 for rejected/error events before 26 Oct. Without them, the
    wasteful-exploration example uses evaluated queries only.
- Received M3's method text and slides (`M3/report/M3_METHOD.md`,
  `M3/report/M3_Method_Draft.pptx`).
- No benchmark job was launched.

### Open

- Send the group message (M2: dispatch Chemeleon × check) and the TA email.
- M1: allow-list for check/hidden methods, hidden split, which planner gets frozen.
- M4: rejected/error event capture before 26 Oct.
- Collect M1, M2, M4 and M5 method text by 24 Oct.

### 2026-10-20 (afternoon)

- Checked `main` at `60d2c2a` against the team's messages:
  - M1: frozen `m1_full` uses M3's planner (confirmed in `run_experiment.py`). The
    held-out allow-list M1 described is **not on main yet**. M5's `log_path` and
    M4's capture overrides are not in `m1_integrated.yaml` yet.
  - M2: dev Random 18/18 accepted; the 17 missing dev Chemeleon units have been
    running on GitHub since 15:24. M2's delivery scope says check/hidden belongs to
    M6, so nobody is running Chemeleon × check yet.
  - M3 labels its results "vs M1 reference" and refuses non-dev systems. M4's
    rejected/error capture and M5's decision-log sidecar are on main.
- Updated `REQUIREMENTS_CHECKLIST.md` and `COMPUTE_PLAN.md` to match.
- Started setting up the MADE environment locally (`uv sync --locked`) for the
  Random × check runs.

### 2026-10-20 (evening): Random × check set

- Ran Random on all 12 check units on this laptop (MacBook Air, arm64, CPU) with
  `run_check_baselines.sh`. **12/12 accepted** by `M2/evaluate.py --split check`.
  mSUN@20 = 5.583 ± 0.629, AUDC = 60.79 ± 0.51. Per system: Ga-Ho-Lu 7.33,
  Al-Li-V 2.33, Al-V-Zn 10.00, Co-Pd-Tl 2.67.
- Dev vs check for Random: 4.056 → 5.583 mSUN@20 (+1.53, +37.7 %). The check systems
  are easier for an untuned baseline, so the agent's held-out result must be read
  against the baselines' own gap.
- Local runs are fast: median 203 s per unit (GitHub runner: 953 s).
- Problems and fixes, all failed attempts kept (`results/20261020-check-random/README.md`):
  - First ORB checkpoint download stalled at 56 MB → stopped, downloaded it separately.
  - Co-Pd-Tl/43 hung twice after finishing, while kaleido closed the system Brave
    browser it used for chart export. Fixed by installing kaleido's own headless
    Chrome for Testing and setting `BROWSER_PATH`; attempt 03 accepted.
  - The laptop slept and ran low on battery (10 %) during the rerun, which slowed it.
    Long local runs need the charger plugged in.
- Fixed `generalization.py` to count zero-baseline AF/EF pairs (Random found 0 on
  Co-Dy-W/17 in dev, which gives EF = 0 under MADE's convention).
- Raw runs preserved as `results/20261020-check-random/raw_artifact.zip` (checked: no
  API key inside).

## 2026-10-21

- Received M2's final handover: 36/36 dev baselines validated, slides
  (`M2/report/M2_Method_and_Dev_Baselines_20261021_36of36.pptx`) and notes. Re-ran their
  final report through `generalization.py`: same means (Random 4.06 ± 0.63, Chemeleon
  6.94 ± 1.11 mSUN@20). Flagged that Chemeleon's EF vs Random (7.53 ± 9.48) is driven by
  one zero-baseline pair (Co-Dy-W/17, EF capped at 100); without it, mean 2.09,
  median 1.5 over 17 pairs.
- Received M5's method text (`M5/report/M5_METHOD.md`). Notes for the report:
  - α₀ = 0.8 was chosen from one dev dry-run pair (Mg-Sn-Sr/17, AUDC 66.5 → 84.5).
    Tuning on dev is allowed; the report must say it rests on one unit, which is also
    one of the 18 dev evaluation units.
  - Limitation: with M3's one-composition-per-step plans, exploration gets at most one
    slot per step.
  - The method text still says "Defaults α₀ = 0.5" in the algorithm section; asked M5
    to align it with 0.8.
  - The dry-run raw outputs are not in the repo, so its numbers and the suggested
    wasteful-exploration example (α₀ = 0.5, steps 10–15) can't be cited yet.
- M4 ran one dev Memory ON/OFF pilot (Mg-Sn-Sr/17): ON 7 vs OFF 8 mSUN@20. Not the
  final ablation; M3 has since fixed `_review` to count only new stable phases. The ON
  run staying in the Sn–Sr binary is a possible over-exploitation illustration.
- M1 has wired M4's proposal-event capture and M5's decision log into
  `m1_integrated.yaml`, so the frozen agent will produce failure-analysis logs.

## 2026-10-27

- Read the team's frozen results. M1 froze the agent on 25 Oct (`m1-freeze-20261025`);
  M2 validated 198 dev runs (PR #6, unmerged): Full 10.00 ± 0.88, Chemeleon 6.94,
  Random 4.06 mSUN@20; ablations (Full − off): planning +4.72, routing +2.28,
  memory +0.89, self-correction +0.50, exploration +0.33.
- Started the held-out check runs on this laptop from a separate worktree at the
  frozen tag (`../gp6-freeze`), with the Chemeleon checkpoints from Figshare (SHA256
  matches M1's record): frozen m1_full × 12 and Chemeleon × 12 (two parallel streams).
- First launch problems, all attempts kept:
  - m1_full needs `M4/src` on `PYTHONPATH` (as in M2's frozen runs); the first agent
    attempts failed on import.
  - Two Chemeleon runs started in the same second shared a Hydra run folder and
    corrupted its `config.yaml`. Stopped both, moved the folder out of the scan path,
    and restarted all streams with a launch lock that keeps starts ≥ 5 s apart.
- Built the group deck (14 slides, 9:55, speaker notes) from all members' material.
  Corrected two outdated numbers in M5's slide text against M2's validated data
  (Mg-Sn-Sr exploration −1.0, not −2.0; per-run SD 5.0 → 2.8) and used M2's audited
  failure-case wording. The generalization slide waits for the check runs.

### 2026-10-27 (evening): held-out runs, bare minimum

- Overnight runs were not possible, so held-out was cut to the protocol's 1-seed
  fallback. Chemeleon on check was stopped (~2.5 h per unit here) and is reported as
  not run. Frozen agent on check, seed 17: 4/4 completed, ~3–12 min each.
- Scored with `M2/evaluate.py --split check`: agent 14.0 mSUN@20 (8, 13, 19, 16) vs
  Random 6.25 (8, 1, 13, 3) on seed 17. Dev seed 17: agent 9.0, Random 3.33. The
  agent's lead over Random grows from +5.7 to +7.8 on held-out systems.
- M2's wrapper exits after the run because it cannot resolve the frozen config's
  `${hydra:…}` interpolation; added `M6/package_check_evidence.py` (reuses M1's
  resolver) to attach the Hydra configs, resolved config and component logs. The
  live per-query history is kept as captured.
- Deck generalization and conclusions slides updated with these numbers.

## 2026-10-28

- Ran Chemeleon on the check set, seed 17 (4 runs in parallel, staggered starts,
  03:04–06:28 UTC, ~3.4 h each on the laptop). All 4 completed with full histories.
- Scored all check runs together: agent 14.00, Chemeleon 7.25, Random 6.25 mSUN@20
  (seed 17). The agent beats Chemeleon on 3 of 4 systems (not Ga-Ho-Lu: 8 vs 10).
- Generalization, seed 17 both sides: lead over Chemeleon grows from +2.3 (dev) to
  +6.8 (check); over Random from +5.7 to +7.8.
- Built the deck as an editable .pptx for Google Slides (local, not committed) and the
  report as a Google Doc for group review.
