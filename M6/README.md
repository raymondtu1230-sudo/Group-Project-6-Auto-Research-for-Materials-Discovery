# M6: experiment design, generalization and report

| File | What |
| --- | --- |
| [WORK_LOG.md](WORK_LOG.md) | Dated log |
| [PROTOCOL_ADOPTION.md](PROTOCOL_ADOPTION.md) | Adopts M1 protocol v1; check set = frozen agent only; hidden-split proposal |
| [COMPUTE_PLAN.md](COMPUTE_PLAN.md) | Unit counts, time estimates, laptop vs GitHub Actions, 1-seed fallback |
| [run_check_baselines.sh](run_check_baselines.sh) | Serial Random + Chemeleon over check (or hidden) systems × seeds; dry run unless `--execute` |
| [generalization.py](generalization.py) | Dev vs held-out table + chart from M2 `per_run.csv` (stdlib only) |
| [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md) | Brief deliverables → owner, status, file |

`comms/`, `report/` and `results/` are kept local (git-ignored). Report text and slides are sent to M6 directly.

Checks (from the repo root):

```bash
uvx pytest -q M6/tests
(cd M6 && uvx ruff check . && uvx ruff format --check .)
bash -n M6/run_check_baselines.sh
```
