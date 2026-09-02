## The design cycle

It slots into the code cycle between *Understand* and *Design*. Here visual
rendering is part of the product: an interface that is correct and ugly is not
a partial success, it is a product that contradicts itself.

**Understand → Direction → Design → Implement → Verify (functional *and*
visual) → Integrate.**

The added step is the second:

**Direction** (`frontend`, before any markup): grid, type scale, palette,
rhythm of space, tone of motion. It is decided **before** writing the first
component, and expressed in tokens, not in adjectives. For ambiguous requests,
plan mode or brainstorming first.

Rules of the cycle:

- **Never jump to markup before deciding the direction.** A component written
  without a system becomes the system, by inertia.
- **Visual verification is neither optional nor automatic.** A green build and
  green tests do not prove it looks right: you look at runtime, and what was
  not looked at goes back into `UNVERIFIED` with the instructions for looking
  at it. An interface task closed without that line is not closed.
- **The unit test covers pure logic**, not rendering. Writing tests on markup
  gives false confidence and breaks at every touch-up.
- **Accessibility and performance are requirements of the cycle**, not a final
  review: they enter the direction, they are not added afterwards.

Operational detail on tokens, motion and accessibility:
`.claude/shared/domain/design-guide.md`.
