# Actual small Chemeleon recovery test

GitHub run 39285316913 succeeded at source 639f47b301d71cc7bd7c66c7832f0ecb75bb5e9d. Artifact 12201404998 was downloaded and its original ZIP SHA256 matched GitHub: 8570dbc27d6a286c60a994ccb4d704169ef4f0c58247c9a0c926ff88a65eace9.

The original continuous, deliberately interrupted and resumed executions use three Python processes and actual Chemeleon model sampling. The two final Structure lists match exactly, final Python/NumPy/Torch RNG matches, the first completed batch is preserved and resume samples only the missing second batch. All four recorded checks passed.

This is an integration fixture with two Li2O candidates and batch size 1, no oracle calls and no scientific discovery score. Formal baseline coverage remains 2/36. Real batch256 and cross-runner artifact recovery verification is separately queued as run 39286986254 at e30b5bb233842797f4ad90c80732bb327d07c0bf. No formal Chemeleon unit uses this experimental cache yet.
