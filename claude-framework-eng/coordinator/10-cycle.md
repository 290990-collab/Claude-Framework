## The code cycle

**Understand → Design → Implement → Verify → Integrate.**

1. `explorer` locates the relevant files (cheap, parallelisable); `api-scout`
   if signatures of external libraries are needed.
2. `architect` if the task touches ≥3 files or a contract; ambiguous requests →
   plan mode first. Otherwise it is skipped: a plan the coordinator writes in
   three lines is not worth a spawn.
3. `implementer`, **one task at a time**: complete, verify, move to the next.
   Test-first when the desired behaviour is expressible as a test (new
   features, well-defined bug fixes, business or API logic). Excluded for
   refactoring, UI, prototypes, dependencies, documentation.
4. `tester` extends coverage beyond the implementer's mini-tests. Few tests
   that assert something true, never many weak ones.
5. If the diff touches the **critical surface** declared by the project, first
   the reviewer of that surface; then `final-reviewer`, which verifies from
   scratch without trusting the reports.
6. The coordinator resolves the findings and integrates. Commit only on
   request.

The cycle is skipped where it is not needed: for a small low-risk change the
coordinator executes it directly.

## Choosing between agents that look close

| Doubt | Discriminator |
|---|---|
| `explorer` or I read it myself | You need >2 files or you do not know where to look → `explorer`. You already know the path → read it yourself: spawning costs more |
| `explorer` or `api-scout` | Inside the repo → `explorer`. Outside the repo (libraries, services) → `api-scout` |
| `architect` or I decide | It touches structure or a contract → `architect`. Otherwise it is a three-line plan, and you write it |
| `implementer` or `debugger` | The cause is known → `implementer`. The cause is unknown → `debugger`, which delivers the diagnosis |
| `implementer` or `refactorer` | It changes behaviour or adds → `implementer`. Observable behaviour unchanged → `refactorer` |
| `implementer` or `frontend` | What decides is the heart of the task: views, markup, style, motion → `frontend`; logic and services with touch-ups to the interface → `implementer`. If it weighs on both, the architect splits it in two |
| `deploy` or `infra` | Simple hosting, a push updates it → `deploy`. Resources defined as code, multiple environments → `infra`. They do not coexist |
| critical reviewer or `final-reviewer` | "Is the code correct?" → `final-reviewer`. "Is this safe / valid / is the data right?" → the reviewer of the critical surface, **first** |
