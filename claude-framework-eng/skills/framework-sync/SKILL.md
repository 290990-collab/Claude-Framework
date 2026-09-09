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

`--down`, `--up`, `--upgrade`, `--activate`, `--deactivate` are **modes of this skill**, not shell flags: `fwbuild` has `doctor`, `source`, `cost` and `report`. The divergence report across several repositories — `python -m fwbuild report <folder>` — is from the shell instead: it reads many projects and modifies none.

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
6. **Update `version` in `.claude/framework.json`**, leaving `source`, `profile` and `accepted` as they are. No step did it: the manifest kept declaring the previous version, and it is the only one readable without opening a generated document. The doctor now sees it (`VERSION_MISMATCH`).
7. **Verify** with `doctor`: it must exit 0.

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
4. **Record the base, if it is not there already**, **before** touching `VERSION`:

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   F = Path('..')
   if upgrade.read_record(F) is None:
       print(upgrade.write_record(F, (F/'VERSION').read_text(encoding='utf-8').strip(),
                                  '<EDITION>', '<repository URL>'))
   "
   ```

   From here on `VERSION` is no longer a published number, and without this line nobody knows which release the source came from any more: it is the only thing that makes your work recoverable at the next upgrade (→ `--upgrade`). **If the record is already there it is not touched:** the base stays what it is, however many promotions you make.
5. **Increment `<FW>/VERSION`:** correction → patch; new or reworded rule → minor; structural change → major.
6. **State what changed**, so whoever updates knows what they receive.
7. **Realign the originating project** with `--down`, so the hash matches again.

⚠️ **A translation of this source is a source of its own**, with its own `VERSION`: `--up` does not reach it. A rule that holds in every language has to be carried across by hand — until it is, the two editions say different things.

---

## `--upgrade` — bringing a new release over a modified source

Only for those who have used `--up`: an untouched source is updated by replacing it. The absence of `upstream.json` **is** that answer, not a fault.

1. **Get the new release** where it disturbs nothing, and from there `<NEW>` is the edition folder inside the clone:

   ```bash
   git clone <repo> <NEW>   # or: git -C <existing clone> pull
   ```

2. **Rebuild the base**, that is the edition as it was at the release your source came from. `upgrade.base_version(<FW>)` gives the number; in the clone, the base is the commit where that edition's `VERSION` held that number, extracted where it touches nothing:

   ```bash
   git -C <NEW> log --format=%H -- <EDITION>/VERSION   # newest first
   git -C <NEW> show <commit>:<EDITION>/VERSION        # until it matches
   git -C <NEW> worktree add --detach <BASE> <commit>
   ```

   **Wrong base, useless comparison:** if no commit matches — wrong repository, truncated history, a number never published — stop and ask. Do not fall back on `VERSION`: that is the right answer only when `upstream.json` is missing.

3. **Classify**, writing nothing:

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   plan = upgrade.classify(Path('<BASE>/<EDITION>'), Path('<FW>'), Path('<NEW>/<EDITION>'))
   for name in ('theirs', 'yours', 'conflict'):
       print(name, len(getattr(plan, name)), getattr(plan, name)[:20])
   "
   ```

   | outcome | what it means | what you do |
   |---|---|---|
   | `same` | you and the release say the same thing — including when your addition landed upstream identical | nothing |
   | `theirs` | you left it as it was and upstream changed it | copy from the release |
   | `yours` | you changed it and upstream did not | **keep yours** |
   | `conflict` | changed by both, differently | the user decides |

4. **Show the plan before applying it**, with the counts and the conflicting paths. `same`, `theirs` and `yours` are mechanical: the second are applied by copying from the release, the third by not touching them.
5. **One conflict at a time:** read the three versions — base, yours, new — and propose a merge that keeps your addition *inside* the new text, not beside it. If your change is already covered by the new text, take that and say so. No conflict is resolved without showing the user what they lose.
6. **`VERSION` is not a conflict:** you take the release's. A source declaring a number that was never published is what created the problem.
7. **Rewrite the record** with the release just taken: it is the base of the next upgrade.

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   F = Path('..')
   print(upgrade.write_record(F, (F/'VERSION').read_text(encoding='utf-8').strip(),
                              '<EDITION>', '<repository URL>'))
   "
   ```

8. **Close with `--down` on the projects**, which are now one version behind, and with `doctor` on each.

⚠️ The source is upgraded **in place**: copy it aside before applying. It is the only operation of this skill that touches the master, and it has no undo.

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
2. **Guides** — copy the new profile's guides plus the ones the activated agents cite (`profile.required_guides`), and add the line in `CLAUDE.md § Shared guides`: what the guide holds, taken from the line under its title. The doctor demands that the path be cited (`SHARED_ORPHAN`), not that the line be written well: that is on whoever installs.
3. **Cycles** — reassemble the coordinator's guide appending the new field's (`assemble.cycle_files`), or without them if it drops them. They live **inside** the kernel region: no finding sees them vanish.
4. **Permissions** — regenerate `.claude/settings.json` from the new profile's `Profile.settings`, **merging** it into the existing file: the old field's `deny` goes, whatever the user added stays. A flat regeneration deletes permissions no profile ever wrote.

Then update `profile` in `framework.json`. Skipping it leaves the project declaring a field it no longer has: the next maintenance regenerates the wrong permissions and no finding notices — the file declares, it does not verify.
