# Meta-framework Claude Code — design

**Data:** 2026-08-31 · **Stato:** approvato in brainstorming, da implementare
**Deriva da:** `sources/base`, `sources/oop`, `sources/research-ai`, `sources/web/{base,website1,website2}`

---

## 1. Obiettivo

Un framework generale per Claude Code che si **installa** in un progetto e si
**adatta** da solo — a un'idea (progetto vuoto) o a un codebase esistente —
mantenendo invariati il metodo di orchestrazione e le regole di economia dei
token, e attivando solo i sottoagenti pertinenti al dominio.

Quattro artefatti, in quest'ordine:

1. **A′** (questa spec) — nucleo versionato + adattatore, con rilevamento del drift.
2. **B** — stesso contenuto, marker e versionamento disattivati: template classico.
3. **A′-EN**, 4. **B-EN** — overlay di traduzione tracciato per versione.

Vincolo di processo: **una sola sorgente, quattro artefatti generati.** Quattro
alberi paralleli scritti a mano ricreerebbero il problema che il framework risolve.

## 2. Diagnosi dei framework sorgente

### 2.1 Cosa va ereditato senza toccarlo

Il metodo è maturo e va portato quasi alla lettera:

- Orchestrazione con main agent coordinatore, che esegue **direttamente** le
  modifiche piccole a basso rischio (≤2-3 file, poche decine di righe, nessun
  contratto): lì delegare costa più che fare.
- Le **10 regole di economia dei token**.
- **Evidence Before Action** (anti-allucinazione), 7 regole.
- Il **report standard** dei subagent (`CONF/CHANGED/ASSUMED/RISK/UNVERIFIED`,
  ≤150 parole, regola anti-eco, sempre `file:riga`).
- I **principi di modifica** (Minimal Safe Change, Existing Pattern First,
  Contract First, KISS, stile locale, niente commenti-cronaca, commit solo su
  richiesta).
- Il ciclo **Think → Plan → Implement → Verify**.
- Lo **stato che si aggiorna da solo** a 4 livelli (esiste solo in `research-ai`,
  va promosso a generale).
- **Load-on-demand**: ciò che non è universale sta dietro un pointer.

### 2.2 Drift misurato — perché serve A′

Il metodo, dichiarato invariante da `base/README.md`, si è biforcato in 4 versioni.

| Sintomo | Evidenza |
|---|---|
| `model: fable` sopravvive solo nel template padre | 4 occorrenze, tutte in `sources/base/`; 0 nei tre derivati |
| La regola 1 (parallelismo) ha 4 semantiche diverse | `base` la lega al modello («mai >1 Fable 5 attivo»), `oop` al ruolo, `web/base` perde la clausola, `research-ai` la estende a «con altri agenti» |
| Le 10 regole token non sono 10 ovunque | `base`/`oop`/`web` 10 · `research-ai/CLAUDE.md` 5 · `research-ai/…/orchestration.md` 8 |
| Il report «schema fisso» ha 3 varianti | deroga di sicurezza persa in `research-ai`; `RISK` ridefinito; clausola visiva aggiunta in `web` |
| Guide `shared/` riscritte, non adattate | `review-checklist.md`: 103 righe cambiate su 72 in `web/base` — la checklist generica non è più estraibile |

**Causa:** metodo e progetto sono paragrafi adiacenti nello stesso file. Non
esiste un confine fisico, quindi ogni adattamento passa il cursore sopra il
metodo e ogni correzione al metodo va riapplicata a mano N volte.

**Ma l'editing a mano non è il difetto.** I miglioramenti nati lavorando
(`deploy`, `design-guide.md`, la sostituzione di Fable) sono buoni. Il difetto è
che erano **a senso unico**: mai risaliti al padre, mai propagati ai fratelli.

### 2.3 Difetti da correggere, non ereditare

1. **Regola 1** → una formulazione sola, legata al **ruolo**, mai a un modello.
   Un vincolo che nomina un modello muore col modello.
2. **Regole token** → lista canonica di 10, per intero nel kernel, nessuna
   rilocazione parziale.
3. **Report standard** → uno schema. La deroga «per finding di sicurezza» diventa
   «per finding del revisore di superficie critica».
4. **`scientific-reviewer`** → riscritto autonomo. Definirsi «il sostituto del
   security reviewer» è un'incongruenza: eredita l'identità di un altro agente.
   **Ogni agente è dedicato e si regge da solo**; il comune arriva dal kernel,
   mai da un rimando fra agenti.
5. **`review-checklist.md`** → blocco generico di correttezza separato e
   estraibile dal blocco di dominio.
6. **Tabella di routing** → generata dal roster reale, mai copiata.
7. **Path dei file di stato** → canonici (`docs/`), oggi divergenti
   (`.claude/TODO.md` in `research-ai` vs `docs/TODO.md` altrove).
8. **`model: fable`** → mai generato. Fable non è disponibile sul piano;
   `architect` = `opus` + `effort: xhigh`.

## 3. Architettura A′

### 3.1 Principio

Il nucleo si **autore in moduli**, si **installa assemblato**, si **verifica per
hash**. Non è bloccato: è tracciato.

- L'utente può modificare qualsiasi cosa, anche dentro il kernel. Nessun blocco,
  nessuna API di estensione da imparare.
- L'hash smette di tornare → `framework-doctor` lo dice.
- Da lì il flusso è **bidirezionale**: si porta giù una versione nuova, oppure si
  promuove su una modifica locale, perché il prossimo progetto nasca con dentro.

### 3.2 Marker

Regione kernel, in `CLAUDE.md` e in ogni `.claude/agents/*.md`:

```html
<!-- FRAMEWORK:KERNEL v1.0.0 sha256:a3f9c1e4 — generato, non modificare a mano -->
…metodo…
<!-- /FRAMEWORK:KERNEL -->
```

- Hash su contenuto **normalizzato**: line ending LF, trailing whitespace rimosso,
  riga del marker esclusa.
- **Il frontmatter YAML resta fuori dalla regione hashata.** Cambiare `model:` o
  `effort:` è configurazione, non drift: non deve accendere un allarme.
- In variante **B** i marker non vengono emessi: stesso contenuto, nessun tracking.

### 3.3 Perché un file solo e non due

`CLAUDE.md` è caricato a ogni spawn: è il contesto più caro del sistema. Un
secondo file sempre caricato aggiungerebbe intestazioni e pointer a costo pieno,
per zero beneficio — la separazione serve all'**autore**, non al runtime. Quindi:
sorgenti separati, artefatto unico.

Se gli `@import` in `CLAUDE.md` sono supportati nella versione di Claude Code in
uso, l'assemblaggio può restare virtuale; altrimenti l'installer concatena.
**Da verificare in fase di installazione, non da assumere.** Il default è la
concatenazione fisica: zero assunzioni sull'harness.

## 4. Layout dei sorgenti

```
framework/
├─ VERSION                       v1.0.0 — versione del kernel
├─ method/                       KERNEL COMUNE → CLAUDE.md (tutti, ogni spawn)
│  ├─ 00-preamble.md               ruolo, chi legge cosa
│  ├─ 10-execution.md              obblighi di chi esegue un task
│  ├─ 20-evidence.md               Evidence Before Action + report + comunicazione
│  └─ 30-code-principles.md        Minimal Safe Change, Contract First, test…
├─ coordinator/                  KERNEL DEL COORDINATORE → shared/orchestration.md
│  ├─ 00-delegation.md             chi fa cosa + le 10 regole della delega
│  ├─ 10-cycle.md                  ciclo del codice + scelta fra agenti vicini
│  ├─ 20-prompt.md                 struttura del prompt di delega
│  └─ 30-state.md                  i 4 livelli di stato auto-aggiornante
├─ agents/                       19 agenti: metodo + slot [DOMINIO]
├─ shared/                       guide on-demand
│  ├─ core/                        generiche (review-checklist, debugging…)
│  └─ domain/                      per dominio (design, research, data…)
├─ profiles/                     mappa risposte → roster + guide + settings (TOML)
│  └─ software.toml  research.toml  web.toml  data.toml  library.toml
├─ cycles/                       cicli di dominio (research, design), accodati
├─ templates/                    file dinamici generati vuoti
│  └─ TODO.md  roadmap.md  status.md
├─ skills/
│  ├─ framework-install/SKILL.md
│  ├─ framework-doctor/SKILL.md
│  └─ framework-sync/SKILL.md
├─ tools/fwbuild/                assemblaggio, hash, verifiche (Python stdlib)
├─ tools/tests/                  74 test
├─ README.md                     come si installa e come è fatto
└─ lang/en/                      overlay di traduzione (artefatti 3-4)
```

## 5. Artefatto installato

```
progetto/
├─ CLAUDE.md                  [KERNEL v1.0.0] + sezioni di progetto
├─ .claude/
│  ├─ agents/                 solo gli agenti attivi
│  ├─ shared/
│  │  ├─ orchestration.md     [KERNEL] delega + roster — SOLO il coordinatore
│  │  └─ …                    solo le guide pertinenti
│  ├─ skills/                 framework-doctor, framework-sync
│  └─ settings.json           permessi/deny derivati dal profilo
└─ docs/
   ├─ TODO.md                 livello 1 — generato vuoto
   ├─ status.md               livello 2 — generato vuoto
   └─ roadmap.md              il cosa/come
```

### 5.1 Attivazione: si installa quello che serve, non si cancella nulla

`.claude/agents/` contiene **solo gli agenti attivi**. Non è una potatura
distruttiva: il master di ogni agente vive in `framework/agents/` e non viene
toccato. Un agente non attivo non è *cancellato*, è **non ancora installato**.

**Perché non lasciarli tutti presenti e disattivati.** Un file in
`.claude/agents/` non è inerte: nome e `description` di ogni agente finiscono nel
contesto del coordinatore, che è come sa quale agente esiste e quando usarlo — le
`description` dei framework sorgente sono infatti scritte come istruzioni di
routing («Da usare quando…»). Tenerne 19 invece di 8 significa pagare 11
descrizioni in **ogni** sessione, per agenti che il progetto non userà mai. È
costo puro sul file più caro del sistema.

**Perché questo non rompe gli aggiornamenti** (l'obiezione è giusta, la risposta
è che il master sta altrove):

| scenario | con file dormienti | con installazione selettiva |
|---|---|---|
| esce v1.2 che migliora `frontend`, il progetto non ha UI | va sincronizzato un file inutile | niente da fare |
| il progetto **aggiunge** una UI | il file dormiente è fermo a v1.0, va aggiornato | `framework-sync --activate frontend` copia la **v1.2**, già aggiornata |
| il progetto rimuove la UI | resta un file morto | `--deactivate frontend`, il master resta intatto |

Attivare più tardi è quindi **meglio** che avere un file dormiente: si prende
sempre la versione corrente. Requisito: `framework-sync` deve poter raggiungere
`framework/` — lo stesso requisito che ha già per portare giù una versione nuova.

Stessa logica per `.claude/shared/`.

## 6. Il kernel — contenuto canonico

### 6.0 Separazione per destinatario (revisione del 31 ago)

`CLAUDE.md` è caricato in **ogni** contesto, compreso quello di ogni subagent —
i framework sorgente lo confermano, chiudendo ogni agente con «usa il report
standard di CLAUDE.md», istruzione che funziona solo se l'agente quel file lo
vede.

Ne segue che il kernel non si divide per argomento ma per **destinatario**.
Misurato sulla prima stesura: 853 parole su 2200 — il 39% — erano istruzioni che
un `tester` o un `explorer` pagava a ogni spawn e non poteva usare.

| sorgente | artefatto | destinatario | contenuto |
|---|---|---|---|
| `method/` | `CLAUDE.md` | tutti, **ogni spawn** | obblighi di esecuzione · evidenza · report · comunicazione · principi di modifica e test |
| `coordinator/` | `.claude/shared/orchestration.md` | solo chi delega | 10 regole della delega · ciclo del codice · prompt di delega · roster · 4 livelli di stato |

Effetto misurato sull'installazione di prova: `CLAUDE.md` da 2639 a **1730**
parole (−34%).

**Le dieci regole restano complete e numerate in un posto solo** (§6.1), nella
guida del coordinatore, perché sono tutte economia della delega. Gli obblighi di
chi esegue sono una lista **distinta** — non un loro sottoinsieme rinumerato:
spezzare la lista canonica sarebbe il difetto §2.3/2 riprodotto.

Il rientro di contenuto da coordinatore dentro `CLAUDE.md` è un rilievo del
doctor (`COORDINATOR_LEAK`), così la separazione non si riperde alla prima
modifica a mano.

⚠️ Le sottosezioni che seguono riportano il testo canonico delle regole; la loro
**collocazione** è quella della tabella qui sopra, non quella dei titoli §6.1-6.4.

### 6.1 `10-orchestration.md`

Il main agent pianifica, delega, verifica e integra. Esegue **direttamente** solo
le modifiche piccole a basso rischio (≤2-3 file, poche decine di righe, nessun
contratto): lì delegare costa più che fare.

**Le 10 regole di economia dei token** — lista canonica, mai parziale, mai rilocata:

1. **Parallelismo.** `architect` uno alla volta, mai in parallelo con altri agenti
   né rilanciato sullo stesso task: è il più costoso e ragiona sull'intero
   contesto. Gli altri agenti su modello Opus in sequenza; max 2 in parallelo solo
   su task **indipendenti** (file disgiunti, nessun output incrociato — altrimenti
   si pagano due volte le stesse letture e i risultati vanno riconciliati a mano).
   Parallelismo libero solo per `explorer`.
   *(Vincolo legato al ruolo, mai a un modello: è la lezione di Fable.)*
2. **Modello al task, non al ruolo.** Niente `architect` per decisioni ovvie né
   `debugger` per cause evidenti. Su lavoro meccanico e senza giudizio, declassa il
   modello dello spawn a Sonnet (override per-spawn: cambia il modello, l'effort
   dell'agente resta). Solo dove non ci sono decisioni non banali: un modello
   troppo debole sbaglia e il giro a vuoto costa più del premium.
3. **Contesto pre-digerito agli agenti costosi.** `explorer` (repo) e `api-scout`
   (fuori dal repo) esplorano una volta a costo basso e consegnano estratti pronti
   — firme, righe attorno al punto, `file:riga` esatti — così l'agente caro legge
   poco a prezzo pieno. Meglio un explorer accurato in più che un agente caro a
   caccia su file interi.
4. **Letture a range.** Se il prompt dà già estratti e `file:riga`, il subagent
   legge solo quei range (Read offset/limit), mai il file intero; allarga solo se
   l'estratto non basta o non combacia col codice attuale.
5. **Prompt digerito per primacy/recency.** Task + criterio di completamento in
   cima → vincoli → estratti e `file:riga` → criterio ripetuto in fondo. Mai
   seppellire un `file:riga` nella prosa.
6. **Load-on-demand, non front-loading.** Ciò che non è universale sta dietro un
   pointer che l'agente recupera se serve (`.claude/shared/`, explorer→ranges),
   non pre-caricato.
7. **Un task per agente**, con criterio di completamento esplicito. Niente task
   ombrello «sistema tutto»: producono report vaghi e lavoro non verificabile.
8. **Continuare, non ri-spawnare.** Per un secondo giro (es. `implementer` dopo i
   finding del reviewer) si riusa l'agente con il contesto intatto: ripartire da
   freddo ri-digerisce tutto da capo.
9. **Una sola review**: `final-reviewer` **oppure** `/code-review`, mai entrambe.
   Skill native pesanti e agenti di livello 3 solo su richiesta esplicita
   dell'utente.
10. **Niente ri-verifiche ridondanti**: build/test appena passati + nessun file
    cambiato = non si rilancia «per sicurezza».

**Il ciclo del codice.** Capire → Progettare → Implementare → Verificare → Integrare.

1. `explorer` individua i file rilevanti (economico, parallelizzabile);
   `api-scout` se servono firme di librerie esterne.
2. `architect` se il task tocca ≥3 file o un contratto; richieste ambigue → plan
   mode prima. Altrimenti si salta.
3. `implementer`, **un task alla volta**: completa, verifica, passa al successivo.
   Test-first quando il comportamento è esprimibile come test (nuove feature, bug
   fix ben definiti, logica di business/API). Escluso per refactoring, UI,
   prototipi/spike, dipendenze, documentazione.
4. `tester` estende la copertura oltre i mini-test dell'implementer; la build
   passa. **Pochi test che asseriscono qualcosa di vero, non molti test deboli**
   (§6.3).
5. **Revisore di superficie critica** se il diff la tocca, poi `final-reviewer`,
   che verifica da zero senza fidarsi dei report.
6. Il main agent risolve i finding e integra. Commit solo su richiesta.

**Cicli aggiuntivi per dominio** (iniettati dal profilo, non nel kernel): il ciclo
della ricerca (Ipotesi → Protocollo → Run → Analisi → Conclusione) per il profilo
`research`, il ciclo di design per `web`.

### 6.2 `20-evidence.md`

**Evidence Before Action.** Ogni azione parte dall'evidenza raccolta, non dalla
memoria del modello. Se manca un'informazione, cercarla (repo → doc ufficiale →
utente), non inventarla.

1. Mai citare API/firme/comportamenti non letti in sessione. «Mi ricordo che il
   framework fa così» non è una fonte.
2. Mai citare un **numero** non letto in sessione: metriche, conteggi, versioni,
   id. Un numero ricordato è un numero inventato.
3. Mai dichiarare funzionante ciò che non è stato verificato (build, test,
   esecuzione); il resto va in «NON verificato».
4. Le ipotesi si dichiarano come tali («probabilmente»), mai come certezze; fatti
   verificati e interpretazioni restano separati anche tipograficamente.
5. File/simbolo/comando non trovato → dirlo; non inventare path o contenuti.
6. Prima di modificare: leggere i file coinvolti nella versione attuale,
   individuare dipendenze e usi, cercare implementazioni simili nel repo,
   verificare le API reali.
7. Nessun agente dichiara «completato»: chiude col report standard e lascia il
   giudizio al coordinatore.
8. Sui bug è vietato indovinare: prima l'evidenza (Read/Grep sul flusso reale,
   log, repro); il fix si scrive solo quando il meccanismo del difetto è
   individuato e spiega **tutti** i sintomi. I fix a tentativi bruciano token e
   creano regressioni.

**Report standard** — obbligatorio per ogni subagent. Schema fisso e telegrafico,
≤150 parole (deroga solo per i finding del revisore di superficie critica).
Niente prosa di cortesia. Regola anti-eco: non ripetere il contesto ricevuto in
input, il main ce l'ha già. Sempre `file:riga`, mai dump di file o diff.

```
CONF: <0-100%> — <motivo in ≤10 parole>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni o effetti collaterali, o "nessuna nota">
UNVERIFIED: <cosa non è stato eseguito/controllato o "-">
```

Il main agent tratta ogni report come input da verificare, non come verità.

**Come si parlano gli agenti — vincolo di prima classe.**

Ogni token scambiato fra agenti è pagato due volte: una da chi scrive, una da chi
legge. La comunicazione è quindi **telegrafica e densa**, mai discorsiva: si
massimizza l'informazione utile per token, senza perdere accuratezza. Le due
direzioni sono governate entrambe.

**Primacy e recency governano il posizionamento, non solo la lunghezza.** Un
modello pesa di più l'inizio e la fine di un testo; il centro è dove le
istruzioni si perdono. Da qui il corollario operativo, che è la regola vera:

> **I bordi sono per le istruzioni, il centro è per il materiale di
> consultazione.** Un vincolo che deve essere rispettato non va mai sepolto in
> mezzo. Estratti, elenchi di `file:riga`, tabelle di riferimento sì: quelli si
> consultano, non si ricordano.

*Coordinatore → agente* (regola 5 dell'economia dei token):

```
1. TASK          una frase: cosa fare
2. DONE QUANDO   il criterio di completamento, verificabile
3. VINCOLI       i divieti duri — pochi, espliciti
4. MATERIALE     estratti con file:riga esatti (la parte lunga: sta in mezzo
                 perché si consulta, non perché conta meno)
5. DONE QUANDO   ripetuto, testuale
```

Il criterio si scrive due volte di proposito: apre e chiude. Se un agente
sbaglia bersaglio, quasi sempre il criterio era implicito o stava in mezzo.

*Agente → coordinatore*: lo schema qui sopra sfrutta la stessa asimmetria e non
va riordinato. `CONF` in testa è il giudizio che il coordinatore legge per primo;
`UNVERIFIED` in coda è ciò che non deve dimenticare — è l'ultima cosa letta
prima di decidere. In mezzo stanno `CHANGED`, `ASSUMED`, `RISK`: dati che si
rileggono al bisogno.

**Un prompt più corto ha meno centro.** È il motivo per cui la regola anti-eco e
il divieto di prosa non sono galateo: ogni frase inutile spinge verso il centro —
la zona debole — qualcosa che avrebbe dovuto stare su un bordo.

Vietato in entrambe le direzioni:

- prosa di cortesia, preamboli, riepiloghi di ciò che si sta per fare;
- **eco del contesto ricevuto** — chi legge ce l'ha già;
- dump di file, diff interi, blocchi di codice citati per intero: si dà
  `file:riga` e si lascia leggere il range a chi serve;
- narrazione del processo («ho cercato, poi ho aperto, poi ho notato»): conta
  l'esito, con il riferimento che lo dimostra;
- ripetere in prosa ciò che una riga strutturata dice meglio.

Criterio di controllo, prima di inviare: *se togliessi questa frase, il
destinatario perderebbe informazione o solo parole?* Se la seconda, si toglie.

### 6.3 `30-code-principles.md`

Minimal Safe Change · Existing Pattern First · Contract First · KISS · stile
locale · niente commenti-cronaca · **commit solo su richiesta esplicita**.

Aggiunta rispetto ai sorgenti, ereditata dalle direttive globali dell'utente:
**nessuna installazione senza conferma esplicita** — pacchetti, dipendenze,
estensioni, tool CLI, modelli, via qualunque gestore. Vale per ogni agente con
accesso a `Bash`.

**Principio sui test — pochi e sensati, mai molti e deboli.**

Il numero di test non è una metrica. Una suite grande può dare una falsa
sicurezza mentre il difetto vero sta a un livello più alto: un'incoerenza di
architettura, un contratto sbagliato, un comportamento corretto in ogni unità e
sbagliato nell'insieme. Centinaia di test unitari verdi non lo vedono.

Regole operative per `tester` e `implementer`:

1. **Un test che passerebbe anche col bug non conta.** È il criterio già usato dal
   `final-reviewer` nei framework sorgente, promosso a principio generale.
2. **Testare al livello a cui il difetto può nascere.** Se il rischio è
   l'integrazione fra due moduli, un test unitario per lato non lo copre: serve il
   test sulla giunzione.
3. **Preferire invarianti a esempi.** «L'ordinamento è stabile», «la
   normalizzazione è idempotente», «round-trip serializza e rilegge identico»
   valgono più di dieci casi particolari.
4. **Coprire i confini dichiarati**: contratti, formati persistiti, casi limite
   reali del dominio. Non la copertura di riga.
5. **Niente test scritti per alzare un numero.** Se un test non fallirebbe per
   nessun difetto plausibile, non si aggiunge.
6. Quando il rischio è a livello macro e non è esprimibile come test, si dice nel
   report sotto `UNVERIFIED`, con i passi di verifica manuale — non si compensa
   con test unitari che non c'entrano.

### 6.4 `40-state.md` — lo stato che si aggiorna da solo

Generalizzato da `research-ai`, dove esiste solo per progetti a cicli lunghi. Vale
ovunque: senza uno stato scritto, ogni sessione riparte a indovinare.

| Liv. | File | Contiene | Si aggiorna | Tetto |
|---|---|---|---|---|
| 1 | `docs/TODO.md` | dove siamo **adesso**: in corso, in attesa, prossimo passo, bloccati | a **ogni** step | ~60 righe |
| 2 | `docs/status.md` | decisioni chiuse, risultati misurati, ipotesi confermate o smentite | quando qualcosa si chiude | 1 voce |
| 3 | `CLAUDE.md § Stato attuale` | il quadro: cosa sa il progetto oggi | solo se **cambia il quadro** | ~25 righe |
| 4 | memoria persistente | fatti che valgono **fra** sessioni | a ogni scoperta o cambio strutturale | 1 file |

Regole:

- **Si aggiunge o si spunta, non si riscrive.**
- **Si comprime prima di aggiungere** quando il tetto è raggiunto.
- **Scrive il main agent.** I subagent riportano e basta: chi scrive lo stato deve
  aver visto il quadro.
- Inizio sessione: livello 1 per primo. Fine task: livello 1 sempre, 2 se qualcosa
  si è chiuso, 3 se una conclusione è cambiata.
- **Niente duplicazione fra livelli.**
- Livello 4 va **rivisitato, non solo riempito**: a ogni cambiamento significativo
  chiedersi «questo supera una memoria?» e correggerla subito. ⚠️ **In conflitto
  vince il repo**: una memoria vecchia non annotata è un bias attivo.

## 7. Roster — 19 agenti, 3 livelli di attivazione

**Ogni agente è dedicato e si regge da solo.** Nessun agente si definisce per
riferimento a un altro; il metodo comune arriva dalla regione kernel del suo file.

### Livello 1 — sempre installati

| agente | modello · effort | ruolo |
|---|---|---|
| `explorer` | haiku · low | ricognizione nel repo; l'unico liberamente parallelizzabile |
| `architect` | opus · **xhigh** | design e piani, mai codice, mai in parallelo |
| `implementer` | opus · high | codice di produzione |
| `tester` | sonnet · medium | copertura oltre i mini-test |
| `refactorer` | opus · high | comportamento invariato |
| `final-reviewer` | opus · high | verifica finale, non si fida dei report |

### Livello 2 — attivati dal questionario, non installati se non scelti

| agente | modello · effort | attivato quando |
|---|---|---|
| `debugger` | opus · high | il runtime è non banale (stato, concorrenza, I/O) |
| `frontend` | opus · high | esiste una UI |
| `api-scout` | sonnet · medium | il progetto dipende da librerie esterne con API da verificare |
| `deploy` | opus · high | hosting statico/edge — **xor** `infra` |
| `infra` | opus · high | IaC, cloud, ambienti multipli — **xor** `deploy` |
| `data-ingestion` | opus · high | dati esterni entrano nel sistema |
| `results-analyst` | opus · high | ci sono misure da interpretare |
| `literature` | sonnet · medium | paper, stato dell'arte, scrittura accademica |
| `security-reviewer` | opus · high | superficie critica = attaccante |
| `scientific-reviewer` | opus · high | superficie critica = validità delle conclusioni |
| `data-quality-reviewer` | opus · high | superficie critica = correttezza del dato a monte |

Dei tre revisori di superficie critica se ne attiva **uno**; due solo se il
progetto ha davvero due superfici (es. prodotto web che tratta dati personali).

### Livello 3 — installati, mai invocati in autonomia

| agente | modello · effort | note |
|---|---|---|
| `compliance-reviewer` | opus · high | normativa (GDPR, licenze, ToS) |
| `perf-analyst` | opus · high | profiling, complessità, memoria |

Il main agent **non ha il permesso di spawnarli da solo**: solo su richiesta
esplicita dell'utente. È lo stesso meccanismo già applicato alle skill native
pesanti (regola 9), esteso agli agenti — così `compliance-reviewer` non si sveglia
ogni volta che qualcuno tocca un campo email.

### `api-scout` — motivazione

Sta all'esterno del repo come `explorer` sta al repo. «Evidence Before Action»
vieta di citare API non lette in sessione, e tutti e tre i framework sorgente
dichiarano librerie «da verificare nell'uso reale, mai dalla memoria». Oggi quella
verifica la fa l'`implementer` **a prezzo Opus** leggendo documentazione esterna.
`api-scout` la fa a costo Sonnet e consegna firme verificate con la fonte: è la
regola 3 applicata dove finora non c'era nessuno.

Tools: `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`. Legge anche i package
installati (`node_modules`, `site-packages`) — la verità è la versione installata,
non l'ultima documentata. Non modifica nulla.

### Scelte esplicitamente non fatte

- **Nessun agente di cybersecurity offensiva.** `security-reviewer` resta review
  difensiva del codice prodotto.
- **Nessun `threat-modeler`** (si sovrappone all'`architect`) né `recon` (si
  sovrappone all'`explorer`).
- **Nessun `docs-writer`**: coperto da `implementer` + `conventions.md`.
- **Nessun agente per i file di stato**: li scrive il main agent (§6.4).

## 8. Installazione e adattamento

### 8.1 Skill `framework-install`

Passi, nell'ordine:

1. **Rileva** il tipo di installazione: progetto vuoto (adatta a un'idea descritta
   a prompt) o codebase esistente (adatta al codice).
2. **Ricognizione a costo basso** se il codebase esiste: delegata a `explorer`
   (haiku) — manifest di pacchetto, struttura cartelle, comandi build/test,
   stack, punti di ingresso. Il main agent non legge il repo a prezzo pieno.
   *(L'installer applica la regola 3 a sé stesso.)*
3. **Questionario** (§8.2).
4. **Selezione del roster** dal profilo + risposte; si installa solo l'attivo (§5.1).
5. **Generazione**: `CLAUDE.md` assemblato, agenti attivati con blocco dominio
   compilato, guide pertinenti, `settings.json`, file dinamici vuoti.
6. **Verifica** (§8.4). Se fallisce, l'installazione non è completa e lo dice.

### 8.2 Questionario

**Sempre — 4 domande.**

1. **Campo del progetto** → profilo: `software` · `research` · `web` · `data` ·
   `library` · altro (descritto a prompt).
2. **Superficie critica**: cosa rende il lavoro sbagliato anche a codice
   perfetto? → seleziona il revisore.
3. **Stile delle risposte in chat**, su due assi indipendenti:
   - *forma*: telegrafica (conclusione prima, zero prosa) · sintetica ma completa
     (default) · esplicativa (si spiega sempre il **perché** di una scelta) ·
     discorsiva.
   - *base di conoscenza assunta*: cosa si può dare per noto e cosa va introdotto
     alla prima comparsa.

   Il secondo asse è l'aggiunta rispetto ai sorgenti. `research-ai` ha l'unico
   esempio calibrato («per uno studente alla prima esperienza di computer vision
   ma con le basi di ML acquisite: si danno per noti training/loss/embedding»), ed
   è più utile di qualsiasi scelta di verbosità: dice **cosa non spiegare**.
4. **Autonomia**: cosa l'agente può fare senza chiedere (commit, deploy,
   installazioni, esecuzioni lunghe). Default conservativo: nessuna delle quattro.

**Condizionali, solo se il profilo le rende pertinenti.** UI sì/no · dati esterni
in ingresso · misure da interpretare · letteratura · hosting semplice o IaC ·
operazioni pesanti lanciate dall'utente anziché dall'agente (generalizzazione
della regola sbatch di `research-ai`) · normativa applicabile.

### 8.3 Cosa viene compilato

- `CLAUDE.md § Il progetto` — descrizione, mappa moduli, **vincoli DURI**, contratti.
- `CLAUDE.md § Comandi` — build, test, run; chi lancia cosa.
- `CLAUDE.md § Stato attuale` — vuoto alla nascita, poi livello 3 di §6.4.
- Tabella di routing — **generata dal roster reale**.
- Blocco `[DOMINIO]` di ogni agente attivato.
- `shared/domain/*` pertinenti.

Convenzione dei segnaposto, ereditata: `{{NOME}}` per valori puntuali,
`[DA COMPILARE]` per blocchi con istruzioni su cosa metterci.

### 8.4 Verifica di installazione

L'installazione è completa solo se **tutte** passano:

1. `grep -rn "DA COMPILARE\|{{" CLAUDE.md .claude/` → vuoto.
2. Ogni agente citato nella tabella di routing esiste come file, e viceversa.
3. Ogni `.claude/shared/*` referenziato esiste.
4. Ogni hash di regione kernel corrisponde (variante A′).
5. `docs/TODO.md`, `docs/status.md`, `docs/roadmap.md` esistono.
6. Nessun `model: fable` generato.
7. `deploy` e `infra` non coesistono.
8. `.claude/shared/orchestration.md` esiste se ci sono agenti installati.
9. Nessun contenuto da coordinatore rientrato in `CLAUDE.md`
   (`COORDINATOR_LEAK`).
10. `framework-doctor` e `framework-sync` installate in `.claude/skills/`
    (`SKILLS_MISSING`) — senza, non sono invocabili nel progetto.

`.claude/skills/` è escluso dalla scansione dei segnaposto: le skill sono file di
framework copiati alla lettera, e `framework-doctor` contiene per forza la
stringa `DA COMPILARE` perché ne spiega il rilievo.

### 8.5 Skill `framework-doctor` e `framework-sync`

**`framework-doctor`** — esegue le 7 verifiche di §8.4 su un'installazione
esistente e stampa il drift:

```
kernel: v1.0.0 locale ≠ v1.2.0 disponibile
  ~ 10-orchestration §token/1   modificato localmente
  + 40-state §livello-4         assente in locale (aggiunto in v1.1.0)
segnaposto residui: 0
roster: security-reviewer citato in CLAUDE.md ma il file non esiste
```

**`framework-sync`** — le due direzioni:

- **giù**: porta una versione nuova del kernel nel progetto, preservando
  l'adattatore; i conflitti sulle regioni modificate localmente si presentano
  all'utente, non si risolvono da soli.
- **su**: promuove una modifica locale nel `framework/` sorgente, così il prossimo
  progetto nasce con dentro. È la direzione che mancava e che ha prodotto il drift.

Le tre skill sono **del coordinatore**: le invoca l'utente o il main agent, mai un
subagent. Questo evita di dipendere dalla disponibilità del tool `Skill` nella
lista `tools:` di un agente — da verificare, non da assumere. Le guide di dominio
restano `.claude/shared/*.md` dietro pointer: meccanismo provato nei sorgenti,
zero assunzioni sull'harness.

## 9. Roadmap

| # | Artefatto | Contenuto |
|---|---|---|
| 1 | **A′** | sorgenti + build con marker/hash + 3 skill |
| 2 | **B** | stessa sorgente, `variants.toml` con marker off |
| 3 | **A′-EN** | overlay `lang/en/`, tracciato per versione |
| 4 | **B-EN** | combinazione di 2 e 3 |

`framework-doctor` verifica anche l'allineamento fra lingue: *«kernel IT v1.2.0,
EN fermo a v1.0.0, disallineati: 10-orchestration §token/1»*. È l'unico modo per
cui la traduzione non diventi il nuovo `base/` fossile.

## 10. Questioni aperte

1. **`@import` in `CLAUDE.md`** — supportati? Se sì, l'assemblaggio resta virtuale.
   Default: concatenazione fisica. Da verificare, non da assumere.
2. **Tool `Skill` nella lista `tools:` di un subagent** — se disponibile, alcune
   guide di dominio potrebbero diventare skill auto-triggerate invece di pointer.
   Non è nel percorso critico: il pointer funziona già.
3. **`docs-writer`** — escluso per YAGNI; da riconsiderare se emerge il bisogno.

**Non in programma:** migrazione dei 3 progetti in `sources/` al nuovo framework.
È lavoro vecchio; servono come materiale di partenza, non come parco installato.
