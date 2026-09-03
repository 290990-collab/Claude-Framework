# Claude Framework

An installable working method for **Claude Code**: specialised agents, delegation
rules, domain guides and state files, generated into a project and then
**verifiable** — with a tool that tells you when the installation has broken and
a channel for pushing improvements back up into the source.

---

## What it solves

Claude Code hands you subagents, MCP and skills. What it
does not hand you is a **method**. Everyone writes that by hand, once per project. The file grows, the rules
drift, and a few months later it becomes inconsistent accross projects.

This is that method. Five problems, one source:

| Problem | What the framework does |
|---|---|
| **Nothing orchestrates the work.** | A roster of specialised agents, a routing table saying which one takes what, ten delegation rules and a mandatory prompt shape. One task per agent, one explicit done-criterion, and no subagent spawning another |
| **Context is paid blindly.** | Each context carries only what its reader needs: the common method in `CLAUDE.md`, the delegation rules in a file only the coordinator opens, each role's mandate in its own card. The guides in `.claude/shared/` are opened when the task enters their domain, never preloaded. The kernel has a word ceiling that fails the build, and `fwbuild cost` turns those words into tokens and dollars per day |
| **The model invents.** | Evidence-before-action rules present in every context, and one fixed report every subagent closes with: confidence, what would disprove it, what it assumed, what it did **not** verify |
| **The harness is wired by hand.** | The profile generates them: cards carrying model and effort, `settings.json` permissions, the skills. The four read-only reviewers have no shell at all — the guarantee is the configuration. |
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
mkdir -p ~/.claude/skills
cp -r ~/.claude/framework/skills/framework-install ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/290990-collab/Claude-Framework.git $HOME\.claude\claude-framework
Copy-Item -Recurse $HOME\.claude\claude-framework\claude-framework-eng $HOME\.claude\framework
New-Item -ItemType Directory -Force $HOME\.claude\skills | Out-Null
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-install $HOME\.claude\skills\framework-install
```

For the Italian edition, swap `claude-framework-eng` for `claude-framework-it`.
Set `CLAUDE_FRAMEWORK` to keep the source anywhere other than
`~/.claude/framework`.

To check that a source is valid (post-installation):

```bash
cd ~/.claude/framework/tools && python -m fwbuild source ..
```

---

## Usage

### Three skills

| Skill | When | What it does |
|---|---|---|
| `/framework-install` | **Once per project** | Reads the project, runs the questionnaire, picks the roster, generates everything, verifies the result |
| `/framework-doctor` | When something is off | 18 checks on the installation, each with its remedy |
| `/framework-sync` | Maintenance | Carries versions **down** into the project, improvements **up** into the source, activates or deactivates an agent |

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

The method itself is never rewritten per project.

### The five profiles

| Profile | Agents | Added cycles | For |
|---|---:|---|---|
| `software` | 9 | — | Applications and services |
| `library` | 9 | — | Libraries and packages |
| `web` | 11 | design | Sites and interfaces |
| `data` | 12 | — | Pipelines and data |
| `research` | 11 | research | Experiments and measurements |

Six agents are always present — `explorer`, `architect`, `implementer`, `tester`,
`refactorer`, `final-reviewer`: they are the code cycle. However the master holds **19** agents and
the rest are added with `--activate` if they are deactivated in your chosen profile.

---

## Commands

All run from `<source>/tools`.

| Command | Answers |
|---|---|
| `python -m fwbuild doctor <project>` | "Does this installation hold?" |
| `python -m fwbuild source <source>` | "Is this source valid?" |
| `python -m fwbuild cost <project>` | "What does the common context cost?" |
| `python -m fwbuild report <folder>` | "How many versions are out there, and where?" |

The doctor runs 18 checks. Each finding lands at one of three levels:
**ERROR** — the installation is broken; it always fails. **WARN** — something
that needs a human call. **NOTE** — a warning the project has declared
acceptable in `framework.json`, with a written reason; it stays visible but no
longer fails the run. Errors cannot be waived this way.

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

- **Improvement**: `/framework-sync` in `--up` mode: the change rises into the
  source, the version is bumped, and the next project is born with it inside.
- **Local waiver**: it gets annotated, so the next person to read the finding
  knows it was deliberate.

This is the direction that is usually missing, and it is why the method forks
elsewhere.

---

## The two editions

`claude-framework-eng/` and `claude-framework-it/` are two **self-standing
editions** of the same framework.

---

## Status

**Version 1.1.0.**

The test suite shows the installation is coherent. Quantified results are
planned for a future release.

## Licence

MIT — see [LICENSE](LICENSE).
