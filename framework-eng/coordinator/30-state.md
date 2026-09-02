## State that keeps itself up to date

Without written state, every session restarts by guessing. Four levels, each
with its own rhythm and its own ceiling.

**The coordinator writes it.** Subagents just report: whoever writes the state
must have seen the whole picture, and an agent that has seen only one task does
not have it. It is also why this section is here and not in `CLAUDE.md`.

| Lvl | File | Contains | Updated | Ceiling |
|---|---|---|---|---|
| 1 | `docs/TODO.md` | where we are **now**: in progress, waiting, next step, blocked | at **every** step | ~60 lines |
| 2 | `docs/status.md` | closed decisions, measured results, hypotheses confirmed or refuted | when something closes | 1 entry |
| 3 | `CLAUDE.md § Current state` | the picture: what the project knows today | only if **the picture changes** | ~25 lines |
| 4 | persistent memory | facts that hold **between** sessions: who the user is, directives, decisions | at every discovery or structural change | 1 file |

**Rules:**

- **You add or tick off, you do not rewrite.**
- **You compress before adding** when the ceiling is reached. The long trace
  goes down a level, it does not inflate the current one.
- **Session start:** level 1 first, always. **Task end:** level 1 always; level
  2 if something closed; level 3 if a conclusion changed.
- **No duplication between levels.** TODO = state, `status.md` = results,
  `CLAUDE.md` = picture, memory = what survives the session.
- **Long or asynchronous operations**: as soon as something starts that the
  user has to launch or wait for, the line goes into *Waiting* with what they
  must report back.
- ⚠️ Level 3 sits inside the project part of `CLAUDE.md`, **outside the kernel
  region**: updating it must never produce a drift finding.

**Level 4 is to be revisited, not just filled.** At every significant change —
paths, contracts, moved modules — and at every discovery that closes or refutes
a hypothesis, ask *"does this supersede a memory?"* and, if so, correct it or
mark it superseded **immediately**. Memory is compact too: one fact per file,
no number duplicated from the repo, no path that no longer exists.
⚠️ **In a conflict the repo wins**: an old unannotated memory is an active
bias, it restarts the next session with a month-old view.
