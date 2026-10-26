# Independent M5 failure-case audit

Snapshot: `a27634d9edbf231d0c034273fa9f977f9d5e799e`. Read-only inspection; no oracle calls or scientific reruns. Full per-query formulas, structure fingerprints, stability, novelty, energies and source hashes are in `failure_cases.json`.

Recorded `is_stable` labels are retained. The saved Full configuration uses `stability_tolerance=0.1` eV/atom; these labels do not mean exactly zero hull distance.

## Recorded evidence

- `exploration_off` Mg–Sn–Sr seed29: first16 queries (zero-based indices0–15; one-based1–16) are Sn–Sr binaries, with6 stable hits. Sn9Sr1 is stable at index1, therefore **one-based query2**, e_hull0.08245191574096733. The four subsequent queries17–20 are ternaries; query19 Mg2Sn5Sr2 and query20 Mg8Sn7Sr3 are stable, e_hull0.07051029205322212 and0.06790838241577157. TotalmSUN8. The report's14 binaries/8stable wording is inaccurate. All20 proposals are newlydiscovered and exactstructure serialization hashes are unique; this doesnot evidence duplicate-structure modecollapse.
- `m1_full` Ga–Pt–Tm seed17:10 stable discoveries comprise9 Ga–Tm binaries and1 Pt–Tm binary. Only **one ternary** was evaluated: zero-based index5 / one-based query6, Ga1Pt4Tm3, unstable, e_hull0.417018556594849. Claimed indices12,13,14,15,18 are Ga–Tm binaries. The alleged sixternary probes do not exist in thistrajectory.
- The actual Full attempt **contains20 original `m5_decisions.jsonl` records**. Index5 is `mixed`, with outgoing UCB ternary Tm3GaPt4 matching the actual query. Indices12,13,14,15,18 are explicitly `exploit`, source `planner`. Do not manually replace these real modes with inferred `explore` labels.
- Same-seed Ga–Pt–Tm17 endpoint is **OFF16 versusON10**, AUDC168 versus93. The report's15.7versus10.3 are the three-seed system means (OFF16,18,13; ON10,12,9), not the same-seed result.

## Interpretation boundary

It is accurate to describe delayed ternary sampling in OFF Mg–Sn–Sr29 and one unsuccessful UCB ternary query in Full Ga–Pt–Tm17. The records do not establish the unobserved counterfactual that a ternary discovered earlier would improve the endpoint, nor that six unstable probes came from exploration. Preserve the actual observed behavior and its original mode evidence. The report's causal rescue/easy-system narrative is a hypothesis, not a measured per-query attribution.
