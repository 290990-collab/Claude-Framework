# Orchestration — coordinator's guide

Content **actionable only by whoever delegates**. Subagents do not read it: for
them what holds is what is in `CLAUDE.md`, which contains none of this
precisely so they do not pay for it at every spawn.

> To be read at the start of a session **if the session involves delegation**.
> For a two-file change the routing table at the bottom is enough.

## Who does what

The coordinator plans, delegates, verifies and integrates. It executes
**directly** only small low-risk changes — ≤2-3 files, a few dozen lines, no
contract touched: there, delegating costs more than doing.

Subagents execute a task and report. They spawn nothing. When a report opens a
question outside the mandate of whoever wrote it, the question goes back to the
coordinator: you do not pass sideways from one agent to another.

## Token economy — the ten rules of delegation

Canonical and complete list. It lives **only here**: the obligations of whoever
executes are a different thing and live in `CLAUDE.md`; they are not a
renumbered subset of these.

1. **Parallelism.** `architect` one at a time, never in parallel with other
   agents nor relaunched on the same task: it is the most expensive and reasons
   over the whole context. Other agents on the Opus model in sequence; max 2 in
   parallel only on **independent** tasks (disjoint files, no crossed output —
   otherwise you pay twice for the same reads and the results have to be
   reconciled by hand). Free parallelism only for `explorer`.
   The constraint is tied to the **role**, never to a model: a constraint that
   names a model dies with the model.
2. **Model to the task, not to the role.** No `architect` for obvious decisions
   nor `debugger` for evident causes. On mechanical work without judgement,
   downgrade the spawn's model to Sonnet (per-spawn override: it changes the
   model, the card's effort stays). Only where there are no non-trivial
   decisions: a model that is too weak gets it wrong, and the wasted round
   costs more than the premium.
3. **Pre-digested context to expensive agents.** `explorer` (inside the repo)
   and `api-scout` (outside the repo) explore once at low cost and deliver
   ready-made excerpts — signatures, lines around the point, exact `file:line`
   — so the expensive agent reads little at full price. Better one more
   accurate explorer than an expensive agent hunting through whole files.
4. **Pass ranges, not files.** The prompt carries the excerpts and the exact
   `file:line`; the agent receiving them is bound not to widen the read.
5. **Prompt digested for primacy/recency.** Mandatory structure in
   `20-prompt.md`. Never bury a `file:line` in prose.
6. **Load-on-demand, not front-loading.** What is not universal sits behind a
   pointer the agent fetches if needed, not pre-loaded into the prompt.
7. **One task per agent**, with an explicit completion criterion. No umbrella
   tasks ("fix everything"): they produce vague reports and unverifiable work.
8. **Continue, do not re-spawn.** For a second round — the implementer after
   the reviewer's findings, the explorer needing one more detail — you reuse
   the agent with its context intact: restarting cold re-digests everything
   from scratch. It is the rule most often forgotten, and among the most
   expensive.
9. **One review only**: the final reviewer **or** a native review skill, never
   both. Heavy native skills are launched only at the user's request.
10. **No redundant re-verification, not even by proxy.** The obligation holds
    for whoever executes; here it holds in addition that you do not spawn an
    agent to redo a verification that already passed and is still valid.
