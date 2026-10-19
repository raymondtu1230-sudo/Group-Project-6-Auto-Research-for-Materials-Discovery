# Draft: group chat message (not sent)

---

Hi all, M6 here. Quick update and four asks. Details on branch `m6/experiment-design-report`, folder `M6/`.

**1. Protocol: I'm adopting M1's protocol v1 as-is.** Same 6 dev / 4 check systems, seeds 17/29/43, B=20, ORB on CPU. One rule added: **the check set is for the frozen agent and the two baselines only.** No agent or ablation runs on check before the 25 Oct freeze, and no changes after seeing check results (`M6/PROTOCOL_ADOPTION.md`).

**2. Chemeleon compute problem: proposing we start check baselines now.**
- Chemeleon takes ~4.4 h per system/seed (15 767 s on a GitHub runner). The 12 check units are ~53 h serial. Random is ~16 min/unit (12 units ≈ 3 h).
- Hidden-test Chemeleon in the 26–27 Oct window will only fit if it runs in parallel.
- **@M2:** could you add a `split` input (`dev|check|hidden`) to `m2-real-baselines.yml` and dispatch Chemeleon × check (12 jobs) as soon as possible? Baselines aren't tuned, so running them early leaks nothing. I'll run Random × check with `M6/run_check_baselines.sh`.
- Plan and numbers: `M6/COMPUTE_PLAN.md`.

**3. @M1: we need a hidden split in the runner.** Proposal (`M6/PROTOCOL_ADOPTION.md` §4):
- Add `M1/protocol/hidden_systems.json` when the TA releases the systems.
- Add `hidden` to the `--split` choices in `run_experiment.py`, `run_baselines.py` and `evaluate.py`.
- Don't edit `protocol_v1.yaml`: `evaluate.py` rejects runs whose recorded settings differ, so that would invalidate every accepted unit.
- Refuse ablations on check/hidden in the runner.

I won't touch M1/M2 code myself.

**4. @M5: what's your ETA for wiring the UCB policy into `m1_integrated.yaml`?** I saw the code and tests landed in `M5/`. I need the frozen agent by 25 Oct for check/hidden runs. Also please keep `decision_log` in the checkpoint: it's our source for the two failure-mode trajectories.

**Reminder:** method text and slide drafts to me by **24 Oct**. Report template is in `M6/report/REPORT_TEMPLATE.md`, 10-min slide plan in `M6/report/SLIDES_OUTLINE.md`. I'm emailing the TA about the frozen commit, B, the hidden-test date and whether 1 seed is OK on held-out.
