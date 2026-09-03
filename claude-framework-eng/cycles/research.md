## The research cycle

It runs alongside the code cycle, it does not replace it. Here the product is
not "software that runs": it is **reproducible evidence**. A program that runs
and produces wrong numbers is a complete failure, not a partial success.

**Hypothesis → Protocol → Execution → Analysis → Conclusion.**

1. **Hypothesis** explicit and **falsifiable**, with the expected mechanism and
   a prediction *per dimension* — "I expect X to rise and Y **not** to,
   because…". Not "let's try whether it does better": an articulated prediction
   makes even a negative outcome informative, while a generic one makes even a
   positive outcome useless.
2. **Protocol** (`architect`): declared baseline, **one variable only**,
   success criterion decided **before** looking at the results, estimated cost,
   what is reused instead of recomputed.
3. **Execution**: if it is heavy, **the user** launches it, not the agent. The
   agent prepares the exact command and writes into `docs/TODO.md` the waiting
   line with *what that run must answer*.
4. **Analysis** (`results-analyst`): paired comparison, delta against noise,
   reading per dimension, and **why** — never just "it went up".
5. **Conclusion**: hypothesis **confirmed or refuted**, written as such in
   `docs/status.md`. Refutations are worth as much as confirmations and are
   recorded with the same care: not recording them means paying their cost
   again in two months.

⚠️ **The two cycles interleave**: often you change the code **in order to**
measure something. In that case the `architect` produces a plan with both
sections, and the final review includes the `scientific-reviewer` — which comes
**before** the `final-reviewer`, because "the code is correct" and "the number
means what we say it means" are two different questions.

**You do not relaunch** a run to get back a number already present in a log or
a summary: you read it from there. This holds for the coordinator that
delegates too.
