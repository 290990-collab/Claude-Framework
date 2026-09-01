# CLAUDE.md — CVCS AI-Assisted Interior Design

Claude Code opera qui come un **team di ricerca coordinato**: massima
accuratezza, minime allucinazioni, budget token come vincolo di prima classe.
Il prodotto non è "software che gira", è **evidenza sperimentale riproducibile**
che finisce in un report.

## Il progetto

Retrieval di planimetrie (floor plan) su **RPLAN**, in due rami paralleli che
condividono metriche e ground truth, poi **late fusion**. Fase 2 (generazione
constraint-aware) non iniziata.

| Path | Ruolo |
|---|---|
| `src/data/rplan_metadata.py` | **core condiviso**: lettore `.mat` RPLAN (`RoomMeta`, `load_metadata`, `get_split`) |
| `src/evaluation/{relevance,metrics}.py` | **core condiviso**: `GalleryAxes` (rilevanza per-asse) + nDCG/Recall/mAP |
| `src/vision/` | ramo vision: encoder frozen → (head) → whitening → FAISS |
| `src/graph/` | ramo graph: `.mat` → grafo PyG → GNN allenata (InfoNCE) → FAISS |
| `configs/` | YAML: `vision_retrieval.yaml` + `vision_models/*`, `graph_retrieval.yaml` + `graph_models/*` |
| `scripts/{vision,graph}/` | job sbatch numerati nell'ordine di esecuzione |
| `tests/` | smoke test CPU (⚠️ `tests/test_vision_retrieval.py` è **l'entrypoint di indicizzazione**, non un test) |

**Vincoli DURI** — violarli invalida i risultati, non solo il codice:

1. **Il test set non sceglie nulla**: iperparametri, checkpoint e varianti si
   scelgono sul `valid`; il `test` si tocca solo per il numero finale.
   Statistiche di normalizzazione dal **solo train**.
2. **Gallery = intero `snapshot_train/`, sempre**: non si splitta il corpus di
   ricerca, lo split restringe le **query**. ⚠️ `snapshot_train/` **mescola** i
   tre split ufficiali nonostante il nome.
3. **Confronti appaiati**: stesse query, stessa gallery, stesse esclusioni.
   Verifica pratica: le esclusioni singleton stampate nei log devono coincidere.
4. **Contratti fra i rami**: `embeddings.npy` + `names.json` allineati per riga
   (interfaccia della late fusion, ⚠️ inner join sui nomi: graph 67.405 vs
   vision 67.453); `BaseVisionEncoder`/`BaseGraphEncoder`; forma
   dell'architettura ↔ checkpoint (un flag che cambia `proj` — es. `raw_skip` —
   rende il checkpoint non ricaricabile).
5. **Circolarità dichiarata**: le label di composizione/topologia derivano da
   `rType`/`rEdge`, che sono **l'input** del ramo graph → su quegli assi il
   graph è un upper bound; l'unico asse alla pari è la **geometria**. Questione
   aperta: `.claude/shared/architecture.md`.

## Comandi

```bash
source ~/floorplan-env/bin/activate      # ⚠️ $HOME dinamico: 3 utenti sul progetto
python -m src.<modulo>                   # ogni modulo è un entrypoint `python -m`
python -m tests.test_vision_retrieval    # indicizzazione vision (nome storico)
```

- **Verifica leggera (la fa l'agente):** import test, smoke test CPU
  deterministici, `python -m compileall`. Niente GPU, niente dataset interi.
- **Run pesanti (le lancia l'UTENTE):** `sbatch scripts/{vision,graph}/NN_*.sh`.
  Gli agenti **non** lanciano sbatch e non aspettano job: preparano il comando,
  l'utente lo esegue e incolla l'output. Dipendenze in `COMANDI.md`.

## Orchestrazione: il main agent coordina

Il main agent pianifica, delega, verifica e integra. Esegue **direttamente** le
modifiche piccole a basso rischio (≤2-3 file, poche decine di righe, nessun
contratto, nessuna conseguenza sui numeri): lì delegare costa più che fare. Il
resto va ai subagent in `.claude/agents/`:

| Situazione | Subagent | Modello/Effort |
|---|---|---|
| Dove sta / chi usa X, quale config o script fa Y | `explorer` | Haiku low |
| Design multi-file, contratti, **protocollo sperimentale** | `architect` | Opus* xhigh |
| Scrivere codice (moduli, config, script, figure) | `implementer` | Opus high · Sonnet se meccanico |
| Smoke test CPU, invarianti, determinismo | `tester` | Sonnet medium |
| Bug a causa ignota, incluse patologie di training | `debugger` | Opus high |
| Leggere i numeri di una run e dire cosa significano | `results-analyst` | Opus high · Sonnet se solo tabelle |
| Validità scientifica (leakage, circolarità, equità, significatività) | `scientific-reviewer` | Opus high |
| Refactoring a comportamento **e numeri** invariati | `refactorer` | Opus high · Sonnet se meccanico |
| Letteratura, SOTA, `PAPER.md` | `literature` | Sonnet medium |
| Verifica finale del task | `final-reviewer` | Opus high |

\* `architect` è il più costoso: si usa per decisioni di struttura o di
protocollo, mai per un piano che il main agent scrive in tre righe.

**Le cinque regole di delega che contano** (dettaglio, cicli di lavoro e
disambiguazione fra agenti simili: `.claude/shared/orchestration.md`):

1. `architect` **mai** in parallelo né rilanciato sullo stesso task; altri Opus
   in sequenza, max 2 in parallelo solo su task indipendenti; `explorer` libero.
2. Modello **al task**, non al ruolo: lavoro meccanico e senza giudizio →
   declassa lo spawn a Sonnet; ma mai dove servono decisioni non banali.
3. Contesto **pre-digerito**: l'`explorer` consegna estratti con `file:riga`,
   così l'Opus legge poco a prezzo pieno.
4. **Un task per agente**, con criterio di completamento esplicito.
5. **Continuare, non ri-spawnare** (secondo giro = stesso agente); **una sola**
   review finale.

**I due cicli.** Codice: `explorer` → `architect` (se ≥3 file o un contratto) →
`implementer` → `tester` → `final-reviewer` (prima `scientific-reviewer` se
cambia *cosa* o *come* si misura) → integrazione.
Ricerca: **Ipotesi** falsificabile con previsione per-asse → **Protocollo** (una
variabile, baseline, criterio deciso prima) → **Run** (la lancia l'utente) →
**Analisi** appaiata → **Conclusione** confermata *o smentita*, scritta in
`.claude/shared/status.md`.

## Evidence Before Action — anti-allucinazione (per tutti, sempre)

Ogni azione parte dall'evidenza raccolta, non dalla memoria del modello. Se
manca un'informazione, cercarla (repo → doc → utente), non inventarla.

1. **Mai citare un numero non letto in sessione.** Metriche, delta, conteggi,
   job id: si leggono da un file o dall'output incollato dall'utente. Un numero
   ricordato è un numero inventato.
2. Mai citare API/firme/comportamenti non letti in sessione. Vale soprattutto
   per `torch`, `torch_geometric`, `transformers`, `faiss`: le firme si
   verificano nell'uso reale del repo.
3. Mai dichiarare funzionante ciò che non è stato eseguito: il resto va in
   "NON verificato". Nessun agente dichiara "completato": chiude col report e
   lascia il giudizio al coordinatore.
4. Ipotesi dichiarate come tali ("probabilmente"); **fatti verificati** e
   **interpretazioni** restano separati anche tipograficamente.
5. File/simbolo/comando non trovato → dirlo, non inventare path o contenuti.
6. Prima di modificare: leggere i file coinvolti nella versione attuale, gli usi
   e le implementazioni simili nel repo. Sui bug è vietato indovinare: il
   meccanismo individuato deve spiegare **tutti** i sintomi.

## Report standard (obbligatorio per ogni subagent)

Schema fisso e telegrafico, ≤150 parole. Niente prosa di cortesia. Regola
anti-eco: non ripetere il contesto ricevuto in input. Sempre `file:riga`, mai
dump di file.

```
CONF: <0-100%> — <motivo in ≤10 parole>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni o effetti sui numeri, o "nessuna nota">
UNVERIFIED: <cosa non è stato eseguito/controllato o "-">
```

Il main agent tratta ogni report come input da verificare, non come verità.

## Principi di modifica del codice

- **Minimal Safe Change**: la modifica più piccola che risolve il problema; un
  solo problema per task; niente refactoring o rename non richiesti.
- **Numeri invariati salvo mandato**: se una modifica può cambiare una metrica
  già riportata va dichiarato — anche se il codice nuovo è "più giusto".
- **Contract First**: prima di cambiare firma/formato/YAML — qual è il
  contratto? chi lo usa (Grep, inclusi `.sh` e ponti YAML→flag)? rompo la
  ricarica di un checkpoint o un artefatto già su disco?

Pattern esistenti, riproducibilità, config-over-hardcoding, niente refactor
cross-ramo e stile: `.claude/shared/conventions.md`.

## Stato attuale (Current Summary Update)

**Fase 1 — Retrieval.** Entrambi i rami implementati, allenati e valutati sulle
stesse 2000 query del test split, gallery intera. (nDCG@10 =
composizione/topologia/geometria.)

- **Vision** (encoder frozen × pooling × trasformazione; registry a **8**, tutti
  estratti — ma i 6 `.npz` valid di `pespatial` sono **da leggere**, `§19`):
  miglior geometria del progetto **0.948**
  (`ijepa/gem/whiten`); dal 13 ago il migliore sugli altri due assi è
  **`tipsv2/gem448/whiten`** (valid: 0.843/0.690/0.935, +0.030 di topologia sul
  precedente candidato, `status.md §18`); sul **partial self-recovery** la head è un guadagno grande
  e crescente col masking (dinov3 a f=0.75: MRR 0.205 → 0.668). ⚠️ «sul full la
  head non aiuta» **non è difendibile**: quella head è selezionata sulla val-loss
  InfoNCE, il criterio che il ramo graph ha smentito.
- **Graph** (GCN/GAT/SAGE, InfoNCE): migliore **`gcn/tau02` = 0.972/0.826/0.940**
  contro baseline training-free `hist` 1.000\*/0.643/0.894 (\*oracolo per
  costruzione). Ordine stabile **GCN > SAGE > GAT**.
- ⚠️ **Come si leggono questi numeri — floor misurato (31 lug)**: un ranking
  casuale prende già **0.739/0.466/0.869**. Quindi lo spazio utile della
  geometria è **0.131** e il margine 0.002 fra i rami ne è l'**1.5%**; l'nDCG@10
  da solo è la metrica **meno** informativa (Recall/mAP dello stesso null
  partono da 0.085 e 0.035). La **topologia** è l'asse che discrimina: il graph
  ne usa il 67% contro il 33% di `hist`. Dettagli in `retrieval.md`.
- **Tre scoperte che guidano il lavoro**: (a) la **val-loss InfoNCE non predice
  il retrieval** e ne inverte la classifica → il checkpoint si sceglie con la
  `RetrievalProbe` sul valid; (b) **gran parte del punteggio viene
  dall'architettura, non dal training**: il training compra la **topologia**;
  (c) **τ=0.3 e "allenare di più" sono stati smentiti dalla misura**.
- **Stato del metodo**: dei rilievi dell'audit **11 su 13 riconfermati** (A5
  ridimensionato — la GT geometrica è solo in parte ricostruibile dal grafo; B6
  aperto). Strumenti pronti: floor, per-query `perquery/1`, test appaiato,
  sensibilità ai pesi. **Nessun fix ancora applicato**: è la fase B.
- **Prossimi**: run per-query dei due rami → test appaiato; poi late fusion
  (D.0), partial sul graph, decisione sulla circolarità, report per i prof.

Numeri e cronologia: **`.claude/shared/status.md`** (§9 riconferme, §10 floor).
Diagnosi metodologica completa: **`current_state.md`**.

## Stato che si aggiorna da solo

Il progetto lavora ad **anelli lunghi e asincroni** (si lancia un job, l'output
arriva ore o giorni dopo): senza uno stato scritto ogni sessione riparte a
indovinare. Regola d'oro: **si aggiunge o si spunta, non si riscrive**.

| Liv. | File | Contiene | Si aggiorna | Costo |
|---|---|---|---|---|
| 1 | `.claude/TODO.md` | dove siamo **adesso**: in corso, job in attesa, prossimo passo, bloccati | a **ogni** step | 1-3 righe |
| 2 | `.claude/shared/status.md` | risultati misurati, ipotesi confermate o smentite | quando un numero è letto o un'ipotesi si chiude | 1 voce |
| 3 | `CLAUDE.md § Stato attuale` | il quadro: cosa sa il progetto oggi | solo se **cambia il quadro** | ≤25 righe |
| 4 | **memoria persistente** | fatti che valgono **fra** sessioni: chi è l'utente, direttive, decisioni | a ogni cambiamento di codice o scoperta | 1 file |

- **Inizio sessione**: `.claude/TODO.md` per primo. **Fine task**: livello 1
  sempre, 2 se ci sono numeri nuovi, 3 se una conclusione è cambiata.
  **Scrive il main agent**: i subagent riportano e basta.
- **Job asincroni**: appena parte un `sbatch`, la riga va in *In attesa
  dell'utente* con `id · script · variante · data · cosa deve rispondere`.
- **Livello 4 — la memoria va rivisitata, non solo riempita.** A ogni
  cambiamento significativo di codice (path, contratti, moduli spostati) e a ogni
  scoperta logica o scientifica (un'ipotesi confermata o **smentita**, un
  criterio che si rivela sbagliato): chiedersi *«questo supera una memoria?»* e,
  se sì, **annotarla come superata o correggerla subito**. Anche la memoria è
  **compatta, densa e informativa**: un fatto per file, nessun numero duplicato
  dal repo, nessun path che non esiste più. ⚠️ In conflitto **vince il repo**:
  una memoria vecchia non annotata è un bias attivo, fa ripartire la sessione
  successiva con la visione di un mese prima.
- **Tetti**: TODO ~60 righe, *Stato attuale* ~25 → si **comprime prima di
  aggiungere**. Niente duplicazione fra livelli: TODO = stato, `.claude/shared/status.md` =
  risultati, qui = quadro, memoria = ciò che sopravvive alla sessione.

## Regole operative (non negoziabili, per tutti)

- **NON usare git** (nemmeno in lettura): il "diff" da rivedere è la lista di
  file che il coordinatore dichiara modificati.
- **Non operare fuori da `/work/cvcs2026/ai_interior_design/`.**
- **Non lanciare sbatch, GPU o job lunghi**: li lancia l'utente. Un agente che
  "prova a vedere se gira" brucia ore di coda.
- **Mai rilanciare un esperimento** per riavere un numero già presente in un
  log, in un `training_summary.json` o in `vision_pipline.xlsx`.
- **Mai scansionare `logs/`** (solo path espliciti dati dall'utente); `results/`
  solo se richiesto; **artefatti pesanti** (`.npy/.npz/.pt/.pth/.mat/.xlsx`) solo
  se indispensabile e **previa conferma**.
- **Letture a range**: se il prompt dà già estratti e `file:riga`, si leggono
  solo quei range (Read offset/limit), mai il file intero. Ciò che non è
  universale sta dietro un pointer in `.claude/shared/`, non pre-caricato.
- **Non toccare gli script HPC** (`scripts/**`) se non esplicitamente richiesto.
- File e cartelle **group-writable** (`umask 002`): cartella condivisa da 3
  utenti.
- Aggiornare `.claude/TODO.md` a ogni step e i `.md` di `.claude/shared/` quando il
  codice cambia in modo sostanziale.

## Guide condivise — si leggono quando servono

Sempre per primo, e non è in `.claude/shared/`: **`.claude/TODO.md`** (stato vivo).
I file della tabella stanno **tutti** in `.claude/shared/` (prefisso obbligatorio
per aprirli: i path si risolvono dalla root del repo, non da `.claude/`).

| File | Quando |
|---|---|
| `orchestration.md` | **main agent**: delega, cicli di lavoro, scelta fra agenti |
| `research-principles.md` | metodo scientifico (architect, reviewer, analyst) |
| `structure.md` | mappa moduli e responsabilità |
| `architecture.md` | flusso, contratti, decisioni vincolanti, circolarità |
| `retrieval.md` | metriche per-asse, rilevanza, partial, benchmark |
| `dataset.md` | RPLAN: path, `.mat`, split, formati, trappole |
| `experiments.md` | protocollo, ablation, ops sbatch, gotcha operativi |
| `status.md` | risultati, decisioni, ipotesi smentite |
| `roadmap.md` | i sei obiettivi in corso, ordinati per dipendenza |
| `conventions.md` | convenzioni di codice e documentazione |
| `testing-guide.md` | cosa è testabile qui (smoke test CPU) |
| `debugging-playbook.md` | mappa sintomo → sospetti |
| `review-checklist.md` | checklist di `final-reviewer` e `scientific-reviewer` |

**Fonte primaria**: la knowledge graph in `graphify-out/` — per domande sul
progetto si interroga per prima (`/graphify query "..."`, fast path); i `.md`
si leggono quando il grafo ci punta o serve il dettaglio esatto. Rigenerata il
30 lug 2026 (indicizza `.claude/shared/`); ⚠️ **non** contiene `current_state.md`.

## Lingua e stile

Italiano con l'utente; codice, identificatori e commenti in inglese.
Spiegazioni **dettagliate ma semplici**, per uno studente universitario alla
prima esperienza di computer vision ma con le basi di ML/CV acquisite: si danno
per noti training/loss/embedding, si spiega sempre il **perché** di una scelta e
si introduce ogni termine nuovo alla prima comparsa. Meglio intuizioni ed esempi
concreti del formalismo pesante.

## File Exclusions

```
claudeMdExcludes:
- ".claude/archive/**"
- "logs/**"
- "notebooks/**"
- "embeddings/**"
- "wandb/**"
- "**/__pycache__/**"
- "**/*.ckpt"
- "**/*.npz"
- "**/*.jpg"
- "**/*.jpeg"
```
