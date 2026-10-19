# M6 Compute Plan: check and hidden runs

Status: 2026-10-19. Owner: M6. Timings come from the two accepted dev units
(`M2/verification/20261019-chemeleon-recovery/per_run.csv`), both on a GitHub
`ubuntu-latest` CPU runner, Mg-Sn-Sr, seed 17, B=20:

| Method | Measured wall time per unit | Source |
| --- | --- | --- |
| Random (`random_generator_baseline`) | 952.7 s ≈ **16 min** | Mg-Sn-Sr/17 |
| Chemeleon (`chemeleon_generative_baseline`) | 15 767 s ≈ **4.4 h** | Mg-Sn-Sr/17 |
| `m1_baseline` (reference only, not `m1_full`) | 304.9 s ≈ 5 min | `M1/WORK_LOG.md`, local CPU |
| `m1_full` (frozen agent) | **unknown** until 25 Oct freeze | see note below |

These are one measurement each. Other systems may be slower (more structures
to relax, larger cells). Treat every estimate as ±50 %.

`m1_full` note: M2's router can choose Chemeleon. If it does, Chemeleon's
generation step (most of the 4.4 h) is paid inside `m1_full` too. Plan for
**5 min to 4.5 h per unit** until a dev `m1_full` unit has been timed.

## 1. Unit counts

A unit = one method × one system × one seed (one process, one episode, 20 queries).

| Split | Systems | Seeds | Methods | Units | Status |
| --- | --- | --- | --- | --- | --- |
| dev (M2 owns baselines) | 6 | 3 | Random, Chemeleon | 36 | 2 done, 34 missing |
| dev | 6 | 3 | `m1_full` | 18 | after 25 Oct freeze |
| dev ablations (M3/M4/M5/M2) | 6 | 3 | 5 ablations | 90 | after freeze; dev only |
| **check** | 4 | 3 | Random, Chemeleon | **24** | **start now** |
| **check** | 4 | 3 | `m1_full` | **12** | after freeze (25–26 Oct) |
| **hidden** | H (TA) | 3 | Random, Chemeleon, `m1_full` | 9·H | 26–27 Oct, if released |

## 2. Time estimates

### Check set (M6)

| Block | Units | Serial CPU time | Parallel on GitHub Actions |
| --- | --- | --- | --- |
| Random × check | 12 | 12 × 16 min ≈ **3.2 h** | ≈ 20 min |
| Chemeleon × check | 12 | 12 × 4.4 h ≈ **53 h** | ≈ 4.5–5 h (12 jobs at once) |
| `m1_full` × check | 12 | 1 h to 53 h | 5 min to 5 h |

### Hidden set (M6, 26–27 Oct)

The window between the freeze (25 Oct) and the M2 handover (27 Oct) is about 48 h.
For H = 4 systems:

| Block | Units | Serial | Parallel |
| --- | --- | --- | --- |
| Random | 12 | 3.2 h | ≈ 20 min |
| Chemeleon | 12 | 53 h (**does not fit serially**) | ≈ 5 h |
| `m1_full` | 12 | 1–53 h | 5 min–5 h |

Hidden Chemeleon cannot run serially in the window. It must run in parallel.

## 3. What runs where

| Work | Where | Why |
| --- | --- | --- |
| Random × check (12) | Laptop, serial, via `M6/run_check_baselines.sh` (or GitHub) | 3.2 h, fine overnight |
| Chemeleon × check (12) | **GitHub Actions**, 12-job matrix, M2's workflow pattern | 53 h serial is too long for a laptop |
| `m1_full` × check (12) | GitHub Actions at the frozen revision | Same revision for every unit |
| Hidden (all three methods) | GitHub Actions | Only option that fits in ~48 h |
| Offline scoring (`M2/evaluate.py`, `M6/generalization.py`) | Laptop | Seconds, no oracle |

GitHub details:

- M2's workflow (`M2/workflows/m2-real-baselines.yml`, active only on branch
  `m2/tool-routing-evaluation`) reads `dev_systems.json` and runs `--split dev`.
  It needs a `split` input (`dev|check|hidden`) that selects `<split>_systems.json`
  and passes `--split`. M2 owns that file and the Materials Project secret, so M6
  is asking M2 to add the input and dispatch it (see `comms/GROUP_MESSAGE.md`).
- Per-job limit: GitHub-hosted jobs stop at 6 h; M2's step timeout is 330 min. A
  4.4 h Chemeleon unit fits, but a slower system might not. One timeout already
  happened (`M2/verification/20261019-chemeleon-timeout/`). Follow the admission
  rules in `RUNTIME_SAFEGUARDS.md` there. A timed-out unit is kept as a failed
  attempt and rerun with a new attempt number, never overwritten.
- Concurrency: 24 check jobs plus M2's 34 remaining dev jobs exceed the usual
  20-job concurrency limit. Dispatch Chemeleon check first (longest), then Random.

Laptop details (for the Random block):

- Needs `cd M1/MADE && uv sync --locked` and `MATERIALS_PROJECT_API_KEY` in the
  ignored `M1/MADE/.env` (see `M1/REPRODUCE.md`).
- Run systems serially (protocol v1). Keep the machine awake. Record the machine
  name; `run_metadata.json` does this automatically.

## 4. Fallback if compute runs out

Decide **before** starting a split, the same for every method on it:

1. **Hidden: 1 seed (17)** for Random, Chemeleon and `m1_full`. 4 Chemeleon units
   ≈ 4.4 h in parallel or ≈ 18 h serial. The report states "one run per method on
   held-out systems because of compute; no SD" in the leaderboard caption and the
   generalization section. The brief allows one run if this is stated. The TA is
   asked to confirm.
2. **Check: 1 seed** under the same rule if the Chemeleon check matrix fails twice.
3. Never cut only one method's seeds, budget or systems. Never replace a missing
   Chemeleon unit with a Random number. Missing units stay blank in every table.

## 5. Start dates

| Date | Action | Owner |
| --- | --- | --- |
| **19–20 Oct (now)** | Dispatch Chemeleon × check (12 units) on GitHub Actions | M2 dispatches, M6 tracks |
| 20 Oct | Random × check (12 units), laptop or GitHub | M6 |
| 24 Oct | Check baselines complete and scored with `M2/evaluate.py --split check` | M6 |
| 25 Oct | Agent freeze; record revision | M1 |
| 25–26 Oct | `m1_full` × check (12 units) at the frozen revision | M6 |
| 26–27 Oct | Hidden: Random, Chemeleon, `m1_full` (if released) | M6 |
| 27 Oct | Per-material table to M2; `generalization.py` dev vs held-out | M6 → M2 |

Nothing in this plan has been launched yet. M6 asks the user before every long job.
