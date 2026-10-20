# Speaker notes for the three-slide M3 draft

These notes are also embedded in the slides. Target: under 2 minutes in
total.

## Slide 1: Plan in sub-goals, review after every batch (~40 s)

M3 decides where the agent spends its 20 oracle queries. I split a chemical
system into sub-goals, one per subset of its elements. A ternary therefore has
three binary edges and the ternary interior. The planner works in batches of
four queries on one sub-goal. It chooses the least-tried, most novel
compositions that pass the charge-balance check. After each batch it reviews
every sub-goal. The score combines the smoothed success rate from what it has
observed, memory from M4 when that is on, and a bonus for unexplored
compositions. The best sub-goal becomes the next target. It uses no language
model, so it adds no API cost, and it never sees hidden labels.

## Slide 2: Detect a stalled search and re-plan (~40 s)

The second part checks every plan before it is used. It declares the search
stuck if six queries in a row found nothing new. It also declares it stuck if
the plan would repeat a formula already tried twice. It then swaps in the
compositions that have been visited least and are farthest from what we just
tried. If the stall continues, it widens generation. That costs no extra
oracle queries, and M1 still caps the plan at the remaining budget. In this
scripted demo on lithium-iron-oxygen, new phases appear only at queries 3 and
13. Self-correction re-plans three times in the dry stretch between them.
Every re-plan is logged, so in the real runs we can trace which discoveries
followed a re-plan.

## Slide 3: Two ablations against M1's reference (~35 s)

We measure M3 against M1's reference agent. In its first runs on all six
development systems and three seeds, it found 5 stable, unique, novel
structures per run on average, with a wide spread. Since then the team added
M4's memory, so I re-run the reference under the same setup as M3. M3 adds
three configurations on exactly the same systems, seeds, budget and oracle:
full M3, M3 with planning off, and M3 with self-correction off. Each is paired
with the re-run reference by system and seed. The difference between full M3
and each ablation isolates what planning and self-correction contribute. Those
runs happen on the 26th and 27th. This slide will then show the paired differences
and one or two traced re-plan cases. No result is claimed yet.
