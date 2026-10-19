# Current-main isolated installation check

Checkout 7369219c5522934e20e4778d0f3931d9b9648239 includes M5 UCB configuration. `M2/install.py` ran in an isolated worktree; shared main/M1 was not changed. Every non-M2 field and all five switches were preserved exactly.

- Locked environment sync and installer: exit 0.
- M1 integration tests: 17 passed.
- Combined M2 tests at that source: 51 passed, 1 failed, 1 skipped. The failure is `test_default_unseeded_configuration_still_initializes_with_routing_off`: Hydra recursively constructs M5 UCB with seed=None and M5 calls int(None). This is an M1/M5 integration dependency; no M5 code was changed.
- Required focused Ruff: passed.
- Original smoke: failed because Chrome was missing in this new environment. A retry using the already-installed Chrome also failed when Chrome closed on startup; the separate log retains that failure. No synthetic smoke score is counted as a material experiment.

Before/after configs, command details, source hashes and complete logs are retained here. Do not represent the current shared-default configuration as fully passed.
