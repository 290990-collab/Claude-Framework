# Datasets Structures for Different Pipelines

Questo documento descrive la struttura, la composizione e il ruolo del dataset RPLAN all'interno del progetto di retrieval di computer vision.
Il progetto sarà composto da due pipeline principali:

1. Pipeline vision-based

   * utilizza immagini rasterizzate delle floorplan;
   * impiega backbone DINOv2 per estrazione di feature visuali;
   * utilizza il dataset RPLAN.

2. Pipeline graph-based

   * rappresenta le floorplan come grafi spaziali, costruiti dai metadati `.mat` di RPLAN;
   * utilizza una GNN (GraphSAGE) per encoding strutturale e topologico;
   * la GNN è addestrata self-supervised con loss contrastive (InfoNCE) sui grafi RPLAN;
   * integra poi gli embedding nella pipeline di retrieval (indice FAISS separato + late fusion col ramo vision).

# 1. Dataset RPLAN

Sorgente principale di floorplan rasterizzate. Si tratta di un dataset su larga scala di planimetrie residenziali, distribuito in due partizioni principali (`Interface/` e `Network/`) che servono rispettivamente la pipeline di retrieval e la pipeline neurale.

## Struttura della directory

Localizzazione: `/work/cvcs2026/ai_interior_design/datasets/RPLAN/`

```
RPLAN/
├── Interface/
│   ├── retrieval/
│   │   └── tf_train.npy              # ~286 MB, feature/tensor precomputati per il retrieval
│   └── static/
│       └── Data/
│           ├── data_train_converted.pkl   # ~127 MB, dati di training serializzati
│           ├── data_test_converted.pkl    # ~53 MB,  dati di test serializzati
│           ├── data_train_eNum.pkl        # ~1.8 MB, conteggio edge/relazioni del train
│           ├── rNum_train.npy             # ~1 MB,   conteggio stanze per ogni layout di train
│           ├── Img/                       # 2.880 PNG a 256x256 RGB (immagini di riferimento)
│           └── snapshot_train/            # 67.453 PNG a 1167x875 RGB (snapshot/rendering di training)
└── Network/
    ├── data.mat                       # ~25 MB,  archivio MATLAB aggregato
    └── data/
        ├── data_train.mat             # ~89 MB,  56.511 piante (split di training)
        ├── data_valid.mat             # ~19 MB,  12.108 piante (split di validazione)
        └── data_test.mat              # ~19 MB,  12.110 piante (split di test)
```

## Scopo delle sottocartelle

* **`Interface/`** — contiene i dati nella forma usata dall'interfaccia di retrieval originale di RPLAN.
  * `retrieval/tf_train.npy` espone feature/tensor precalcolati su cui costruire indici di similarità (es. FAISS) nella pipeline vision-based.
  * `static/Data/*.pkl` racchiudono le strutture serializzate dei layout (geometrie delle stanze, etichette, vincoli) usate sia per la generazione del grafo sia per visualizzazioni.
  * `static/Data/Img/` raccoglie le planimetrie rasterizzate a 256x256 — formato pensato per l'ingresso di backbone visuali (DINOv2).
  * `static/Data/snapshot_train/` raccoglie rendering ad alta risoluzione (1167x875) utili per analisi qualitative e debugging visivo.
  * `rNum_train.npy` e `data_train_eNum.pkl` forniscono metadati strutturali (numero di stanze, numero di adiacenze) utilizzabili come label semantici o come filtri durante il retrieval.

* **`Network/`** — file MATLAB (`.mat`) con i campi **strutturali** di ogni pianta: `boundary` (contorno esterno), `rType` (tipo di ogni stanza, intero), `rEdge` (`E×3`: `[nodo_i, nodo_j, tipo_relazione]`, adiacenze tipizzate), `gtBoxNew` (bounding box per stanza), `rBoundary` (poligoni per stanza), `name` (ID = stem del PNG). Questi `.mat` servono **entrambi i rami**: (i) sono la sorgente del grafo per il ramo graph-based (si costruisce il grafo da qui, non si segmenta il raster); (ii) sono la sorgente delle **label di rilevanza reali per la valutazione vision** — `rType`/`rEdge`/`rBoundary` si agganciano a ogni embedding via `name` e sostituiscono la label placeholder (primi 3 char dell'ID). Forniscono anche la **suddivisione ufficiale train/valid/test** (disgiunta: 56.511 / 12.108 / 12.110, union 80.729). La gallery resta l'**intero** `snapshot_train/` (non si splitta il corpus di ricerca), ma la valutazione **usa lo split per scegliere le query** (`eval.split: valid|test` → `get_split`); `null` = intera gallery come pool. ⚠️ **`snapshot_train/` NON è il solo training** nonostante il nome: i 67.453 PNG **mescolano** i tre split (47.126 train + 10.152 valid + 10.127 test + 48 senza `.mat`). Per il training di Fase 3 (projection-head/LoRA) il pool sarà lo split `train`, disgiunto da valid/test. `splits.py` è rimosso: lato vision non si addestra (Fase 1-2).

## Grafi costruiti dai `.mat` (ramo graph-based)

> **Stato (lug 2026): implementato.** `src/graph/graph_builder.py` (adapter) + `src/graph/graph_dataset.py` (cache PyG) + `src/graph/draw_graph.py` (visualizzazione). Il builder **non riparsa i `.mat`**: chiama `load_metadata` da `src/data/rplan_metadata.py` (core condiviso col ramo vision).

`src/graph/graph_builder.py` costruisce un grafo PyG `Data` per pianta. `src/graph/graph_dataset.py` (`RplanGraphDataset`, `InMemoryDataset`) li costruisce **una volta** e li serializza in `embeddings/graph/rplan/processed/graphs.pt` (117 MB): build 2m47s → reload ~15s. Il costo evitato è la lettura dei tre `.mat` aggregati (~35s per processo), che altrimenti si pagherebbe a ogni epoca.

**I grafi si costruiscono dai PNG della gallery, non da tutti gli 80.729 record `.mat`** — così il corpus del ramo graph coincide con quello del ramo vision (`snapshot_train/`) e i due sono confrontabili. Numeri effettivi:

| Split   | Grafi  |
| ------- | -----: |
| `train` | 47.126 |
| `valid` | 10.152 |
| `test`  | 10.127 |
| **Totale** | **67.405** |

(48 dei 67.453 PNG non hanno record `.mat` e vengono saltati.) Lo split è già dentro ogni grafo (`data.split`), quindi `RplanGraphDataset(split="train")` filtra **in memoria** senza riprocessare la cache.

Sono **molti ma piccoli**: 4–8 nodi (media ≈ 6.8) e ~14–28 archi non orientati per grafo, quindi l'intero dataset sta comodamente in RAM.

I grafi in cache sono **GREZZI**: nessuna normalizzazione delle feature, topologia intatta. Una sola cache serve così tutte le varianti di ablation; le trasformazioni si applicano al volo col `transform` nativo di PyG (stessa logica dell'embedding raw sul ramo vision). La **fase di adjustment** è implementata in `src/graph/transforms.py` (z-score delle 6 colonne continue con statistiche dal solo train + clip di `aspect` al p99; rimozione dei self-loop spurii), componibile via `build_node_transform(...)` secondo i flag di ablation. Dettagli in `.claude/ai/structure.md`.

Schema delle feature del grafo:

* **Nodi** `x` `[N, 19]` = one-hot del tipo stanza (`rType`, classi 0..12 → 13 dim) + 6 feature geometriche da `gtBoxNew` (`[xmin,ymin,xmax,ymax]`) normalizzate su griglia 256: `cx, cy, w, h, area, aspect`.
* **Archi** `edge_index` `[2, 2E]`: da `rEdge` (`[i, j, tipo]`), resi **non orientati** (`to_undirected`) per il message passing simmetrico.
* **edge_attr** `[2E, 10]`: one-hot del tipo di relazione RPLAN (valori 0..9). Usabile da GAT (`edge_dim`), ignorato da GCN/SAGE.
* **Attributi graph-level** (fuori dal message passing): `name` (ID pianta → mappa ogni embedding alla sua floor plan, sopravvive al collate PyG), `split`, `num_rooms`, `footprint_area`, `footprint_aspect`, `type_histogram` `[1,13]` (base della baseline training-free). Il tipo stanza per nodo non serve come `y` separato: è già recuperabile dall'argmax dell'one-hot (`node_room_types`).

⚠️ **Trappola assi.** La geometria dei nodi usa **solo `gtBoxNew`** (`[x0,y0,x1,y1]`); `gtBox`/`footprint` ha gli **assi scambiati** (`[y0,x0,y1,x1]`). Del footprint si usano solo area e aspect, invarianti allo scambio → il baco non può materializzarsi.

> Nota: i `.mat` di `Network/` e gli snapshot del ramo vision **condividono gli ID** (campo `name` = stem del PNG). Verificato: **67.405/67.453 PNG (99,9%)** di `snapshot_train/` hanno una struct `.mat` corrispondente nell'unione dei tre split. `snapshot_train/` è quindi (quasi esattamente) un **sottoinsieme** dell'unione `.mat`; i ~13k campioni in più nei `.mat` sono piante senza snapshot renderizzato. È questo join che abilita le label di rilevanza reali per la valutazione vision.

## Formato delle immagini

Le floorplan vengono salvate come PNG, in due varianti coesistenti nel dataset:

| Cartella                          | Risoluzione | Canali | Quantità  | Uso tipico                                     |
| --------------------------------- | ----------- | ------ | --------- | ---------------------------------------------- |
| `Interface/static/Data/Img/`      | 256x256     | RGB    | 2.880     | Input compatto per encoder visuali (DINOv2)    |
| `Interface/static/Data/snapshot_train/` | 1167x875 | RGB | 67.453   | Rendering ad alta risoluzione, analisi visiva  |

### Caratteristiche tipiche

| Proprietà    | Valore tipico                          |
| ------------ | -------------------------------------- |
| Risoluzione  | 256x256 (input encoder) / 1167x875 (snapshot) |
| Colori       | RGB (codifica semantica per tipo stanza) |
| Dominio      | planimetrie residenziali (stile cinese) |
| Orientamento | top-down                               |
| Split        | train / valid / test (forniti in `Network/data/`) |

