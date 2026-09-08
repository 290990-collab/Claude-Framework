## How to write a delegation prompt

The edge rule, non-negotiable: **operative instructions at the margins, data and reference material in the middle.**

### Mandatory structure

```
1. TASK:        [one sentence: what to do]
2. DONE WHEN:   [verifiable completion criterion]
3. CONSTRAINTS: [hard prohibitions, few and specific]
4. MATERIAL:    [excerpts and a list of exact file:line]
5. DONE WHEN:   [repeated identically to point 2]
```

The criterion opens and closes on purpose: if an agent misses the target, almost always it was implicit or sat in the middle.

### Non-negotiable rules

- **Zero `file:line` in prose:** they go only in a list, in the MATERIAL block.
- **Essential constraints:** few and hard. Ten constraints amount to no constraint.
- **Zero echo:** do not repeat what is already in `CLAUDE.md`. Pass only the task's delta.
- **Objective criterion:** verifiable by whoever receives it ("the tests in `tests/x.py` pass and the build is clean"), not "do a good job".
- **Second round (rule 8):** for corrections or iterations continue the existing session sending ONLY the findings. Never rebuild the prompt from scratch.
