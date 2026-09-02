## How to write a delegation prompt

The edge rule — instructions at the margins, reference material in the middle —
holds here more than anywhere else. Mandatory structure:

```
1. TASK          one sentence: what to do
2. DONE WHEN     the completion criterion, verifiable
3. CONSTRAINTS   the hard prohibitions — few, explicit
4. MATERIAL      excerpts with exact file:line (the long part: it sits in the
                 middle because it is consulted, not because it matters less)
5. DONE WHEN     repeated, verbatim
```

The criterion is written twice on purpose: it opens and closes. **If an agent
misses the target, almost always the criterion was implicit or sat in the
middle.**

Practical rules:

- **Never a `file:line` buried in prose.** It goes in a list, in the material
  block.
- **Few, hard constraints.** Ten constraints amount to no constraint: the ones
  that matter are chosen, not accumulated.
- **No echo and no context the agent will not use** — what is in `CLAUDE.md` it
  already has, and every extra line pushes towards the middle something that
  belonged on an edge.
- **The criterion must be verifiable by whoever receives it.** "Do a good job"
  is not a criterion; "the tests in `tests/x.py` pass and the build is clean"
  is.

For a second round on the same agent, rule 8 applies: you continue the existing
conversation and send **only the delta** — the findings to resolve — not a new
prompt that re-digests the context from scratch.
