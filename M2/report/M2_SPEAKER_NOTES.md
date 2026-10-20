# M2 speaker notes, 21 October

## Tool routing, about40 seconds

Our router chooses between Random and Chemeleon using feedback from completed queries. It tries each tool first, then combines observed reward with an upper-confidence bonus. Stable new observations earn one, while stable-only observations earn a quarter. This reward is a proxy, distinct from mSUN. For the final two queries, the router uses the smoothed reward alone. Routing makes no oracle call. The final routing-off comparison changes one switch in M1's frozen full system. We have not measured the router's scientific benefit yet.

## Development baselines, about40 seconds

All36 development baseline units have passed validation. Random and Chemeleon each cover six systems and three seeds, with20 queries per unit. These curves show the matched Mg-Sn-Sr, seed17 example. Random reaches mSUN7 and AUDC55.5. Chemeleon reaches16 and161. Across the full development sweep, Random's mean mSUN is4.06 and Chemeleon's is6.94. Their mean AUDCs are40.58 and71.31. These results establish our development baselines. The routing comparison comes later.

## Protocol and cost backups

We average the six systems equally within each seed, then calculate the mean and sample SD over three seeds. Random's mSUN SD is0.63 and Chemeleon's is1.11. AUDC SDs are9.46 and9.50. All36 units total720 queries. Mean driver times are16.0 and234.3 minutes. The final Au-K-Tb/17 and Co-Dy-W/43 runs both completed20 queries and reached mSUN3, with AUDC33.5 and35.5.

Known recorded model fees are zero. Hardware, electricity and all failed attempts are not fully priced. Missing token fields remain unreported. AF/EF use official discovery metrics and zero-baseline conventions, not wall-time speedups. M1 owns the frozen full reference. M6 owns check/hidden and final group assembly. M2's full-system ablation and team comparison remain later work.

Sources: ../verification/direct-39432570527-1/final-report/per_run.csv, per_method_summary.csv, validation.json and ../verification/stage-closeout-39432570527/terminal-validation.json. Chart example: verified_pair_chart_data.json. Current editable deck: M2_Method_and_Dev_Baselines_20261021_36of36.pptx. Older decks remain history.
