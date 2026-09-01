# CLAUDE.md — Framework "Enterprise" per FindShop

Claude Code opera qui come un team di senior coordinati: massima accuratezza,
minime allucinazioni, budget token come vincolo di prima classe.

## Il progetto

FindShop — app web e mobile per cercare, in un'area geografica scelta
dall'utente, quali negozi hanno un dato capo d'abbigliamento (modello di
scarpe, giacca, maglia, pantaloni…) e a che prezzo. Italia come primo
mercato, architettura pensata per scalare oltre.

Monorepo TypeScript (pnpm + Turborepo). Mappa moduli (`path` → ruolo):

- `apps/web` → front-end web Next.js (React/TS): ricerca, mappa, risultati, prezzi.
- `apps/mobile` → app iOS+Android Expo/React Native.
- `apps/api` → backend NestJS: API pubblica versionata, ricerca, auth, admin.
- `apps/ingestion` → worker di acquisizione dati negozi: adapter → ETL → indice.
- `packages/core` → dominio PURO (match capo↔offerta, ranking, geo, prezzi/taglie); zero dipendenze da framework/UI/DB.
- `packages/shared` → tipi + schemi Zod = contratti API + client generato.
- `packages/tokens` → design tokens Swiss (colore, tipografia, spaziatura) condivisi web/mobile.
- `infra/` → IaC, CI/CD, migrazioni DB, observability.

Dati: PostgreSQL+PostGIS (source of truth) + Typesense (indice geo + facet).

Vincoli DURI:

- **Superfici sensibili** (ogni modifica lì va pesata): auth/authz e
  multi-tenant, PII/GDPR e geolocalizzazione (dato personale: minimizzare,
  consenso, no persistenza oltre il necessario), secret (DB/Typesense/mappe/
  partner), input non fidato (query, payload API, feed di ingestion da
  terzi), rate limiting. Dettaglio in `.claude/agents/security-reviewer.md`.
- **Multi-region ready**: niente hardcode di valuta/lingua/fuso/unità/formato
  indirizzo; i18n dall'inizio.
- **Origine dati negozi = questione aperta #1**: non ancora decisa; l'ingestion
  resta dietro l'interfaccia adapter, mai accoppiata a una singola fonte.
  Legalità delle fonti (ToS/scraping/accordi) = vincolo di prima classe.
- **API dei framework** (Next.js, Expo/React Native, NestJS, Prisma, Typesense)
  verificate nell'uso reale del repo, mai dalla memoria: evolvono in fretta.
- **Contratti** (cambiarli = aggiornare tutti i lati + versione): API pubblica
  versionata `/v1` (`packages/shared`), schema DB/migrazioni, schema indice
  Typesense (un cambio impone reindicizzazione), interfaccia adapter di ingestion.

Build: `pnpm turbo build` (completa) o `pnpm turbo build --filter=<app>` (parziale).

## Orchestrazione: il main agent coordina

Il main agent pianifica, delega, verifica e integra. Esegue direttamente solo
modifiche piccole a basso rischio (≤2-3 file, poche decine di righe, nessun
contratto): lì delegare costa più che fare. Il resto va ai subagent in
`.claude/agents/`:

| Situazione | Subagent | Modello/Effort |
|---|---|---|
| Dove sta / chi usa X | `explorer` | Haiku low |
| Design, piani multi-file | `architect` | Opus xhigh |
| Implementare feature/fix | `implementer` | Opus high · Sonnet se meccanico |
| UI (viste, markup, stile) | `frontend` | Opus high · Sonnet se meccanico |
| Pipeline dati negozi (ingestion/ETL) | `data-ingestion` | Opus high · Sonnet se meccanico |
| Infrastruttura, CI/CD, deploy, migrazioni | `infra` | Opus high · Sonnet se meccanico |
| Refactoring a comportamento invariato | `refactorer` | Opus high · Sonnet se meccanico |
| Scrivere/aggiornare test | `tester` | Sonnet medium |
| Bug a causa ignota | `debugger` | Opus high · Sonnet se meccanico |
| Superficie di sicurezza | `security-reviewer` | Opus high |
| Verifica finale | `final-reviewer` | Opus high |

`frontend` vs `implementer`: decide il cuore del task (viste/markup/stile →
`frontend`; servizi/logica con ritocchi UI → `implementer`; se pesa su
entrambi, l'architect lo spezza in due task). `data-ingestion` prende i task
il cui cuore è la pipeline dati negozi (adapter, ETL, normalizzazione,
product-matching, sync verso l'indice); `infra` quelli su IaC, CI/CD, deploy,
ambienti e migrazioni DB. Logica di dominio/API generica resta all'`implementer`.

### Economia dei token (vincolo forte)

1. Parallelismo: `architect` mai in parallelo né
   rilanciato sullo stesso task. Opus in sequenza, max 2 in parallelo solo
   su task indipendenti (file disgiunti, nessun output incrociato).
   Parallelismo libero solo per `explorer`.
2. Modello al task, non solo al ruolo: niente `architect` per decisioni
   ovvie né `debugger` per cause evidenti; su lavoro meccanico e senza
   giudizio declassa il modello dello spawn a Sonnet (override per-spawn: il
   modello sì, l'effort dell'agente resta) invece di Opus. Solo senza
   decisioni non banali però: un modello troppo debole sbaglia e il giro a
   vuoto costa più del premium.
3. Contesto pre-digerito agli agenti costosi: l'`explorer` (economico)
   esplora una volta e consegna estratti rilevanti (firme, righe attorno al
   punto) con `file:riga` esatti, così l'Opus legge meno a prezzo pieno —
   meglio un explorer accurato in più che un agente caro a caccia su file
   interi.
4. Letture a range: se il prompt dà già estratti e `file:riga`, il subagent
   legge solo quei range (Read offset/limit), mai il file intero; allarga
   solo se l'estratto non basta o non combacia col codice attuale.
5. Prompt digerito per primacy/recency: task + criterio di completamento in
   cima → vincoli → estratti e `file:riga` → done-criterion ripetuto in
   fondo. Mai seppellire il `file:riga` nella prosa.
6. Load-on-demand, non front-loading: ciò che non è universale sta dietro un
   pointer che l'agente recupera se serve (`.claude/shared/`,
   explorer→ranges), non pre-caricato.
7. Un task per agente, con criterio di completamento esplicito; niente task
   ombrello "sistema tutto".
8. Continuare, non ri-spawnare: per un secondo giro (es. `implementer` dopo
   i finding del reviewer) riusare l'agente con contesto intatto — ripartire
   da freddo ri-digerisce tutto.
9. Una sola review: `final-reviewer` **oppure** `/code-review`, mai entrambe;
   skill native pesanti (`/code-review`, `/verify`, ultra) solo su richiesta
   esplicita dell'utente.
10. Niente ri-verifiche ridondanti: build appena passata + nessun file
    cambiato = non si rilancia "per sicurezza".

### Workflow per task non banali — Think → Plan → Implement → Verify

Capire (sui bug: trovare la causa) → progettare → implementare → verificare
→ concludere. Mai saltare al codice prima di aver capito.

1. **Esplora** — `explorer` individua i file rilevanti.
2. **Progetta** — task che tocca ≥3 file o un contratto: `architect` produce
   piano, rischi e ordine. Richieste ambigue → plan mode nativo prima.
3. **Implementa** — `implementer`, un task alla volta. Test-first quando il
   comportamento desiderato è esprimibile come test (nuove feature, bug fix
   ben definiti, logica di business/API): prima mini-test precisi, poi
   l'implementazione fino a farli passare. Escluso per refactoring, UI,
   prototipi/spike, dipendenze, documentazione.
4. **Testa** — `tester` estende la copertura (edge case, regressioni) oltre
   i mini-test dell'implementer; la build deve passare.
5. **Review** — `final-reviewer` verifica da zero senza fidarsi dei report;
   se il diff tocca le superfici sensibili dichiarate sopra, prima
   `security-reviewer`.
6. **Integra** — il main agent risolve i finding; commit solo su richiesta
   dell'utente.

## Evidence Before Action — anti-allucinazione (per tutti, sempre)

Mai assumere: ogni azione parte dall'evidenza raccolta, non dalla memoria del
modello. Se manca un'informazione, cercarla (repo, poi doc ufficiale), non
inventarla.

1. Mai citare API/firme/comportamenti non letti in sessione (repo o doc
   ufficiale). "Mi ricordo che il framework fa così" non è una fonte.
2. Mai dichiarare funzionante ciò che non è stato verificato (build, test,
   esecuzione); il resto va nella sezione "NON verificato" del report.
3. Le ipotesi si dichiarano come tali ("probabilmente"), mai come certezze.
4. File/simbolo/comando non trovato → dirlo; non inventare path o contenuti.
5. Prima di modificare: leggere i file coinvolti nella versione attuale,
   individuare dipendenze e usi, cercare implementazioni simili nel repo,
   verificare le API reali.
6. Nessun agente dichiara "completato": chiude col report standard e lascia
   il giudizio al coordinatore.
7. Sui bug è vietato indovinare: prima l'evidenza (Read/Grep sul flusso
   reale, log, repro); il fix si scrive solo quando il meccanismo del
   difetto è individuato e spiega il sintomo. I fix a tentativi bruciano
   token e creano regressioni.

## Report standard (obbligatorio per ogni subagent)

Schema fisso e telegrafico, ≤150 parole (deroga solo per finding di
sicurezza). Niente prosa di cortesia. Regola anti-eco: non ripetere il
contesto ricevuto in input — il main ce l'ha già. Sempre `file:riga`, mai
dump di file o diff.

```
CONF: <0-100%> — <motivo in ≤10 parole>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni possibili o "nessuna nota">
UNVERIFIED: <cosa non è stato controllato o "-">
```

Il main agent tratta ogni report come input da verificare, non come verità.

## Principi di modifica del codice

- **Minimal Safe Change**: la modifica più piccola che risolve il problema;
  un solo problema per task/PR. Niente refactoring non richiesti, rename
  inutili, spostamenti di file, cambi di stile o comportamento non
  richiesti. Il refactoring è un task separato per `refactorer`.
- **Existing Pattern First**: prima di scrivere codice nuovo cercare nel
  repo qualcosa da riusare o estendere; consistenza prima della creatività.
- **Contract First**: prima di cambiare funzione/API/formato: qual è il
  contratto? chi lo usa (Grep, inclusi file di markup, script e riferimenti
  per stringa)? rompo compatibilità o comportamento osservabile? Se sì:
  dichiararlo nel report e gestire la migrazione (vale soprattutto per i
  contratti dichiarati nel blocco "Il progetto": protocolli, formati
  persistiti, path utente).
- **KISS**: a parità di risultato vince la soluzione più semplice.
- **Stile locale**: il codice nuovo imita il file in cui vive.
- **Niente commenti-cronaca**: i commenti spiegano vincoli non evidenti,
  non cosa fa la riga successiva.
- **Commit solo su richiesta esplicita** dell'utente, mai in autonomia.

## Tracking: docs/TODO.md

Leggerla a inizio task; aggiornarla a ogni step completato (spunte, voci
nuove emerse, riga "Ultimo aggiornamento"). Il *cosa/come* sta in
`docs/roadmap.md`; il TODO tiene solo lo stato. File pubblicabile: mai
riferimenti a note interne.

## Guide condivise (.claude/shared/)

Da leggere quando il task rientra nel dominio: `conventions.md` (codice e
commit), `coding-standards.md` (per stack), `architecture-guide.md`
(confini e contratti), `testing-guide.md`, `debugging-playbook.md`,
`review-checklist.md` (per final-reviewer).

## Lingua

Italiano con l'utente; codice, identificatori e messaggi di commit in
inglese.
