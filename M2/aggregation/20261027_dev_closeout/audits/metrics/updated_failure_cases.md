# Updated M5 failure-narrative audit

Snapshot `b36e2a50d9d3e31fc941d827addab94db2c5d3cc`. Read-only review; no source edits, oracle calls or scientific reruns.

The corrected counts and endpoints now match the original trajectories: OFF Mg–Sn–Sr29 has16 initial Sn–Sr binaries,6 stable, then4 ternaries with2 stable; Sn9Sr1 is query2. Full Ga–Pt–Tm17 has one ternary, query6 Ga1Pt4Tm3, unstable with e_hull0.417018556594849; its10 stable hits comprise9 Ga–Tm plus1 Pt–Tm. The same-seed comparison is OFF16/AUDC168 versus ON10/AUDC93.

One factual sentence remains wrong: “all other steps were exploit mode on planner compositions.” The original20-record log has **8 mixed steps (queries1–8) and12 exploit steps (queries9–20)**. Joining by original zero-based `query_count` and matching the recorded actual formula to original outgoing compositions identifies evaluated UCB compositions at queries **1,2,3,4,6**. Queries5,7,8 match planner compositions within mixed steps; queries9–20 are planner-only exploit steps. Only query6 is ternary. These are distinct facts and should not be collapsed into one mode claim. No new mode labels were invented.

“Trades a small amount of mean performance” is misleading for mSUN: ON gains0.3333 mSUN (10.0000vs9.6667), while AUDC differs by−0.1111 (88.1111vs88.2222). The lower pooled episode population SD (ON2.728451vsOFF4.830459) is descriptive across heterogeneous systems; it does not establish within-system reliability or causal consistency improvement. Seed-first sample SDs for the primary mSUN aggregation are ON0.881917, OFF1.154701.

The explicit interpretation-boundary paragraph appropriately labels hard-system rescue/easy-system cost as a hypothesis. The headings “Over-exploitation” and “Wasteful exploration” should likewise remain hypotheses or become descriptive (“delayed ternary sampling”; “one unsuccessful UCB ternary query”). The counterfactual value of alternate queries remains unobserved.

All **90 selected original scientific payload files** compared against the prior intake are byte-identical: trajectories and metadata for18OFF+18acceptedFull units, plus the18Full M5logs. Formula, structure, observed novelty/stability and original mode evidence were preserved. The notes above qualify narrative claims and do **not** block data ingestion. See `updated_failure_cases.json` for hashes, the full20-row mode join and exact values.
