---
name: framework-install
description: >
  Installs and adapts the framework in a project: detects whether the project
  is empty or already has code, runs the questionnaire, chooses the agent
  roster, generates CLAUDE.md, the active agents, the guides and the state
  files, and verifies the result. To be used once per project:
  `/framework-install`.
---

# Installing and adapting the framework

You are the coordinator. This procedure requires judgement: you read a project,
ask questions, decide a roster and fill in content. The tooling does only what
is mechanical — assembly, hashing, checks.

**You install nothing** (packages, dependencies, extensions) at any step. If
something seems to be missing, you flag it and ask.

---

## Step 0 — Find and validate the source

The source lives in one of these places, **in this order**: `./framework/`
(copied into the project), `$CLAUDE_FRAMEWORK`, `~/.claude/framework/`. Take the
**first that exists** — not the first that works — and validate it:

```bash
cd <FW>/tools && python -m fwbuild source ..
```

It prints root and version, or what is missing and exits 1.

**If it exits 1, stop here.** Do not create folders and do not write files: a
wrong source discovered halfway leaves a project worse than a virgin one. Ask
the user where the framework is and retry with that path. **Found but
incomplete is an error, not a reason to try the next one.**

From here on `<FW>` is the validated root and `<PRJ>` the project root: replace
them with the real paths, do not leave them literal.

## Step 1 — Detect the kind of installation

```bash
ls -A | head -50
```

- **Empty project** (or only configuration files): the adaptation starts from
  an **idea**, which the user describes in words. Go to Step 3.
- **Existing codebase**: the adaptation starts from the **code**. Go to Step 2.

## Step 2 — Low-cost reconnaissance (only if there is code)

**Do not read the repository yourself.** Delegate to `explorer` — the framework
preaches pre-digested context, and its own installation is the first place
where it must practise it.

Prompt for `explorer`, in the mandatory structure:

```
TASK: map this repository in order to adapt a working framework.

DONE WHEN: you have delivered, in compact form:
  1. languages and stack, with versions where declared
  2. "folder → responsibility" map of the real modules (not generated ones)
  3. build, test and startup commands — taken from the configuration files, not deduced
  4. entry points
  5. presence or absence of: user interface, data pipelines,
     publication configuration, tests, documentation
  6. visible contracts: public APIs, persisted formats, schemas
  7. what looks relevant but is generated or third-party

CONSTRAINTS:
  - read only, no changes
  - do not open heavy artefacts or dependency folders
  - if a command is not declared anywhere, say so instead of inventing it

DONE WHEN: the 7 points above, in compact form, with file:line where needed.
```

If the repository is large, several `explorer`s in parallel on disjoint
subtrees: it is the only agent for which parallelism is free.

## Step 3 — Questionnaire

**One question at a time**, not a single block. Every answer can change the
following questions. Offer concrete options and a recommendation motivated by
the code or by the idea, when you have one.

### Always — four questions

**1. Field of the project** → profile in `<FW>/profiles/`:

| profile | when |
|---|---|
| `software` | applications, services, command-line tools, desktop |
| `library` | libraries and packages: the public contract is the product |
| `web` | sites and applications where visual rendering is part of the product |
| `research` | the product is reproducible evidence, not software that runs |
| `data` | acquisition, transformation and indexing pipelines |

If none fits, ask the user to describe the field and build the roster by hand
starting from the closest profile.

**2. Critical surface** — *"what is the critical surface of this work, that is,
what makes it wrong even with perfect code?"* It determines the reviewer, and
**one** is activated.

The chosen profile already declares one in `critical_surface`: it is the
**field's**, known before knowing the project. Read it to the user as a
starting point — not as an answer given — and have it confirmed, narrowed or
replaced. A project can have one that its field does not imply.

| answer | reviewer |
|---|---|
| **Security** — someone could abuse it | `security-reviewer` |
| **Scientific validity** — the conclusions might not hold | `scientific-reviewer` |
| **Data quality** — it might be wrong upstream | `data-quality-reviewer` |
| **Regulation and licences** — personal data, dependency licences, legal obligations | `compliance-reviewer` |
| **Performance** — only if the requirement is declared and measurable | `perf-analyst` |

Two reviewers only if the project really has two distinct critical surfaces.

**If the answer is not in the table** — the public contract that must not
break, accessibility, operational cost — **you do not invent an agent**: it
would be a role paid by everyone for a single case. The surface is written in
two places: in the *Critical surface* section of `CLAUDE.md`, and in
`final-reviewer`'s project context, as one line of "here verified also means".
Point 4 of its checklist already covers external consumers and contracts; what
it does not know without this line is **which** surface, in this project, comes
before the others.

**3. Style of chat replies**, on **two independent axes**:

*Form* — telegraphic (conclusion first, zero prose) · concise but complete
(default) · explanatory (the **why** of a choice is always explained) ·
discursive.

*Assumed knowledge base* — what can be taken as known and what must be
introduced at first mention. It is the axis that matters most: it says **what
not to explain**. Ask it like this: *"what should I take for granted that you
already know, and what would you rather I explained every time?"*

**4. Autonomy** — what can be done without asking. Conservative default: **none
of this**. Commits · publication · installing dependencies · long or expensive
runs · irreversible changes.

### Conditional — only for what the profile does not already install

**Ask only about agents the roster does not have.** Compute it first (Step 4)
and skip every question whose answer is already installed: a question that
cannot change anything teaches the user that the questionnaire is a formality.

Is there an interface? → `frontend` · Does external data come in? →
`data-ingestion` · Are there measurements to interpret? → `results-analyst` ·
Is literature or academic writing needed? → `literature` · Does the project get
published, and with simple hosting or infrastructure defined as code? →
`deploy` **or** `infra`, never both · Are there heavy operations launched by the
user and not by the agent? → they go into the commands.

Regulatory constraints and performance requirements belong to **question 2**,
not here: they are critical surfaces, not contours of the profile.

## Step 4 — Roster and selective installation

**Only the active is installed.** The master stays in `<FW>/agents/`: an agent
not chosen is not deleted, it is *not yet installed*, and it will be added
later already up to date with `framework-sync --activate`.

Reason: the name and `description` of every file in `.claude/agents/` end up in
the coordinator's context in every session. Keeping 19 instead of 11 is pure
cost on the most expensive file in the system.

**Six cannot be removed** — `explorer`, `architect`, `implementer`, `tester`,
`refactorer`, `final-reviewer`: they are the code cycle, and a project that
skips one is not choosing a roster, it is choosing not to have the cycle.
`drop` ignores them on purpose. Everything else is optional and comes back with
`--activate`, already up to date.

The commands start from `<FW>/tools`: there the framework root is `..`, the
project's is `<PRJ>`.

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import profile
prof = profile.load(Path('../profiles/<PROFILE>.toml'))
print(profile.roster(prof, extras=[], drop=[]))
print('conflicts:', profile.check_exclusive(profile.roster(prof, [], [])))
"
```

## Step 5 — Generation

**Two** documents with a kernel region are generated, not one. The difference
is the recipient, and everything else follows from that.

| document | kernel source | who reads it | cost |
|---|---|---|---|
| `CLAUDE.md` | `<FW>/method/` | **everyone**, at every spawn | always paid |
| `.claude/shared/orchestration.md` | `<FW>/coordinator/` | only whoever delegates | on demand |

**Never put in `CLAUDE.md`** the routing table, the work cycle, the delegation
rules or the state levels: they are instructions a `tester` or an `explorer`
pays for at every spawn and cannot use. The doctor detects it
(`COORDINATOR_LEAK`).

### `CLAUDE.md` — project sections

```
[KERNEL REGION from <FW>/method/]

## The project
one-line description · "path → role" map · HARD constraints (violating them
invalidates the work, not just the code) · contracts, with their consumers

## Commands
build, test, startup · quick check the agent runs · heavy operations the user
launches, with what they must report back

## Critical surface
what the critical surface is — what makes the work wrong even with perfect
code — and who reviews it. It starts from `prof.critical_surface` and from the
answer to question 2: if they coincide you write one line, if they diverge both
hold

## Current state
empty at birth — it is level 3 of the self-updating state

## Shared guides
first line: `orchestration.md`, only for the coordinator and first if the
session delegates. Then the domain guides installed, with when to open them

## Reply style
form and assumed knowledge base, from the answers to Step 3
```

### `.claude/shared/orchestration.md` — project sections

```
[KERNEL REGION from <FW>/coordinator/]

## This project's roster
table GENERATED from the real roster, never copied: | Situation | Agent | Model |
one row per installed agent, none excluded.
**The columns are a contract**, not a matter of style: the doctor reads the
agent name in backticks in the **second** one. Swapping them produces an
all-orphan roster and names that do not exist

## Delegation notes for this project
operations the user launches and not the agent · specific parallelism
constraints · when to skip a step of the cycle
```

### Assembly

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import assemble
F = Path('..'); V = (F/'VERSION').read_text(encoding='utf-8').strip()
P = Path('<PRJ>')
for d in ('.claude/shared', '.claude/agents', '.claude/skills', 'docs'):
    P.joinpath(d).mkdir(parents=True, exist_ok=True)
P.joinpath('CLAUDE.md').write_text(
    assemble.build_document(F/'method', V, PROJECT_SECTIONS), encoding='utf-8')
P.joinpath('.claude/shared/orchestration.md').write_text(
    assemble.build_document(F/'coordinator', V, ROSTER_SECTIONS), encoding='utf-8')
"
```

**Active agents** — for each one: read the source with `assemble.split_source`,
**fill in the `## Project context` block** with the specific directives (every
block declares in its placeholder what to put there), reassemble with
`assemble.build_agent`, write into `.claude/agents/`.

**Domain cycles** — if the profile declares `cycles`, the corresponding files
from `<FW>/cycles/` are appended to the kernel region of the coordinator's
guide (`extra=assemble.cycle_files(...)`): they are orchestration, not
execution, so they do not go into `CLAUDE.md`.

**Guides** — copy from `<FW>/shared/` those of the profile **plus those the
chosen agents cite**, filling in the project block there too. An extra brings
its own: without them, the card goes out with a dead pointer and the doctor
sees it only once the installation is already written (`SHARED_MISSING`).

```python
sorted(set(prof.shared) | set(profile.required_guides(F, roster)))
```

**Lifecycle skills** — copy `<FW>/skills/framework-doctor` and
`framework-sync` into `.claude/skills/`. Without them they are not invocable in
the project and the doctor flags it (`SKILLS_MISSING`).

**`.claude/settings.json`** — serialise `Profile.settings` to JSON.

**`.claude/framework.json`** — `source`, `version` and `profile`: it is how
`framework-doctor` and `framework-sync` find the source again later, and the
only place that records **what** the installation is made of. Without the
profile, "regenerate the permissions of the project's profile" is an instruction
that cannot be carried out. The shape **is not written by you**:
`source.manifest` makes the path relative when the source sits inside the
project — the first of the three supported ways — and absolute only when it sits
outside. An absolute path to an internal source is the machine of whoever
installed it, and it dies at the first clone.

```python
source.manifest(PRJ, FW, version, prof.name)
```

The `accepted` field **is not written at installation**: it is born empty and is
added by whoever decides to live with a warning. What belongs in it and what
does not: the `framework-doctor` skill.

**State files** — copy the three templates into `docs/` and fill in every
`[TO FILL IN — …]` block **immediately**: the first real entry and the first
step in `TODO.md` with today's date, the first goal with its criterion in
`roadmap.md`. `status.md` is born empty by construction — you write in it when
something closes. The sections that may legitimately stay empty (waiting,
blocked, open decisions) carry no placeholder: they already hold the right text
for an empty section, and it is replaced when there is something. It must be
done here, not later: at Step 6 a residual placeholder is a `PLACEHOLDER`, and
`TODO.md` is the file every future session reads first.

### Note on `@import`

If `CLAUDE.md` supports `@import` in the version of Claude Code in use, the
assembly could stay virtual. **It must be verified, not assumed.** The default
is physical concatenation, which does not depend on any feature of the harness.
Do not introduce `@import` without having first verified that they work.

## Step 6 — Verification

```bash
cd <FW>/tools && python -m fwbuild doctor --strict <PRJ>
```

It must print `OK — no findings` and exit 0. `--strict` makes the rule
mechanical: **as long as one finding remains, of any severity, the installation
is not complete.** What each code means and what to do about it: skill
`framework-doctor`.
