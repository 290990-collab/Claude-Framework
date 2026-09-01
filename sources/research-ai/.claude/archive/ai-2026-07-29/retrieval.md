# Retrieval — Vision Pipeline

Ramo vision (il ramo graph è ripartito a lug 2026, vedi `src/graph/` e [structure.md](structure.md)).

## Pipeline

```
PNG → encoder frozen (DINOv2/DINOv3/SigLIP2/RADIO/I-JEPA) → L2-norm → PCA whitening → FAISS (cosine) → top-K
```

- **Encoder intercambiabili** ([src/vision/models/vision_encoders/](../../src/vision/models/vision_encoders/)): tutti rispettano il contratto `BaseVisionEncoder` (`forward→[B,D] L2-norm`, `build_transform`, `embedding_dim`), tutti **frozen**. Selezione da config via [VisionModelManager](../../src/vision/models/vision_model_manager.py): cambiare encoder = cambiare `model.name` in [configs/vision_retrieval.yaml](../../configs/vision_retrieval.yaml). Backend unico HuggingFace `transformers`. Il **pooling "naturale" è per-modello** (DINOv2/v3 token [CLS]; SigLIP2 attention pooling; RADIO summary token; I-JEPA mean-pool patch), ma è **configurabile** (`pooling: natural|mean|gem`, helper `pool_global`/`gem_pool` in [base.py](../../src/vision/models/vision_encoders/base.py)) → vedi sezione Ablation.
- **Preprocessing per-modello**: ogni encoder porta la propria normalizzazione/risoluzione (`build_transform`), letta dal processor HF. `ResizeWithPad` (no distorsione) resta condiviso. Questo risolve il punto critico SigLIP2 ([0.5]x3) e RADIO (input grezzo [0,1], normalizza internamente) → NON usano le costanti ImageNet.
- **Whitening** ([retrieval_model.py](../../src/vision/models/retrieval_model.py)): DINOv2 su colormap RPLAN collassa gli score in `[0.97, 0.99]`; il whitening li spalma e rende il ranking discriminativo. Applicato anche alle query. Ora **opzionale** (`whitening.enabled`) e con **riduzione PCA** facoltativa (`whitening.dim` = top-D componenti; `null` = tutte).
- **Gallery = query pool**: si indicizza tutto `snapshot_train/` (67.453 PNG); self-match escluso. ⚠️ `snapshot_train/` **mescola** i 3 split ufficiali RPLAN (47k train + 10k valid + 10k test, vedi [dataset.md](dataset.md)): la gallery resta **intera**, ma le query si possono restringere a uno split con `eval.split: valid|test` (lookup via `get_split` in [rplan_metadata.py](../../src/data/rplan_metadata.py)). `null` = intera gallery come pool (default storico).
- **ID join**: nome file PNG = campo `name` nei `.mat` → collega ogni embedding ai metadati strutturali. Verificato: **67.405/67.453 (99,9%)** dei PNG hanno una struct `.mat`. I `.mat` sono 3 file aggregati (`data_{train,valid,test}.mat`, 80.729 piante in totale), non uno per pianta; `rNum` non è un campo → si deriva da `len(rType)`.

## Score vs ranking vs metriche (non confonderli)

| Livello | Stato |
| --- | --- |
| **Score** (cosine tra embedding) | ✅ reale |
| **Ranking** (top-K nearest neighbor) | ✅ reale, non casuale |
| **Metriche** (per-asse, contro l'intera gallery) | ✅ ridisegnate (vedi sotto) |

Il problema delle label toccava **solo la valutazione**, non lo score né il ranking. Le metriche vecchie (score fuso + soglia, valutate solo sui top-k recuperati) erano **sature e insignificanti**: misurato empiricamente, il **96% di coppie casuali** superava la soglia 0.5, quindi Recall@5≈1.0 anche per un retriever casuale. Due bug compounding — **ambito circolare** (nessun insieme di rilevanti definito sulla gallery) e **etichetta troppo permissiva**. Risolti col redesign per-asse qui sotto.

## Rilevanza architettonica vs similarità visiva

**La similarità visiva non coincide automaticamente con la rilevanza architettonica.** Un encoder su raster cattura geometria/forma/colore; la rilevanza per un architetto è soprattutto **funzione e topologia** (quali stanze sono connesse, come si accede, la circolazione). Due piante possono *sembrare* simili ma essere funzionalmente diverse, o *sembrare* diverse (ruotate, riproporzionate) ed essere funzionalmente identiche.

**Evidenza empirica (SSIG, Vidanapathirana et al. 2023):** uno user study mostra che il giudizio umano di similarità tra piante correla con una **Graph Edit Distance (GED)** sul grafo delle stanze (nodo = tipo stanza, arco = accesso/porta vs sola adiacenza/muro), *non* con la pura somiglianza di forma. Quindi la rilevanza ha **due assi separabili**:

| Asse | Cosa misura | Metrica naturale |
| --- | --- | --- |
| **Geometrico** | forma/scala delle stanze | IoU sulle maschere |
| **Topologico** | quali stanze sono connesse | GED sul grafo accesso/adiacenza |

> **GED** (Graph Edit Distance) = numero minimo di modifiche (aggiungi/togli/rietichetta nodi e archi) per trasformare un grafo nell'altro. È l'edit distance applicata ai grafi. Mappa direttamente sui campi RPLAN: nodi = `rType`, archi = `rEdge`.

**Interazione con l'encoder**: DINOv2/DINOv3/I-JEPA (self-supervised) enfatizzano la struttura spaziale fine (asse geometrico), SigLIP2 (vision-language) l'allineamento semantico, RADIO (agglomerativo) fonde i due assi. → Riportare le metriche **scomposte per asse** (geometria vs topologia) è più informativo di un singolo mAP e separa gli encoder in modo interpretabile (cuore del report).

**Riferimenti** (dettaglio in memoria `reference-relevance-literature`): SSIG (arXiv 2309.04357, relevance = IoU + GED, user study); DANIEL/ROBIN (Sharma et al. ICDAR 2017, primo CBIR deep per piante); lato architettura **Space Syntax / Justified Plan Graph** (Hillier & Hanson 1984; Lee, Ostwald & Gu 2018) — misure configurazionali (depth, integration, connectivity) validate sull'uso umano.

## Metriche (redesign per-asse, giugno 2026)

**Principio**: niente più score fuso con pesi né soglia assoluta. La rilevanza è **scomposta nei 3 assi indipendenti**, e ogni metrica è valutata **contro l'intera gallery** (non solo sui top-k recuperati), così può davvero *fallire*. Tutto in [relevance.py](../../src/evaluation/relevance.py) (`GalleryAxes`, unica fonte di verità, vettorializzata) + [metrics.py](../../src/evaluation/metrics.py) + orchestrato da [evaluate.py](../../src/vision/evaluation/evaluate.py).

Le 3 similarità per-asse (ciascuna in [0,1], Weighted Jaccard per le prime due):
- **composizione** (`rType` → istogramma a 13 tipi);
- **topologia** (`rEdge` → adiacenza per *tipo* di stanza, invariante alla permutazione; vettore denso di 91 coppie);
- **geometria** (`gtBoxNew`/`gtBox` → area+aspect del footprint + distribuzione di area per tipo).

Due famiglie di metriche, per ogni asse, a **K ∈ {1,5,10,100}**:
- **nDCG@K = primaria**: usa la similarità graduata come gain, IDCG calcolato sui migliori K dell'**intera gallery**. Niente M, niente soglia → copre tutti e 3 gli assi (geometria compresa, che essendo continua ha *solo* nDCG).
- **Recall@K + mAP@K = secondarie**, solo sugli assi **discreti** (composizione, topologia): l'insieme dei rilevanti è la **classe di equivalenza esatta** (stesso istogramma / stessa adiacenza), quindi M emerge dai dati. Normalizzano per `min(K, |R|)`. Le query con classe singleton (nessun rilevante) sono **escluse e contate** a parte. **MRR rimossa** (saturava sugli assi densi).

Misure empiriche sulle classi di equivalenza (67k): composizione 721 classi, solo 0,4% singleton (sana, de-saturata: un retriever casuale fa ~6% di Recall@10); topologia 15.815 classi ma **15% di piante singleton** (match esatto sparso) → per la topologia ci si appoggia soprattutto a nDCG; il rilassamento delle classi (Jaccard alto / GED≤1) è un'opzione futura se serve più copertura su Recall/mAP.

I metadati strutturali sono estratti in [rplan_metadata.py](../../src/data/rplan_metadata.py) (`RoomMeta` con `room_types`, `edges` tipizzati, `boxes`, `footprint`, `entrance` + proprietà derivate).

**Da fare** (raffinamenti): **GED** (stile SSIG) sul grafo accesso/adiacenza come alternativa/affianco al Jaccard topologico; **sensitivity analysis** su K (e su eventuale rilassamento topologico) per mostrare robustezza del ranking degli encoder; semantiche diagnostiche sui top-K (room-count MAE, adjacency preservation) per spiegare *perché* un encoder vince.

## Partial retrieval (implementato — vision)

Query = pianta **degradata** (stanze rimosse), cercata contro la gallery completa invariata. Riusa tutta la pipeline: cambia solo *cosa* si passa a `pipeline.query()`. Codice in [vision_partial_query.py](../../src/vision/data/vision_partial_query.py); modalità guidata dal blocco `partial` di [vision_retrieval.yaml](../../configs/vision_retrieval.yaml) (`partial.enabled: true` → `evaluate.py`/`retrieval_visualization.py` eseguono il partial al posto del full). Due livelli di interruttori: **master** `partial.enabled` (full↔partial; override da CLI con `--partial`) e **per-strategia** `strategies.<random|semantic|topology>.enabled` (quali strategie girano *dentro* il partial). In full il blocco `strategies` non viene letto.

- **Costruzione query**: mascheramento sullo **snapshot** (stesso dominio della gallery). Affine per-immagine griglia-256→px (unione bbox `gtBoxNew` ↔ bbox non-bianco), poi flood-fill della regione-stanza a bianco. ⚠️ `gtBoxNew` è `[x0,y0,x1,y1]`, mentre `gtBox`/`footprint` è ad **assi scambiati** `[y0,x0,y1,x1]` (area/aspect restano corretti perché simmetrici).
- **Bordo aperto** (`open_boundary: true`): oltre a sbiancare l'interno, si **cancellano i muri** che bordavano la stanza rimossa (esterni e condivisi), così l'incompletezza è **visibile** e non si crea un appartamento completo più piccolo (mai muri nuovi).
- **3 strategie configurabili separatamente**: `random` (frazione di stanze, sweep `fractions` → curva masking-level), `semantic` (tieni `keep_types`, es. Living/Kitchen/Bathroom), `topology` (togli stanze foglia, `max_degree`).
- **Ground truth doppia**: (1) **self-recovery** = rank/Recall@K + MRR della pianta sorgente originale; (2) **per-asse** (composizione/topologia/geometria) calcolata rispetto alla pianta **completa** (riga `qi`). In partial il self **non** è escluso (la query degradata ≠ immagine originale → ritrovarla è un successo legittimo).
- **Visualizzazione** ([retrieval_visualization.py](../../src/vision/utils/retrieval_visualization.py)): stesso blocco `partial` del config → modalità partial che mostra la query **mascherata** e marca la pianta originale ritrovata (`[orig]`, bordo arancio = self-recovery); output in `results/visualizations/partial/<run>/`.

## Benchmark multi-encoder (piano del team, confermato dai prof)

Set **proposto dal team e confermato dai prof** (mid-paper): **5 encoder che coprono assi di rappresentazione diversi**, non una lista casuale di SOTA.

| Encoder | Famiglia | Ruolo nel benchmark | Pooling | Default checkpoint |
| --- | --- | --- | --- | --- |
| **DINOv2** | self-supervised | baseline self-sup standard | token [CLS] | `facebook/dinov2-base` |
| **DINOv3** | self-supervised | secondo self-sup, generazione successiva (delta su stessa famiglia) | token [CLS] | `facebook/dinov3-vitb16-pretrain-lvd1689m` (gated) |
| **SigLIP2** | vision-language | rappresentazione guidata dal linguaggio (semantica) | attention pooling | `google/siglip2-base-patch16-224` |
| **RADIO** | agglomerativo/"misto" | distilla DINOv2+CLIP+SAM → ipotesi più robusto (fonde gli assi) | summary token | `nvidia/C-RADIOv2-B` |
| **I-JEPA** | self-sup *predittivo* | predice regioni mascherate nel latente → concettualmente vicino al partial retrieval | mean-pool patch | `facebook/ijepa_vith14_1k` |

- **Infrastruttura pronta**: encoder intercambiabili dietro `BaseVisionEncoder` + `VisionModelManager` config-driven; ogni encoder ha il proprio `build_transform` (pooling/preprocessing per-modello). Risolto il problema del preprocessing SigLIP2/RADIO (≠ ImageNet).
- `save_dir` namespaced per encoder **e variante** (`embeddings/vision/${model.name}/${model.variant}`) → indici separati per ogni punto dello sweep, nessun clobber. Stesso namespacing nelle visualizzazioni (`<name>_<variant>_<full|partial>`).
- Whitening da rifare per ogni encoder (già: `fit_whitening` gira su qualunque embedding). Stessa suite di metriche → tabella comparativa = cuore del report.
- **Equità — capacità fissa a ViT-B**: per non confondere "famiglia/obiettivo" con "numero di parametri", si tiene **ViT-Base per tutti**. I-JEPA è l'**eccezione obbligata** (nessun checkpoint ViT-B ufficiale → si usa il più piccolo, `ijepa_vith14_1k` ViT-H): divario di capacità da **dichiarare nel report**. Le varianti di taglia (small/large/ViT-L/H) **non** si confrontano (sporcherebbero gli assi veri). RADIO `trust_remote_code=True`.
- ~~Smoke test/forward reale per DINOv3, SigLIP2, RADIO, I-JEPA~~ **fatto**: tutti e 5 gli encoder sono stati indicizzati e valutati end-to-end via sbatch (full + partial, lug 2026 — vedi sezione Risultati).

## Ablation studies (Fase 1 — frozen, training-free)

Tutti gli assi sono **config-driven** e si lanciano variando **un asse alla volta** rispetto a una baseline per encoder, riportando i risultati **per-asse** (composizione/topologia/geometria) che li rendono interpretabili. Lo sweep si fa con **override CLI dotlist** (no editing dei YAML): `load_vision_config(path, overrides)` li applica dopo l'innesto del preset. `model.variant` è solo un'**etichetta** che namespacia output (non auto-configura nulla; i knob vanno impostati esplicitamente).

| Asse | Knob (config / override) | Note per-modello |
| --- | --- | --- |
| **Pooling** | `model.kwargs.pooling` = natural\|mean\|gem (+`gem_p`) | CLS↔mean↔gem pieno solo su DINOv2/v3; gli altri: naturale vs gem-su-patch |
| **PCA whitening** | `whitening.enabled`, `whitening.dim` | dim = top-D componenti; neutralizza anche la differenza di dim nativa (I-JEPA 1280 vs 768) |
| **Risoluzione** | `model.kwargs.image_size` (multiplo del patch) | **SigLIP2**: risoluzione legata al checkpoint → sweep via `model.kwargs.hf_name` (-224/-256/-384), non `image_size` |
| **Extraction layer** | `model.kwargs.extraction_layer` (-1 ultimo, -2 penultimo…) | wired su **DINOv2/v3/I-JEPA** (via `output_hidden_states`); **non** applicabile a SigLIP2 (testa di pooling solo sull'ultimo layer) né RADIO (API espone solo l'output finale) |

Esempio di un punto di sweep (indicizza + valuta una variante):
```
python -m tests.test_vision_retrieval  model.variant=gem model.kwargs.pooling=gem
python -m src.vision.evaluation.evaluate model.variant=gem eval.split=test partial.enabled=false
```

## Fase 3 — projection head (implementata e valutata)

Head = MLP `Linear→GELU→Linear` + L2-norm ([projection_head.py](../../src/vision/models/projection_head.py)), allenata **sopra l'encoder frozen** con **InfoNCE self-supervised**: positivo = stessa pianta **degradata** (masking via `vision_partial_query`) + augmentation valide (flip/rot90) → nessuna circolarità con le label di valutazione. Pipeline **disaccoppiata** in [retrieval_model.py](../../src/vision/models/retrieval_model.py): su disco si salva l'**embedding RAW**, e `prepare_index(head, whiten, whiten_dim)` applica le trasformazioni **al volo** → una sola estrazione GPU per (encoder, pooling) serve tutte le combinazioni raw/whiten/head/head+whiten. Training su vettori cachati (`pairs.npz` con campo `split`; [train_projection.py](../../src/vision/training/train_projection.py) allena su train, **early stopping sulla val-loss del valid** → il test non sceglie mai iperparametri). Job sbatch numerati in [scripts/vision/](../../scripts/vision/) (`01_extract_raw → 02_build_pairs → 03_train_head → 04/05_eval_*_full → 06/07_eval_*_partial`), comandi in [COMANDI.md](../../COMANDI.md). LoRA esclusa per ora.

## Risultati (luglio 2026 — fonte: `vision_pipline.xlsx`, log vx04–vx07)

Setup: gallery = intero `snapshot_train/` (67.453); query = **2.000 campionate dallo split di test** (10.127 candidate) sia per full che per partial; griglia = 5 encoder × pooling (natural/gem/mean) × trasformazione (raw/whiten/head/head+whiten) = 28 combinazioni per contributo. Tutti i numeri in [vision_pipline.xlsx](../../vision_pipline.xlsx) (fogli Full / Partial self-recovery / Partial per-asse / Sintesi).

- **Full retrieval: la head NON aiuta.** Frozen `whiten` (larghezza nativa) ≥ head/head+whiten (256d) su ogni asse/modello per ~0.01 nDCG — atteso: la head comprime e il suo obiettivo è il masking, non il full.
- **Partial self-recovery: la head è un grande guadagno, crescente col masking** (il suo scopo). Es. dinov3/natural, MRR a f=0.75: 0.205 frozen-whiten → **0.668 head** (~3×). Con raw puro siglip2/radio/ijepa collassano già a f=0.25; il whitening da solo li recupera in gran parte.
- **Head pura vs head+whiten dipende dal modello**: per dinov3/siglip2 la head pura è pari o migliore già a masking medio; per radio/ijepa il whiten-dopo-head aiuta; a f=0.75 la head pura vince quasi ovunque (eccezione ijepa).
- **Ranking partial con head (f=0.5, natural)**: dinov3 > dinov2 > radio > siglip2 > ijepa. La strategia `topology` (togli foglie) è quasi satura per tutti; i casi duri sono `random` pesante e `semantic`.
- **Tetto a f=0.0 = MRR 0.970 identico per tutti gli encoder** → limite dei **dati**, non dei modelli: a f=0.0 la query è il PNG originale intatto (`render_partial_image` ritorna l'immagine se non c'è nulla da rimuovere) e RPLAN contiene **duplicati esatti** (3% dei PNG ha un gemello pixel-identico: 970 gruppi/2.020 file, verificato via md5) + quasi-duplicati che pareggiano il self-match.
- ⚠️ Incidente riproducibilità: i primi rilanci vx07 (job 65653–65657) sono morti su nodo **GPU Blackwell sm_120** non supportata dal PyTorch dell'env (`no kernel image` al forward della head; il frozen passa perché non fa forward torch su GPU). Rilancio riuscito su GPU compatibile (job 67424, 67448, 67451–67453).

Da analizzare ancora: confronto sistematico pooling gem/mean e metriche per-asse-vs-pianta-completa sotto masking.

## Ordine di lavoro

Scope corrente: **solo RPLAN** (validazione su ResPlan/Maticad rimandata a una fase successiva, su indicazione dei prof).

1. ~~Label reali dai `.mat` + mAP/nDCG~~ **fatto** (`relevance.py` + mAP/nDCG in `metrics.py`).
1b. ~~Redesign metriche: ambito sull'intera gallery + scomposizione per asse, niente score fuso/soglia, MRR rimossa~~ **fatto** (`GalleryAxes` + nDCG/Recall/mAP per-asse, K={1,5,10,100}).
2. Metriche semantiche/diagnostiche sui top-K (room-count MAE, adjacency preservation).
3. ~~Masking su immagine + studio sul livello di masking~~ **fatto e lanciato** (curva masking-level in `vision_pipline.xlsx`, vedi sezione Risultati).
4. ~~Astrazione encoder/preprocessing + benchmark multi-modello~~ **fatto** (5 encoder valutati full+partial, frozen e con head).
5. **Report breve per i prof**: metriche usate/introdotte, livello di masking nelle query parziali (con lo studio del punto 3), sintesi delle performance e tabella comparativa multi-encoder. ← **prossimo passo vision**, insieme alle analisi residue (pooling gem/mean, per-asse sotto masking).
