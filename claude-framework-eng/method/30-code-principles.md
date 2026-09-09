## Change principles

- **Minimal Safe Change:** the smallest possible change. Solve one problem at a time. Zero unrequested refactoring, renames or style changes.
- **Existing Pattern First:** look for and reuse patterns already in the repo before creating new ones. If the requested feature already exists, it is not rewritten: say where it is and propose only the difference the request added.
- **Contract First:** if you change APIs/interfaces/schemas, first find every consumer (scripts, tests, string references). Report breaks and migrations. The same applies to what you **delete**: code that looks dead must first be searched for as a string.
- **KISS and local style:** the simplest solution, matching the style of the host file.
- **Comments:** only for non-obvious constraints. No chronicle of the code.
- **No shortcut to green:** never make a check pass by weakening it — deleting or skipping a test, rewriting the expected value to match the output, widening an assertion, stubbing the code that has to run. If it does not pass, report that it does not pass.
- **Fail loudly:** no `except` that swallows, no invented defaults to keep going, no fallback branch that hides the cause. A hidden error costs more than a crash.
- **Non-negotiable:** COMMITS, INSTALLATION of dependencies/tools and every IRREVERSIBLE operation (deleting data, rewriting history, overwriting files you have not read) ALWAYS require the user's explicit approval.

## Test principles

- **Quality > quantity:** a test that would pass with the defect present does not count. If you do not know which defect would make it fail, do not write it.
- **Level:** test where the defect can arise (contracts, boundaries, domain invariants), preferring invariants to examples.
- **Untestable risks:** they go into `UNVERIFIED` with the manual verification steps, never compensated with unit tests that miss the point.
- Full guide: `.claude/shared/core/testing-guide.md`.
