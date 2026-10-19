# Slides Outline: 10-minute talk + 5-minute Q&A

Owner: M6. Status: skeleton, 2026-10-19. Rehearsal 29 Oct; submit 30 Oct.

Budget: **14 slides, 9:55 total** (5 s spare). Time is per slide and includes the
transition. Owners send slide drafts and speaker notes by **24 Oct**; M6 trims them
to the times below and moves them into one deck.

Existing drafts run long. M3's three slides are about 2 min (`M3/report/M3_SPEAKER_NOTES.md`)
and M4's two slides about 90 s (`M4/report/M4_SPEAKER_NOTES.md`). Here they get one slide each.

The brief requires five things in the talk: (a) main idea and architecture, (b) how
the system uses MADE and manages the budget, (c) key results against both baselines,
(d) representative trajectories, discoveries and failures, (e) conclusions and lessons.

| # | Slide | Time | Covers | Owner / speaker | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Title, team, one-line claim | 0:15 | – | M6 | – |
| 2 | Problem: closed-loop discovery on MADE, B = 20, what is fixed vs what we change | 0:45 | b | M6 | brief, `M1/EXPERIMENT_PROTOCOL.md` |
| 3 | Architecture: planner → reflection → exploration → router → filter → scorer → 1 query | 0:55 | a, b | M1 | `M1/SLIDES_DRAFT.md` slides 1–2 |
| 4 | Planning + self-correction | 0:50 | a | M3 | `M3/report/M3_Method_Draft.pptx`, `M3_SPEAKER_NOTES.md` |
| 5 | Memory and evidence | 0:40 | a | M4 | `M4/report/M4_Method_Draft.pptx`, `M4_SPEAKER_NOTES.md` |
| 6 | Exploration: budget-annealed UCB | 0:40 | a | M5 | `M5/DESIGN.md`, `M5/README.md` |
| 7 | Tool routing: Random vs Chemeleon by observed reward | 0:40 | a | M2 | `M2/METHODS_AND_M6_HANDOFF.md` slide 1 |
| 8 | Protocol and fairness: splits, seeds, same oracle/budget, check = frozen only | 0:35 | b | M6 | `M6/PROTOCOL_ADOPTION.md`, M2 slide 2 |
| 9 | Leaderboard: mSUN@20, AUDC, AF, EF, cost (held-out first, dev second) | 1:00 | c | M6 | report Table 1 |
| 10 | Discovery curves | 0:40 | c | M2 | report Figure 2 |
| 11 | Component ablation (paired Δ mSUN) | 0:50 | c | M6 (M3 data) | report Table 2 |
| 12 | Generalization: dev vs held-out | 0:40 | c | M6 | report Figure 3 (`generalization.svg`) |
| 13 | Failure cases: over-exploitation and wasteful exploration, one trajectory each | 0:50 | d | M5 / M6 | report section 8 |
| 14 | Conclusions, lessons, cost | 0:35 | e | M6 | report sections 9–10 |
|   | **Total** | **9:55** | | | |

## Rules for every slide

- One message per slide, written as the slide title (a full sentence, not a topic).
- Results slides show only numbers from the report tables, with split, units and
  seeds in the footer. No "TBD" on the final deck: if a result is missing, the slide
  says "not run: why".
- Say "public check set" if no hidden set was released. Never "test set".
- Large fonts (≥ 20 pt body). Max ~25 words of body text on method slides.
- Discoveries (slide 13 or a backup): show 1–2 actual new stable formulas from a
  trajectory, with their e_above_hull from the oracle. No claim of lab validation.

## Backup slides (for Q&A, not timed)

- B1 Per-material table (Appendix A).
- B2 Cost breakdown and compute plan (`M6/COMPUTE_PLAN.md`).
- B3 Hidden-split handling and fallback (1 seed) if used.
- B4 Plug-in interface and switches (`M1/PLUGIN_INTERFACE.md`).
- B5 Reproduction commands.

## Rehearsal (29 Oct)

1. Full run with a timer. Any slide over its time by > 10 s gets cut.
2. Every number on screen checked against its source file.
3. Q&A drill: why B=20, why CPU, check vs hidden, what the agent reads (no hidden
   labels), what "USD 0" means, seed count.
