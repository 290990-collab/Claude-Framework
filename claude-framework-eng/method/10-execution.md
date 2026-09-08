## Execution obligations

They hold for every agent that receives a task, coordinator included when it works directly.

- **No sub-delegation:** subagents spawn no other agents. If work outside your mandate is needed, report it to the coordinator.
- **Strict scope:** execute *only* the assigned task. Any extra problem noticed goes into the report, NEVER into the diff.
- **Range reads:** read the `file:line` ranges you receive, not whole files. Widen only if the excerpt is not enough, and say so.
- **Zero redundancy:** build/tests passed and no file changed → do not re-run.
- **Stop criterion:** no verifiable completion criterion → ask for it before proceeding.
