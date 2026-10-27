# Three example discoveries

These are queried structures from the frozen full-agent ON reference. Each record is newly discovered and stable under the observed phase-diagram tolerance of 0.1 eV/atom at its evaluation step, and adds one to the recorded official mSUN count. These benchmark outcomes are not experimental confirmation of a new physical material.

| Candidate formula | System / seed | Query | Observed E above hull (eV/atom) | Official mSUN before / after |
| --- | --- | ---: | ---: | --- |
| Mg1 Na6 | Co-Mg-Na / 29 | 5 | 0.084047 | 0 / 1 |
| Mg4 Na3 | Co-Mg-Na / 29 | 6 | 0.060825 | 1 / 2 |
| Sn7 Sr1 | Mg-Sn-Sr / 17 | 3 | 0.082563 | 0 / 1 |

`discovery_examples.csv` supplies the exact source trajectory, attempt, query and SHA-256 of the original serialized proposal. Use all those fields to identify a structure, rather than formula alone. Full atomic structures and oracle results remain in the source trajectories. This selects examples already included in the preserved case-study runs and adds no experiment.

The reference ON runs belong to M1's full agent. M4's contribution is the evidence management and Memory OFF comparison. These examples demonstrate what the full agent discovered; they do not by themselves prove that Memory caused a particular discovery. See [the paired cases](TRACED_CASES.md) for favourable, adverse and equal outcomes.
