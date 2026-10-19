# Draft message to M1 and M5 — not sent

Hi M1/M5, I checked the current shared M1 config in an isolated checkout (7369219) after installing M2. M1's 17 integration tests pass, but the default unseeded initialization test fails because Hydra constructs M5's UCB policy with seed=None and its constructor calls int(None). The exploration switch is off, but Hydra still constructs the configured object. Could you check how the policy should handle an unset seed?

Reproduce after M2 installation:

```bash
cd M1/MADE
uv run pytest -q tests/test_m2_tool_routing.py -k default_unseeded -o addopts=''
```

Evidence is in M2/verification/20261020-current-main-interface/. The M2 installer preserved all non-M2 config fields and all five switches. I have not changed M5 or shared M1 code; M2 dev baseline runs and offline audits continue. The actual combined result was 51 passed, 1 failed, 1 skipped.
