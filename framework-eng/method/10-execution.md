## Obligations of whoever executes

They hold for every agent that receives a task, coordinator included when it
works directly. They are a different thing from the delegation rules, which
concern only whoever spawns.

- **You do not delegate.** A subagent spawns no other agents. If the task needs
  work outside your mandate, you report it to the coordinator instead of
  fetching it yourself or improvising it.
- **Do only the task you received.** What you find along the way that would
  deserve an intervention goes into the report, not into the diff. An umbrella
  task produces unverifiable work.
- **Range reads.** If the prompt gives you excerpts and `file:line`, read only
  those ranges — never the whole file. You widen only if the excerpt is not
  enough or does not match the current code, and you say so.
- **Fetch on demand, not in advance.** The guides in `.claude/shared/` are
  opened when the task enters their domain, not out of diligence. Context
  loaded and unused is pure cost.
- **No redundant re-verification.** Build or tests just passed and no file
  changed: you do not re-run them "to be safe".
- **An explicit completion criterion.** If the task you received has none that
  is verifiable, you ask for it instead of guessing it.
