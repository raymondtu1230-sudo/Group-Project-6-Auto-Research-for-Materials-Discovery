# Draft: email to the TA (not sent)

To: Dr Xiao Yushan <yushan.xiao@ntu.edu.sg>
Subject: Group Project 6 (Auto Research for Materials Discovery): questions on frozen settings and held-out evaluation

---

Dear Dr Xiao,

I am writing on behalf of Group 6 (Auto Research for Materials Discovery on MADE). We are
planning our final evaluation runs and would be grateful for your guidance on the
following points.

1. **Frozen MADE commit.** We are currently using MADE upstream commit
   `bffda0c9a1fa1904b35c0ef67b455881c975df86`. Will the course freeze a different
   commit or environment configuration? If so, when will it be announced?

2. **Base model and oracle settings.** We use the ORB oracle
   `orb-v3-conservative-inf-omat` on CPU, with FIRE relaxation (fmax = 0.02, at most 500
   steps, unit cell relaxed). Is this the intended base model and inference setting,
   or should we use another one?

3. **Query budget B.** We use B = 20 oracle queries per system and seed for every
   method. Could you confirm the budget the course will use for mSUN@B?

4. **Hidden test systems.** When will the held-out test systems be released, and in
   what form (for example, a list of element systems from the same MADE system file)?
   We plan to run the frozen agent and both baselines on them on 26–27 October. If they
   will not be released, may we report our public check set (four systems we held out
   from tuning) instead, stating clearly that it is not the course hidden test?

5. **Deliverables due on 30 October.** Could you confirm what must be submitted on
   30 October (code repository, report and slides), the expected report format or page
   limit, and whether the presentation slides are due at the same time as the report?

6. **Number of repeats on held-out systems.** Each Chemeleon baseline run takes about
   4.4 hours on a CPU runner. If compute is limited, is one seed per method on the
   held-out systems acceptable, provided it is the same for every method and stated in
   the report? We would keep three seeds on the development systems.

Thank you very much for your time. We are happy to provide more details on our protocol
if helpful.

Kind regards,
[[Name]]
Member 6 (experiment design and report), Group Project 6
[[Matriculation number]]
