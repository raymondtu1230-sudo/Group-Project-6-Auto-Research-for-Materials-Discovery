# M3 report materials

| File | What it is | For |
| --- | --- | --- |
| [M3_METHOD.md](M3_METHOD.md) | Method text for the group report: how the planner and self-correction work, and how both studies were evaluated | M6 |
| `M3_Method_Draft.pptx` | M3's three slides, with speaker notes | M6, presenter |
| [M3_SPEAKER_NOTES.md](M3_SPEAKER_NOTES.md) | Script for the slides (about 2 minutes), plus likely Q&A | Presenter |
| [M3_RESULTS.md](M3_RESULTS.md) | Results of both studies: the full-agent ablations against `m1_full` (36 runs) and the component study (72 runs), with the hand-written "Why" section | M2, M6 |

M2 also uses the component-study tables in `../results/*.csv`. Evidence: the
component study's development runs are in
[`../evidence/20261021-dev-ablations/`](../evidence/20261021-dev-ablations/),
and all 90 frozen-agent result folders are in
[`../results/frozen_20261025/`](../results/frozen_20261025/).

`summarize_ablations.py` regenerates `M3_RESULTS.md` from the component study
only. It overwrites two hand-written sections, the full-agent ablations near
the top and "Why" at the end, so copy both back after re-running it.
