# FindShop

App web e mobile per cercare, in un'area geografica scelta dall'utente, quali
negozi hanno un dato capo d'abbigliamento (un modello di scarpe, giacca,
maglia, pantaloni…) e a che prezzo. Italia come primo mercato, architettura
pensata per scalare oltre. Design minimale, Swiss.

> Stato: bootstrap. Nessun codice applicativo ancora; questo repo contiene il
> framework di lavoro (istruzioni per il team di agenti). Roadmap e stato in
> [docs/roadmap.md](docs/roadmap.md) e [docs/TODO.md](docs/TODO.md).

## Stack

- **Web** — Next.js (React, TypeScript).
- **Mobile** — Expo / React Native (iOS + Android).
- **Backend** — NestJS (Node, TypeScript), API pubblica versionata.
- **Ingestion** — worker con adapter pluggabili per i dati di inventario dei negozi.
- **Dati** — PostgreSQL + PostGIS (source of truth) + Typesense (indice geo + facet).
- **Monorepo** — pnpm + Turborepo; codice condiviso in `packages/`.

Origine dei dati di inventario dei negozi: **questione aperta #1**, non ancora
decisa. La pipeline di ingestion resta dietro un'interfaccia adapter astratta.

## Struttura

```
apps/web         Next.js — ricerca, mappa, risultati, prezzi
apps/mobile      Expo/React Native — iOS + Android
apps/api         NestJS — API pubblica, ricerca, auth, admin
apps/ingestion   worker: adapter dati negozi → ETL → indice
packages/core    dominio puro (match, ranking, geo, prezzi) — zero dipendenze framework
packages/shared  tipi + schemi Zod (contratti API) + client
packages/tokens  design tokens Swiss condivisi web/mobile
infra/           IaC, CI/CD, migrazioni DB, observability
docs/            roadmap.md (cosa/come) · TODO.md (stato) · business.md (analisi economica)
```

## Come si lavora (team di agenti)

Il repo usa un framework di orchestrazione multi-agente: il main agent
pianifica, delega a subagent specializzati (`.claude/agents/`) e verifica.
Regole di metodo, economia dei token e anti-allucinazione in
[CLAUDE.md](CLAUDE.md); guide di dominio caricate on-demand in
[.claude/shared/](.claude/shared/).

| Ambito | Agente |
|---|---|
| Ricognizione codebase | `explorer` |
| Design e piani multi-file | `architect` |
| Implementazione feature/fix | `implementer` |
| UI web/mobile e design | `frontend` |
| Pipeline dati negozi | `data-ingestion` |
| Infra, CI/CD, deploy | `infra` |
| Refactoring | `refactorer` |
| Test | `tester` |
| Debug di cause ignote | `debugger` |
| Review di sicurezza | `security-reviewer` |
| Verifica finale | `final-reviewer` |

## Build

```
pnpm install
pnpm turbo build            # build completa
pnpm turbo build --filter=<app>   # build del singolo package/app
pnpm turbo test            # test
```

(I comandi diventano operativi con lo scaffolding del monorepo.)

## Lingua

Italiano nella collaborazione; codice, identificatori e commit in inglese.
