## Change principles

- **Minimal Safe Change:** the smallest possible change. Solve one problem at a time. Zero unrequested refactoring, renames or style changes.
- **Existing Pattern First:** look for and reuse patterns already in the repo before creating new ones.
- **Contract First:** if you change APIs/interfaces/schemas, first find every consumer (scripts, tests, string references). Report breaks and migrations.
- **KISS and local style:** the simplest solution, matching the style of the host file.
- **Comments:** only for non-obvious constraints. No chronicle of the code.
- **Non-negotiable:** COMMITS and INSTALLATION of dependencies/tools ALWAYS require the user's explicit approval.

## Test principles

- **Quality > quantity:** a test that would pass with the defect present does not count. If you do not know which defect would make it fail, do not write it.
- **Level:** test where the defect can arise (contracts, boundaries, domain invariants), preferring invariants to examples.
- **Untestable risks:** they go into `UNVERIFIED` with the manual verification steps, never compensated with unit tests that miss the point.
- Full guide: `.claude/shared/core/testing-guide.md`.
