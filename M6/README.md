# M6: experiment design, generalization and report

| File | What |
| --- | --- |
| [WORK_LOG.md](WORK_LOG.md) | Dated log |
| [PROTOCOL_ADOPTION.md](PROTOCOL_ADOPTION.md) | Adopts M1 protocol v1; check set = frozen agent only; hidden-split proposal |
| [COMPUTE_PLAN.md](COMPUTE_PLAN.md) | Unit counts, time estimates, laptop vs GitHub Actions, 1-seed fallback |
| [run_check_baselines.sh](run_check_baselines.sh) | Serial Random + Chemeleon over check (or hidden) systems × seeds; dry run unless `--execute` |
| [generalization.py](generalization.py) | Dev vs held-out table + chart from M2 `per_run.csv` (stdlib only) |
| [results/20261019-dev-partial/](results/20261019-dev-partial/) | `generalization.py` on the 2 accepted dev units (no held-out data yet) |
| [report/REPORT_TEMPLATE.md](report/REPORT_TEMPLATE.md) | Report skeleton with owners and sources |
| [report/SLIDES_OUTLINE.md](report/SLIDES_OUTLINE.md) | 14 slides, 9:55 |
| [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md) | Brief deliverables → owner, status, file |
| [comms/](comms/) | Drafts: TA email, group message (not sent) |

Checks (from the repo root):

```bash
uvx pytest -q M6/tests
(cd M6 && uvx ruff check . && uvx ruff format --check .)
bash -n M6/run_check_baselines.sh
```
