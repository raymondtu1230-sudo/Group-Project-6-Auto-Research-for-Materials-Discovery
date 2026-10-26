# M2 speaking text — development results and tool routing

Spoken text: **213 words** by whitespace count. About 1 minute 40 seconds at 130 words/minute; rehearse below the team's two-minute limit. Read the four paragraphs with slides 1–4. The title and timing note are not spoken.

<!-- BEGIN SPOKEN TEXT -->
Our tool router selects a generator using only feedback already observed. It probes Random and Chemeleon, then balances reward with an upper confidence bonus. The last two queries use the current reward greedily. Our ablation changes only the routing switch.

We evaluated six development systems with three seeds and twenty queries per episode. The completed package contains one hundred and sixty-two episodes. The table uses equal system weights within each seed. Full averages ten novel stable discoveries, compared with four point zero six for Random and six point nine four for Chemeleon. Routing OFF reaches seven point seven two. Its lower discovery-curve area also suggests earlier useful discoveries with routing in this setting.

Memory and exploration show smaller average effects and mixed outcomes. The separate M3 study keeps exploration and routing off, so its planning and self-correction gains are relative to M3 full rather than the all-enabled agent.

Costs retain machine labels and missing counters. Twenty budgeted queries do not cover every initialization cost, and zero recorded model fees do not mean zero resource cost. We learned to check matched configurations and original trajectories before explaining results. Raw records remain separate from later curve analysis. All assigned development packages are now available, but the final held-out comparison is still needed before claiming generalization.
<!-- END SPOKEN TEXT -->
