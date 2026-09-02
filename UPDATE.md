# UPDATE — problemi aperti e direttive

Sintesi di una valutazione esterna del framework, **riallineata al codice il
2026-09-01**. Documento operativo: cosa non regge, cosa fare, in che ordine.

**Premessa epistemica.** La valutazione del panorama esterno viene da conoscenza
pregressa (cutoff maggio 2026), non da fonti verificate. La valutazione del
framework viene invece dalla lettura diretta dei file. Le due cose hanno peso
diverso e vanno trattate diversamente.

**Stato misurato.** v1.0.0 · **103 test verdi** (`pytest -q` e `unittest
discover` danno lo stesso numero) · kernel comune **1265 parole** su un tetto di
1600 · guida del coordinatore 1601 parole base, **1882 sul profilo `research`**
su un tetto di 2000 · **19 agenti in catalogo, 11–14 installati per progetto**.
`framework/` è autosufficiente: nessun file al suo interno cita `scripts/`,
`sources/`, `docs/`, `_build/` o questo documento.

**Lavoro attivo:** **D1**. D0 e la sezione [Installing](#installing) sono
**chiuse** (2026-09-01). D1 ha protocollo e strumenti; mancano i task e le
prove. Il 2026-09-02 il framework è stato installato **sul repository che lo
produce** e poi rimosso: era una prova, e ciò che ne resta sta in **P4** e in
[La prova sul campo](#la-prova-sul-campo--2026-09-02).
I confronti esterni, con i riferimenti fissati a un commit, stanno in
[Riferimenti esterni](#riferimenti-esterni): le sigle **R1–R3** (da cui
prendere) ed **E1–E6** (prove) sono citate dalle direttive.

---

## Verdetto

Scrittura e architettura di livello alto. Un'idea buona, sepolta in una quantità
di contenuto che non è mai stata misurata. **Vendibile nella forma attuale: no** —
e non per la qualità.

---

## Cosa regge (non toccare)

| Elemento | Perché regge |
|---|---|
| Tesi del kernel comune | «CLAUDE.md è pagata a ogni spawn, quindi le regole di delega le paga anche un explorer che non delega» è un'osservazione corretta, non ovvia, con conseguenze economiche reali |
| Vincolo meccanico sul budget | [test_end_to_end.py:83](framework/tools/tests/test_end_to_end.py#L83) fa fallire la build sopra 1600 parole. Non è un consiglio in un README: rompe la build |
| `COORDINATOR_LEAK` nel doctor | [doctor.py:245](framework/tools/fwbuild/doctor.py#L245) — il vincolo è verificato, non solo dichiarato |
| Sync con regione hash (`--up`) | Rende il drift visibile invece che sepolto, e lo tratta come segnale anziché errore |
| Doctor come linter di configurazione agentica | Pointer penzolanti, roster orfani, segnaposto non compilati, agenti mutuamente esclusivi. È la parte con più potenziale di prodotto |
| Domanda del Passo 3.2 | «Cosa rende il lavoro sbagliato anche a codice perfetto?» — una riga che fa il lavoro di una matrice |
| Tooling | stdlib pura, zero dipendenze, 103 test verdi |

**Il contributo originale è il quartetto**, non i singoli ingredienti:
separazione per destinatario + budget del kernel come test + doctor che verifica
l'installazione + promozione bidirezionale. Ingegnerizzazione seria di intuizioni
sparse. Va chiamato col suo nome: non è una rivoluzione.

**Ingredienti non differenzianti** (esistono già, pubblici e gratuiti): roster di
agenti con mandato, regole anti-allucinazione, economia dei token, primacy/recency,
cicli per dominio, questionario di installazione, spec-driven.

---

## Problemi

### P1 — Zero evidenza (blocca tutto il resto)

I 103 test verificano l'assemblatore, non il metodo. Non esiste ancora una
baseline, né un confronto appaiato, né un tasso di successo.

Aggiornamento del 2026-09-01: **la misura non manca più, mancano le prove.**
`docs/eval/` esiste col protocollo e il criterio fissato, e `transcript.py`
misura i token per task su dati reali (**D0**). Restano i 21 task da scegliere e
le sessioni da eseguire. P1 resta aperta, ma non è più «non si sa come si
misurerebbe»: è «non è stato ancora misurato».

[research-principles.md](framework/shared/domain/research-principles.md) pretende
ipotesi falsificabile, baseline prima della complessità, criterio deciso prima.
**Il framework non applica a sé stesso lo standard che impone agli altri.**

Conseguenza: nessuno può dire quale parte del metodo è portante e quale è prosa
inerte che il modello avrebbe prodotto comunque.

### P2 — `CONF: <0-100%>` in testa al report

[20-evidence.md:34](framework/method/20-evidence.md#L34). È il campo che il
coordinatore legge per primo, per design. Ma la confidenza auto-riportata da un
LLM è mal calibrata: **segnale debole in posizione di segnale forte.** La
precisione percentuale è finta.

Nota di stato: `CONF` compare in **un solo punto** dell'intero framework, e
**nessun test ne verifica il formato**. Cambiarlo è una riga; impedire che il
formato vecchio sopravviva nei progetti già installati richiede un test che oggi
non c'è.

### P3 — Rotta di collisione con la piattaforma

Claude Code assorbe questa superficie a ogni release: subagent nativi, skill,
`model:`/`tools:` nel frontmatter, memoria, hook. Un framework il cui valore è
«file di metodo + roster» viene eroso dal basso.

La differenziazione deve stare dove la piattaforma non andrà: **verifica
dell'installazione** e **sincronizzazione fra molti repo**. Non nel testo.

### P4 — Il tetto di parole copre meno di metà del file che si paga

Misurato il 2026-09-02 installando il framework su sé stesso.

I due tetti sono test veri, ma stanno **sul sorgente**:
[test_end_to_end.py:87](framework/tools/tests/test_end_to_end.py#L87) limita
`read_method(method/)` a 1600 parole, [:82](framework/tools/tests/test_end_to_end.py#L82)
la guida del coordinatore a 2000. Il file che ogni spawn paga davvero è però
`CLAUDE.md` **assemblata** — kernel *più* sezioni di progetto — e le sezioni di
progetto non le tocca nessun tetto.

| `CLAUDE.md` generata | totale | kernel | sezioni di progetto |
|---|---|---|---|
| questo repo, profilo `library` | 2367 | 1265 | **1102 (47%)** |
| prova di `trial_install.py`, profilo `research` | 1588 | 1265 | 323 (20%) |

Non è prolissità di chi installa: quelle sezioni sono esattamente ciò che il
Passo 5 di `framework-install` chiede — mappa dei path, vincoli duri, contratti
con chi li consuma, comandi, verifica rapida, operazioni dell'utente, superficie
critica, stato, guide, stile. La prova ne scrive 323 perché descrive un progetto
finto: è il numero di un caso sintetico, non di un progetto vero.

**Perché conta.** La separazione per destinatario è la mossa migliore del
framework, e i numeri la confermano: tiene **1601 parole** di kernel del
coordinatore fuori da `CLAUDE.md`, così ogni subagent ne paga 1265 invece di
2866. Quel risparmio è reale, ed è fisso.

Il problema è che accanto a un risparmio fisso di 1601 c'è un costo **libero** di
1102, sullo stesso file e con la stessa frequenza. La disciplina misura la parte
che il framework scrive e lascia scoperta quella che l'installazione scrive — e
solo la seconda cresce, perché cresce col progetto. Su un progetto più grande di
questo non c'è niente che dica quando è troppo.

Da decidere, non da correggere di slancio: un tetto sul totale assemblato
romperebbe la build **di un progetto**, non del framework, e il framework non ha
un posto dove farlo scattare. Il posto giusto è un rilievo WARN del doctor, che
già guarda l'installazione. Ma la soglia va scelta su un numero, non a occhio —
quindi passa da D1/D2 come tutto il resto.

### Minori ma reali

| Problema | Sintomo |
|---|---|
| Agenti che entrano in **ogni** roster senza mandato automatico | `compliance-reviewer` e `perf-analyst` sono `on_demand` in **tutti e cinque** i profili: sono installati sempre, e sono proprio i due a sola invocazione esplicita. Costo fisso per progetto, ritorno mai misurato |
| Sovrapposizione `deploy`/`infra` | Il check `EXCLUSIVE` ([doctor.py:205](framework/tools/fwbuild/doctor.py#L205)) esiste perché il taglio non è netto. Da correggere la diagnosi precedente: **nessun profilo li installa insieme** (web→`deploy`, data→`infra`), quindi il check non scatta mai di default — si attiva solo dopo un `--activate` a mano. Resta un problema di mandato, non un sintomo osservabile |
| Margine sul tetto del coordinatore | `research` è a 1882/2000 parole (94%), `web` a 1827. Un ciclo di dominio in più sfonda la soglia e rompe la build |
| ~~Dipendenza agente → guida non dichiarata~~ **risolto 2026-09-02** | Un agente attivato con `extras` portava pointer a guide che il profilo non installa: `scientific-reviewer` e `results-analyst` citano `shared/domain/research-principles.md`, elencata solo da `research.toml` → due `SHARED_MISSING`. `profile.roster` risolveva gli agenti, **niente risolveva le loro guide**. Chiuso da [`profile.required_guides`](framework/tools/fwbuild/profile.py) e dal Passo 5 della skill, con 4 test. Misurato: **nessun profilo ha il buco da solo** — lo aprono solo gli extra, ed è per questo che la prova `trial_install.py` non poteva vederlo (usa `research`, che quella guida la installa già) |
| Due profili indistinguibili | `software.toml` e `library.toml` dichiarano lo stesso `agents`, lo stesso `on_demand`, le stesse sei guide e gli stessi `settings`: differiscono solo per `name` e `description`. Sceglierli non ha conseguenze meccaniche. Candidato per la potatura di **D2** |
| `framework.json` con percorso assoluto | La skill fa scrivere `source` come path assoluto. Quando il sorgente è **dentro** il progetto — il primo dei tre modi previsti — l'assoluto è la macchina di chi ha installato, e rompe qualunque clone. Va relativo in quel caso |
| Lingua | L'italiano taglia fuori quasi tutto il mercato |

---

## Direttive

Ordine vincolante. D1 è un cancello: D5–D7 senza un numero sono opinioni. D0 è
il prerequisito di D1: senza strumento, il criterio di D1 non è misurabile.

**D9-D10 non sono in fila: sono aperte alla discussione.** A differenza delle
altre toccano i file di `method/` e `coordinator/` — la parte che ogni agente
paga — quindi la domanda «dove va scritto» pesa quanto «cosa va scritto».

### D0 — Strumentazione dell'eval

D1 chiede token per task, tasso di successo, interventi umani. Oggi non esiste
niente che li misuri, ed è il motivo per cui il cancello è fermo. **Il dato però
è già sul disco.**

Claude Code scrive un transcript `.jsonl` per sessione in
`~/.claude/projects/<progetto>/<id>/`, e **un file separato per ogni subagent**
in `.../subagents/agent-*.jsonl`. Verificato su questa macchina il 2026-09-01,
per ogni entrata: `type`, `timestamp`, `sessionId`, `promptId`, `uuid`,
`parentUuid`, `cwd`, `gitBranch`, `version`, `agentId`, `isSidechain`, `effort`,
`attributionAgent`, `attributionSkill`, `toolUseResult`. E sulle entrate
`assistant`, `message.usage` porta `input_tokens`, `output_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`.

Conseguenza che vale più dell'eval stessa: **la tesi centrale del framework
diventa misurabile invece che argomentata.** «CLAUDE.md è pagata a ogni spawn»
smette di essere un'osservazione e diventa un numero — `isSidechain: true` più
`usage`, per ogni subagent, sessione per sessione.

**✅ Fatto.** [scripts/transcript.py](scripts/transcript.py), 297 righe, stdlib
pura, 16 test. Fuori dal pacchetto: resta materiale di lavoro finché non si è
guadagnato un posto in `framework/`.

Il criterio di chiusura era «su una sessione reale già archiviata, produrre i
token totali e la ripartizione fra coordinatore e subagent». Eseguito su una
sessione con due spawn veri:

```
  ramo                       turni  umani  tool   contesto       totale
  coordinatore                  54      3    29     72.403    5.258.896
  general-purpose/graphify      27      1    14     35.979    2.635.563
  general-purpose/graphify      24      1    13     36.257    2.095.218

  totale di sessione   9.989.677 token
  ripartizione         coordinatore 53% · subagent 47% su 2 spawn
  caricato agli spawn  72.236 token — contesto pagato prima che un subagent lavori
```

**La tesi del framework ha finalmente un numero.** Su due soli spawn, il 47%
dei token di sessione è finito nei subagent, e 72.236 sono stati caricati
*prima* che uno di loro facesse qualcosa. Ogni riga del kernel comune è dentro
quel numero, moltiplicata per il numero di spawn.

Tre accertamenti che cambiano il disegno dell'eval:

- **I due insiemi sono disgiunti**: il transcript del coordinatore non contiene
  entrate `isSidechain`, quindi sommarlo ai file dei subagent non conta niente
  due volte. Se non lo fosse stato, ogni misura sarebbe stata gonfia
- **Il contesto di uno spawn è il prompt del *primo* turno**, non la somma dei
  prompt di tutti i turni: quella conta lo stesso contesto una volta per turno
  ed è il modo più facile di gonfiare proprio la tesi che si vuole misurare
- **`cache_read` è il 95% del totale** (4,99M su 5,26M nel coordinatore). Un
  «totale token» crudo misura più il funzionamento della cache che il metodo:
  per questo il CSV tiene i quattro tipi separati e il protocollo definisce la
  metrica primaria, invece di dire «token» e basta

Riferimento **R1**, usato come previsto — **letto, non copiato**. Il loro
`SessionData` cattura la conversazione e ignora `usage`, `agentId`,
`isSidechain`, `effort`: serviva esattamente la metà che a loro non serviva.
Dalla loro lettura vengono le forme delle entrate (`message.content` a parti,
`tool_use`, `tool_result`); il resto è nuovo.

### D1 — Eval del metodo

Applicare [cycles/research.md](framework/cycles/research.md) al framework stesso.

**◐ Protocollo scritto, prove non iniziate.**

| | |
|---|---|
| ✅ [docs/eval/protocollo.md](docs/eval/protocollo.md) | criterio **fissato il 2026-09-01, prima di qualunque prova** |
| ✅ strumento | `transcript.py --csv`, la metrica primaria è calcolabile |
| ✅ corpus | **230 richieste umane reali** estraibili con `--prompts` su quattro progetti |
| ◐ [docs/eval/task.md](docs/eval/task.md) | regole, stratificazione e formato scritti; **3 task su 24 compilati** |
| ⬜ `docs/eval/risultati/` | vuoto: nessuna prova eseguita |
| ⬜ `docs/eval/esito.md` | si scrive dopo, e si scrive anche se negativo |

Tre decisioni prese nel protocollo, che non erano nella direttiva e la cambiano:

- **La baseline conosce il progetto.** Condizione B = `CLAUDE.md` con le sole
  sezioni di progetto, senza kernel, agenti e guide. Una baseline all'oscuro
  del progetto misurerebbe «sapere del progetto», non il metodo
- **La metrica primaria è il *contesto*, non «i token».** `input +
  cache_creation + cache_read` sommati su tutti i rami. Un totale crudo è per
  il 95% `cache_read` e misura la cache. Nessun costo in euro: i quattro tipi
  si pagano a tariffe diverse, il CSV li tiene separati e il conto si fa dopo
- **La guardia è vincolante.** Primario superato e tasso di successo peggiore
  ⇒ esito **negativo**. Un metodo che costa meno e riesce meno non ha vinto

Soglia, invariata: **mediana ≥ 35% di riduzione, su N ≥ 20 task appaiati, a
tasso di successo non inferiore**, con giudizio alla cieca sul «Fatto quando»
scritto prima.

**Cosa manca, ed è giudizio.** Ventuno task da scegliere dal corpus e il loro
criterio di riuscita. Finché la tabella non è piena D1 non è iniziata: scegliere
i task dopo aver visto i primi risultati è ciò che il protocollo vieta.

### D2 — Ablation e potatura

Terza condizione: framework meno una sezione alla volta.

- Aspettarsi di scoprire che metà del metodo è inerte
- **Tagliare quella metà.** È il risultato più prezioso possibile, ed è
  esattamente ciò che oggi non si sa
- Regola permanente: nessuna sezione sopravvive senza un delta misurato

### D3 — Sostituire `CONF` numerico (non bloccata da D1)

In [20-evidence.md](framework/method/20-evidence.md), sostituire la percentuale
con un giudizio categorico più un falsificatore:

```
CONF: ALTA | MEDIA | BASSA
SMENTIRE: <cosa mi farebbe cambiare idea>
```

Il campo `SMENTIRE` è più difendibile della finta precisione di un numero e più
utile al coordinatore.

Il cambio è una riga sola. Il lavoro vero è il vincolo: **aggiungere il test che
oggi manca**, che fallisca se il formato percentuale ricompare nel metodo. Senza,
i due formati coesistono e nessun rilievo lo vede.

### D4 — Ridurre il costo del roster, non il catalogo

Correzione della direttiva precedente, che misurava la cosa sbagliata. **19 è la
dimensione del catalogo, e il catalogo non si paga**: un agente non installato
resta nel master. Ciò che si paga è il roster installato — già a 11 (software,
library), 13 (web, research), 14 (data) — più le `description` di
`.claude/agents/`, ~70 parole per sessione.

Il taglio a costo zero, che non richiede i dati di D2:

- **Togliere `compliance-reviewer` e `perf-analyst` dagli `on_demand` di tutti e
  cinque i profili.** Sono −2 agenti su ogni progetto, e sono esattamente i due
  che il framework stesso marca «solo su richiesta». Il master resta: chi li
  vuole li prende con `--activate`, già aggiornati
- **Fondere `deploy` e `infra`**: mandato disgiunto è la regola d'ingresso, e qui
  non lo è. `EXCLUSIVE` sparisce insieme alla causa

Regola d'ingresso permanente: un agente entra in un profilo solo se ha mandato
disgiunto **e** un trigger automatico. Un agente a sola invocazione esplicita sta
nel catalogo, non nei profili.

I tagli oltre questi vanno decisi con i dati di D2.

### D5 — Il doctor come punta di lancia

Il prodotto è il doctor, non il metodo. Il metodo diventa contenuto di
riferimento gratuito che porta al tool.

**Prova sul campo, non più solo argomento.** Il confronto con `claude-os`
([Riferimenti esterni](#riferimenti-esterni)) ha prodotto l'esempio che mancava:
un progetto molto più grande, con 638 test e un packaging curato, **spedisce un
agente il cui nome non corrisponde a quello con cui viene delegato** (prova E1).
I loro test non lo vedono, perché testano l'applicazione. Il doctor lo stampa
come `ROSTER_MISSING` in millisecondi. È il mercato, mostrato invece che
descritto — e va usato così quando il tool si presenta.

- Nuovo check `TOKEN_BUDGET`: dimensione della CLAUDE.md **installata** in token.
  È la misura che manca: il test a 1600 parole vincola il *sorgente*, ma la parte
  che l'utente può gonfiare sono le sezioni di progetto. Riferimento reale
  dall'installazione di prova: 1265 parole di kernel + 326 di progetto = **1591
  parole ≈ 2,1k token**, pagate a ogni spawn
- Output con un numero in euro: «la tua CLAUDE.md pesa 4.000 token e viene pagata
  200 volte al giorno da 12 sviluppatori». Una frase che un responsabile capisce
  e che ha una voce di bilancio
- Formato JSON per l'uso in CI (l'exit code non-zero c'è già: `--strict`)

### D6 — `--up` a livello di organizzazione

Tenere allineato il metodo su 40 repo e 15 persone è un problema da azienda, non
da singolo. Serve un rapporto di divergenza aggregato: `fwbuild sync --report`.

### D7 — Inglese

Solo dopo D2. Tradurre prima significa tradurre anche la prosa inerte.

### D8 — Difesa continua dall'erosione di piattaforma

A ogni release di Claude Code: mappare cosa la piattaforma fa ora nativamente ed
eliminare dal framework ciò che la duplica. Check ricorrente, non una tantum.

### D9 — Propagazione dell'errore nel lavoro multi-step

**Da discutere.** Tocca il metodo, non il tooling: si paga in parole nei file che
ogni agente carica a ogni spawn.

**Cosa c'è oggi.** Il ciclo
([10-cycle.md:3](framework/coordinator/10-cycle.md#L3)) è lineare e verifica **in
fondo**: revisore di superficie critica e `final-reviewer` stanno ai punti 5-6.
L'unico presidio intermedio è «`implementer`, un task alla volta: completa,
verifica, passa al successivo»
([10-cycle.md:10-11](framework/coordinator/10-cycle.md#L10-L11)) — che dice di
verificare, non cosa fare **se la verifica smentisce uno step precedente**.

**Il difetto è strutturale, non una svista.** La regola 3
([00-delegation.md:39-43](framework/coordinator/00-delegation.md#L39-L43)) fa
esplorare a `explorer` — `effort: low`
([explorer.md:9](framework/agents/explorer.md#L9)) — per consegnare estratti
pre-digeriti agli agenti cari, che per la regola 4 «non allargano la lettura». È
la regola che fa risparmiare di più, ed è **la stessa** che dà all'errore
dell'agente più economico l'amplificazione più costosa: un `file:riga` sbagliato
a monte diventa un'implementazione sbagliata, una review che valida la cosa
sbagliata, un rifacimento a valle. L'inversione fra costo dell'errore e costo di
chi lo commette non è un caso limite: è il disegno.

**Il segnale esiste già e non ha un consumatore.** Il report standard porta
`ASSUMED` e `UNVERIFIED`
([20-evidence.md:36-38](framework/method/20-evidence.md#L36-L38)): è esattamente
il punto in cui un agente dichiara di passare avanti qualcosa di non verificato.
Nessuna riga dice al coordinatore cosa farne. Un campo scritto e mai letto è
costo puro — lo stesso rilievo che il framework muove agli altri.

E la regola 8 ([00-delegation.md:52-55](framework/coordinator/00-delegation.md#L52-L55)),
«continuare, non ri-spawnare», è economia di token e insieme il canale per cui una
premessa sbagliata sopravvive: continuare un agente ne conserva il contesto,
**errore incluso**.

Da discutere:

- **Dove va il presidio, e quanto costa.** Verificare fra uno step e l'altro si
  paga a ogni step; oggi si paga una volta sola, in fondo. Quale conviene dipende
  dal tasso d'errore reale, che nessuno ha misurato: passa da D0/D1, non da
  un'opinione.
- **Qual è l'unità di ritorno.** Oggi non c'è: nessuno stato di partenza
  registrato prima di uno step, e il commit è solo su richiesta
  ([10-cycle.md:19](framework/coordinator/10-cycle.md#L19)). Senza un punto a cui
  tornare, «non propagare» si riduce a «rifare».
- **Dare un consumatore ad `ASSUMED`.** È la forma più economica: una riga in
  `coordinator/`, zero parole in `CLAUDE.md`, e usa un campo che si scrive già.
- **Nessun agente di checkpoint.** Sarebbe un ruolo in più prima di D1 — vietato
  da *Cosa non fare* — e farebbe pagare la sorveglianza anche dove non serve.

Candidato naturale per D2: non «aggiungere un presidio», ma **spostare** dove sta
la verifica e misurare la differenza.

### D10 — Overthinking: divagazione dal problema centrale

**Da discutere** — con D9, e più a fondo di così.

**Non è la quantità di ragionamento.** Capacità ed `effort` restano dove sono: la
questione è **su cosa** il modello ragiona. Dare peso a problemi secondari,
cercare una soluzione difficile a un problema semplice, allontanarsi dal centro
della richiesta. Il costo non è il token speso a pensare — è il lavoro giusto
fatto sul problema sbagliato.

La distinzione va tenuta ferma perché la cura sbagliata è vicina e sembra la
stessa cosa: **abbassare l'effort non è questa direttiva.**

**Dov'è il buco.** Tutti i presidi esistenti guardano l'**artefatto**, non
l'attenzione:

- «Fai solo il task che hai ricevuto»
  ([10-execution.md:10-12](framework/method/10-execution.md#L10-L12)) limita il
  **diff**: ciò che scopri strada facendo va nel report. Non dice nulla su quanto
  peso gli hai dato mentre lavoravi.
- I divieti su preamboli e narrazione del processo
  ([20-evidence.md:64-72](framework/method/20-evidence.md#L64-L72)) limitano il
  **report**, cioè la prosa in uscita.
- «Un criterio di completamento esplicito… lo chiedi invece di indovinarlo»
  ([10-execution.md:21-22](framework/method/10-execution.md#L21-L22)) è l'unica
  regola che dice *chiedi* — e vale fra coordinatore e subagent, sul solo
  criterio.

**Manca il bordo che conta: coordinatore ↔ utente.** È lì che entra
l'interpretazione sbagliata, ed è l'errore di livello zero del meccanismo di D9 —
quello con l'amplificazione più lunga a valle.

**Le tre intuizioni da cui partire** (utente, 2026-09-01):

1. **Chiedere invece di supporre.** Quando l'interpretazione concettuale della
   richiesta non è sicura — soprattutto su questioni di rilevanza tecnica o
   pratica — si chiede. Non si sceglie la lettura più probabile dichiarandola come
   ipotesi: [20-evidence.md:13-14](framework/method/20-evidence.md#L13-L14)
   permette di procedere dichiarando («probabilmente»), e sull'**intento
   dell'utente** quel permesso è la porta della divagazione.
2. **Non filosofeggiare.** Il registro riflessivo su un problema pratico è
   divagazione travestita da profondità.
3. **L'utente non è ground truth al 100% — e nemmeno il contrario.** A volte sa
   con precisione cosa vuole; a volte sbaglia; a volte non ha le idee chiare su
   ciò che sta facendo. Quindi: **verificare** lo stato delle cose senza farsi
   determinare al 100% dalle sue parole *quando si trova un conflitto*,
   **chiedere** quando una questione concettuale non è esposta chiaramente, e
   **dargli ragione quando ha ragione**. Oggi la catena delle fonti
   ([20-evidence.md:3-5](framework/method/20-evidence.md#L3-L5)) è «repo →
   documentazione ufficiale → utente»: l'utente compare come fonte a cui
   **chiedere**, mai come affermazione da **controllare**.

**La cura ha un modo di andare storta, ed è peggio del male.** Un modello che
generalizza «l'utente può sbagliare» in «l'utente ha di solito torto» fa come gli
pare con una giustificazione epistemica addosso. Il disaccordo di facciata è
divagazione identica a quella che si voleva togliere, e in più costa la fiducia.
Qualunque regola si scriva deve essere scritta **contro entrambi** gli errori.

**Chi arbitra, per tipo di questione.** È qui che la regola diventa scrivibile
senza dare ragione a nessuno per default:

| in gioco | arbitro | cosa fa il modello |
|---|---|---|
| *com'è* — un fatto sul progetto | il repo | verifica: né la parola dell'utente né la propria memoria fanno fede |
| *cosa vuole* — intento, obiettivi, priorità | l'utente | chiede: non deduce dalla lettura più probabile |
| *come si ragiona sul problema* | nessuno dei due | l'ancora è la richiesta centrale; se il ragionamento non ci si riaggancia, è deriva |

Le prime due righe sono 1 e 3 che smettono di sembrare in contraddizione: si
chiede ciò che solo lui sa, si verifica ciò che dice il repo. Confonderle produce
i due errori speculari — chiedere ciò che si poteva leggere, credere ciò che si
poteva smentire.

**Il precedente esiste già, scritto una volta sola e in piccolo.**
[30-state.md:37](framework/coordinator/30-state.md#L37) dice «⚠️ **In conflitto
vince il repo**», ma solo per la memoria persistente contro il repo. È
esattamente l'arbitrato della prima riga, applicato a una coppia sola.
Generalizzarlo è la mossa più economica sul tavolo: sta in `coordinator/`, non in
`CLAUDE.md`.

**Il caso che rende la questione non accademica: la deriva accoppiata.** Quando il
modello va alla deriva su una cosa concettualmente banale *e* l'utente non ha le
idee chiarissime, l'utente si lascia guidare per non portare fuori strada
entrambi — e in quel momento **nessuno dei due tiene l'ancora**. È il meccanismo
di D9 al bordo umano, con il presidio umano disattivato proprio quando servirebbe.
Ed è il motivo per cui l'ancora non può essere una delle due parti: dev'essere lo
stato verificabile del progetto.

Da discutere:

- **Dove va scritto.** 1 e 2 riguardano chiunque riceva un task, quindi
  costerebbero parole in `CLAUDE.md`: il posto più caro. 3 potrebbe essere una
  riga dentro la catena delle fonti che esiste già — quasi gratis.
- **Qual è l'osservabile.** Da fissare prima della prosa, come in D1.
  `output_tokens` **non** misura questo: misura quanto, non su cosa. Più vicini:
  lavoro poi scartato, file toccati fuori dal bersaglio, giri di chiarimento
  arrivati **dopo** una consegna invece che prima.
- **Il limite di «chiedi sempre».** Portato all'estremo scarica sull'utente ogni
  decisione e costa più della divagazione. Serve la soglia: cosa rende
  un'ambiguità degna di una domanda.
- **Come si riconosce la deriva dall'interno.** È il punto duro: una regola che
  scatta quando si è già fuori strada la applica lo stesso ragionamento che è
  uscito di strada. Proxy da valutare: riformulare la richiesta centrale in una
  frase prima di procedere; accorgersi che la soluzione è diventata più difficile
  del problema.
- **Il subagent non parla con l'utente.** Per lui «chiedere» significa fermarsi e
  riportare al coordinatore. Sono due regole diverse, non una scritta due volte.

*Parcheggiato, questione distinta:* `effort` è fissato nella scheda del ruolo e la
regola 2 ([00-delegation.md:34-38](framework/coordinator/00-delegation.md#L34-L38))
lascia declassare per-spawn il **modello** dicendo che «l'effort della scheda
resta» — cioè *al task, non al ruolo* vale su un asse e non sull'altro. È un
rilievo vero, ma non è D10.

**D9 e D10 si toccano.** La divagazione è l'errore di livello zero di D9: una
richiesta letta male è uno step sbagliato in cima alla catena. E il rimedio più
ovvio a D9 — verificare di più, più spesso — è divagazione istituzionalizzata.
Vanno discusse insieme, non in fila.

---

## Cosa non fare

- Non tradurre in inglese prima di aver misurato e potato
- Non aggiungere agenti, cicli o sezioni di metodo finché D1 non è chiuso
- **`framework+sec` è congelato.**
  [docs/design/2026-08-31-framework-sec.md](docs/design/2026-08-31-framework-sec.md)
  è marcato «approvato, da implementare», ma aggiunge agenti, un ciclo, una guida
  e un check: è precisamente ciò che la riga sopra vieta. C'è anche un vincolo
  meccanico che decide la questione da solo — il profilo `research` è a 1882/2000
  parole, e un ciclo sec fa fallire
  [test_end_to_end.py:69](framework/tools/tests/test_end_to_end.py#L69). O si
  chiude D1, o quel design resta fermo: non è una terza opzione
- **Non prendere da `claude-os` niente oltre R1–R3.** In particolare: lo stack
  RAG (LlamaIndex, sqlite-vec, sentence-transformers, Ollama), l'indicizzazione
  tree-sitter, Redis/RQ, i 30 tool MCP, la UI React. Non per qualità — sono
  fatti bene — ma perché sono un **secondo prodotto con un secondo ciclo di
  manutenzione**, e 24.600 righe non misurate sono peggio di 1265 parole non
  misurate. Vale anche il vincolo pratico: quel progetto è macOS/Linux,
  «Windows support coming soon»
- Non spingere il metodo come prodotto: è prosa, e la prosa buona viene copiata
  in una settimana. Nessun fossato, nessun effetto rete, nessun vantaggio di dati
- Non contare i 103 test come evidenza sul metodo: verificano l'assemblatore

---

## Nota di chiusura

Il pezzo forte non è il metodo. È il fatto che esista qualcosa che si accorge
quando il metodo si rompe. Quello, un file di prompt non lo fa — ed è lì che
vanno spinti gli investimenti.

---

# Riferimenti esterni

## `claude-os` — confronto sul campo, 2026-09-01

<https://github.com/brobertsaz/claude-os> · MIT · commit
**`ee7b62bc5bf36541018a1c14592bcac2b59022f9`** (`main`, 6 febbraio 2026).

Ogni riferimento qui sotto è **fissato a quel commit**, righe comprese. Per
riaprirlo:

```bash
git clone https://github.com/brobertsaz/claude-os.git
cd claude-os && git checkout ee7b62bc5bf36541018a1c14592bcac2b59022f9
```

**Cos'è.** Un'applicazione, non un framework di metodo: FastAPI + React + server
MCP + Redis/RQ + Ollama, ~24.600 righe di Python su 60 file, 638 test, ~15
dipendenze. Risolve un problema diverso — «Claude dimentica fra sessioni», via
RAG locale — e tocca questo progetto in **un punto solo**: `templates/` (un
CLAUDE.md, 8 agenti, 9 slash command, 3 skill).

### Da cui prendere

| # | dove | cosa | serve a |
|---|---|---|---|
| **R1** | `app/core/session_parser.py` (368 righe) — `SessionData` alle righe 44-57, `SessionParser.parse()` alla 76 | Parsa i `.jsonl` di `~/.claude/projects/` in messaggi, `ToolCall`, `FileChange`, `cwd`, `gitBranch`. **Ignora `usage`, `agentId`, `isSidechain`, `effort`**: cattura la conversazione, non il costo | **D0** |
| **R2** | `templates/commands/claude-os-init.md:18-22` | «Deriva la directory dalla posizione di questo file di comando — è due livelli sopra». Risolve il problema del percorso senza cablarlo | **I1** |
| **R3** | `install.sh`, `uninstall.sh`, `.github/ISSUE_TEMPLATE/`, `.github/workflows/tests.yml` | Scheletro di pacchetto pubblico già fatto: bootstrap una riga, disinstallazione, template di issue, CI | **I5** |

### Prove a sostegno delle direttive già aperte

| # | prova | dove | sostiene |
|---|---|---|---|
| **E1** | Un agente spedito col nome sbagliato: il file dichiara `name: task-list-creator`, ma README, sezione di progetto e documentazione delegano tutti a `tasks-list-creator`. In Claude Code il nome viene dal frontmatter: **quell'agente non esiste con il nome con cui viene chiamato.** 638 test non lo vedono | `templates/agents/tasks-list-creator.md:2` contro `README.md:543`, `templates/project-files/agent-os-section.md:37`, `docs/guides/WHAT_IS_CLAUDE_OS.md:433` | **D5** · `ROSTER_MISSING` |
| **E2** | Nessun versionamento né drift dei prompt installati. Gli unici `sha256` del repo servono a rilevare file cambiati durante l'indicizzazione. Una volta copiati in un progetto, CLAUDE.md e agenti divergono in silenzio, e non esiste una direzione `--up` | `app/core/hooks.py:273` (unica occorrenza non crittografica) | **D5** · `--up` · `KERNEL_DRIFT` |
| **E3** | Il loro `CLAUDE.md` è `COORDINATOR_LEAK` da manuale: 461 parole, in maggioranza catalogo — 10 tool MCP, 7 slash command, 4 knowledge base, le skill. Roba che solo chi orchestra può usare, pagata da ogni subagent a ogni spawn | `templates/project-files/CLAUDE.md.template` | separazione per destinatario |
| **E4** | «Automatic Recall» è **dichiarato, non meccanico**: `SessionStart`, `PreToolUse`, `PostToolUse`, `UserPromptSubmit` non compaiono in nessun file del repo. Non usano gli hook nativi dell'harness; i loro `hooks.json` sono un sistema interno ai demoni. Il richiamo «automatico» è una frase in CLAUDE.md più comandi che l'utente digita | ricerca su tutto il repo, zero occorrenze | `--strict` · dichiarato vs verificato |
| **E5** | Confidenza finta, in peggio: le soglie sono **costanti cablate** — `0.95`, `0.90`, `0.85`, `0.80` — assegnate a pattern regex. Non le stima nemmeno un modello | `app/core/conversation_watcher.py:22-57` | **P2** · **D3** |
| **E6** | L'unico «health» è di servizio, non di configurazione: `check_ollama_health`, `check_sqlite_health`, `wait_for_services`. Verificano che i processi rispondano. **Niente verifica i prompt installati** — ed è il motivo per cui E1 è passata | `app/core/health.py:16,61,87` | **D5** |

### Nota di lettura

E1–E6 non sono critiche a quel progetto: sono la mappa di dove il valore di
questo sta. Il confronto va rifatto a ogni release loro **e a ogni release di
Claude Code** — è la stessa disciplina di D8, applicata a un concorrente invece
che alla piattaforma. Loro sono più esposti a P3 di quanto lo sia questo
progetto: memoria persistente, skill e hook sono già nativi nell'harness.

---

# Installing

**Chiusa.** Cosa era rotto nel guscio, perché la procedura di installazione non
reggeva per un prodotto pubblico, e cosa è stato fatto — **I0–I5 fatte**, il
2026-09-01.

### Stato

| | | |
|---|---|---|
| **I0** | ✅ | `roadmap.md` compilata dalla prova; `doctor --strict` esce 0 |
| **I1** | ✅ | [source.py](framework/tools/fwbuild/source.py) + `python -m fwbuild source` |
| **I2** | ✅ | `trial_install.py` nel pacchetto, con il test che installa davvero |
| **I3** | ✅ | Passo 0 nella skill; `<FW>`/`<PRJ>` al posto dei percorsi relativi; scrive `.claude/framework.json` |
| **I4** | ✅ | `framework-doctor` e `framework-sync` leggono `<FW>` da `framework.json`, con fallback su `./framework/` |
| **I5** | ✅ | [README](framework/README.md): i due modi, bootstrap bash e PowerShell, comandi aggiornati |

Suite da 90 a **103 test**.

**Il costo pagato a ogni spawn è invariato, verificato e non stimato:** nessun
file di `method/`, `coordinator/`, `agents/`, `shared/`, `cycles/`, `templates/`
o `profiles/` è stato toccato. Kernel comune fermo a **1265/1600**, coordinatore
a 1601/1882/1827 su 2000. Il lavoro sta tutto in `tools/`, che nessun agente
carica, e nelle tre skill, che si caricano su invocazione.

**La convenzione `<FW>`/`<PRJ>` ha ridotto le skill invece di gonfiarle.** Ogni
`framework/…` letterale era una presunzione sbagliata *e* cinque caratteri in
più di `<FW>/…`: correggerle è costato meno di lasciarle. Il netto di I3 su
`framework-install` è +23 righe, tutte nel Passo 0 e nella riga di
`framework.json`.

Due correzioni di coerenza obbligate: le skill dichiaravano `doctor` «unico
sottocomando di `fwbuild`», falso dopo I1; il README contava 90 test e non
elencava la prova eseguibile.

`scripts/` è rimasta vuota dopo I2. Cancellarla resta la decisione separata di
*Cosa non si tocca*, ma il prossimo file che ci finirà è `transcript.py` di
**D0** — quindi conviene lasciarla.

### La prova sul campo — 2026-09-02

Il framework è stato installato **sul repository che lo produce**, seguendo
`framework-install` passo per passo: profilo `library`, revisore
`scientific-reviewer`, 12 agenti, 7 guide. Alla fine
`python -m fwbuild doctor --strict ../..` ha stampato `OK — nessun rilievo`,
uscita 0.

Poi l'installazione è stata **rimossa**, per riportare il repo allo stato
precedente: era una prova, e ciò che vale non sono i file generati ma quello che
la prova ha fatto vedere.

**Cosa ha retto.** La procedura è eseguibile come scritta. Il Passo 0 valida il
sorgente, i due documenti si assemblano, i blocchi di progetto si compilano, il
doctor chiude. Nessun passo si è rivelato impossibile o ambiguo.

**Cosa si è rotto, ed è il valore della prova.**

1. **Un difetto vero, ora chiuso**: la dipendenza agente → guida (in *Minori ma
   reali*). Il doctor l'ha visto al primo colpo, con due `SHARED_MISSING` — ma
   *dopo* che l'installazione era già scritta. Invisibile alla prova automatica,
   che usa un profilo dove il buco non si apre.
2. **P4**, sopra: il tetto di parole copre meno di metà del file che si paga a
   ogni spawn. È la scoperta che conta di più, e non si vede senza scrivere le
   sezioni di progetto di un progetto **vero**.
3. Due profili indistinguibili e un `framework.json` non portabile, entrambi in
   *Minori ma reali*.

**La lezione di metodo.** Tre difetti su tre erano invisibili ai 103 test e li ha
trovati un'installazione reale. `trial_install.py` verifica che il meccanismo
giri; installare su un progetto vero verifica che il **risultato** regga. Sono
due cose diverse, e finora c'era solo la prima.

### Premessa — il guscio, corretto

Sette buchi trovati rileggendo il verificatore, tutti riproducibili, tutti chiusi
con un test che fallisce se il buco torna. La suite è oggi a **103 test verdi**:

| # | buco | prima | ora |
|---|---|---|---|
| 1 | `kernel.verify` restituiva `MISSING` e nessuno lo leggeva: togliere i marker silenziava il drift | `OK`, uscita 0 | `KERNEL_MISSING`, ERRORE — [doctor.py:119](framework/tools/fwbuild/doctor.py#L119) |
| 2 | i pointer si verificavano solo in `CLAUDE.md`, dove ne vivono 2 su 14 | `OK`, uscita 0 | verificati in ogni file installato — [doctor.py:130](framework/tools/fwbuild/doctor.py#L130) |
| 3 | `docs/` non veniva mai ispezionato: un template di stato copiato e non compilato passava | `OK`, uscita 0 | `PLACEHOLDER` — [doctor.py:71](framework/tools/fwbuild/doctor.py#L71) |
| 4 | la tabella di routing era documentata in tre posti in disaccordo | 3 versioni | 1, quella del codice: `orchestration.md` |
| 5 | «qualunque rilievo la lascia incompleta» era prosa, la CLI usciva 0 sugli avvisi | dichiarato | `--strict` — [cli.py:32](framework/tools/fwbuild/cli.py#L32) |
| 6 | lo snippet del Passo 5 moriva su progetto vergine, dopo aver scritto `CLAUDE.md` | installazione a metà | `mkdir` — [install/SKILL.md:208](framework/skills/framework-install/SKILL.md#L208) |
| 7 | i titoli sorvegliati da `COORDINATOR_LEAK` erano una stringa duplicata: rinominarli spegneva il check in silenzio | suite verde | un test fallisce — [test_end_to_end.py:59](framework/tools/tests/test_end_to_end.py#L59) |

La variante senza marker resta legittima: il rilievo 1 non scatta se **nessun**
file tracciato ne ha ([doctor.py:102](framework/tools/fwbuild/doctor.py#L102)).
Aggiunto `Roster di questo progetto` ai titoli sorvegliati
([doctor.py:32](framework/tools/fwbuild/doctor.py#L32)): una tabella di routing
incollata in `CLAUDE.md` prima passava indisturbata.

⚠️ **Questo non intacca P1.** Quei test verificano il **verificatore**, non il
metodo. La D1 resta aperta e resta il cancello.

### Perché l'installazione andava rifatta

Tutte chiuse da I0–I5, tranne l'ultima riga: `.gitignore` e fine riga restano da
sistemare prima di pubblicare.

| problema | sintomo |
|---|---|
| Uovo-gallina | La skill che installa non è invocabile finché non la copi a mano in `.claude/skills/`. È il Passo 2 del README: attrito puro, ripetuto a ogni progetto, e il primo punto in cui un utente nuovo si perde |
| Sorgente presunto dentro il progetto | Ogni comando delle skill è `cd framework/tools`. Se il sorgente vive in un posto solo sulla macchina, quei comandi sono tutti rotti |
| Nessuna validazione del sorgente | Un percorso sbagliato non viene riconosciuto: si scrive prima e ci si accorge dopo. Verificato in sessione sul Passo 5 |
| Pacchetto non definito | `docs/`, `sources/`, `scripts/`, `_build/` stanno accanto a `framework/` e nulla dice quali si pubblicano |
| Pacchetto non pulito | Nessun `.gitignore` nel repo: `framework/tools/.pytest_cache/` e due `__pycache__/` sono dentro la cartella che si pubblica. E 19 file di `framework/` hanno fine riga CRLF contro il resto a LF — il tooling normalizza, quindi nessun test se ne accorge |

### Decisioni

| decisione | motivo |
|---|---|
| **Il prodotto è `framework/`, e basta** | `docs/` (piani di costruzione), `sources/`, `scripts/`, `_build/`, `UPDATE.md`, `dictionary.txt` sono materiale di lavoro. Verificato: nessun file dentro `framework/` cita nulla fuori da sé — la cartella è già impacchettabile |
| **Nel repo pubblico `framework/` è la root** | Altrimenti il percorso di installazione diventa `~/.claude/framework/framework/`, e un prodotto non si presenta così |
| **`framework-install` diventa skill personale** | È l'unico modo di togliere l'uovo-gallina: Claude Code non conosce una skill finché non sta in una cartella che legge. Costo residuo: un bootstrap una volta per macchina, non per progetto |
| **Ricerca in ordine, non un percorso fisso** | Un prodotto scaricabile non può cablare il percorso di una macchina. La stessa validazione copre le due forme — sorgente copiato nel progetto e master unico — senza regole in più |
| **Sorgente trovato ma invalido → stop duro** | Un fallback che passa al candidato successivo maschera un percorso sbagliato. Meglio fermarsi prima di aver creato una cartella |
| **Questionario invariato** | È la parte irriducibilmente di giudizio. Il tooling continua a fare solo il meccanico: trovare, validare, creare, copiare, verificare |
| **`trial_install` entra nel pacchetto** | È l'unica cosa che, eseguendola, esercita un'installazione **intera**. Correzione rispetto alla versione precedente di questo documento: **oggi non dimostra che passa il doctor — dimostra il contrario** (vedi I0). Entra nel pacchetto proprio per essere vincolata da un test |

### I0 — Il difetto, chiuso per primo

**✅ Fatto.** L'installazione di prova copiava i tre template di stato e ne
compilava uno: `roadmap.md` restava con `{{titolo}}`, e il Passo 6 usciva 1 con
`ERROR PLACEHOLDER docs/roadmap.md`.

Non era ambiguità sul comportamento atteso — il Passo 5 dice di compilare
**subito** la roadmap, e
[test_end_to_end.py:188](framework/tools/tests/test_end_to_end.py#L188) pretende
che il template contenga un segnaposto riconoscibile: lo script era l'unico
pezzo fuori allineamento. Ora scrive il primo obiettivo col suo «Fatto quando».
`status.md` resta vuoto per costruzione
([test_end_to_end.py:195](framework/tools/tests/test_end_to_end.py#L195)).

Il difetto è stato ritrovato di proposito dopo il fix, per verificare che il
test di I2 sia portante: reintrodotto, la suite diventa rossa su quel solo test,
con quel solo rilievo.

### I1 — Il gate

**✅ Fatto.** [source.py](framework/tools/fwbuild/source.py), 50 righe con i
commenti, test prima del codice.

- `missing(p)` → le voci obbligatorie assenti. Vuoto = è un framework
- `resolve(bases)` → **pura**: prova `<base>` e `<base>/framework` in ordine e
  restituisce la prima root valida, o solleva dicendo cosa manca in ognuna
- `python -m fwbuild source [percorso]` → root e versione, uscita 0; oppure
  cosa manca, uscita 1
- L'ordine di ricerca — progetto → `$CLAUDE_FRAMEWORK` → `~/.claude/framework/`
  — sta in `cli._bases()`, la parte impura, **fuori** dalla funzione pura

**«Percorso indicato ma invalido: errore, nessun fallback» non è un caso
speciale nel codice**: è che `_bases()`, avendo un percorso, restituisce un
candidato solo. La regola cade fuori dalla struttura invece di essere scritta —
un ramo in meno e una cosa in meno che può divergere dalla sua descrizione.

Riferimento **R2**: `claude-os` risolve lo stesso problema derivando la root
dalla posizione del file di comando, invece di cablarla. L'idea è buona e va
tenuta come **primo candidato** in `resolve()` quando la skill è personale. Ma
lì è **prosa dentro un prompt**: se sbaglia, se ne accorge dopo aver scritto. La
differenza che vale è tutta qui — la stessa idea, dietro una funzione pura con
stop duro.

### I2 — La prova eseguibile

**✅ Fatto.** `scripts/trial-install.py` → `framework/tools/trial_install.py`,
`main()` → `install(out)` con la destinazione come argomento; il default
`_build/prova` è calcolato **fuori** dalla root del framework, così `_build/`
non entra nel pacchetto.

Il test nuovo (`TestRealInstall`) installa davvero in una cartella temporanea e
pretende `doctor(root) == []`. È l'unico test che cade se l'installazione,
tutta intera, smette di reggere il Passo 6: il resto della suite verifica i
pezzi, non l'atto di installare.

### I3 — La skill personale

**✅ Fatto.** Passo 0 nuovo: prendi il **primo candidato che esiste** — non il
primo che funziona — fra `./framework/`, `$CLAUDE_FRAMEWORK`,
`~/.claude/framework/`, e validalo con `fwbuild source`. Se esce 1 ci si ferma
**prima di creare qualunque cartella**: trovato ma incompleto è un errore, non
un motivo per provare il successivo.

Da lì in poi la skill usa `<FW>` (root validata) e `<PRJ>` (root del progetto)
al posto di `..`/`../..`, e a fine installazione scrive `.claude/framework.json`
con `source` e `version`. La descrizione del frontmatter non dice più «dopo aver
copiato `framework/`»: non si copia più niente.

### I4 — Le due skill di ciclo di vita

**✅ Fatto.** Entrambe aprono con la stessa riga: `<FW>` è il campo `source` di
`.claude/framework.json`, e se il file manca è `./framework/`. È ciò che fa
convivere davvero il modo «master unico» e il modo «copiato nel progetto».

`trial_install.py` scrive anche lui `framework.json`: era diventato l'unico
pezzo che simulava un'installazione senza produrre il file che le due skill ora
si aspettano.

### I5 — README

**✅ Fatto**, in [framework/README.md](framework/README.md) — nel repo pubblico
`framework/` è la root, quindi quello **è** il README del prodotto.

La procedura a quattro passi è sostituita dai due modi, col bootstrap in bash e
PowerShell. L'uovo-gallina non è nascosto: è dichiarato per quello che è —
**l'unico attrito, pagato una volta per macchina e non a ogni progetto.**

Riferimento **R3**: lo scheletro di pacchetto pubblico da guardare quando si
arriva qui — bootstrap in una riga, `uninstall.sh` (che qui non esiste affatto),
template di issue, workflow di CI. Da usare come lista di controllo di ciò che
un progetto scaricabile ha e questo non ha ancora, non come codice da copiare.

### Verifica di chiusura

Il conteggio dei test **non è un criterio**: la suite era già a 90 con I0–I5 non
iniziate. Si chiude su fatti, non su un numero:

1. ✅ `python -m fwbuild source [percorso]` risolve e valida nell'ordine previsto
2. ✅ Le quattro rotture del gate provate a mano: cartella qualsiasi, sorgente
   monco, **percorso indicato invalido che non ricade sui successivi**,
   sorgente trovato come `<base>/framework` invece che come `<base>`
3. ✅ Il test di I2 verde — e provato portante: reintrodotto il difetto di I0,
   diventa rosso su quel solo test
4. ✅ `python -m fwbuild doctor --strict` a 0 sull'installazione di prova, da
   riga di comando
5. ◐ Il modo «master unico» provato su root vere in cartella temporanea: master
   trovato via `$CLAUDE_FRAMEWORK` da un progetto vergine, sorgente copiato nel
   progetto che ha la precedenza sul master, percorso indicato invalido che non
   ricade sul master. **Il meccanismo regge.** Resta da fare una volta sola, a
   mano: invocare davvero `/framework-install` da skill personale su un progetto
   vergine. È giudizio più tooling, e il tooling è quello provato qui

### Cosa non si tocca

I due kernel — 1265 parole in `CLAUDE.md`, costo pagato a ogni spawn, verificato
invariato — il questionario e la compilazione dei blocchi, la lingua, e il layout
di questo repo: cancellare `docs/`, `sources/`, `scripts/`, `_build/` è una
decisione separata, non una conseguenza.

### Costo

Speso, misurato: **+28 righe** in `trial_install.py` (I0 e `framework.json`),
**50** in `source.py` nuovo più **+30** in `cli.py` (I1), lo spostamento di
`trial_install.py` (I2), **+23** nella skill di installazione (I3), poche righe
in doctor e sync (I4), la sezione di installazione del README riscritta (I5), e
**13 test** nuovi (90 → 103).

**Zero nel costo pagato a ogni spawn**, verificato e non stimato: nessun file
sotto `method/`, `coordinator/`, `agents/`, `shared/`, `cycles/`, `templates/`,
`profiles/` è stato toccato. Le tre skill pesano 1659, 1264 e 754 parole e si
caricano su invocazione: non le paga un `explorer` che non installa niente.
