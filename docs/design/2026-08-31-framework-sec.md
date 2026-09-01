# framework+sec — estensione cyber-security del framework — design

**Data:** 2026-08-31 · **Stato:** approvato in brainstorming, da implementare
**Deriva da:** `framework/` v1.0.0 · `docs/design/2026-08-31-meta-framework.md`

---

## 1. Obiettivo

Un'**estensione** del framework per il lavoro di sicurezza su artefatti non
fidati: reverse engineering e threat analysis. Vive in `framework+sec/`, una
copia di `framework/` che si estende; `framework/` non viene toccato in nessun
passo.

Tre decisioni prese in brainstorming, che governano tutto il resto:

1. **Estensione, non copia sincronizzata.** I due alberi possono divergere. Il
   secondo è il primo *più* il dominio sec, non una sua replica da tenere
   allineata riga per riga.
2. **Innesto ovunque, più un profilo dedicato.** Gli agenti sec compaiono come
   `on_demand` nei profili esistenti dove hanno senso, *e* esiste un profilo
   `security` pieno per i progetti che sono di sicurezza.
3. **Infrastruttura di metodo completa:** un ciclo di dominio, una guida
   condivisa, e una verifica meccanica nel doctor. Il metodo non si duplica
   dentro le schede agente.

## 2. Perché un dominio e non «qualche agente in più»

Il framework distingue già i domini in cui **il prodotto non è software che
gira**. `research` esiste perché lì il prodotto è evidenza riproducibile: un
programma che gira e produce numeri sbagliati è un fallimento completo, non un
successo parziale.

L'analisi di sicurezza ha la stessa forma. Il prodotto è **un verdetto sostenuto
da evidenza su un artefatto**. Un'analisi elegante che sbaglia il verdetto è un
fallimento completo. Quindi merita lo stesso trattamento che ha avuto `research`:
un ciclo proprio, non una manciata di schede.

### 2.1 Il confine con `security-reviewer`

`security-reviewer` esiste già e **non viene toccato**. Guarda il codice che
*questo progetto* scrive: input non fidato, segreti, autorizzazione, dipendenze.
Difensivo, verso l'interno.

Gli agenti nuovi guardano **artefatti altrui**: binari, campioni, catture di
rete, log. Analitici, verso l'esterno.

È la confusione più probabile del roster, quindi va scritta esplicitamente nella
tabella di routing generata, non lasciata dedurre dalle `description`.

## 3. Layout di `framework+sec/`

Copia integrale di `framework/`, esclusi i `__pycache__`, poi il delta:

| file | stato | nota |
|---|---|---|
| `VERSION` | modificato | `1.0.0` → `1.0.0+sec.1` |
| `README.md` | modificato | numeri aggiornati, sezione «Estensione sec» |
| `agents/` | 19 → **27** | 8 file nuovi, 19 invariati |
| `cycles/threat-analysis.md` | nuovo | terzo ciclo di dominio |
| `shared/domain/security-guide.md` | nuovo | quarta guida di dominio |
| `profiles/security.toml` | nuovo | sesto profilo |
| `profiles/software.toml` | modificato | solo `on_demand +=` |
| `profiles/web.toml` | modificato | solo `on_demand +=` |
| `profiles/data.toml` | modificato | solo `on_demand +=` |
| `profiles/library.toml` | invariato | innestare qui sarebbe rumore |
| `profiles/research.toml` | invariato | idem |
| `skills/framework-install/SKILL.md` | modificata | profilo, domande, sezione perimetro |
| `skills/framework-doctor/SKILL.md` | modificata | undicesimo codice |
| `skills/framework-sync/SKILL.md` | modificata | nota sul sync fra i due alberi |
| `tools/fwbuild/doctor.py` | modificato | `SCOPE_MISSING` |
| `tools/tests/` | 74 → 74 + ~11 | ~8 su roster/profili, 3 su `SCOPE_MISSING`; i 74 esistenti devono restare verdi |
| `method/`, `coordinator/` | **invariati** | il metodo comune non si riscrive per un dominio |
| `tools/fwbuild/{kernel,assemble,profile,cli}.py` | **invariati** | — |

### 3.1 La versione

`1.0.0+sec.1`. Serve a una cosa sola: il marker kernel di un progetto installato
diventa `v1.0.0+sec.1`, quindi si sa **quale dei due alberi l'ha generato**.

Verificato: `kernel.OPEN_RE` cattura la versione con `v(?P<version>\S+)`, e `+`
non è uno spazio. Nessuna modifica a `kernel.py` è necessaria.

## 4. Roster — 8 agenti

Cinque attivi nel profilo `security`, tre a invocazione esplicita. La colonna
«non fa» è parte della specifica: nel framework il confine del mandato è metà
della scheda.

### 4.1 Attivi

| agente | model | effort | tools | color |
|---|---|---|---|---|
| `sample-triage` | sonnet | medium | Read, Grep, Glob, Bash | cyan |
| `binary-analyst` | opus | high | Read, Grep, Glob, Bash | orange |
| `dynamic-analyst` | opus | high | Read, Grep, Glob, Bash | magenta |
| `threat-analyst` | opus | high | Read, Grep, Glob, WebSearch, WebFetch | brown |
| `detection-engineer` | opus | high | Read, Grep, Glob, Edit, Bash | yellow |

I colori si ripetono con agenti già esistenti (`orange` è di `deploy`/`infra`,
`magenta` del `debugger`, `cyan` di `explorer`/`api-scout`). La regola adottata:
un colore può ripetersi purché i due agenti **non finiscano nello stesso roster
installato**. L'unica coppia a rischio è `binary-analyst` (orange) con
`deploy`/`infra` nel profilo `software`: `binary-analyst` lì passa a `red-orange`
se il conflitto risulta visivamente fastidioso — è configurazione, non metodo, e
sta fuori dalla regione kernel.

**`sample-triage`** — prima passata a costo basso su un artefatto: tipo di file,
hash, entropia, sezioni, import, stringhe notevoli, indizi di packing, IOC di
superficie. Consegna estratti pronti e **una domanda** per l'analista caro.
È `explorer` applicato al dominio: esiste per una ragione economica, cioè perché
la ricognizione non la paghi a prezzo Opus (regola 3 della delega).
*Non fa:* non conclude, non attribuisce, non esegue.

**`binary-analyst`** — il **meccanismo** del binario: cosa fa, come, e con quale
evidenza a offset o funzione. L'asticella è quella del `debugger`: capito quando
sai dire *questo input, per questo percorso, produce questo effetto*, e la
spiegazione copre **tutti** i comportamenti osservati, non solo quello vistoso.
*Non fa:* non esegue l'artefatto, non scrive regole di rilevamento.

**`dynamic-analyst`** — interpreta evidenza di esecuzione **già prodotta**: log
di sandbox, catture di rete, trace, snapshot, differenze di stato. Quando serve
una detonazione, **prepara il comando esatto** e la riga di attesa in
`docs/TODO.md` con *cosa deve rispondere* quell'esecuzione.
*Non fa:* non detona.

**`threat-analyst`** — TTP osservate → tecniche ATT&CK, correlazione con
campagne note, ipotesi di attribuzione. Ogni affermazione porta un livello di
confidenza esplicito. Usa `WebSearch`/`WebFetch` come `api-scout` e `literature`:
fatti verificati con la fonte, mai memoria del modello.
*Non fa:* non presenta un'attribuzione come fatto.

**`detection-engineer`** — YARA, Sigma, Suricata, più la **validazione**: falsi
positivi contro un corpus dichiarato, falsi negativi contro le varianti note.
Una regola non validata non è una regola, è un'ipotesi con la sintassi di una
regola — e va marcata come tale.
*Non fa:* non firma su IOC volatili senza dichiararne la deperibilità.

### 4.2 On demand

| agente | model | effort | tools | mandato |
|---|---|---|---|---|
| `vuln-researcher` | opus | high | Read, Grep, Glob, Edit, Bash | memory safety, disegno di harness, triage di crash, giudizio di sfruttabilità |
| `protocol-analyst` | opus | high | Read, Grep, Glob, Bash | ricostruzione di formati e protocolli, uso della crittografia |
| `forensics-analyst` | opus | high | Read, Grep, Glob, Bash | artefatti host, timeline, meccanismi di persistenza |

`vuln-researcher` produce **giudizi di sfruttabilità e correzioni**, non exploit
funzionanti: il prodotto è «questo crash è sfruttabile perché…, si chiude così».

### 4.3 Formato dei report

Tutti chiudono col report standard di `method/20-evidence.md`
(`CONF/CHANGED/ASSUMED/RISK/UNVERIFIED`, ≤150 parole).

`threat-analyst` e `detection-engineer` usano la **deroga finding** già prevista
per i revisori di superficie critica: un elenco strutturato prima del report, con
lo stesso impianto di `security-reviewer` (gravità, scenario, correzione minima).

`ANALYZED` sostituisce `CHANGED` per tutti gli agenti in sola lettura, come già
fa `security-reviewer`.

## 5. Il ciclo `threat-analysis`

Si affianca al ciclo del codice come fa `research`, non lo sostituisce.

**Perimetro → Triage → Meccanismo → Attribuzione → Rilevamento**

1. **Perimetro** — cosa si può toccare e con quale autorizzazione, deciso prima
   di aprire il primo file. Passo zero, non saltabile.
2. **Triage** (`sample-triage`) — una passata a costo basso, estratti pronti per
   chi costa. Saltarlo significa far leggere l'artefatto grezzo a un agente caro.
3. **Meccanismo** (`binary-analyst`, `dynamic-analyst`) — cosa fa davvero, con
   evidenza puntuale. La spiegazione deve coprire tutti i comportamenti visti.
4. **Attribuzione** (`threat-analyst`) — **ipotesi finché non c'è evidenza
   indipendente**. Tre livelli, mai impliciti: certo · probabile · ipotesi.
5. **Rilevamento** (`detection-engineer`) — la regola, e la prova che regge sui
   falsi positivi.

### 5.1 Vincoli duri del ciclo

- **L'agente non esegue mai l'artefatto.** Prepara il comando, scrive la riga di
  attesa in `docs/TODO.md` con cosa deve rispondere quell'esecuzione, e l'utente
  detona nel proprio ambiente. È il punto 3 del ciclo `research` («se è pesante
  la lancia l'utente») applicato qui: non è una regola nuova, è coerenza.
- **Il perimetro è dichiarato, o non si lavora.** Verificato meccanicamente (§7).
- **Confidenza sempre esplicita.** L'attribuzione senza confidenza è la modalità
  di fallimento tipica del threat intel.
- **Catena di custodia:** hash dell'artefatto dichiarato all'inizio; l'artefatto
  non si modifica in place; le copie di lavoro sono dichiarate.
- **L'assenza di prova non è prova di assenza.** «Non ho trovato comportamento
  malevolo» va scritto così, non come «pulito».

## 6. Profili

### 6.1 `security.toml`

```toml
name = "security"
description = "Analisi di artefatti non fidati: reverse engineering, threat analysis, rilevamento."

agents = ["sample-triage", "binary-analyst", "dynamic-analyst",
          "threat-analyst", "detection-engineer"]
on_demand = ["vuln-researcher", "protocol-analyst", "forensics-analyst",
             "compliance-reviewer", "security-reviewer"]
cycles = ["threat-analysis"]

shared = [
  "core/conventions.md",
  "core/coding-standards.md",
  "core/architecture-guide.md",
  "core/testing-guide.md",
  "core/debugging-playbook.md",
  "core/review-checklist.md",
  "domain/security-guide.md",
]

[settings.permissions]
deny = ["Read(./**/*.env)", "Read(./**/*.key)", "Read(./**/*.pem)"]
# + regole di contenimento sull'esecuzione — vedi §9.1
```

Con `ALWAYS` (6 agenti) il roster attivo risulta di **11** agenti.

I tre `deny` di lettura sopra sono quelli già collaudati in `software.toml` e si
ereditano tali e quali: sono il **contenuto minimo garantito** del profilo. Le
regole di contenimento sull'esecuzione (impedire che un agente lanci l'artefatto
o lo renda eseguibile) richiedono la sintassi `Bash(...)`, che va verificata in
implementazione e non assunta — §9.1 dice cosa fare in entrambi gli esiti.

### 6.2 Innesto nei profili esistenti

Solo aggiunte in coda a `on_demand`. Nessun'altra chiave toccata.

| profilo | aggiunta | perché |
|---|---|---|
| `software` | `binary-analyst`, `vuln-researcher` | si spedisce un binario; il crash triage serve |
| `web` | `vuln-researcher` | superficie raggiungibile per definizione |
| `data` | `threat-analyst` | i dati in ingresso possono essere ostili |
| `library` | — | innestare qui sarebbe rumore |
| `research` | — | idem |

`profile.roster()` mette `on_demand` in coda e deduplica: l'aggiunta non altera
l'ordine degli agenti già presenti. Nessuna nuova coppia in `EXCLUSIVE`.

## 7. `SCOPE_MISSING` — undicesimo codice del doctor

Gravità **ERRORE**. Sette codici ERROR, quattro WARN.

Il doctor riceve solo la root del progetto: **non conosce il profilo**. Quindi
rileva dal roster installato, senza introdurre stato nuovo:

```
SEC_AGENTS = {sample-triage, binary-analyst, dynamic-analyst, threat-analyst,
              detection-engineer, vuln-researcher, protocol-analyst,
              forensics-analyst}

se  (agenti presenti in .claude/agents/) ∩ SEC_AGENTS  ≠ ∅
e   "## Perimetro e autorizzazione" ∉ CLAUDE.md
→   SCOPE_MISSING  ERROR
```

Un progetto senza agenti sec non è mai toccato da questa regola.

Modifiche collegate:

- docstring di `doctor.py`: «Dieci codici… sei ERROR… quattro WARN» → undici,
  sette, quattro;
- tabella dei codici in `framework-install/SKILL.md` e in
  `framework-doctor/SKILL.md`: riga nuova con spiegazione e rimedio.

## 8. Installazione

Modifiche a `framework-install/SKILL.md`:

1. **Tabella dei profili** (Passo 3, domanda 1): riga `security` — «analisi di
   artefatti non fidati: reverse engineering, threat intelligence, rilevamento».
2. **Superficie critica** (domanda 2): la risposta «l'artefatto potrebbe non
   essere quello che sembra» attiva il ciclo sec, non un revisore in più.
3. **Domanda nuova, obbligatoria se il profilo è `security`:** perimetro e
   autorizzazione — su quali artefatti e sistemi si lavora, con quale mandato,
   cosa è fuori perimetro. Senza risposta non si genera.
4. **Sezione nuova in `CLAUDE.md`**, `## Perimetro e autorizzazione`, compilata
   da quella risposta. È il livello di stato che il doctor verifica.
5. **Domande condizionali:** «ci sono catture di rete o protocolli da
   ricostruire?» → `protocol-analyst`; «si lavora su immagini di disco o
   memoria?» → `forensics-analyst`; «serve cercare vulnerabilità nel codice
   analizzato?» → `vuln-researcher`.

La sezione `## Perimetro e autorizzazione` sta in `CLAUDE.md`, non nella guida
del coordinatore: la leggono **tutti** gli agenti, ed è la sola parte di
contenuto sec che sia legittimo far pagare a ogni spawn.

## 9. Rischi e punti aperti

### 9.1 Sintassi dei permessi

I `deny` di `security.toml` che vanno oltre le regole `Read(...)` già in uso
richiedono di conoscere la sintassi reale delle regole `Bash(...)`. Va
**verificata**, non dedotta: una regola scritta a memoria che non matcha dà una
falsa sensazione di contenimento, che è peggio di nessuna regola.

Se la verifica non riesce, il profilo si limita ai `deny` di lettura già
collaudati, e il contenimento resta affidato ai vincoli del ciclo (§5.1).

### 9.2 Sync fra i due alberi

Con versioni divergenti il confronto sul marker funziona, ma un
`framework-sync --giù` eseguito da `framework/` su un progetto nato da
`framework+sec/` **degraderebbe silenziosamente** il progetto: kernel comune
uguale, ma versione e aspettative diverse.

Decisione: si **annota nel README** di `framework+sec/` e in
`framework-sync/SKILL.md`. Non si risolve con codice adesso — servirebbe un
identificativo di albero nel marker, cioè una modifica a `kernel.py`, che è
sproporzionata rispetto al rischio.

### 9.3 Il contenuto delle schede è il lavoro vero

Otto schede agente sono la parte lunga del piano, e devono contenere metodo
reale — modelli di minaccia, ordini di operazione, formati — non boilerplate
riscritto otto volte. Ciò che è comune sta nel ciclo e nella guida di dominio.

## 10. Verifica di completamento

L'estensione è finita quando, in quest'ordine:

1. `cd framework+sec/tools && python -m unittest discover -s tests -t . -v`
   passa: i 74 test esistenti **più** quelli nuovi;
2. `cd framework/tools && python -m unittest discover -s tests -t . -v` passa
   ancora, e il filesystem conferma che `framework/` non ha differenze;
3. un'installazione di prova con profilo `security` (sul modello di
   `scripts/trial-install.py`) produce `OK — nessun rilievo`;
4. la stessa installazione, **rimossa** la sezione `## Perimetro e
   autorizzazione`, produce `SCOPE_MISSING`;
5. un'installazione con profilo `software` resta identica a quella prodotta da
   `framework/`, a meno della versione nel marker.

Il punto 5 è la prova che l'innesto negli `on_demand` non ha cambiato il
comportamento dei profili esistenti.
