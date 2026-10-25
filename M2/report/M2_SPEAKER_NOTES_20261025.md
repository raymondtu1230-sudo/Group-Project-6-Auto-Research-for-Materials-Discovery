# M2 speaker notes, 25 October 2026

About two minutes across four slides. This matches [the four-slide content source](M2_Frozen_Routing_Slide_Content_20261025.md). Native PPTX refresh and visual checking remain pending.

## Slide 1: Controlled tool routing

Our part is tool routing and evaluation. The router chooses between Random and Chemeleon using feedback from completed queries. It tries each tool first, then combines observed reward with an upper-confidence bonus. For the final two queries, it uses the reward alone. To test this part, we switched routing off in M1's frozen full system. The other four components stayed on, and the primary generator stayed Random.

## Slide 2: The frozen experiment

We ran six development systems with seeds 17, 29 and 43. That gives eighteen separate episodes, each with twenty queries. Every run used the same frozen source and CPU ORB settings. All eighteen completed. We also checked the original thirty-six baseline results and reused them. We did not run any ablation on check or hidden systems.

## Slide 3: Full compared with routing off

The Full system reached an average mSUN of ten, compared with seven point seven two with routing off. Its average AUDC was eighty-eight point one one, compared with seventy point one four. We averaged the six systems within each seed, then used the three seed means. This supports routing in this development setting, but the result varied across systems and seeds.

## Slide 4: Baselines, evidence and cost

Random averaged four point zero six mSUN, and Chemeleon averaged six point nine four. We kept the original results and checked the curves separately from recorded structures and energies. That analysis matched seven hundred and twenty baseline prefixes and all seventy-two final endpoints, without new model calls. Some original hidden attachments are still missing and are listed in the audit. Recorded model fees were zero, but compute was not free. We keep the hardware and timing limits clear, and M2 still needs the other members' results for the final group table.

Sources: ../verification/preserved-40204426478/report/endpoint_comparison/, ../verification/preserved-40204426478/report/baseline_compatibility/ and ../verification/preserved-40204426478/report/recorded_curve_analysis/. AF/EF use the official discovery definitions, not elapsed-time speedups.
