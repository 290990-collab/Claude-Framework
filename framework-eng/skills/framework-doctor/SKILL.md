---
name: framework-doctor
description: >
  Checks the integrity of a framework installation: unfilled placeholders, a
  roster inconsistent with the routing table, missing guides, drift of the
  kernel region, absent state files. Use when something does not add up, after
  hand edits to the framework, or before updating it.
---

# Diagnosing an installation

```bash
cd <FW>/tools && python -m fwbuild doctor --strict <PRJ>
```

`<FW>` is the `source` field of `.claude/framework.json`; if the file is
missing, `./framework/`. That field may be **relative to the project root** —
`source.dereference(<PRJ>, source)` resolves it. `<PRJ>` is the project root.
`fwbuild` has **four** subcommands: `doctor`, `source`, `cost` and `report`.
The modes of `framework-sync` (`--down`, `--up`, `--activate`, `--deactivate`)
belong to that skill instead, they are not shell flags.

A complete installation prints `OK — no findings`. Without `--strict` the exit
code is 0 even with warnings only: always use it, in CI and by hand.

`--json` prints the same findings plus the measurement of `CLAUDE.md` in a
single structure, for CI: the exit code does not change.

## How to read each finding

### `PLACEHOLDER` — ERROR

A `[TO FILL IN]` block or a `{{placeholder}}` was left unfilled. The agent
reading it receives instructions instead of directives.

**What to do:** open the file, read what the placeholder asks to be written,
and fill it with the project's real directives. If the information is not
there, ask the user — do not invent it.

### `ROSTER_MISSING` — ERROR

An agent is cited in the routing table of `.claude/shared/orchestration.md` (or
of `CLAUDE.md`, if that guide is absent) but the file does not exist in
`.claude/agents/`. The coordinator will try to delegate to something that is
not there.

**What to do:** either install the agent (`framework-sync --activate <name>`,
which takes the current version from the master), or remove the row from the
table.

### `ROSTER_ORPHAN` — WARNING

The agent's file exists but does not appear in the routing table. The agent
exists, costs context in every session, and will never be chosen.

**What to do:** either add it to the table, or deactivate it
(`framework-sync --deactivate <name>`). No exceptions: an installed agent that
is not in the table is either superfluous, or the table is incomplete.

### `SHARED_MISSING` — ERROR

An installed file — `CLAUDE.md`, an agent, a guide — points at a guide that was
not installed. A broken pointer is worse than an absent one: the agent tries
and finds nothing. The finding says **which file** it starts from.

Special case: **`.claude/shared/orchestration.md` absent** while installed
agents exist. It is the coordinator's guide — without it, whoever delegates has
neither the delegation rules nor the routing table, and the doctor cannot even
check the roster.

**What to do:** copy the guide from `<FW>/shared/` and fill in its project
block, or remove the pointer. For `orchestration.md`, regenerate it by
assembling `<FW>/coordinator/` and adding the project's routing table.

### `SHARED_ORPHAN` — WARNING

A guide is installed in `.claude/shared/` and no file cites it. It is context
the project carries around and never opens: cost without use, the exact inverse
of `SHARED_MISSING`.

**What to do:** either cite it from where it is needed — generic guides are
listed in `CLAUDE.md § Shared guides`, role guides are pointed at by the agent
that uses them — or remove it from the installation.

### `COORDINATOR_LEAK` — WARNING

`CLAUDE.md` contains a section that belongs to the coordinator's guide: the
delegation rules, the work cycle, the prompt template, the state levels, the
disambiguation between agents.

**Why it is a problem.** `CLAUDE.md` is loaded into **every** context,
including every subagent's. An `explorer` on Haiku looking for a function pays
for the code cycle and the four levels of state, and can use none of it — it
does not delegate and does not write state. Over a session with ten spawns it
is pure waste on the most expensive file in the system.

**What to do:** move the section into `.claude/shared/orchestration.md` and
leave at most a one-line pointer in `CLAUDE.md`. If the content is really
needed by whoever executes and not only by whoever delegates, then rewrite it
as an execution obligation — that is a different thing, and it lives in
`<FW>/method/`.

⚠️ The check compares **titles**, not meaning: the same section reworded under
a different title does not trigger it. On content leakage, reading is what
counts; the finding covers only the six known titles.

### `KERNEL_MISSING` — ERROR

The kernel region's markers have disappeared from a file that has one by
construction — `CLAUDE.md`, `orchestration.md`, an agent. **It is more serious
than drift:** with the markers, the check disappears, and a method rewritten by
hand becomes indistinguishable from the generated one. It does not trigger if
**no** tracked file has markers: that is the installation without tracking, and
it is a choice.

**What to do:** reassemble the file with `framework-sync --down`, after
comparing the current content with the source — inside there may be a change
worth promoting.

### `KERNEL_DRIFT` — WARNING, and it is not an error

The kernel region was modified by hand. **This is information, not a fault.**
The framework does not forbid modifying the method: it makes the modification
visible.

**There is only one right question to put to the user:**

> "You modified the method in `<file>`. Is it an improvement that holds for all
> projects — so I promote it into the source — or is it a derogation specific
> to this project?"

- **Improvement** → `framework-sync --up`: it goes up into the source,
  increments the version, and the next project is born with it inside. It is
  the direction that did not exist in previous frameworks, and the reason the
  method had forked into four different versions.
- **Local derogation** → it is noted in the project so that the next person to
  read the finding knows it is deliberate.

Never "correct" a drift by overwriting it without having asked that question:
you would throw away a change someone had a reason to make.

### `VERSION_MISMATCH` — WARNING

The project's kernel regions do not all declare the same version, or the
project is on a different version from the source. **No other finding sees it:**
on an old method the hash matches, because it matches the old one. It is the
fork between projects, that is, the defect the framework exists to avoid.

**What to do:** `framework-sync --down`, on **both** versioned documents and on
every installed agent. A gap between a single agent and the rest is normal
right after an `--activate`, which takes the current master: it is closed with
the same `--down`.

### `SETTINGS_MISSING` — WARNING

`.claude/settings.json` is absent, but the project has installed agents. It is
the file that carries the profile's permissions — among them the prohibition on
reading `.env`, keys and certificates: without it, that prohibition is not in
force and nobody notices.

**What to do:** regenerate it by serialising the `Profile.settings` of the
project's profile, as in Step 5 of the installation.

### `SKILLS_MISSING` — WARNING

`framework-doctor` or `framework-sync` are not in `.claude/skills/`: they exist
in the source but are not invocable in this project. Nobody notices until they
are needed — that is, when something has already gone wrong.

**What to do:** copy them from `<FW>/skills/` into `.claude/skills/`. No
adaptation is needed: they are framework files, copied verbatim.

### `STATE_MISSING` — ERROR

One of `docs/TODO.md`, `docs/status.md`, `docs/roadmap.md` is missing.

**What to do:** copy the missing template from `<FW>/templates/`. Without level
1, every session restarts by guessing.

### `FABLE` — ERROR

`model: fable` was generated. That model is not available: the agent does not
start.

**What to do:** replace it with `model: opus`. For `architect`,
`effort: xhigh`.

### `EXCLUSIVE` — ERROR

`deploy` and `infra` are installed together. They cover the same space with
opposite postures — simple publication versus infrastructure defined as code —
and the overlap produces ambiguous routing.

**What to do:** choose which one really describes this project and deactivate
the other.

### `TOKEN_BUDGET` — WARNING

The project sections of `CLAUDE.md` have exceeded the kernel region in words.
The ceiling that breaks the build sits on the **source** and constrains only
the method; the assembled `CLAUDE.md` is instead what every subagent pays at
**every spawn**, and the part the installation writes had no threshold at all —
and it is the only one that grows, because it grows with the project.

The threshold is the kernel itself, that is, the only known quantity: *the
project does not write more than the method*. It does not come from a measure
of effectiveness — none exists — it is a judgement call, and must be treated as
such. Below the ceiling the framework sets itself for the method alone the
finding stays silent: on a small file the ratio is true and irrelevant.

**What to do:** do not cut at random. Move into `.claude/shared/` what only a
few agents need and leave the pointer, remove what the repository already says
by itself (structure that can be derived, commands already in a `Makefile` or
in `package.json`), and keep in `CLAUDE.md` only what an agent cannot deduce:
hard constraints, contracts with their consumers, the critical surface. If
after the cut the file stays over the threshold because the project really is
large, it is a warning to accept knowingly, not an error.

To turn it into a figure: `python -m fwbuild cost <PRJ> --spawns N --devs N`.

### `REPORT_FORMAT` — WARNING

The installed report schema still carries confidence as a percentage. It is the
previous format: fake precision in the field the coordinator reads first, while
a model's self-reported confidence is poorly calibrated.

No other finding sees it: the kernel region's hash matches, because it matches
that very text, and the declared version is the one the project was born with.

**What to do:** `framework-sync --down`. The current format is categorical and
carries the falsifier (`REFUTE`) with it, which is what makes a judgement
without numbers readable.

## Several projects at once

```bash
cd <FW>/tools && python -m fwbuild report <folder-of-repositories>
```

`doctor` answers "does this installation hold?". `report` answers a question a
single person does not ask and whoever has forty repositories does: **how many
versions of the method are out there, and where**. It looks for
`.claude/framework.json` under the given paths (two levels, `--depth` to change
that), calls the doctor on each and lines up version, findings and the size of
`CLAUDE.md`.

The reference is the version of the **source** you run from, not the most
widespread one: the majority is not a reference. `--strict` exits 1 if a
project diverges or has findings; `--json` gives the same report for CI.

## After the diagnosis

Report to the user: how many findings by severity, what you corrected, what
requires a decision from them. `KERNEL_DRIFT` findings are always listed, even
when everything else is clean: they are the useful part of the report.
