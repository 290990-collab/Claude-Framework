# Conventions

Cross-cutting rules of form. The working method lives elsewhere: here there is only how things are written.

## Commits

- **Only on the user's explicit request.**
- Messages in English, imperative, first line ≤ 72 characters (`Fix …`, `Add …`, `Remove …`).
- One commit = one logical change. No refactoring mixed with new features.
- The body explains the **why**, not the what (the what is in the diff).
- Never rewrite shared history, never force a push, never skip the automated checks.

## Scope of a change

- Only what is asked; the rest is flagged in the report instead of being done.
- Refactoring, dependency updates and mass reformatting are separate tasks.
- Do not touch generated artefacts: they are regenerated, not edited by hand.

## Names

- A name expresses **what something is or does**, not how it is implemented (avoid types/structures in names).
- Consistency before elegance: use the terminology already present in the project.
- No abbreviations that are not standard in the domain.
- New files follow the naming convention of their neighbours.

## Comments

- They explain **non-obvious constraints**: reasons for non-obvious choices, edge cases or formats imposed from outside.
- Never describe what the code below already expresses.
- Update or remove comments together with the code they describe.
- Delete unused commented-out code: either it is needed now, or it goes.

## Documentation

- User-visible changes are recorded in the registers the project has established.
- Any change to a versioned contract forces a version bump and an explicit note.
- Behavioural documentation must be verified against the real code before being written.

## Non-negotiable minimum quality

- The build must pass after every task.
- No new warning introduced without flagging it.
- No empty error handling: handle or propagate, providing context.
- No dead code for future uses: either it is needed now, or it is not added.

## In this project

[TO FILL IN — language of code and comments, "kind of code → folder" map,
specific naming conventions, where user-visible changes are recorded, which
folders contain generated artefacts not to be touched.]
