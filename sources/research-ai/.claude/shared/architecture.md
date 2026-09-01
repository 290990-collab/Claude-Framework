# Architettura — flusso, confini, contratti

## Le due fasi

1. **Fase 1 — Retrieval** (in corso): data una pianta (anche **parziale**),
   restituire le top-k più simili da RPLAN. Due pipeline complementari che
   condividono ground truth e metriche, poi **late fusion**.
2. **Fase 2 — Generazione** (non iniziata): generazione di layout
   constraint-aware condizionata su input parziali (numero/tipi di stanze,
   adiacenze) con loop di raffinamento iterativo.

## Flusso dei due rami

```
VISION   PNG → encoder frozen → pooling → [head] → [PCA whitening] → L2 → FAISS(IP) → top-K
GRAPH    .mat → grafo PyG → [transform] → GNN allenata (InfoNCE) → L2 → FAISS(IP) → top-K
FUSIONE  concatenazione pesata [√α·v ; √(1−α)·g] su embedding L2-norm  (da fare)
```

Entrambi i rami producono **embedding L2-normalizzati** indicizzati in
`IndexFlatIP` (coseno = prodotto interno) e le **stesse tabelle per-asse**.

**Perché il whitening.** Un encoder frozen su colormap RPLAN (sintetiche, fuori
distribuzione rispetto alle immagini naturali su cui è pre-allenato) produce
embedding collassati in una piccola regione dell'ipersfera: gli score finiscono
tutti in `[0.97, 0.99]` e il ranking diventa indiscriminato. Il PCA whitening li
spalma e rende il ranking discriminativo. Va applicato **anche alle query**.

**Perché l'embedding RAW su disco.** Whitening e head sono trasformazioni
lineari/leggere applicabili al volo: salvando il RAW, una sola estrazione GPU per
(encoder, pooling) alimenta tutte e quattro le combinazioni a costo ~0.
Simmetricamente, nel ramo graph si cachano i **grafi grezzi** e non gli
embedding — che cambierebbero a ogni epoca, dato che lì la rete si allena.

## Confini e responsabilità

- **`src/data/` + `src/evaluation/` = core condiviso.** Sono l'unico punto in cui
  si legge la ground truth RPLAN e l'unico in cui vivono le funzioni di metrica.
  Entrambi i rami li usano **as-is**. Motivo: se la definizione di rilevanza
  divergesse fra i rami, i loro numeri non sarebbero più confrontabili.
- **`src/vision/` e `src/graph/` sono autonomi.** Nessun refactor cross-ramo: gli
  helper di *accumulo* delle metriche sono duplicati **di proposito**. Si
  condividono le funzioni numeriche, non l'orchestrazione.
- **Config e codice separati**: gli iperparametri vivono nei YAML; il codice non
  contiene default nascosti che li contraddicono.
- **Gli script `.sh` sono parte del sistema**, non un dettaglio operativo: i
  ponti YAML→flag rendono i config vivi, quindi una chiave YAML è a tutti gli
  effetti un'API.

## I contratti (cambiarli è una decisione architetturale)

1. **Artefatti su disco.** `embeddings.npy` (RAW, vision) + `image_paths.json` ·
   `embeddings.npy` + `names.json` allineati per riga (graph, **interfaccia
   della late fusion**) · `graphs.pt` (grafi grezzi) · `pairs.npz` (con campo
   `splits`) · `head.pt` · `encoder.pt` + `geom_stats.npz` +
   `training_summary.json` · render-cache. Cambiare un formato **obbliga a
   rigenerare** e costa ore di GPU: va dichiarato.
2. **Forma dell'architettura ↔ checkpoint.** Ogni flag che cambia la forma di un
   layer (`raw_skip`, `hidden_dim`, `out_dim`, `pooling`, `heads`) dev'essere
   identico fra training ed eval, e quindi presente in **tutti e quattro** i
   livelli: codice, argparse, YAML, ponte YAML→flag. Presente in tre su quattro
   = ignorato in silenzio.
3. **Ordine indice ↔ nome.** `shuffle=False` nei loader di indicizzazione:
   la riga `i` dell'embedding *è* la pianta `i` della lista di nomi. Rompere
   questo invalida silenziosamente ogni metrica.
4. **Namespacing degli output.** `save_dir` è composto da
   `model.name`/`model.variant` (vision) e `encoder`/`variant` (graph): due run
   con lo stesso `variant` **si sovrascrivono**. È il meccanismo di tracciabilità
   degli esperimenti e insieme la trappola più insidiosa nei confronti.
5. **Contratti dei registry**: `BaseVisionEncoder` (`forward → [B,D]` L2-norm,
   `build_transform`, `embedding_dim`) e `BaseGraphEncoder` (`build_conv` è
   l'unico punto di variazione). Un encoder nuovo si aggiunge implementando il
   contratto e registrandolo, senza toccare la pipeline.
6. **`perquery/1` — i valori per-query** (`src/evaluation/perquery.py`, 31 lug
   2026). Un `.npz` per run di valutazione: `names` (stem, **chiave di join fra
   run: mai `qi`**, le due gallery hanno righe diverse), `qi`, `ndcg/recall/map`
   `[assi,K,query]` con **NaN = query saltata** su quell'asse, `num_relevant`
   (0 = skip singleton), `ret_rows` (top-K recuperati) e un `meta` JSON con
   `gallery{n,sha1}`, `split`, `exclude_self`, `query_seed`, `geometry_weights`.
   Opt-in: `eval.perquery_dir` (vision, default `null`), `--perquery-out`
   (graph), `PERQUERY_OUT` per `scripts/graph/04_eval_gnn.sh`. Senza, il
   comportamento è identico a prima.
   **A cosa serve**: `significance.py` rifiuta di appaiare due run se `meta`
   discorda (gallery, split, seed…) — è la guardia che impedisce confronti non
   appaiati; `geometry_variants.py` ricalcola l'asse geometria da `ret_rows`
   **senza rilanciare il retrieval** (i pesi cambiano il gain, non il ranking).
   ⚠️ I `ret_rows` valgono solo per la gallery con quel `sha1`.

## Decisioni vincolanti già prese

- **Gallery = intero `snapshot_train/`**, mai splittata: lo split restringe le
  **query**. Il corpus di ricerca è il mondo, non un fold.
- **Selezione sul valid, test solo per il numero finale.**
- **Il checkpoint del ramo graph si sceglie sulla sonda di retrieval**, non sulla
  val-loss InfoNCE (che ne inverte la classifica — vedi `.claude/shared/status.md`).
- **Capacità fissa ViT-B** per il benchmark vision (I-JEPA è l'eccezione
  obbligata, ViT-H: divario da dichiarare). Le varianti di taglia non si
  confrontano.
- **Encoder vision frozen**; l'unica parte allenabile lì è la projection head.
- **Nessuna dipendenza di rete per il ramo graph**: GNN da zero, dati locali,
  wandb spento di default (e comunque `offline`-capace).
- **Scope Fase 1: solo RPLAN.** ResPlan escluso come corpus di training (nessuna
  label di rilevanza, out-of-domain, tassonomia non allineabile senza perdite);
  Maticad rimandato.

## Valutare una proposta di design

1. Quali contratti tocca? (nessuno = rischio molto più basso)
2. Obbliga a rigenerare artefatti? Quante ore di GPU costa all'utente?
3. Può cambiare numeri già riportati? Se sì, il confronto resta appaiato?
4. Introduce una via per cui il test influenza una scelta? (allora è da rifare)
5. Il guadagno atteso è misurabile e superiore al rumore noto?
6. Qual è l'alternativa più semplice che risolve il 90% del problema? (KISS)

## Questione aperta — circolarità della valutazione

Le label di rilevanza degli assi **composizione** e **topologia** derivano da
`rType`/`rEdge`, che sono **esattamente** l'input del ramo graph (node features
ed `edge_index`). Il grafo riceve in ingresso ciò che la ground truth misura in
uscita → il confronto con il ramo vision (che deve inferire quella struttura dai
pixel) **non è alla pari** su quei due assi. L'unico asse equo è la
**geometria**. Tre uscite possibili:

1. dichiararlo e presentare il ramo graph come **oracle / upper bound**;
2. valutare il ramo graph **solo sulla geometria**;
3. estrarre il grafo **dall'immagine** (stile Graph2Plan) → confronto onesto e
   fusione pienamente sensata, ma fuori scope per la Fase 1.

**Decisione da prendere.** Finché non è presa, ogni tabella che confronta i due
rami su composizione/topologia porta il caveat.
