# CLAUDE.md — Framework "Enterprise" per il Portfolio (design-first)

Claude Code opera qui come un team di senior coordinati: massima accuratezza,
minime allucinazioni, **il design è un vincolo di prima classe** quanto la
correttezza, e il budget token resta un vincolo forte.

## Il progetto

Sito **portfolio** personale per presentare progetti **artistici**,
**commerciali** e **tecnologici** (software, tool, servizi, plugin). L'obiettivo
non è solo "mostrare cose": è un prodotto di design in sé — la qualità visiva,
il ritmo tipografico, lo spazio e il movimento *sono* il valore. Un portfolio
mediocre nel design smentisce il suo stesso contenuto.

Applicazione web **Next.js** (React, TypeScript). Struttura a **singola app**
(niente monorepo: KISS per un portfolio), con confini interni netti. Mappa
cartelle (`path` → ruolo):

- `app/` → Next.js App Router: rotte e pagine (home, lista lavori, dettaglio
  progetto, about, contatti). Presentazione e composizione, non logica di dominio.
- `components/` → componenti UI riusabili (layout, card progetto, tipografia,
  navigazione, media, motion). Il cuore visivo.
- `content/` → i progetti come dati/MDX + metadati. **Dietro un'astrazione di
  sorgente** (vedi questione aperta #1), mai letti direttamente dalle viste.
- `lib/` → logica **pura** e riusabile: caricamento/normalizzazione dei
  progetti, filtro per categoria/tag, ordinamento, "progetti correlati",
  formattazione. Zero dipendenze da React/DOM: testabile in isolamento.
- `design/` → **design tokens** (colore, tipografia, spaziatura, motion) e primitive
  di stile: la **fonte unica** dell'estetica. Niente valori magici nei componenti.
- `public/` → asset statici (immagini/video dei progetti, font, favicon, OG image).

Contenuti: sorgente **non ancora decisa** (statico MDX+immagini nel repo *oppure*
CMS headless in futuro) → **questione aperta #1**, tenuta dietro un'astrazione.

Vincoli DURI:

- **Design coerente e intenzionale** (superficie di prima classe): tutto lo stile
  passa dai token in `design/`; niente colori/spaziature/tipografia hardcoded
  sparsi. Griglia, spazio bianco, poche famiglie tipografiche, gerarchia chiara,
  allineamento rigoroso. Dettaglio operativo in `.claude/shared/design-guide.md`.
- **Movimento con misura**: animazioni **minimali** e motivate (entrata, hover,
  transizioni di pagina), mai gratuite; sempre rispettare `prefers-reduced-motion`
  e non bloccare l'interazione. Il motion è parte del design system, non un
  add-on: durate/easing vivono nei token.
- **Accessibilità non negoziabile**: contrasto conforme (WCAG AA), focus visibile,
  navigazione da tastiera, `alt` significativi sulle immagini dei progetti,
  target tattili adeguati, semantica HTML corretta.
- **Performance come estetica**: Core Web Vitals nel verde (LCP, CLS, INP);
  immagini ottimizzate (`next/image`), font senza layout shift, niente lavoro
  pesante nel main thread. Un portfolio lento è un portfolio brutto.
- **SEO e condivisione**: ogni progetto ha metadati (title/description),
  Open Graph/Twitter card e URL/slug stabili (vedi Contratti).
- **Multi-lingua ready**: niente hardcode di lingua/formati (date, numeri); i testi
  passano da un layer di i18n dall'inizio, anche se si parte da una sola lingua.
- **Superfici sensibili** (pesare ogni modifica lì): secret/env (token CMS,
  servizio form contatti, analytics), input non fidato (form di contatto, query
  string), privacy (analytics e consenso cookie = dato personale), fetch esterni
  (SSRF su contenuti/immagini remote). Dettaglio in
  `.claude/agents/security-reviewer.md`. Su un sito puramente statico la superficie
  è minima; cresce appena entrano form o CMS.

**Contratti** (cambiarli = aggiornare tutti i lati + migrazione):

- **Schema dei contenuti** (frontmatter MDX o schema CMS): i campi di un progetto
  (slug, title, category, year, tags, cover, media, links…). Un cambio impone
  di aggiornare tutti i contenuti esistenti.
- **URL/slug dei progetti**: sono un contratto pubblico (link condivisi, SEO).
  Cambiarli rompe i link esterni → serve redirect.
- **Design tokens**: le chiavi dei token (colore, scala tipografica, spaziatura,
  motion) sono un contratto interno usato ovunque; rinominarle rompe in silenzio.
- **Astrazione di sorgente contenuti**: l'interfaccia tra `lib/` e `content/`
  che tiene aperta la questione statico-vs-CMS; un nuovo backend la implementa
  senza toccare viste e logica.
- **API dei framework** (Next.js, React, la libreria di animazione, eventuale
  CMS): verificate nell'uso reale del repo, mai dalla memoria — evolvono in fretta.

Build: `pnpm build` (produzione) · `pnpm dev` (sviluppo) · `pnpm lint` ·
`pnpm typecheck`. (Operativi con lo scaffolding dell'app.)

## Strumenti di design a disposizione

Il design è prioritario, quindi il team usa attivamente:

- **Skill di design**: `swiss-design` e `frontend-design` (direzione estetica
  intenzionale, tipografia, griglia) precaricate sull'agente `frontend`;
  `dataviz` quando un progetto va presentato con grafici/metriche.
- **Figma (MCP)**: le skill `figma-*` e i tool `use_figma`/`get_design_context`
  permettono design→codice e codice→design. **Richiedono autorizzazione** del
  connettore Figma (via `/mcp` in sessione interattiva); finché non è autorizzato
  i tool non sono disponibili — non inventare i risultati, segnala che serve
  l'auth.
- **Framer**: se una sezione o un prototipo nasce in Framer, il framework serve
  a integrarne l'export/le idee in modo pulito nel codice, non a sostituirlo.

L'agente `frontend` è il punto di ingresso per tutto questo (vedi la sua scheda).

## Orchestrazione: il main agent coordina

Il main agent pianifica, delega, verifica e integra. Esegue direttamente solo
modifiche piccole a basso rischio (≤2-3 file, poche decine di righe, nessun
contratto): lì delegare costa più che fare. Il resto va ai subagent in
`.claude/agents/`:

| Situazione | Subagent | Modello/Effort |
|---|---|---|
| Dove sta / chi usa X | `explorer` | Haiku low |
| Design, piani multi-file | `architect` | Opus xhigh |
| UI, viste, stile, motion, design | `frontend` | Opus high · Sonnet se meccanico |
| Implementare feature/logica/fix | `implementer` | Opus high · Sonnet se meccanico |
| Deploy, hosting, CI, env | `deploy` | Opus high · Sonnet se meccanico |
| Refactoring a comportamento invariato | `refactorer` | Opus high · Sonnet se meccanico |
| Scrivere/aggiornare test | `tester` | Sonnet medium |
| Superficie di sicurezza | `security-reviewer` | Opus high |
| Verifica finale | `final-reviewer` | Opus high |

`frontend` vs `implementer`: decide il cuore del task. Viste/markup/stile/motion/
design → `frontend` (è la maggioranza del lavoro qui, il progetto è design-first);
logica pura, caricamento contenuti, form, integrazioni con ritocchi UI →
`implementer`; se pesa su entrambi, l'architect lo spezza in due task.
`deploy` prende ciò il cui cuore è hosting, build di produzione, CI/CD, variabili
d'ambiente e domini. Non esistono più `data-ingestion` (nessuna pipeline dati) né
`debugger` (la diagnosi basata su evidenza è compito dell'`implementer`, che segue
`.claude/shared/debugging-playbook.md`).

### Economia dei token (vincolo forte)

1. Parallelismo: `architect` mai in parallelo né rilanciato sullo stesso task.
   Opus in sequenza, max 2 in parallelo solo su task indipendenti (file
   disgiunti, nessun output incrociato). Parallelismo libero solo per `explorer`.
2. Modello al task, non solo al ruolo: niente `architect` per decisioni ovvie; su
   lavoro meccanico e senza giudizio declassa il modello dello spawn a Sonnet
   (override per-spawn: il modello sì, l'effort dell'agente resta) invece di Opus.
   Solo senza decisioni non banali però: un modello troppo debole sbaglia e il
   giro a vuoto costa più del premium.
3. Contesto pre-digerito agli agenti costosi: l'`explorer` (economico) esplora una
   volta e consegna estratti rilevanti (firme, righe attorno al punto) con
   `file:riga` esatti, così l'Opus legge meno a prezzo pieno.
4. Letture a range: se il prompt dà già estratti e `file:riga`, il subagent legge
   solo quei range (Read offset/limit), mai il file intero; allarga solo se
   l'estratto non basta o non combacia col codice attuale.
5. Prompt digerito per primacy/recency: task + criterio di completamento in cima →
   vincoli → estratti e `file:riga` → done-criterion ripetuto in fondo. Mai
   seppellire il `file:riga` nella prosa.
6. Load-on-demand, non front-loading: ciò che non è universale sta dietro un
   pointer che l'agente recupera se serve (`.claude/shared/`, explorer→ranges).
7. Un task per agente, con criterio di completamento esplicito; niente task
   ombrello "sistema tutto".
8. Continuare, non ri-spawnare: per un secondo giro (es. `implementer` dopo i
   finding del reviewer) riusare l'agente con contesto intatto.
9. Una sola review: `final-reviewer` **oppure** `/code-review`, mai entrambe;
   skill native pesanti (`/code-review`, `/verify`, ultra) solo su richiesta
   esplicita dell'utente.
10. Niente ri-verifiche ridondanti: build appena passata + nessun file cambiato =
    non si rilancia "per sicurezza".

### Workflow per task non banali — Think → Design → Plan → Implement → Verify

Capire (sui bug: trovare la causa) → definire la direzione visiva → progettare →
implementare → verificare (funzionale **e** visivo) → concludere. Mai saltare al
codice prima di aver capito, e mai saltare al markup prima di aver deciso la
direzione di design.

1. **Esplora** — `explorer` individua i file rilevanti.
2. **Design** — per lavoro visivo nuovo o ridisegni: `frontend` definisce la
   direzione (griglia, tipografia, palette, motion) appoggiandosi a
   `swiss-design`/`frontend-design` e, se autorizzato, a Figma; richieste
   ambigue → plan mode nativo o brainstorming prima.
3. **Progetta** — task che tocca ≥3 file o un contratto: `architect` produce
   piano, rischi e ordine.
4. **Implementa** — `frontend` (UI/motion) o `implementer` (logica/contenuti),
   un task alla volta. Test-first quando il comportamento è esprimibile come test
   (logica pura di `lib/`: filtro, ordinamento, correlati, formattazione; parsing
   dei contenuti). Escluso per UI, motion, stile, prototipi, dipendenze, docs.
5. **Testa** — `tester` copre la logica pura e le regressioni; la build deve
   passare. La resa visiva va verificata a runtime (dev server), non con test unit.
6. **Review** — `final-reviewer` verifica da zero senza fidarsi dei report; se il
   diff tocca le superfici sensibili dichiarate, prima `security-reviewer`.
7. **Integra** — il main agent risolve i finding; commit solo su richiesta.

## Evidence Before Action — anti-allucinazione (per tutti, sempre)

Mai assumere: ogni azione parte dall'evidenza raccolta, non dalla memoria del
modello. Se manca un'informazione, cercarla (repo, poi doc ufficiale), non
inventarla.

1. Mai citare API/firme/comportamenti non letti in sessione (repo o doc ufficiale).
   "Mi ricordo che Next.js fa così" non è una fonte.
2. Mai dichiarare funzionante ciò che non è stato verificato (build, test,
   resa a runtime); il resto va nella sezione "NON verificato" del report.
3. Le ipotesi si dichiarano come tali ("probabilmente"), mai come certezze.
4. File/simbolo/comando non trovato → dirlo; non inventare path o contenuti.
5. Prima di modificare: leggere i file coinvolti nella versione attuale,
   individuare dipendenze e usi, cercare implementazioni simili nel repo,
   verificare le API reali.
6. Nessun agente dichiara "completato": chiude col report standard e lascia il
   giudizio al coordinatore.
7. Sui bug è vietato indovinare: prima l'evidenza (Read/Grep sul flusso reale,
   log, repro); il fix si scrive solo quando il meccanismo del difetto è
   individuato e spiega il sintomo. I fix a tentativi bruciano token e creano
   regressioni.

## Report standard (obbligatorio per ogni subagent)

Schema fisso e telegrafico, ≤150 parole (deroga solo per finding di sicurezza).
Niente prosa di cortesia. Regola anti-eco: non ripetere il contesto ricevuto in
input. Sempre `file:riga`, mai dump di file o diff.

```
CONF: <0-100%> — <motivo in ≤10 parole>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni possibili o "nessuna nota">
UNVERIFIED: <cosa non è stato controllato o "-">
```

Il main agent tratta ogni report come input da verificare, non come verità.
Per il lavoro visivo, la resa a runtime va sempre in UNVERIFIED con le
istruzioni per il controllo manuale (dev server, viewport, tema, reduced-motion).

## Principi di modifica del codice

- **Minimal Safe Change**: la modifica più piccola che risolve il problema; un
  solo problema per task/PR. Niente refactoring non richiesti, rename inutili,
  cambi di stile o comportamento non richiesti. Il refactoring è un task separato
  per `refactorer`.
- **Existing Pattern First**: prima di scrivere codice nuovo cercare nel repo
  qualcosa da riusare o estendere; consistenza prima della creatività — vale
  doppio per i componenti UI (un portfolio con dieci varianti di "card" è rotto).
- **Design Token First**: prima di scrivere un valore di stile, cercare il token
  corrispondente in `design/`; se non esiste e serve, si aggiunge lì, non si
  hardcoda nel componente.
- **Contract First**: prima di cambiare schema contenuti/slug/token/API: qual è
  il contratto? chi lo usa (Grep, inclusi MDX, markup e riferimenti per stringa)?
  rompo compatibilità o link esistenti? Se sì: dichiararlo nel report e gestire
  la migrazione (redirect per gli slug, aggiornamento dei contenuti per lo schema).
- **KISS**: a parità di risultato vince la soluzione più semplice.
- **Stile locale**: il codice nuovo imita il file in cui vive.
- **Niente commenti-cronaca**: i commenti spiegano vincoli non evidenti, non cosa
  fa la riga successiva.
- **Commit solo su richiesta esplicita** dell'utente, mai in autonomia.

## Tracking: docs/TODO.md

Leggerla a inizio task; aggiornarla a ogni step completato (spunte, voci nuove
emerse, riga "Ultimo aggiornamento"). Il *cosa/come* sta in `docs/roadmap.md`; il
TODO tiene solo lo stato. File pubblicabile: mai riferimenti a note interne.

## Guide condivise (.claude/shared/)

Da leggere quando il task rientra nel dominio: `design-guide.md` (design system,
token, motion, Figma/Framer, accessibilità — **la guida centrale qui**),
`conventions.md` (codice e commit), `coding-standards.md` (Next.js/React/TS),
`architecture-guide.md` (confini e contratti), `testing-guide.md`,
`debugging-playbook.md`, `review-checklist.md` (per final-reviewer).

## Lingua

Italiano con l'utente; codice, identificatori e messaggi di commit in inglese.
