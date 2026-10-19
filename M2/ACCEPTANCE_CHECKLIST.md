# M2 handoff acceptance checklist

Reviewed on 19 October 2026 against the user's supplied M1 handoff instructions.
This checklist covers the M2 component handoff. Completion of the team's full
scientific comparison is a separate gate.

## Ownership and reviewed source

- Canonical sources, tests, workflow definitions, evidence and notes are in
  `M2/` on `main`, beside the other members' folders.
- The integration candidate is `m2/tool-routing-evaluation`, revision
  `2b2c675317b3530963c27f69d8d88490d7b31dd4`, in
  [PR #2](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/pull/2).
- All five required M1 files were read: `M1/PLUGIN_INTERFACE.md`,
  `M1/INTEGRATION.md`, the M1 integrated agent, its Hydra configuration, and
  `tests/test_m1_integrated.py`.
- M2 implements tool routing and checkpointable generator adapters. M3's
  planning/reflection, M4's memory and M5's composition exploration stay with
  their respective owners.

## Requirement mapping

| Requirement | Implementation and verified evidence |
| --- | --- |
| Importable component | `integration/m2_tool_routing.py`; `install.py` copies it to `M1/MADE/src/made/agents/m2_tool_routing.py`. |
| Hydra configuration and existing field names | `configs/m2_routing.yaml` is installed into M1's agent config directory. The installer connects `tool_router` and `generators` in `m1_integrated.yaml`. |
| Preserve `agent(state) -> (Composition, Structure)` | The existing M1 agent is unchanged. Contract tests verify the returned composition and structure. |
| Preserve all five independent switches | The M2 profile inherits the existing configuration and changes only `enable_tool_routing`. Tests compare the other four switches. |
| Correct router/generator types | The router returns a configured generator name. Its adapters return `list[Structure]`. M1's existing Plan and memory contracts are unchanged. |
| Respect remaining queries | The router checks `m1_queries_remaining` and rejects exhausted/invalid budgets. M1's original budget caps remain in force. |
| One environment step per oracle query | No runner, environment or budget code is changed. The router only selects a generator and never evaluates a structure. |
| No oracle calls or hidden-state access in the plug-in | The reviewed plug-in reads query count, remaining budget and the previous public observation. It does not import oracle/evaluator/environment code or read hidden labels. |
| JSON checkpoint state | Router and both generator adapters implement `get_state` and `load_state`. JSON round-trip and resumed-decision/structure checks pass. |
| Seeded reproducibility | Router checks cover seeds 17/29/43. Random generation restores its RNG. A separate real CPU Chemeleon check verified equal continuous/resumed structures and preservation of external random streams. |
| Enabled and disabled behavior | `integration/test_m2_tool_routing.py` checks routed selection and primary-generator fallback. |
| Invalid outputs and checkpoints | Tests reject unknown names/unrelated objects, corrupt state, changed configuration and invalid budgets. |
| Required test inputs | Contract/unit tests use fake MADE state and synthetic structures as requested. They are actually executed and are not reported as materials benchmark results. |
| Environment and API setup | CI installs the frozen environment using `uv sync --locked`. Actual Materials Project access and real Chemeleon generation passed separately; see the JSON evidence under `verification/`. |
| No embedded credentials or machine-specific source paths | Credentials use the existing repository Secret, mapped to `MATERIALS_PROJECT_API_KEY`. Plug-in source contains no key values or hard-coded workspace paths. |
| Independent folder | The published `main/M2` directory contains the canonical package and validated evidence. Installing its integration copies is a separate, explicit operation. |

Against current `main`, the integration candidate changes only four M1 slots:
the new module, new component test, new M2 Hydra profile, and the existing
`m1_integrated.yaml` configuration. The official runner, oracle, evaluator,
environment, budget logic, M1 agent implementation and original M1 tests are
unchanged. Current M4 contents are preserved exactly.

## Executed checks

[GitHub run 39221672640](https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery/actions/runs/39221672640)
passed on revision `2b2c6753`:

- 17 original M1 contract tests and 45 M2 tests passed, with no skips.
- Focused Ruff and the complete M2 Ruff check passed.
- Re-running the installer produced no tracked changes.
- The unchanged official `M1/run_smoke_test.py` passed.
- Artifact `12172061499`, `m2-integration-verification`, preserves JUnit and
  smoke evidence. The job logs preserve the actual command output.

The local continuation also ran the checks: 17 M1 and 44 M2 tests passed, and
one process-CPU test was explicitly skipped because the local `/proc` namespace
does not match the process IDs. That same CPU test passed in GitHub Linux;
the skipped local assertion is not counted as a local pass.

Reproduce from the repository root:

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

Unit tests and the AnalyticOracle smoke establish integration behavior. Actual
API/model checks establish real access and model continuation. Scientific
performance is accepted only from completed, validated protocol experiments.

## Remaining acceptance gates and branch policy

- The component implementation and its checks are ready for M1 review. PR #2
  contains the separately prepared M1 integration slots and active GitHub
  workflow files; these have not been merged into `main` by this handoff.
- Two of 36 development baseline units are accepted: Random Mg-Sn-Sr/17
  (B=20, mSUN=7, AUDC=55.5) and Chemeleon on the same unit (mSUN=16,
  AUDC=161). The [paired recovery package](verification/20261019-chemeleon-recovery/README.md)
  validates the identical protocol and material-reference snapshot. No overall
  method score exists. Another 34 baseline units, the full integrated reference
  and routing-off comparison remain incomplete.
- Keep `main`: it is the shared delivery branch. Keep the single M2 development
  branch while PR review/integration and experiment work remain active. The
  repository has two branches in total, not two separate M2 branches.
- Retire the M2 branch only after its required changes are accepted into the
  shared branch, checks pass, and experiment evidence and remaining workflow
  needs are accounted for. Folder delivery alone is not a reason to delete it.
- Do not announce that the whole M2 scientific task is finished while those
  experiment gates are pending. A group-chat completion notice remains a
  separate communication step.
