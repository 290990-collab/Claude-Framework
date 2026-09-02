# Working method

Claude Code operates here as a **coordinated team of seniors**: maximum
accuracy, minimum hallucination, token budget as a first-class constraint.

This is the **common method**: it holds for anyone working in this project,
coordinator or subagent, and is not customised. What concerns *this* project
lives in the sections outside the marker-delimited region.

**Who reads what.** This file is loaded into every context, so it contains only
what everyone needs. The rest lives elsewhere and is opened on demand:

- **delegation** — when to spawn, which agent, with what prompt, how project
  state is kept → `.claude/shared/orchestration.md`. It concerns **the
  coordinator only**: if this session delegates, it is the first file to read.
- **a role's mandate** → its card in `.claude/agents/`, which does not repeat
  this method.
- **the task's domain** → the guides in `.claude/shared/`, opened only when the
  task falls within them.
