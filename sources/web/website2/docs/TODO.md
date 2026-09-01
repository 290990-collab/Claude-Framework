# TODO — FindShop

Solo lo stato. Il *cosa/come* sta in [roadmap.md](roadmap.md). Aggiornare a ogni
step completato (spunte, voci nuove, riga "Ultimo aggiornamento").

## In corso

- [x] Adattare il framework di lavoro (CLAUDE.md, `.claude/`, README) al progetto FindShop.

## Prossimi (Fase 0 — Fondamenta)

- [ ] Definire la toolchain esatta del monorepo (pnpm + Turborepo) e le versioni.
- [ ] Scaffolding di `apps/*` e `packages/*` vuoti ma coerenti.
- [ ] `packages/tokens`: prime scelte di design Swiss (scala tipografica, palette, spaziatura).
- [ ] CI di base con `pnpm turbo build` e `pnpm turbo test`.

## Decisioni aperte

- [ ] **Questione aperta #1 — origine dei dati di inventario dei negozi** (rinviata di proposito).
      Da definire: esistono database pubblici? a che livello di dettaglio? oppure serve
      richiedere l'accesso (accordi/API partner, integrazioni POS/e-commerce)? Per una demo
      si può richiedere l'accesso al momento della presentazione del prodotto.
      Opzioni valutate: (A) adapter pluggabili — posture architetturale già adottata, la
      pipeline resta astratta sulla fonte; (B) solo partner/API per il pilota. Vincolo:
      legalità delle fonti (ToS/scraping/accordi). Blocca la Fase 4 e la ricerca su dati reali.
- [ ] Conferma librerie: ORM (Prisma), motore di ricerca (Typesense vs Meilisearch), e2e mobile (Detox vs Maestro).
- [ ] Pilota: città candidata **Modena**, una categoria (es. sneakers/streetwear); confermare le fonti dati ottenibili per prime (vedi [business.md](business.md)).
- [ ] **Nome prodotto** non deciso: il repo usa "FindShop" (nome di lavoro), il collaboratore propone "Style Way". Sceglierne uno prima di consolidare (se cambia, rename in tutto il repo).

## Da riconciliare (proposta collaboratore "Style Way")

- [ ] **Ambito AI** (direzione concordata): la ricerca core resta senza AI; l'AI è una superficie *separata e post-MVP* di discovery guidata per chi non sa cosa cercare (assistente/consiglio), con costo token misurato e degrado con grazia. Resta valida anche per product-matching/normalizzazione in ingestion.
- [x] **Quantità disponibile** in tempo reale: concordato — opzionale/best-effort, non requisito MVP; stessa logica per campi/filtri secondari (progressivi). MVP = presenza + prezzo + facet core.
- [ ] **Customer-tracking / dati venduti** — attenzione GDPR: togliere il nome NON rende anonimo il dato (età + zona + comportamento = dato personale *pseudonimo*; "pubblicamente disponibile" non è una base giuridica). Lecito solo con (a) base giuridica/consenso per la raccolta e (b) vendita di sole statistiche *aggregate sopra soglia* (nessun individuo isolabile). Vincolo già in [architecture-guide.md](../.claude/shared/architecture-guide.md) e `security-reviewer`.
- [ ] **Timing marketing**: IG/TikTok/sponsorizzate dopo aver raggiunto densità nel pilota, non prima (evita cold-start a vuoto).

---

Ultimo aggiornamento: 2026-07-24
