# Claude Framework

An installable working method for **Claude Code**: specialised agents, delegation
rules, domain guides and state files, generated into a project and then
**verifiable** — with a tool that tells you when the installation has broken, and
a channel for pushing improvements back up into the source.

---

## What it solves

Claude Code hands you subagents, permissions, skills and a `CLAUDE.md`. What it
does not hand you is a **method** — who delegates what to whom, how a prompt is
shaped, what a subagent must hand back, and what nobody may claim without having
run it. Everyone writes that by hand, once per project. The file grows, the rules
drift, and a few months later no two projects work the same way.

This is that method, made installable and verifiable. Five problems, one source:

| Problem | What the framework does |
|---|---|
| **Nothing orchestrates the work.** One context does everything, or agents fan out with no rules | A roster of specialised agents, a routing table saying which one takes what, ten delegation rules and a mandatory prompt shape. One task per agent, one explicit done-criterion, and no subagent spawning another |
| **Context is paid blindly.** `CLAUDE.md` is loaded into every subagent at every spawn, and it only ever grows | Split by **recipient**: the delegation rules sit in a file only the coordinator opens. Guides load on demand. Word ceilings break the build, and `fwbuild cost` turns the file into tokens and money |
| **The model invents.** Remembered APIs, remembered numbers, "it works" without having run it | Evidence-before-action rules present in every context, and one fixed report every subagent closes with: confidence, what would disprove it, what it assumed, what it did **not** verify |
| **The harness is wired by hand.** Models, tools, permissions and skills, one agent at a time | The profile generates them: cards carrying model and effort, `settings.json` permissions, the skills. The four read-only reviewers have no shell at all — the guarantee is the configuration, not a sentence in a prompt |
| **The method forks.** Each project's copy drifts, and the good hand edits are lost | One versioned source. The generated method sits in a hashed **kernel region**: editing it is allowed and becomes *visible*, and `framework-sync` carries the edits worth keeping back up |

---

## Requirements

- **Claude Code**
- **Python 3.11+** — for the tooling, `tomllib` from the stdlib

---

## Installation

Done **once per machine**. From then on, every new project is one line.

**macOS / Linux**

```bash
git clone https://github.com/290990-collab/Claude-Framework.git ~/.claude/claude-framework
cp -r ~/.claude/claude-framework/claude-framework-eng ~/.claude/framework
cp -r ~/.claude/framework/skills/framework-install ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/290990-collab/Claude-Framework.git $HOME\.claude\claude-framework
Copy-Item -Recurse $HOME\.claude\claude-framework\claude-framework-eng $HOME\.claude\framework
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-install $HOME\.claude\skills\
```

It goes to `framework/` because that is where the installer looks: `./framework/`
in the project, then `$CLAUDE_FRAMEWORK`, then `~/.claude/framework/`. Set the
variable to keep the source anywhere else.

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
`--deactivate <agent>` — are asked of the skill in natural language.

### What it writes into a project

Whatever the profile, `/framework-install` produces the same shape:

```
CLAUDE.md                        the common method + this project's context
.claude/framework.json           source, version, profile — how the project finds its way home
.claude/settings.json            permissions from the profile, secrets denied
.claude/agents/                  one card per agent in the chosen roster
.claude/shared/orchestration.md  delegation rules + routing table — opened only by whoever delegates
.claude/shared/core/             six cross-project guides, opened on demand
.claude/shared/domain/           the domain guide, when the profile calls for one
.claude/skills/                  framework-doctor, framework-sync
docs/TODO.md                     where the project stands right now
docs/status.md                   closed decisions, measured results
docs/roadmap.md                  where it is going
```

The profile decides how many agents and which domain guide. Nothing else is
written: the framework does not touch your code, your build or your dependencies,
and it installs nothing.

Every generated file carries `[TO FILL IN — …]` blocks — the constraints, the
critical surface, the commands a subagent cannot deduce. The installer fills them
in with you during the questionnaire, and they are the **only** part that gets
personalised: the method itself is never rewritten per project.

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
