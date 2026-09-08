---
name: framework-sync
description: >
  Aligns an installation with the source framework: brings a new version of the
  method down while preserving the adaptation, promotes a local change up so
  the next project inherits it, activates or deactivates an agent. Use when a
  new version comes out or when a local change deserves to become general.
---

# Synchronisation with the source

Connects the **source** (the master) to the **installations** (the projects). Requirement: the source must be reachable from the machine; if it is not, only `doctor` is usable.

`--down`, `--up`, `--activate`, `--deactivate` are **modes of this skill**, not shell flags: `fwbuild` has `doctor`, `source`, `cost` and `report`. The divergence report across several repositories — `python -m fwbuild report <folder>` — is from the shell instead: it reads many projects and modifies none.

The snippets start from `<FW>/tools`. `<PRJ>` is the project root; `<FW>` is the `source` field of `.claude/framework.json` (if missing, `./framework/`), which may be **relative to the project root**, not to the directory you run from: resolve it with `source.dereference(<PRJ>, source)`.

---

## `--down` — bringing a new version into the project

Updates the method while preserving the adaptation.

1. **Compare the versions:** the project's is in the kernel region's marker, the source's in `<FW>/VERSION`.
2. **Diagnosis first.** `KERNEL_DRIFT` findings must be resolved *first*: updating over a local change erases it silently.
3. **Reassemble** with the new method and the existing project sections, extracted from the current installation and rewritten unchanged.

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import assemble, kernel
p = Path('<PRJ>/CLAUDE.md')
text = p.read_text(encoding='utf-8')
region = kernel.parse(text)
sections = text[region.end:].lstrip('\n')          # the adaptation, unchanged
version = Path('../VERSION').read_text(encoding='utf-8').strip()
p.write_text(assemble.build_document(Path('../method'), version, sections), encoding='utf-8')
"
```

4. **Same operation on `.claude/shared/orchestration.md`**, with the kernel from `<FW>/coordinator/`: the versioned documents are **two**, updating only one leaves them misaligned. There the domain cycles are **inside** the region and the project does not record which profile it was born from: they must be passed again with `extra=assemble.installed_cycles(region.body, Path('..'))`, or they disappear without any finding seeing it.
5. **Same operation on every installed agent**, with `split_source` and `build_agent`: front matter and the `## Project context` block stay the project's, the method comes from the master.
6. **Verify** with `doctor`: it must exit 0.

**Conflicts are presented, they do not resolve themselves:** on a region modified locally the user must see both versions and decide.

---

## `--up` — promoting a local change into the source

1. **Locate the change:** `doctor` flags it as `KERNEL_DRIFT`; the content is obtained by comparing the project's kernel region with the corresponding source.
2. **Ask whether it holds for everyone.** An improvement to the method goes up, a derogation specific to that project does not: the question is put to the user, not decided.
3. **Apply it to the source**, and the choice of destination is **by
   recipient**:

   | the change concerns… | it goes in |
   |---|---|
   | what holds for anyone executing a task | `<FW>/method/` |
   | when to delegate, to whom, with what prompt, the project's state | `<FW>/coordinator/` |
   | the mandate of a specific role | `<FW>/agents/<name>.md` |
   | reference material of a domain | `<FW>/shared/` |

   Getting this wrong costs: a delegation rule in `method/` is paid by every subagent at every spawn without being usable; an execution rule in `coordinator/` will never be seen by whoever executes.
4. **Increment `<FW>/VERSION`:** correction → patch; new or reworded rule → minor; structural change → major.
5. **State what changed**, so whoever updates knows what they receive.
6. **Realign the originating project** with `--down`, so the hash matches again.

⚠️ **A translation of this source is a source of its own**, with its own `VERSION`: `--up` does not reach it. A rule that holds in every language has to be carried across by hand — until it is, the two editions say different things.

---

## `--activate <agent>` / `--deactivate <agent>`

**Activating** copies the agent from the master at its **current version**, fills in its `## Project context` block and adds the row to the routing table in `.claude/shared/orchestration.md` — never in `CLAUDE.md`: routing is coordinator content.

Mandatory shape of the row, because the doctor reads it:

```
| Situation | `agent-name` | Model |
```

The name goes in backticks in the **second** column. Anywhere else, that agent shows up as `ROSTER_ORPHAN` and the table cites a `ROSTER_MISSING` that does not exist.

Activating later is *better* than a dormant file: you always take the latest version, not one frozen at installation day.

**Deactivating** removes the file from `.claude/agents/` and the row from the routing. **The master is not touched.** If the project block held information that cannot be reconstructed, save it first.

Always check for conflicts after an activation:

```bash
cd <FW>/tools && python -c "
from fwbuild import profile
import pathlib
present = sorted(p.stem for p in pathlib.Path('<PRJ>/.claude/agents').glob('*.md'))
print('conflicts:', profile.check_exclusive(present) or 'none')
"
```

Always close with `doctor`.

---

## Change of field

A project does not stay where it was born: a library grows a demo, a tool becomes a service. The field lives in `profile` inside `.claude/framework.json`, the only place that knows it. No dedicated mode: these are the same four operations of an installation, on the new profile.

1. **Roster** — `--activate` what the new field implies, `--deactivate` the rest. Check for conflicts afterwards.
2. **Guides** — copy the new profile's guides plus the ones the activated agents cite (`profile.required_guides`). The old ones nobody cites any more are found by the doctor as `SHARED_ORPHAN`.
3. **Cycles** — reassemble the coordinator's guide appending the new field's (`assemble.cycle_files`), or without them if it drops them. They live **inside** the kernel region: no finding sees them vanish.
4. **Permissions** — regenerate `.claude/settings.json` from the new profile's `Profile.settings`.

Then update `profile` in `framework.json`. Skipping it leaves the project declaring a field it no longer has: the next maintenance regenerates the wrong permissions and no finding notices — the file declares, it does not verify.
