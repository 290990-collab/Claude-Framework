# Conventions

Cross-cutting rules of form. The working method lives elsewhere: here there is
only how things are written.

## Commits

- **Only on the user's explicit request.**
- Messages in English, imperative, first line ≤ 72 characters: `Fix …`,
  `Add …`, `Remove …`.
- One commit = one logical change. Never refactoring and features together: the
  first hides the second in review.
- The body explains **why**, not what: the what is in the diff.
- Never rewrite an already shared history, never force a push, never skip the
  automated checks.

## Scope of a change

- Only what is asked; the rest is flagged in the report instead of being done.
- Refactoring, dependency updates and mass reformatting are separate tasks:
  mixed with something else they make the diff unreadable.
- Do not touch generated artefacts: they are regenerated, not edited by hand.

## Names

- A name says **what something is or does**, not how it is implemented. A name
  containing the type or the structure ages at the first change.
- Consistency before elegance: if the project calls something one way, it is
  called that everywhere. Two names for the same concept cost more than one
  imperfect name.
- No abbreviations that are not standard in the domain.
- New files follow the convention of their neighbours, not a personal
  preference.

## Comments

- They explain **non-obvious constraints**: why this choice instead of the
  obvious one, which edge case forced a strange line, which external reference
  imposes a format.
- Never a chronicle of what the line below already says.
- A comment describing changed code is worse than no comment: it is updated
  along with the code or removed.
- Code commented out "for later" is not left: either it is needed, or it goes.

## Documentation

- User-visible changes are recorded where the project records them.
- A versioned contract that changes forces a version bump and saying so.
- Documentation that describes behaviour must be verified against the real code
  before writing it: it is the point where the two silently diverge.

## Non-negotiable minimum quality

- The build passes after every task.
- No new warning knowingly introduced without flagging it.
- No empty error handling added: handle or propagate, with context.
- No dead code "for later": either it is needed now, or it is not added.

## In this project

[TO FILL IN — language of code and comments, "kind of code → folder" map,
specific naming conventions, where user-visible changes are recorded, which
folders contain generated artefacts not to be touched.]
