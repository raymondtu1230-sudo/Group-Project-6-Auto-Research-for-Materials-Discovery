# M2 speaker notes for the M6 outline

## Slide 7: Tool routing, 40 seconds

Our router chooses between Random and Chemeleon using feedback from completed queries. It first tries each tool, then combines the observed reward with an upper-confidence bonus. Stable new observations earn one, while stable-only observations earn a quarter. This reward is a proxy, distinct from mSUN. For the final two queries, the router uses only the smoothed reward. M1 keeps the five independent switches. The final routing-off comparison will change one switch in M1's frozen full system.

## Slide 10: Discovery curves, 40 seconds

This is the currently verified example, one development system and seed. Random reaches mSUN seven and AUDC 55.5. Chemeleon reaches sixteen and 161. The curves come from all twenty official query positions. mSUN and the AUDC source curve use different definitions, even though they coincide in this pair. Two of thirty-six baseline units are accepted here, so there is no overall ranking or variability estimate. We will update this slide from validated new results.

## Protocol / cost backups

The development protocol fixes six systems, three seeds and twenty queries per unit. Both baselines use the official models and inference settings. Successful driver times were 15.9 and 262.8 minutes for this pair. Recorded inference fees are zero, while hardware, electricity, interrupted-attempt charges and unreported token fields remain unmeasured. AF/EF measure discovery-curve improvement, not wall-time speedup. M6 owns public-check and hidden-test evaluation. M1 owns the frozen full-system reference.
