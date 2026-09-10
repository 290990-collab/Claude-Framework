# Orchestration — coordinator's guide

Content actionable **only by the coordinator**. Subagents do NOT read this file.

> To be read at the start of a session **if the session delegates**. For a two-file change the routing table at the bottom is enough.

## Who does what

- **Coordinator:** plans, delegates, verifies and integrates.
- **Direct execution:** small changes (≤2-3 files, a few dozen lines, no contract touched) are executed directly: delegating costs more.
- **Subagents:** execute the task and report to the coordinator. They spawn no subagents and do not communicate sideways: a question outside the mandate goes back to the coordinator.

## Token economy — the ten rules of delegation

Canonical and complete list, it lives **only here**. The obligations of whoever executes are in `CLAUDE.md` and are a different thing, not a renumbered subset of these.

1. **Parallelism by role** — the constraint belongs to the role, never to a model: a constraint that names a model dies with the model.
   - `architect`: max 1 at a time. Never in parallel, never relaunched on the same task.
   - Other high-reasoning agents: in sequence. Max 2 in parallel ONLY on completely disjoint tasks and files.
   - `explorer`: free parallelism.
2. **Agent and model to the task, not to the role:** no `architect` for obvious decisions nor `debugger` for evident causes. For mechanical, judgement-free or low-risk tasks, downgrade the spawn's model to a lighter one (the card's effort stays). A model that is too weak gets it wrong, and the wasted round costs more than the premium.
3. **Pre-digest the context:** first `explorer` (repo) or `api-scout` (libraries, services, docs) at low cost to extract exact `file:line` and signatures, then pass the excerpts to the expensive agents. **Scanning is not main-context work:** a broad task, a narrow answer, no judgment delegated (“of N files, which ones touch X” → a table) goes to `explorer` even when doing it yourself looks faster, because the coordinator costs more per token and keeps the noise for the whole session. What stays with you is work whose **judgment** is the product, not the scan that precedes it.
4. **Pass ranges, not files:** the prompt carries only excerpts and exact `file:line`; whoever receives them does not widen the read.
5. **Prompt structure:** mandatory, section "How to write a delegation prompt". Instructions at the edges, data and excerpts in the middle.
6. **Load-on-demand:** pass pointers to resources and guides. The agent opens them if and when needed.
7. **One task per agent,** with a verifiable completion criterion. Zero umbrella tasks ("fix X").
8. **Reuse the session, never re-spawn:** to iterate on the same task send the delta to the SAME agent without closing it. Restarting cold re-digests everything and costs double.
9. **One review only:** the final reviewer **or** a native review skill, never both. Heavy native skills are launched only at the user's request.
10. **Zero useless re-verification:** do not spawn agents to re-run builds/tests that just passed if nothing has changed.
