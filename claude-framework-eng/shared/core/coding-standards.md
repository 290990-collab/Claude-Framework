# Coding standards

Language-independent writing rules, plus the block for this project's stack.
The conventions of form (names, commits, comments) live in `conventions.md`;
here there is how code is structured.

## Functions

- **One level of abstraction per function.** If a function alternates low-level
  details and high-level decisions, it is two functions.
- Few nested conditions: returning early on degenerate cases leaves the main
  path flat and readable.
- Boolean arguments that change behaviour are two functions disguised as one.
- A function that returns a value **and** modifies observable state is hard to
  use correctly: separate them where possible.
- The return value also represents the "not found" or "not applicable" case
  explicitly, not with an ambiguous special value.

## State and mutability

- Immutable by default; mutable where it is really needed and in a narrow
  scope.
- No mutable global state: it makes every test order-dependent and every defect
  irreproducible.
- A data structure is not left in an invalid intermediate state, not even
  temporarily, if someone else can observe it.

## Errors

- An expected error is part of the contract and is represented in the return
  type or in the declared exception; an unexpected error propagates.
- You catch only what you know how to handle. Catching everything and carrying
  on turns a fault into silent corruption.
- Context is added on the way up: which operation, on which datum — never the
  secret or the personal datum.
- Resource cleanup is guaranteed on the error path too, with the language
  construct meant for it.

## Dependencies

- Every dependency is a permanent cost: maintenance, security, updates. For a
  few lines of code, you write the lines.
- External dependencies are isolated behind a project boundary, so replacing
  them touches a single point.
- **No installation without the user's explicit confirmation.**

## Concurrency

- Share as little as possible; where you share, the access protocol is explicit
  and documented.
- No assumption about execution order that is not guaranteed.
- Every wait has a time limit; every retry has a maximum.

## Readability

- New code imitates the file it lives in: consistency before preferences.
- Formatting is automatic where a tool exists: it is not argued by hand.
- The complexity that remains is the problem's, not the one added by the
  implementation. If a function is hard to read and the problem is not hard,
  the function is wrong.

## In this project

[TO FILL IN — languages and versions, formatting and static analysis tools with
their commands, stack-specific conventions, patterns adopted and patterns
explicitly discarded, runtime constraints that limit what can be used.]
