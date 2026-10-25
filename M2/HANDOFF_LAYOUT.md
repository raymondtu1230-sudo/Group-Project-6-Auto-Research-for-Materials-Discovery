> **Current frozen-release warning, 25 October 2026:** M1 has already integrated M2 routing and frozen `m1-freeze-20261025` at `02e0026bf450f71f4f7862228d295f5b02b49e12`. Do not run the old installer or alter agent/configuration files on that release. M2's 18 routing-off episodes are complete. Use [STAGE_ACCEPTANCE_20261025.md](STAGE_ACCEPTANCE_20261025.md) and [METHODS_AND_M6_HANDOFF.md](METHODS_AND_M6_HANDOFF.md) for current results. The installation steps and shared-config failure notes below describe the earlier pre-freeze handoff; they are historical instructions, not a current freeze blocker.

---

# Independent M2 component handoff

Canonical delivery is main/M2/. M1 owns installation into the shared framework. The following mapping is verified only in an isolated test checkout.

| M2 source | M1 installation slot |
| --- | --- |
| integration/m2_tool_routing.py | M1/MADE/src/made/agents/m2_tool_routing.py |
| integration/test_m2_tool_routing.py | M1/MADE/tests/test_m2_tool_routing.py |
| configs/m2_routing.yaml | M1/MADE/configs/agent/m2_routing.yaml |
| install.py: tool_router/generators mapping | Existing fields in M1/MADE/configs/agent/m1_integrated.yaml |

M1 can run the installer after review. It refuses to overwrite another configured router or an unrelated generator mapping. It preserves the other four switches, the M1 agent, all other member files, and the official runner/oracle/evaluator/environment/budget implementation.

```bash
cd M1/MADE
uv sync --locked
uv run python ../../M2/install.py
uv run pytest -q tests/test_m1_integrated.py
uv run pytest -q tests/test_m2_tool_routing.py ../../M2/tests -o addopts=''
uv run ruff check src/made/agents/m2_tool_routing.py tests/test_m2_tool_routing.py
uv run ruff check ../../M2
uv run python ../run_smoke_test.py
```

Fake state and synthetic structures in contract tests establish interface behavior. The official smoke is also synthetic. Neither counts toward the scientific baseline coverage. Real accepted units require full B=20 trajectories and the offline evaluator.

Current shared-main unseeded initialization has a separately reproduced M5 seed=None failure. M2 does not edit that member's policy or remove its configuration. Source-specific integration CI passed on the earlier M2 development snapshot; see ACCEPTANCE_CHECKLIST.md and the dated audit. M1/M5 should resolve the shared issue before claiming full shared-config acceptance.

Code/config/test evidence goes to M1 by24 Oct. Method text and draft slides go to M6 by24 Oct, then final result material by27 Oct. Draft messages have not been sent and no receipt/acceptance is recorded. PR2 remains a draft and is not merged.
