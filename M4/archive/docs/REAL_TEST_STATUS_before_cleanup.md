# Historical documentation snapshot

Preserved before the 26 October final documentation cleanup. Statements about pending work describe earlier stages. See [the current M4 index](../../README.md) for final status and reproduction.

# M4 real-material workflow validation

On 19 October 2026, the temporary integration based on team revision bf141ca ran M1 protocol v1, method m1_baseline, dev system Mg-Sn-Sr, seed 17, one episode, and 20 budgeted queries. The oracle was CPU ORB orb-v3-conservative-inf-omat; other policies used the existing defaults. GitHub authorship was later corrected without changing the tested code.

Status: completed. Official wall time was 157.193 seconds, approximately 2 minutes 37 seconds. Materials Project returned 203 entries, filtered to 194. Initialization re-evaluated 112 stable/near-stable structures. The 20-query count covers campaign queries only, not the extra initialization computations. This first successful run also downloaded approximately 102 MB of model weights, so its duration is not a universal estimate for later runs.

The official mSUN count was 7 and AUDC was 49.5. These are results from the existing M1 agent with M4 logging, not a Memory performance gain or the final full-team method. The default Planner did not consume m1_memory. No ON/OFF comparison was run.

Evidence validation: the official trajectory contains 20 observations; the online M4 log contains 19 because updates occur on the next proposal. Offline evidence.jsonl contains all 20, including the final query. overview.csv is available locally for M5. Proposal structures are preserved in JSONL and the official trajectory. Selection rationale and exploration modes still require policy-layer records from M5 and cannot be inferred from the current logs.

This test used no LLM/OpenRouter calls. The official cost record lists known ORB and Materials Project charges as zero, excluding electricity and equipment. LLM accounting fields are not_reported; that field alone is not an independent measurement of zero calls.

Raw official outputs remain local at protocol_v1/m1_baseline/dev/Mg-Sn-Sr/seed_17/attempt_02/ and remain local. Derived queried-candidate records are available in evidence/real-workflow; they exclude initialization and evaluation-only envelope data. Evaluation metrics and ground-truth phase diagrams are for post-experiment analysis only and must not become retrieval inputs for later agents. The M4 evidence export extracts only queried observations.

Next: obtain M5's log-format confirmation, connect M3's Planner to m1_memory, and run Memory ON/OFF under the frozen protocol. Do not expand experiment volume yet.
