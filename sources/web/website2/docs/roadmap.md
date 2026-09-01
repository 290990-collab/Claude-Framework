# Roadmap — FindShop

Il *cosa* e il *come* per fasi. Lo stato operativo (spunte) sta in
[TODO.md](TODO.md). Ordine pensato per ridurre il rischio: prima dominio e
contratti, poi la ricerca, poi i client, e solo dopo i dati reali.

## Fase 0 — Fondamenta

Scaffolding del monorepo (pnpm + Turborepo), toolchain condivisa (TypeScript
stretto, lint, Vitest), CI di base, `packages/tokens` con i design token Swiss
(colore, tipografia, spaziatura). Obiettivo: `pnpm turbo build` verde su uno
scheletro vuoto ma coerente.

## Fase 1 — Dominio e contratti

Modello di dominio in `packages/core` (capo, negozio, offerta/prezzo, geo),
schema DB PostgreSQL+PostGIS con migrazioni, contratti API `/v1` in
`packages/shared` (tipi + Zod). Nessuna dipendenza framework nel core.

## Fase 2 — Ricerca

Indice Typesense (geo + facet), geo-ricerca "capo in un'area → negozi + prezzo",
API di ricerca in `apps/api`. Pipeline `apps/ingestion` con l'interfaccia
adapter e un adapter di test/import manuale per popolare dati di prova.

## Fase 3 — Client

`apps/web` (Next.js): selezione dell'area come cerchio a raggio regolabile sulla
mappa (point&click + drag), ricerca con autocomplete, lista risultati con prezzo,
dettaglio.
`apps/mobile` (Expo/React Native): stesse funzioni core. Estetica Swiss dai
token condivisi; i18n dall'inizio.

## Fase 4 — Dati reali (questione aperta #1)

Risolvere l'origine dei dati di inventario dei negozi: valutare fonti pubbliche,
accordi/API partner, integrazioni POS/e-commerce; implementare gli adapter
corrispondenti. Pilota con un insieme ristretto di negozi/catene. Vincolo di
prima classe: legalità delle fonti (ToS/accordi).

## Fase 5 — Hardening e scala

Auth e multi-tenancy, conformità GDPR (consenso, minimizzazione, cancellazione),
rate limiting, observability end-to-end, preparazione alla scala multi-region
oltre l'Italia.
