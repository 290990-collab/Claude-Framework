# Claude Framework

An installable working method for **Claude Code**: specialised agents, delegation
rules, domain guides and state files, generated into a project and then
**verifiable** — with a tool that tells you when the installation has broken, and
a channel for pushing improvements back up into the source.

> **Italiano** — lo stesso framework, interamente in italiano, sta in
> [`claude-framework-it/`](claude-framework-it/README.md). Se ne installa uno,
> non entrambi.

---

## What it solves

Anyone using Claude Code across several projects ends up with a hand-written
`CLAUDE.md` for each. After a few months the versions have diverged, nobody knows
which one is the good one, and the file has grown until every subagent pays for
context it cannot use.

The framework attacks the three causes:

| Problem | What the framework does |
|---|---|
| The method forks between projects | One versioned source; `framework-sync` carries versions down and improvements up |
| Hand edits disappear | The generated method lives in a **kernel region** with a hash: editing it is allowed, but it becomes visible |
| `CLAUDE.md` bloats and costs | Split by **recipient**: whoever delegates reads a separate file the others never pay for |

---

## Requirements

- **Claude Code**
- **Python 3.11+** — for the tooling only, and only `tomllib` from the stdlib

Nothing to install.

---

## Installation

Done **once per machine**. From then on, every new project is one line.

```bash
git clone https://github.com/290990-collab/Claude-Framework.git ~/.claude/claude-framework
cp -r ~/.claude/claude-framework/claude-framework-eng ~/.claude/framework
cp -r ~/.claude/framework/skills/framework-install ~/.claude/skills/
```

```powershell
git clone https://github.com/290990-collab/Claude-Framework.git $HOME\.claude\claude-framework
Copy-Item -Recurse $HOME\.claude\claude-framework\claude-framework-eng $HOME\.claude\framework
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-install $HOME\.claude\skills\
```

For Italian, use `claude-framework-it` in place of `claude-framework-eng`.

The destination is named `framework/` because that is one of the places the
installer looks in. It searches in this order: `./framework/` inside the project,
`$CLAUDE_FRAMEWORK`, `~/.claude/framework/`. To keep the source elsewhere, the
environment variable is enough.

To check that a source is valid:

```bash
cd ~/.claude/framework/tools && python -m fwbuild source ..
```

---

## Usage

### The three skills

| Skill | When | What it does |
|---|---|---|
| `/framework-install` | **once per project** | Reads the project, runs the questionnaire, picks the roster, generates everything, verifies the result |
| `/framework-doctor` | when something is off | 18 checks on the installation, each with its remedy |
| `/framework-sync` | maintenance | Carries versions **down** into the project, improvements **up** into the source, activates or deactivates an agent |

The modes of `framework-sync` — `--down`, `--up`, `--activate <agent>`,
`--deactivate <agent>` — are asked of the skill in natural language: **they are
not shell flags.**

### What it writes into a project

`/framework-install` with the `software` profile produces:

```
CLAUDE.md                        common method + project context
.claude/framework.json           source, version, profile
.claude/settings.json            profile permissions (including the ban on reading secrets)
.claude/agents/                  9 cards: only the chosen roster
.claude/shared/orchestration.md  delegation rules + routing table — only for whoever delegates
.claude/shared/core/             6 guides, opened on demand
.claude/skills/                  framework-doctor, framework-sync
docs/TODO.md                     where we are right now
docs/status.md                   closed decisions and measured results
docs/roadmap.md                  where it is going
```

The `[TO FILL IN — …]` blocks are the points the installer fills in with you
during the questionnaire: they are the project's context, the only part that gets
personalised.

### The five profiles

| Profile | Agents | Added cycles | For |
|---|---:|---|---|
| `software` | 9 | — | Applications and services |
| `library` | 9 | — | Libraries and packages |
| `web` | 11 | design | Sites and interfaces |
| `data` | 12 | — | Pipelines and data |
| `research` | 11 | research | Experiments and measurements |

Six agents are always present — `explorer`, `architect`, `implementer`, `tester`,
`refactorer`, `final-reviewer`: they are the code cycle. The master holds **19**;
the rest are added with `--activate`.

---

## Commands

All run from `<source>/tools`.

| Command | Answers |
|---|---|
| `python -m fwbuild doctor <project>` | "Does this installation hold?" |
| `python -m fwbuild source <source>` | "Is this source valid?" |
| `python -m fwbuild cost <project>` | "What does the common context cost?" |
| `python -m fwbuild report <folder>` | "How many versions are out there, and where?" |

Options that matter:

| Flag | On | Effect |
|---|---|---|
| `--strict` | `doctor`, `report` | Exits 1 on warnings too. **Always use it**, in CI and by hand |
| `--json` | `doctor`, `report` | Same content in a single structure. Does not change the exit code |
| `--spawns N --devs N --price N` | `cost` | Turns words into tokens and into real spend |
| `--depth N` | `report` | How many levels down to look for installations |

```
$ python -m fwbuild doctor --strict ../../my-project
OK — no findings

$ python -m fwbuild cost ../../my-project --spawns 200 --devs 12
CLAUDE.md: 1,602 words ≈ 2,131 tokens, paid at every spawn.
  of which kernel 1,303 (with a ceiling) and project 299 (without).
200 spawns a day × 12 people = 5.1 million tokens a day of common context alone.
```

The doctor produces 18 findings at three levels: **ERROR** (broken installation),
**WARN** (a judgement), **NOTE** (a warning the project declares it accepts, in
`framework.json`, with a written reason — errors cannot be accepted).

---

## The maintenance loop

The generated method lives inside a delimited region:

```html
<!-- FRAMEWORK:KERNEL v1.1.0 sha256:a3f9c1e4 — generated, do not edit by hand -->
…
<!-- /FRAMEWORK:KERNEL -->
```

It is not locked. If you edit it, the hash stops matching and the doctor reports
`KERNEL_DRIFT` — which is **not an error**, it is information. At that point
there is only one question:

> Is this an improvement that holds for every project, or a waiver for this one?

- **Improvement** → `/framework-sync` in `--up` mode: the change rises into the
  source, the version is bumped, and the next project is born with it inside.
- **Local waiver** → it gets annotated, so the next person to read the finding
  knows it was deliberate.

This is the direction that is usually missing, and it is why the method forks
elsewhere.

---

## The two editions

`claude-framework-eng/` and `claude-framework-it/` are two **self-standing
editions** of the same framework, not one an appendix of the other. They start
from the same version and each carries its own source, tooling, tests and
`VERSION`.

You install one. They are not meant to be used together, and nothing links them
at runtime: an improvement promoted with `framework-sync --up` rises into the
edition you installed, and stays there. From 1.1.0 onwards each edition follows
the people who use it.

```bash
cd claude-framework-eng/tools && python -m unittest discover -s tests -t . -q  # 160 tests
cd claude-framework-it/tools && python -m unittest discover -s tests -t . -q   # 160 tests
```

---

## Status

**Version 1.1.0**, both editions. 160 tests green each, trial installation clean
under `doctor --strict` in both.

What has **not** been verified, and should be said: the framework has not yet
been used end to end on a real project in production. The tests prove that the
installation is coherent and that the tooling does what it claims — not that the
method produces better work. That measurement does not exist, and until it does,
no savings figure should be believed.

## Licence

No licence declared: all rights reserved by the author.
