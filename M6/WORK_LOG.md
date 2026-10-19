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
