# Integrated M4 interface

The official frozen M1 full agent uses M4 memory, M3 planning and the independent generator/filter capture wrapper. The final development ablation is complete.

- [ADOPTION.md](ADOPTION.md): current package setup and authoritative configuration.
- [EVENT_CAPTURE.md](EVENT_CAPTURE.md): capture coverage, isolation and checkpoint semantics.
- [m4_capture_overrides.yaml](m4_capture_overrides.yaml): reference fields adopted by M1; preserve official settings.
- [Current validation](../VALIDATION.md): complete 72-test command and result evidence.
- [Runbook](../EXPERIMENT_RUNBOOK.md): offline reproduction and original scientific execution.
- [archive/](archive/README.md): obsolete initial memory-only YAML, retained for history.

`test_joint_capture.py` and `test_dev_pilot.py` remain active regression tests. The saved component test under `M1/MADE/tests/` is a handoff copy. The installed authoritative test is in the repository's top-level M1 tree.
