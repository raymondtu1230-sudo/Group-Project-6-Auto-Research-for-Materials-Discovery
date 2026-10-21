# M1 integration references

M1 adopted M4 on 20 October (`9acd3c9`) and integrated M3 (`2fcc214`). The older full YAML and component test retained here document the earlier validation; do not overwrite newer team files with those snapshots.

- [ADOPTION.md](ADOPTION.md): package/configuration and M3 consumption checks.
- [EVENT_CAPTURE.md](EVENT_CAPTURE.md): optional generator/filter rejection and error capture, exact coverage limits and tests.
- [m4_capture_overrides.yaml](m4_capture_overrides.yaml): reference fields adopted by M1 in `3f8d48f`, identical in both comparison arms.
- [../EXPERIMENT_RUNBOOK.md](../EXPERIMENT_RUNBOOK.md): official capture and result handoff.

M1 enabled the capture target in its official profile on 21 October (`3f8d48f`). Default diversity still ignores memory; use M3 for consumption checks. Historical real-ORB validation is not a final full-agent Memory ablation.
