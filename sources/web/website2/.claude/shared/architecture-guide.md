# Guida all'architettura — FindShop

Topologia: i client web (Next.js) e mobile (Expo/React Native) parlano con
un'unica API backend (NestJS) che orchestra la ricerca su un indice Typesense
(geo + facet); l'indice e il DB PostgreSQL+PostGIS (source of truth) sono
alimentati da un worker di ingestion con adapter pluggabili per i dati dei
negozi.

## Confini e responsabilità

- `packages/core` — logica di dominio PURA (match capo↔offerta, ranking,
  calcoli geo, normalizzazione prezzi/taglie). Nessuna dipendenza da framework,
  UI, DB o rete: il cuore testabile in isolamento.
- `packages/shared` — contratti condivisi: tipi + schemi Zod dell'API e client.
  Nessuna logica di business né I/O.
- `packages/tokens` — design tokens (colore, tipografia, spaziatura); nessuna
  logica.
- `apps/api` — tutto ciò che tocca rete/DB/indice/auth: espone l'API pubblica e
  usa il core per le decisioni di dominio. Non duplica la logica del core.
- `apps/web`, `apps/mobile` — presentazione e interazione; consumano l'API via
  il client di `packages/shared`. Nessuna logica di dominio nei componenti.
- `apps/ingestion` — acquisizione dati negozi: adapter → normalizzazione →
  scrittura su DB → indicizzazione su Typesense. Isolato dietro l'interfaccia
  adapter.
- `infra/` — infrastruttura, deploy, migrazioni; versionata a parte.

Regola pratica: una funzione di un'app (web/mobile/api) che non tocca UI, rete,
DB o framework probabilmente va in `packages/core`.

## I contratti (cambiarli = decisione architetturale)

1. **API pubblica web/mobile** (`/v1`, definita in `packages/shared`): cambio
   coordinato di tutti i client, versione incrementata, gestito il caso "app
   mobile vecchia (non aggiornata dallo store) contro API nuova" —
   retrocompatibilità o versionamento, mai breaking silenzioso.
2. **Schema DB (PostgreSQL)** — formato persistito: migrazioni versionate e
   reversibili; le versioni nuove leggono i dati esistenti (default per campi
   nuovi, mai rename/drop senza compatibilità di lettura).
3. **Schema indice Typesense** — formato rigenerabile: si ricostruisce dal DB,
   ma un cambio di schema impone una reindicizzazione (costo operativo da
   segnalare).
4. **Interfaccia adapter di ingestion** — il contratto verso le fonti dati
   negozi: input eterogeneo (API partner, CSV/XML, POS) → output normalizzato.
   È il punto di estensione che tiene aperta la questione dell'origine dati;
   un nuovo adapter la implementa senza toccare il resto della pipeline.

Input da fonti esterne (feed di ingestion, payload API, webhook) = confine di
fiducia: validati (schema, lunghezze, range), mai eseguiti, mai fidati per
authz. Gli adapter che chiamano URL esterni passano da una allowlist (anti-SSRF).

## Decisioni vincolanti già prese

- **Core puro**: nessuna dipendenza da framework/UI/DB in `packages/core`.
- **Multi-region ready**: niente hardcode di valuta, lingua, fuso, unità o
  formato indirizzo; i18n e multi-valuta dall'inizio, anche col primo mercato
  in Italia.
- **Privacy della posizione**: la geolocalizzazione dell'utente è dato
  personale — si minimizza, si chiede consenso, non si persiste oltre il
  necessario.
- **Origine dati negozi non decisa (questione aperta #1)**: l'ingestion resta
  dietro l'interfaccia adapter; nessuna scelta architetturale la incastra su
  una singola fonte. Da risolvere prima di consolidare la ricerca.
- **Superficie sensibile minima**: a parità di risultato vince l'alternativa
  che espone meno dati e meno permessi.

## Valutare una proposta di design (per l'architect)

1. Quali contratti tocca? (nessuno = rischio molto più basso)
2. Cosa succede ai client esistenti — in particolare a un'app mobile non ancora
   aggiornata — al primo utilizzo dopo il cambio?
3. Degrada con grazia se una dipendenza esterna (indice, DB, fonte dati,
   provider mappe) è assente o cambia?
4. Aggiunge superficie sensibile, dati personali o permessi nuovi?
5. Regge la scala multi-region (nessun assunto Italia-only nascosto)?
6. Qual è l'alternativa più semplice che risolve il 90% del problema? (KISS)
