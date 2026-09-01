# Portfolio (nome di lavoro)

Sito **portfolio** personale, design-first, per presentare progetti
**artistici**, **commerciali** e **tecnologici** (software, tool, servizi,
plugin). Il design — tipografia, griglia, spazio, movimento minimale — è parte
del valore, non decorazione.

> Stato: bootstrap. Nessun codice applicativo ancora; questo repo contiene il
> framework di lavoro (istruzioni per il team di agenti) adattato da un
> framework precedente a un sito portfolio Next.js. Roadmap e stato in
> [docs/roadmap.md](docs/roadmap.md) e [docs/TODO.md](docs/TODO.md).

## Stack

- **Web** — Next.js (React, TypeScript), App Router.
- **Stile** — design tokens propri (colore, tipografia, spaziatura, motion) come
  fonte unica; libreria di animazione (es. Framer Motion) con movimento minimale.
- **Contenuti** — sorgente **non ancora decisa** (questione aperta #1): statico
  MDX/Markdown nel repo *oppure* CMS headless in futuro, tenuta dietro
  un'astrazione di sorgente.
- **Deploy** — hosting statico/edge (es. Vercel o Netlify).

## Struttura

```
app/          Next.js App Router — home, lista lavori, dettaglio progetto, about, contatti
components/    componenti UI riusabili (layout, card, tipografia, media, motion)
content/       progetti come dati/MDX — dietro un'astrazione di sorgente
lib/           logica pura: caricamento/filtro/ordinamento progetti, formattazione (no React/DOM)
design/        design tokens e primitive di stile — la fonte unica dell'estetica
public/        asset statici (immagini/video progetti, font, favicon, OG image)
docs/          roadmap.md (cosa/come) · TODO.md (stato)
```

## Come si lavora (team di agenti)

Il repo usa un framework di orchestrazione multi-agente **design-first**: il main
agent pianifica, delega a subagent specializzati (`.claude/agents/`) e verifica.
Regole di metodo, priorità al design, economia dei token e anti-allucinazione in
[CLAUDE.md](CLAUDE.md); guide caricate on-demand in
[.claude/shared/](.claude/shared/) — a partire da `design-guide.md`.

| Ambito | Agente |
|---|---|
| Ricognizione codebase | `explorer` |
| Design e piani multi-file | `architect` |
| UI, viste, stile, motion, design | `frontend` |
| Logica, contenuti, form, fix | `implementer` |
| Deploy, hosting, CI, env | `deploy` |
| Refactoring | `refactorer` |
| Test | `tester` |
| Review di sicurezza | `security-reviewer` |
| Verifica finale | `final-reviewer` |

Strumenti di design attivi: skill `swiss-design` / `frontend-design` / `dataviz`,
Figma via MCP (previa autorizzazione del connettore), e integrazione di lavoro
nato in Framer. Dettagli in [CLAUDE.md](CLAUDE.md) e nella scheda dell'agente
`frontend`.

## Build

```
pnpm install
pnpm dev          # sviluppo
pnpm build        # build di produzione
pnpm lint         # lint
pnpm typecheck    # type-check
```

(I comandi diventano operativi con lo scaffolding dell'app.)

## Lingua

Italiano nella collaborazione; codice, identificatori e commit in inglese.
