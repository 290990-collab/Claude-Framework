# Dataset — RPLAN

Unico dataset in uso in Fase 1. Planimetrie residenziali (stile cinese),
top-down, con codifica semantica a colori per tipo di stanza.

**Localizzazione:** `/work/cvcs2026/ai_interior_design/datasets/RPLAN/`

```
RPLAN/
├── Interface/
│   ├── retrieval/tf_train.npy            # ~286 MB, feature precomputate (non usate)
│   └── static/Data/
│       ├── data_train_converted.pkl      # ~127 MB
│       ├── data_test_converted.pkl       # ~53 MB
│       ├── data_train_eNum.pkl           # conteggio adiacenze
│       ├── rNum_train.npy                # conteggio stanze
│       ├── Img/                          # 2.880 PNG 256×256 RGB
│       └── snapshot_train/               # 67.453 PNG 1167×875 RGB  ← LA GALLERY
└── Network/
    ├── data.mat                          # ~25 MB, archivio aggregato
    └── data/
        ├── data_train.mat                # 56.511 piante
        ├── data_valid.mat                # 12.108 piante
        └── data_test.mat                 # 12.110 piante   (union 80.729)
```

## I `.mat` — la sorgente di verità strutturale

Tre file **aggregati** (non uno per pianta), letti solo da
`src/data/rplan_metadata.py`. Campi usati:

| Campo | Contenuto |
|---|---|
| `name` | ID pianta = **stem del PNG** → è il join fra i due rami |
| `rType` | tipo di ogni stanza (intero, 13 classi) |
| `rEdge` | `E×3`: `[nodo_i, nodo_j, tipo_relazione]` — adiacenze **tipizzate** (0..9) |
| `gtBoxNew` | bounding box per stanza, `[x0,y0,x1,y1]` |
| `gtBox` | footprint, ⚠️ **assi scambiati** `[y0,x0,y1,x1]` |
| `rBoundary` | poligoni per stanza |
| `boundary` | contorno esterno (da cui l'ingresso) |

Servono a **entrambi i rami**: sono la sorgente del grafo per il ramo graph
(il grafo si costruisce da qui, **non** segmentando il raster) e la sorgente
delle **label di rilevanza** per la valutazione di entrambi.

⚠️ **Trappola assi.** La geometria dei nodi usa **solo `gtBoxNew`**; di `gtBox`
si usano solo area e aspect, invarianti allo scambio → il baco non può
materializzarsi. Non introdurre usi nuovi di `footprint` per le posizioni.
`rNum` non esiste come campo: il numero di stanze si deriva da `len(rType)`.

## Split ufficiali — e la trappola del nome

I `.mat` forniscono la suddivisione ufficiale **disgiunta** 56.511 / 12.108 /
12.110 (union 80.729).

⚠️ **`snapshot_train/` NON è il solo split di training**, nonostante il nome: i
67.453 PNG **mescolano i tre split** (47.126 train + 10.152 valid + 10.127 test
+ 48 senza record `.mat`).

Conseguenze operative, valide per entrambi i rami:

- La **gallery resta l'intero `snapshot_train/`** — non si splitta il corpus di
  ricerca.
- Lo split serve a scegliere le **query** (`eval.split: valid|test`, lookup via
  `get_split`); `null` = intera gallery come pool.
- Il pool di **training** è lo split `train`, disgiunto da valid e test.

## Il join PNG ↔ `.mat`

Verificato: **67.405 / 67.453 (99,9%)** dei PNG hanno una struct `.mat`
corrispondente. `snapshot_train/` è quindi quasi esattamente un **sottoinsieme**
dell'unione dei `.mat`; i ~13k record in più sono piante senza snapshot
renderizzato. ⚠️ Da qui la differenza di conteggio fra i rami: **graph 67.405 vs
vision 67.453** → la late fusion richiede un **inner join sui nomi**.

## Grafi costruiti dai `.mat` (ramo graph)

I grafi si costruiscono **dai PNG della gallery**, non da tutti gli 80.729
record: così il corpus dei due rami coincide e sono confrontabili.

| Split | Grafi |
|---|---:|
| train | 47.126 |
| valid | 10.152 |
| test | 10.127 |
| **Totale** | **67.405** |

Sono **molti ma piccoli**: 4-8 nodi (media ≈ 6,8) e ~14-28 archi non orientati
per grafo → l'intero dataset sta comodamente in RAM. È questa scala che motiva
`num_layers=2` (diametro 2-3: più hop = over-smoothing).

**Schema delle feature:**

- **Nodi** `x` `[N, 19]` = one-hot `rType` (13) + 6 feature geometriche da
  `gtBoxNew` normalizzate su griglia 256: `cx, cy, w, h, area, aspect`.
- **Archi** `edge_index` `[2, 2E]` da `rEdge`, resi non orientati
  (`to_undirected`) per il message passing simmetrico.
- **`edge_attr`** `[2E, 10]` = one-hot del tipo di relazione (0..9). Usato solo
  da GAT (`edge_dim`), ignorato da GCN/SAGE.
- **Attributi graph-level** (fuori dal message passing): `name`, `split`,
  `num_rooms`, `footprint_area`, `footprint_aspect`, `type_histogram` `[1,13]`
  (base della baseline training-free). Il tipo per nodo non serve come `y`: è
  l'argmax dell'one-hot.

I grafi in cache sono **grezzi** (nessuna normalizzazione, topologia intatta):
una sola cache serve tutte le varianti di ablation, le trasformazioni si
applicano al volo. Stessa logica dell'embedding RAW sul ramo vision.

## Immagini

| Cartella | Risoluzione | Quantità | Uso |
|---|---|---:|---|
| `Img/` | 256×256 RGB | 2.880 | input compatto (non usata nella gallery) |
| `snapshot_train/` | 1167×875 RGB | 67.453 | **gallery**, masking, visualizzazioni |

## Trappole note del dataset

- ⚠️ **Duplicati esatti**: il **3% dei PNG ha un gemello pixel-identico** (970
  gruppi / 2.020 file, verificato via md5), più quasi-duplicati. È il motivo per
  cui il self-recovery a masking nullo si ferma a MRR 0.970 **identico per tutti
  gli encoder**: è un limite dei **dati**, non dei modelli.
- ⚠️ 48 PNG senza record `.mat`: vanno **saltati**, non fatti fallire.
- ⚠️ RPLAN **centra** ogni pianta nel canvas (centro footprint 0.500 ± 0.001):
  quindi `cx/cy` misurano davvero la posizione *dentro* l'appartamento e non
  serve ricentrarli. Ma **non** sono invarianti a rotazione/riflessione: quella
  è materia di augmentation, non di preprocessing.
- ⚠️ Le statistiche geometriche **non sono isotrope**: `std(cy)/std(cx) = 1.24`,
  `std(h)/std(w) = 1.26` (le piante non sono simmetriche negli assi) → le
  simmetrie vanno applicate in coordinate **grezze**, non z-scorate.
- `aspect` arriva a **37** su stanze degeneri contro one-hot ≤ 1 → clip al p99
  (= 4.58) prima dello z-score, altrimenti la coda domina media e std.

## Altri dataset

- **ResPlan — escluso** come corpus di training: nessuna label di rilevanza,
  out-of-domain, tassonomia non allineabile senza perdite.
- **Maticad** — rimandato a una fase successiva (indicazione dei prof).
