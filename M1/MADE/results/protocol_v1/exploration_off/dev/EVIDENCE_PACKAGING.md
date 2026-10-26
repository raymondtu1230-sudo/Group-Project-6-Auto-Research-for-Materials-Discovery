# exploration_off evidence packaging (26 Oct)

Packaged 18 attempts from their original timestamped Hydra run dirs; no rerun performed. Recorded revision: aedf8ca238d2ef56948c0eadf2c897aef67f5104.

- `hydra/` = the run's saved Hydra config/overrides (original bytes)
- `m4_evidence.jsonl`, `run_benchmark.log`, `console_attempt_*.log` = original retained logs
- `resolved_config.yaml` = composed from the saved hydra config with interpolations resolved at packaging time (no rerun)
- `m2_metrics_history.json` = lossless reconstruction from the official trajectory (labelled in-file), per M1's packaging approach
- `m5_decisions.jsonl` is absent by design: exploration_off disables the M5 hook, so no decisions exist. The absence is intentional.
