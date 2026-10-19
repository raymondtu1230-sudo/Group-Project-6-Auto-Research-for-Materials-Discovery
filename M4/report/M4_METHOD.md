# Memory and evidence management

## Method

The memory component stores the public feedback from evaluated candidates within each episode. Records identify the run, episode, query step and candidate attempt. They include the chemical system, composition when recoverable from the proposal, and available energy and stability feedback. Candidate identity remains separate from reduced formula so that multiple structures of the same composition retain independent outcomes. Stability labels refer to the observed phase diagram at the evaluation step and are not treated as permanent ground-truth labels.

The M1 adapter exposes a bounded list of recent observations with contrasting outcomes through the existing MemoryManager interface. The default limits are eight records and 4,000 serialized JSON characters. These bounds limit context size but do not specify a token budget. The independent core also supports retrieval by composition-fraction distance. That targeted mode is not currently exercised by M1's argument-free get_memory() hook and is not claimed as active behavior in the integrated method.

The component uses only public post-query feedback and makes no oracle calls. It preserves the official MADE runner, scientific oracle, evaluator and budget logic. Each episode uses a separate memory instance, with JSON checkpoint state and idempotent event recording. The generic storage API accepts rejected and error events when explicitly supplied, but automatic framework capture of those events remains pending. Recorded instability explains an observed outcome without inferring its physical cause.

For complete evidence, both Memory ON and OFF runs export the official trajectory. This includes the final evaluation, which the online update hook otherwise receives only at a subsequent proposal. Online logs serve as diagnostics. Policy reasons and the actual memory consumed by decisions require records from the planning and exploration components.

## Current implementation status

M4 is available under the repository's M4/ directory. The main agent does not automatically enable it. Deferred M1 configuration and integration tests remain in M4/integration. The default Planner does not consume m1_memory; therefore neither completed workflow establishes a change in decisions attributable to Memory.

Earlier temporary wiring passed a synthetic episode and one real Mg-Sn-Sr CPU ORB episode using seed 17 and 20 campaign queries. The real run took 157.193 seconds and produced official trajectories and metrics. These values validate execution and evidence completeness only. Initialization includes additional oracle evaluations and must be included separately in final cost accounting. The unchanged original run reports mSUN count 7 and AUDC 49.5, without a Memory-OFF comparison.

## Planned evaluation

After M1/M3 activate the manager and verify Planner consumption, compare the frozen full agent with Memory OFF under the same systems, initial conditions, query budget, oracle, base model/inference settings, tool set and paired seeds. Keep complete evidence in both conditions and hold other history mechanisms fixed. This measures M4's incremental contribution. Follow M6's tuning/check split and the official held-out protocol.

Use the official mSUN@B, AUDC, AF and EF implementations, discovery curves and research-cost records. Prefer three repeated runs as specified in the brief; disclose limited repetition where compute is constrained. Account for campaign queries separately from initialization and scoring computations. Report measured LLM usage if introduced, rather than interpreting an unavailable counter as zero.

Select two or three representative discovery cases only after the controlled runs. Each case should link queried evidence, memory supplied to the Planner, the resulting choice, and official feedback. Preserve neutral or negative findings. The current submission contains no completed Memory ablation or claim of improved discovery performance.

## Reporting references

Implementation: M4/src/m4_memory/; evidence contract: M4/EVIDENCE_SCHEMA.md; real-run record: M4/REAL_TEST_STATUS.md; integration boundary: M1/PLUGIN_INTERFACE.md. The course brief defines final evaluation requirements; team protocol values remain subject to the teaching team's frozen configuration.
