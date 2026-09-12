<p align="center">
  <img src="assets/claw.png" alt="CLAW, an orange block with two claws, sitting cross-legged in calm focus" width="440">
</p>

<h1 align="center">CLAW</h1>

```
┌── claude-framework-eng ──────────────────────────────────────────────┐
│                                                                      │
│       method   coordinator   cycles   agents   shared   hooks        │
│                                                                      │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │                             ▲
                             ┌──────┴──────┐                      │
                             │   profile   │                      │
                             └──────┬──────┘                      │
                                    │                             │
  /framework-install ─┐      ┌──────┴──────┐                      │
  /framework-doctor  ─┼──────┤   fwbuild   │                      │
  /framework-sync    ─┤      └──────┬──────┘                      │
  /framework-comply  ─┘             │                             │
                                    │                             │
┌── project ────────────────────────┴─────────────────────────────┴────┐
│                                                                      │
│  CLAUDE.md   .claude/agents   .claude/shared   .claude/hooks   docs  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**A working method for Claude Code, installed in one command and kept honest by a doctor.**

Specialised subagents, delegation rules, evidence-before-action and a context
budget per role — generated into your project, versioned, and checked by a tool
that tells you the moment an installation drifts.

---

## Why

Claude Code gives you subagents, hooks and skills. It does not give you a
**method** — so everyone writes one by hand, per project, and watches it drift.

- **Agents that stay in their lane.** A roster picked for your project, a routing
  table, one task per agent with a verifiable done-criterion, and one fixed report
  every subagent closes with: confidence, what would disprove it, what it did
  **not** verify.
- **Context you actually use.** The method every agent needs lives in
  `CLAUDE.md`; delegation lives where only the coordinator reads it; guides load
  on demand. `fwbuild cost` turns the words into tokens and dollars.
- **Guardrails that don't trust the model.** Hooks block `--no-verify` and edits
  that loosen an existing linter config. Read-only reviewers get no shell at all.
- **One method, every project.** The generated method sits in a hashed kernel
  region: edit it and the doctor sees it, and `framework-sync` carries the edits
  worth keeping back into the source.

---

## Install

Once per machine. Requires Claude Code and Python 3.11+ — stdlib only, nothing to
install. Two self-standing editions: swap `claude-framework-eng` for
`claude-framework-it` to work in Italian.

```bash
git clone https://github.com/290990-collab/CLAW.git ~/.claude/claude-framework
cp -r ~/.claude/claude-framework/claude-framework-eng ~/.claude/framework
mkdir -p ~/.claude/skills
cp -r ~/.claude/framework/skills/framework-install ~/.claude/skills/
cp -r ~/.claude/framework/skills/framework-comply ~/.claude/skills/
```

```powershell
git clone https://github.com/290990-collab/CLAW.git $HOME\.claude\claude-framework
Copy-Item -Recurse $HOME\.claude\claude-framework\claude-framework-eng $HOME\.claude\framework
New-Item -ItemType Directory -Force $HOME\.claude\skills | Out-Null
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-install $HOME\.claude\skills\framework-install
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-comply $HOME\.claude\skills\framework-comply
```

Then, in any project: `/framework-install`.

---

## Use

| Slash command | What it does |
|---|---|
| `/framework-install` | Reads the repo, asks a short questionnaire, picks the roster, generates everything, verifies it |
| `/framework-doctor` | Checks the installation; every finding comes with its remedy |
| `/framework-sync` | New versions **down** into the project, improvements **up** into the source, agents on and off |
| `/framework-memory` | Pairs every stale memory with the repo line that contradicts it |
| `/framework-comply` | Measures whether a rule is actually followed, across real `claude -p` runs |

**Profiles:** `software` · `library` · `web` · `data` · `research` · `llm` ·
`marketing` — each sets the roster, the guides and the permissions for its
field.

The framework writes `CLAUDE.md`, `.claude/` and `docs/`, and nothing else. Your
code, build and dependencies stay untouched.

---

## Version 1.4.0

MIT — see [LICENSE](LICENSE).
