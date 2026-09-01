# TODO — Portfolio

Solo lo stato. Il *cosa/come* sta in [roadmap.md](roadmap.md). Aggiornare a ogni
step completato (spunte, voci nuove, riga "Ultimo aggiornamento").

## In corso

- [x] Adattare il framework di lavoro (CLAUDE.md, `.claude/`, README) al sito
      portfolio design-first Next.js.

## Prossimi (Fase 0 — Fondamenta)

- [ ] Scaffolding dell'app Next.js (App Router, TypeScript stretto, lint) e versioni.
- [ ] Struttura cartelle coerente (`app/`, `components/`, `content/`, `lib/`, `design/`).
- [ ] `design/`: primi design token (scala tipografica, palette, spaziatura, motion).
- [ ] CI di base con `pnpm build`, `pnpm lint`, `pnpm typecheck`.

## Decisioni aperte

- [ ] **Questione aperta #1 — sorgente dei contenuti** (rinviata di proposito).
      Statico MDX/Markdown nel repo *oppure* CMS headless (Sanity/Contentful/Notion…)?
      Per ora la logica resta dietro un'astrazione di sorgente: nessun accoppiamento
      a una scelta. Da definire prima della Fase 5. Vincolo se CMS: gestione secret
      e input non fidato (vedi `security-reviewer`).
- [ ] **Nome del sito/dominio** non deciso: il repo usa "Portfolio" (nome di lavoro).
- [ ] Direzione visiva: font, palette, tono del movimento — da fissare in Fase 1.
- [ ] Multilingua sì/no: se sì, i18n dall'inizio; se no, tenerlo comunque non-hardcoded.
- [ ] Libreria di animazione (es. Framer Motion) e libreria di stile — da confermare.
- [ ] Uso di Figma (MCP) e/o Framer: autorizzare il connettore Figma se si vuole
      il flusso design↔codice.

---

Ultimo aggiornamento: 2026-07-24
