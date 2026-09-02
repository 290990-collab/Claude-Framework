## Change principles

- **Minimal Safe Change** — the smallest change that solves the problem; one
  problem per task. No unrequested refactoring, pointless renames, file moves,
  or unasked changes of style or behaviour. Refactoring is a separate task.
- **Existing Pattern First** — before writing new code, look in the repo for
  something to reuse or extend. Consistency before creativity.
- **Contract First** — before changing a function, an API, a persisted format
  or a schema: what is the contract? who uses it (textual search including
  markup, scripts in other languages and string references)? am I breaking
  compatibility or observable behaviour? If so: state it in the report and
  handle the migration.
- **KISS** — for equal results, the simplest solution wins.
- **Local style** — new code imitates the file it lives in.
- **No chronicle comments** — comments explain non-obvious constraints, not
  what the next line does.
- **Commit only on the user's explicit request**, never on your own initiative.
- **No installation without explicit confirmation** — packages, dependencies,
  extensions, tools, models, through any manager. It holds for every agent with
  shell access, even when the installation seems obvious or implied.

## Principle on tests — few and meaningful, never many and weak

The number of tests is not a metric. A large suite can give false confidence
while the real defect sits at a higher level: an architectural inconsistency, a
wrong contract, behaviour that is correct in every unit and wrong as a whole.
Hundreds of green unit tests do not see it.

- **A test that would pass with the defect present does not count.** It is the
  criterion by which a suite is judged, not line coverage. If you do not know
  which plausible defect would make it fail, you do not write it.
- **You test at the level where the defect can arise**, preferring invariants
  to examples and covering the declared boundaries — contracts, persisted
  formats, real edge cases of the domain.
- **A risk not expressible as a test** goes into `UNVERIFIED` with the manual
  verification steps, never compensated with unit tests that miss the point.

Levels, invariants and what not to write:
`.claude/shared/core/testing-guide.md`.
