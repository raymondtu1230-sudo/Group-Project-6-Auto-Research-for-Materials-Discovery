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

## Slide 3: M3 lifts weak systems, loses on strong ones (~40 s)

All 72 runs finished. The re-run reference matches M1's recorded numbers
exactly, so the comparison is clean. Full M3 finds 1.5 more stable, unique,
novel structures per run than the reference, but the spread is larger than
the mean, and the effect depends on the system. On the three systems where the
reference finds almost nothing, M3 goes from about 1 to about 7. On the three
where the reference already does well, M3 drops from about 9 to about 6. The
reason is the planner: it commits to binary edges and gives the ternary
interior at most two of its five batches. That pays off when the stable phases
sit on an edge, like gold-terbium, and costs discoveries in
hafnium-nickel-zirconium, where the interior is rich. Planning adds 1.4 over
planning off. Self-correction adds 0.7: it re-planned 16 times, all for no
progress, and the clearest case is cobalt-magnesium-sodium, where re-plans at
queries 6 and 13 lift the three seeds from 3 structures in total to 13. Next step: keep a minimum
share of queries for the ternary interior.
