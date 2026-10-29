# Speaker notes for the three M3 slides

These notes are also embedded in the slides. Target: about 2 minutes 20 seconds
in total.

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

## Slide 3: Planning matters most in the full agent (~60 s)

In M1's full frozen agent, with every part on, the agent finds 10 new stable
materials per run. Switching off only my planner drops that to 5.3, lower in
15 of 18 paired runs: the largest effect of any part. Switching off only
self-correction gives 9.5, with as many runs better as worse, so it shows no
clear effect there.

The table is my earlier component study, with exploration and tool routing
off. There, both my parts together beat the reference by 1.5 per run, and the
gain came from the hard systems: about 1 to 7 on the three hard ones, but about
9 to 6 on the three easy ones, because the planner rarely tries all three
elements together.

Next step: always save some tries for the three-element mix.

## If asked in Q&A

| Question | Short answer |
| --- | --- |
| Why four areas? | Good materials often cluster in one region; splitting lets the agent focus there. |
| Why four tries per area? | Enough to judge an area, few enough not to waste budget on a bad one. |
| Why does planning matter more in the full agent? | Without the planner, the agent asks for the whole three-element system every time. With it, tries are spread over the pairs and the mix. In the full agent it is lower without planning on all six systems. A plausible reason it no longer loses on Hf-Ni-Zr is that M5's exploration offsets the planner's preference for pairs; we did not test that separately. |
| Does self-correction help at all? | Not measurably in the full agent (8 better, 8 worse). Its one consistent gain is Co-Mg-Na (9.0 with it, 5.7 without), the same system where it helped most in the component study. |
| Why does it lose on easy systems? | It sticks to the pairs; in Hf-Ni-Zr most finds are in the three-element mix, which the reference samples more. |
| How do you know self-correction works? | Before a bug fix it never fired, and on and off gave identical results in all 18 pairs. After the fix it changed course 16 times and helped most in Co-Mg-Na. |
| What was the bug? | The simulator marks every new structure as "newly discovered", even unstable ones, so the agent never thought it was stuck. Now only stable finds count as progress. |
| Is the comparison fair? | Component study: same systems, repeats, 20-try budget, simulator and memory for every version, all run on one machine; the reference reproduced exactly. Full-agent ablations: M1's `m1_full` reference ran on M1's machine, and mine on my PC, from the same frozen tag, settings, seeds and Chemeleon archive; M2's evaluator accepted all of them. |
