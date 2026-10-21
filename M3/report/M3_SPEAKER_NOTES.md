# Speaker notes for the three M3 slides

These notes are also embedded in the slides. Target: about 2 minutes in total.

Plain words used throughout: a "try" is one oracle query (20 per run), an
"area" is a search region (each pair of elements, or all three together), and
a "recipe" is a composition.

## Slide 1: Plan the search in parts (~40 s)

Our agent only gets 20 tries to find new materials, so my first part decides
where those tries go.

Each search uses three elements, for example magnesium, tin and strontium. A
new material can combine any two of them, or all three. So I split the search
into four areas: the three pairs, and the three-element mix.

The agent spends four tries at a time in one area. Within that area, it picks
recipes it hasn't tried yet, choosing ones that are as different as possible
from earlier tries, and skips recipes that fail a basic chemistry check.

After every four tries, it compares the areas: how many stable materials each
has produced, what our shared memory says, and how much is still untried. It
then moves to the most promising area.

It's a set of simple rules, not an AI model, so it costs nothing to run, and it
never looks at the answers.

## Slide 2: Notice when the search is stuck (~40 s)

My second part checks the plan before every try, looking for two signs that
the search is stuck: six tries in a row with no new stable material, or a plan
to repeat a recipe that's already been tried twice.

When either happens, it changes course. It swaps in the recipes that have been
tried least and are most different from the recent ones. If the search stays
stuck, it also generates more candidate structures for each recipe. That
doesn't use up any of the 20 tries.

This small demo shows the idea with made-up results: finds only at tries 3 and
13. In the empty stretch between them, the agent changed course three times.

Every change of course is recorded, so in the real runs we can see what
happened after each one.

## Slide 3: Better on hard systems, worse on easy ones (~45 s)

We ran 72 tests: six practice systems, three repeats each, with and without
each part. The reference agent reproduced its earlier numbers exactly, so the
comparison is fair.

With both of my parts on, the agent found 1.5 more new stable materials per
run than the reference: 6.5 instead of 5. But this depends heavily on the
system.

On the three hard systems, where the reference found almost nothing, it went
from about 1 to about 7. On the three easy ones, it dropped from about 9 to
about 6.

The reason is that my planner mostly stays with the pairs and rarely tries all
three elements together. That works when the good materials are in a pair, like
gold-potassium-terbium, but misses them in hafnium-nickel-zirconium, where most
are in the three-element mix.

Planning adds about 1.4 materials per run, and self-correction about 0.7. The
clearest case is cobalt-magnesium-sodium: changing course after six empty tries
raised the total from 3 to 13 across its three runs.

Next step: always save some tries for the three-element mix.

## If asked in Q&A

| Question | Short answer |
| --- | --- |
| Why four areas? | Good materials often cluster in one region; splitting lets the agent focus there. |
| Why four tries per area? | Enough to judge an area, few enough not to waste budget on a bad one. |
| Why does it lose on easy systems? | It sticks to the pairs; in Hf-Ni-Zr most finds are in the three-element mix, which the reference samples more. |
| How do you know self-correction works? | Before a bug fix it never fired, and on and off gave identical results in all 18 pairs. After the fix it changed course 16 times and helped most in Co-Mg-Na. |
| What was the bug? | The simulator marks every new structure as "newly discovered", even unstable ones, so the agent never thought it was stuck. Now only stable finds count as progress. |
| Is the comparison fair? | Same systems, repeats, 20-try budget, simulator and memory for every version, all run on one machine; the reference reproduced exactly. |
