# PAPER.md — Indice dei contenuti per il paper/report

> **Documento vivo.** Non è il paper: è l'*indice* di tutto ciò che deve finirci,
> con le motivazioni e i numeri da non dimenticare. Va aggiornato a ogni
> cambiamento della pipeline.

## Come usare questo file (convenzione)

- **Mai dare per scontato ciò che è scritto qui.** Ogni affermazione numerica o
  di design va **ri-verificata contro il codice/log finali** prima di entrare
  nel paper. Per questo ogni punto "duro" è taggato con il **file sorgente**.
- Marker di stato:
  - `[DONE]` implementato e verificato sui dati;
  - `[TODO]` da fare;
  - `[VERIFY]` scritto qui ma **da riconfermare contro il codice** prima del paper;
  - `[DECISION]` scelta di design da motivare nel paper.
- Quando la pipeline cambia: aggiorna il punto **e** sposta/aggiorna il marker.
- Scope attuale: **solo RPLAN, Fase 1 (Retrieval)**. Lingua del paper: probabilmente EN.
- Tipo: mid-paper / report per i prof.
- **Fonti vive dei numeri** (questo file NON li duplica): `.claude/shared/status.md`
  (risultati e ipotesi smentite), `vision_pipline.xlsx` (benchmark vision),
  `spiegazione_metriche_e_risultati_grafi.md` (spiegazione discorsiva per il report).

---

## 0. Checklist di verifica pre-paper (da rifare a ridosso della stesura)

Spuntare **eseguendo/leggendo il codice**, non a memoria:

- [ ] Numeri dataset (quante piante, copertura `.mat`) → da `src/data/rplan_metadata.py` + log indicizzazione.
- [ ] Dettagli encoder (dim embedding, pooling, input size) → `src/vision/models/vision_encoders/` + log.
- [ ] Parametri pipeline (whitening, tipo indice FAISS) → `src/vision/models/retrieval_model.py`.
- [ ] Definizione esatta delle 3 similarità d'asse → `src/evaluation/relevance.py` (`GalleryAxes`).
- [ ] Definizione esatta delle metriche + normalizzazioni → `src/evaluation/metrics.py`.
- [ ] Valori di K, num query, seed → `configs/vision_retrieval.yaml` (`eval`).
- [ ] Tabella risultati rigenerata con l'ultimo codice (non copiare vecchi log).
- [ ] Ogni claim "X motiva Y" regge ancora dopo eventuali modifiche.

---

## 1. Abstract & Contributi

Bullet dei **contributi** (da limare):
- Due pipeline di retrieval complementari per piante RPLAN: **vision** (encoder frozen → whitening → FAISS) e **graph** (GNN, Fase successiva).
- **Ground truth di rilevanza architettonica scomposta per asse** (composizione/topologia/geometria) derivata dai metadati `.mat`, come *proxy* trasparente in assenza di label umane.
- **Protocollo di valutazione de-saturato**: diagnosi della saturazione delle metriche ingenue + redesign con ambito sull'intera gallery e metriche per-asse.
- Analisi di *quale* asse ogni encoder cattura (geometria vs topologia) → motiva il ramo graph.
- [TODO] Studio di **partial layout retrieval** al variare del livello di masking.

---

## 2. Introduzione & Motivazione

- Workflow architettonico reale: si parte da layout **parziali/incompleti** → retrieval deve completare semanticamente, non solo somigliare. `[DECISION]`
- **La similarità visiva ≠ rilevanza architettonica.** Un encoder su raster cattura forma/colore; per un architetto contano funzione e **topologia** (connessioni, accessi, circolazione). Due piante possono *sembrare* simili ed essere funzionalmente diverse (e viceversa). → fonte: `.claude/shared/retrieval.md`. `[DECISION]`
- Perché RPLAN per primo: fornisce direttamente raster + metadati strutturali `.mat` (composizione/topologia/geometria) → consente sia il retrieval visivo sia la ground truth strutturale.

---

## 3. Related Work / Background

Da citare (dettaglio bibliografico in memoria `reference-relevance-literature`; **verificare le citazioni esatte**):
- **Rappresentazioni graph-based di piante**: Graph2Plan; HouseGAN++; modelli di layout transformer/diffusion (LayoutDM). `[VERIFY]`
- **Retrieval di piante (CBIR)**: DANIEL/ROBIN (Sharma et al., ICDAR 2017) — primo CBIR deep per piante. `[VERIFY]`
- **Rilevanza/similarità tra piante**: **SSIG** (Vidanapathirana et al., 2023, arXiv 2309.04357) — relevance = **IoU + GED**, validata con user study; il giudizio umano correla con la **Graph Edit Distance** sul grafo delle stanze, *non* con la pura forma. `[VERIFY]`
- **Teoria architettonica**: **Space Syntax / Justified Plan Graph** (Hillier & Hanson 1984; Lee, Ostwald & Gu 2018) — misure configurazionali (depth, integration, connectivity) validate sull'uso umano → fondamento teorico dell'asse topologico. `[VERIFY]`
- **Vision encoders** usati nel benchmark: DINOv2, DINOv3, SigLIP2, RADIO, I-JEPA (vedi §6.3).
- **GED** (Graph Edit Distance): numero minimo di modifiche (nodi/archi) per trasformare un grafo nell'altro; mappa diretta sui campi RPLAN (`rType`=nodi, `rEdge`=archi).

> Tesi di fondo del paper (da rendere esplicita): **la rilevanza ha assi separabili**
> (geometrico vs topologico) e gli encoder li catturano in modo diverso.

---

## 4. Dataset (RPLAN)

`[VERIFY]` tutti i numeri contro `src/data/rplan_metadata.py` + log:
- ~**67.453** PNG in `snapshot_train/` (gallery unica = anche pool di query).
- Metadati `.mat`: **67.405/67.453 (99,9%)** delle piante hanno una struct → join via `name` = stem del PNG. ~0,1% senza metadati (esclusi dalla rilevanza).
- I `.mat` sono **3 file aggregati** (`data_{train,valid,test}.mat` = **56.511 / 12.108 / 12.110**, disgiunti, union 80.729), non uno per pianta.
- **13 tipi di stanza** (`ROOM_TYPES` in `rplan_metadata.py`): LivingRoom, MasterRoom, Kitchen, Bathroom, DiningRoom, ChildRoom, StudyRoom, SecondRoom, GuestRoom, Balcony, Entrance, Storage, Wall-in.
- Campi `.mat` usati: `rType` (tipi), `rEdge` (archi i,j,relazione 0..9), `gtBoxNew` (bbox per stanza), `gtBox` (+footprint globale), `boundary` (contorno + ingresso). Coordinate su griglia 256.
- **`[DECISION]` Split ufficiali (verificato giugno 2026):** ⚠️ `snapshot_train/` **NON è il solo training** nonostante il nome: i 67.453 PNG **mescolano** i 3 split (47.126 train + 10.152 valid + 10.127 test + 48 senza `.mat`). La gallery di retrieval resta l'**intero** snapshot (non si splitta il corpus di ricerca); la valutazione **restringe le query** allo split val/test (`eval.split`, lookup `get_split`/`RoomMeta.split`) per evitare il *fishing* nelle ablation. Per il training di Fase 3 il pool sarà lo split `train` (disgiunto da valid/test). Usare lo split **ufficiale** dà riproducibilità e confrontabilità con la letteratura RPLAN.

---

## 5. Metodo

### 5.1 Pipeline vision retrieval `[DONE]`
Fonte: `src/vision/models/retrieval_model.py`, `src/vision/models/vision_model_manager.py`.
- Encoder **frozen** → embedding (pooling configurabile `natural|mean|gem`) → **PCA whitening** opzionale (centering + decorrelazione + scaling a varianza unitaria + L2, con riduzione facoltativa a `whitening.dim` componenti) → **FAISS `IndexFlatIP`** (inner product = cosine su vettori L2-normalizzati).
- Motivazione whitening: su colormap RPLAN gli score DINOv2 collassano in `[0.97, 0.99]`; il whitening li "spalma" e rende il ranking discriminativo. Le **stesse** trasformazioni si applicano alla query. `[VERIFY]` (numeri std: log mostra 0.0080 → 0.0361).
- `save_dir` namespaced per encoder **e variante** (`embeddings/vision/${model.name}/${model.variant}`) → indici separati per ogni punto di sweep.

### 5.2 Ground truth di rilevanza per-asse `[DONE]` `[DECISION]`
Fonte: `src/evaluation/relevance.py` (`GalleryAxes`), `src/data/rplan_metadata.py`.
- **Perché un proxy**: per RPLAN **non esistono label di rilevanza umane** → qualsiasi definizione è un proxy. La forza sta nell'essere **trasparente e scomponibile**, non in una formula.
- **Tre assi indipendenti** (ognuno in [0,1]):
  - **Composizione**: Weighted Jaccard sull'istogramma dei 13 tipi (`composition_vector`).
  - **Topologia**: Weighted Jaccard sull'adiacenza **per tipo** di stanza, **invariante alla permutazione**; vettore denso di **91 coppie** (`topology_vector`).
  - **Geometria**: media di area-footprint, aspect ratio, distribuzione di area per tipo.
- **`[DECISION]` Niente score fuso / niente pesi / niente soglia assoluta.** Motivazione: i pesi (vecchi 0.5/0.3/0.2) sono arbitrari e indifendibili; la decomposizione per-asse è più onesta e più informativa, ed elimina il problema dei pesi.
- **Classi di equivalenza esatta** (per gli assi discreti): rilevante = *stesso istogramma* (composizione) / *stessa adiacenza* (topologia). La dimensione del set rilevante **emerge dai dati**, nessun M da scegliere. (`composition_relevant`, `topology_relevant`).
- **Da dire nel paper**: perché Weighted Jaccard (∈[0,1], gestisce i conteggi — 2 bagni ≠ 1 bagno — penalizza sia il mancante sia l'eccesso).
- **`[TODO]` rifinitura**: validare il proxy contro un *piccolo* set di giudizi umani (correlazione), **senza allenarci sopra** (allenare i pesi sarebbe circolare; per 3 scalari basterebbe comunque una logistic/learning-to-rank, non una rete).

### 5.3 Metriche `[DONE]` `[DECISION]`
Fonte: `src/evaluation/metrics.py`, orchestrazione `src/evaluation/evaluate.py`.
- **Ambito = intera gallery** (non solo i top-k recuperati). È la correzione chiave: senza un insieme di rilevanti definito sui 67k, la metrica è circolare e non può fallire.
- **nDCG@K = primaria**: rilevanza **graduata** come gain, **IDCG sui migliori K della gallery**. Niente M, niente soglia → copre **tutti e 3** gli assi (geometria continua compresa).
- **Recall@K + mAP@K = secondarie**, solo assi **discreti** (composizione, topologia): rilevanti = classe di equivalenza esatta, normalizzazione **`min(K, |R|)`**; query **singleton escluse e contate** a parte.
- **MRR rimossa** `[DECISION]`: satura sugli assi densi (con classi grandi il primo hit è quasi sempre al rango 1) → niente segnale.
- **K ∈ {1, 5, 10, 100}** (`configs/vision_retrieval.yaml`, `eval.k_values`); num_queries=2000, seed=42. `[VERIFY]`
- **⚠️ Caveat metodologico da scrivere esplicitamente** (vedi §7).

### 5.4 Partial layout retrieval `[TODO]`
- Mascherare l'**immagine** (occludere stanze / patch) e cercare la query parziale contro la gallery completa.
- Ground truth: la pianta originale completa deve riemergere in alto (+ piante con stessa composizione).
- Metriche: rank del source plan + le metriche per-asse al variare del **livello di masking** → **curva di robustezza** (deliverable centrale del mid-paper).

### 5.5 Ramo graph `[DONE]` `[VERIFY]`
- Grafi PyG dai `.mat` → **GCN / GAT / GraphSAGE** addestrate con **InfoNCE contrastive** → FAISS. Implementate, allenate e valutate (memoria `project-graph-pipeline`, `project-gnn-requirement`).
- Requisito prof soddisfatto: l'encoder finale è una **GNN addestrata**; il descrittore training-free (istogramma dei tipi) resta come **baseline** — ⚠️ sulla composizione è un oracolo per costruzione.
- Da riportare nel paper: la selezione del checkpoint usa una **sonda di retrieval sul valid**, non la val-loss InfoNCE (che ne inverte la classifica), e il denominatore onesto è la **GNN a pesi casuali**, non solo la baseline.
- **Fusione**: due indici FAISS + late fusion score-level (`α·ẑV + (1−α)·ẑG`) — `[TODO]`, embedding già salvati e allineati.
- ⚠️ **Circolarità** da dichiarare: su composizione/topologia il grafo riceve in input ciò che la ground truth misura; l'unico asse alla pari è la geometria.
- Numeri: `.claude/shared/status.md`; versione discorsiva: `spiegazione_metriche_e_risultati_grafi.md`.

---

## 6. Esperimenti & Risultati

### 6.1 Setup `[VERIFY]`
- **Tutti e 5 gli encoder verificati end-to-end** su GPU (run 29 giu 2026), input **224px**, frozen → whitening → FAISS. Dim embedding di output: DINOv2/DINOv3/SigLIP2 **768-d**, I-JEPA **1280-d** (ViT-H), RADIO **2304-d** (summary multi-teacher). DINOv3 gated (auth HF, poi in cache).
- **2000 query** campionate dallo split **test** (seed 42); self-match escluso in fase di metrica. VRAM: **16 GB bastano per tutti** (I-JEPA ViT-H incluso, batch 256).

### 6.2 Diagnosi della saturazione (contributo metodologico) `[DONE]`
**Da raccontare come motivazione del redesign** — è un risultato, non solo un bugfix:
- Metriche ingenue (score fuso + soglia 0.5, valutate solo sui top-k): Recall@5 = 1.0, mAP = 0.99, nDCG = 0.97 → **sature**.
- **Prova quantitativa**: su 2000 coppie **casuali** (indipendenti dal retriever) il **96% supera la soglia 0.5** → "rilevante". Quindi anche un retriever casuale avrebbe Recall@5 ≈ 1. (script di misura: scratchpad, **rigenerabile**).
- Cause: (1) **ambito circolare**, (2) **etichetta troppo permissiva** (geometria ~0.85 quasi costante e già vista dall'encoder; composizione ~0.74 perché tutte le piante condividono il set base di stanze; topologia ~0.46 = unico asse discriminante).

### 6.3 Risultati DINOv2 per-asse `[DONE]` — **rigenerare prima del paper**
Run del **29 giu 2026** (DINOv2, split test, **n=2000**). **NON copiare ciecamente: rilanciare e riverificare.**

| K | asse | nDCG | Recall | mAP |
|---|---|---|---|---|
| 1 | composition | 0.862 | 0.458 | 0.458 |
| 1 | topology | 0.724 | 0.374 | 0.374 |
| 1 | geometry | 0.949 | — | — |
| 5 | composition | 0.836 | 0.328 | 0.273 |
| 5 | topology | 0.676 | 0.251 | 0.217 |
| 5 | geometry | 0.939 | — | — |
| 10 | composition | 0.826 | 0.287 | 0.211 |
| 10 | topology | 0.659 | 0.216 | 0.173 |
| 10 | geometry | 0.935 | — | — |
| 100 | composition | 0.800 | 0.201 | 0.095 |
| 100 | topology | 0.623 | 0.173 | 0.106 |
| 100 | geometry | 0.925 | — | — |

- Topologia: **313/2000 query escluse** (classe singleton, ~15,6%).
- **Lettura**: ordinamento nDCG **geometria > composizione > topologia** su tutti i K → DINOv2 cattura forma bene, topologia peggio. **Sanity anti-saturazione**: random composizione ≈ 6%, DINOv2 ≈ 29% @K=10 (~5×).

### 6.4 Benchmark multi-encoder `[DONE]` — **rigenerare prima del paper**
5 encoder **scelti per coprire assi diversi** (proposto dal team, confermato dai prof):

| Encoder | Famiglia | Ruolo | Pooling |
|---|---|---|---|
| DINOv2 | self-supervised | baseline self-sup | [CLS] |
| DINOv3 | self-supervised | generazione successiva | [CLS] |
| SigLIP2 | vision-language | semantica guidata dal linguaggio | attention pooling |
| RADIO | agglomerativo | distilla DINOv2+CLIP+SAM | summary token |
| I-JEPA | self-sup predittivo | vicino al partial retrieval | mean-pool patch |

**Run del 29 giu 2026** (full mode, query = split **test**, **n=2000**, seed 42; eval-only, indici riusati). nDCG@10 per asse (+ Recall@10/mAP@10 per gli assi discreti):

| Encoder | comp nDCG | comp R@10 | comp mAP@10 | topo nDCG | topo R@10 | topo mAP@10 | geo nDCG |
|---|---|---|---|---|---|---|---|
| DINOv2 | 0.826 | 0.287 | 0.211 | 0.659 | 0.216 | 0.173 | 0.935 |
| DINOv3 | 0.824 | 0.285 | 0.207 | **0.662** | 0.218 | 0.174 | 0.934 |
| SigLIP2 | 0.822 | 0.273 | 0.197 | 0.637 | 0.195 | 0.156 | 0.928 |
| RADIO | 0.812 | 0.252 | 0.177 | 0.630 | 0.181 | 0.145 | 0.935 |
| I-JEPA* | 0.826 | 0.290 | 0.209 | 0.654 | 0.199 | 0.158 | **0.943** |

(*I-JEPA = ViT-H, vedi nota capacità.) **Stabilità**: i numeri a n=2000 coincidono con quelli del primo giro a n=200 entro **≤0.008** → stime affidabili, ranking non rumore.

**Letture (tutte stabili a n=200 e n=2000):**
- Pattern per-asse **geometria ≫ composizione > topologia** identico per tutti e 5 → robusto, **motiva il ramo graph** (la topologia è l'asse dove la visione pura è più debole).
- **Terzetto di testa DINOv2 ≈ DINOv3 ≈ I-JEPA**, appaiati su composizione/topologia (entro ~0.003–0.008): su questi assi **non si incorona un vincitore**.
- **I-JEPA nettamente migliore sulla geometria** (0.943 vs ~0.934), distacco identico a n=200 → **reale**, coerente col pretraining predittivo/spaziale (+ ViT-H).
- **SigLIP2** sotto il terzetto (soprattutto topologia); **RADIO** il più debole su comp/topo (pareggia solo la geometria).
- **Conclusioni forti**: (1) **DINOv3 non batte DINOv2** → pretraining più nuovo non si trasferisce al dominio planimetrico; (2) **I-JEPA ViT-H (~7× i parametri di un ViT-B) guadagna solo sulla geometria** → collo di bottiglia = **domain gap**, non la taglia; (3) né il vision-language (SigLIP2) né l'agglomerativo (RADIO) aiutano qui. Encoder di **default pragmatico**: DINOv2 ViT-B.
- **Ipotesi confermata**: la **topologia separa gli encoder più della geometria** (spread nDCG@10 ~0.032 vs ~0.015).

- **`[DECISION]` Equità — due "taglie" da non confondere.**
  1. **Capacità del backbone** (n. parametri / classe ViT): DINOv2, DINOv3, SigLIP2 e **RADIO** (`C-RADIOv2-B`) sono **tutti ViT-Base** → capacità *appaiata*. **I-JEPA è l'unica eccezione** (nessun checkpoint ViT-B ufficiale → `ijepa_vith14_1k` ViT-H): divario di capacità **da dichiarare**.
  2. **Dimensione dell'embedding di output** (larghezza del vettore): cosa **diversa** dalla capacità — i 768-d di DINOv2/v3/SigLIP2 convivono coi **2304-d di RADIO** (la summary multi-teacher è più larga, *non* è più capacità del backbone) e i **1280-d di I-JEPA**. **Non confonde le conclusioni**: RADIO ha l'embedding più largo ma è il **peggiore** su comp/topo → la larghezza non dà vantaggio. Per azzerare anche questo confondente: riduzione PCA `whitening.dim=768` (ablation già pronta, §6.5).
  - Le **varianti di taglia** (small/large/ViT-L/H) **non** si confrontano (sporcherebbero gli assi veri).

### 6.5 Ablation / Sensitivity — frozen `[DONE infra]`, da lanciare
Tutte **config-driven**, **un-asse-alla-volta** rispetto a una baseline per encoder, riportate **per-asse** (C/T/G); sweep via **override CLI** (`model.variant=... model.kwargs.<knob>=...`), output namespaced per `model.variant`. `[DECISION]`
- **Pooling**: `natural | mean | gem` (`pool_global`/`gem_pool`, `gem_p`). CLS↔mean↔gem pieno solo DINOv2/v3; gli altri naturale-vs-gem.
- **PCA whitening**: `whitening.enabled` + `whitening.dim` (top-D componenti; neutralizza anche le differenze di dim nativa di **output** — RADIO 2304, I-JEPA 1280 vs 768 — riducendo tutti a una larghezza comune).
- **Risoluzione**: `model.kwargs.image_size` (SigLIP2: via cambio `hf_name` -224/-256/-384, non `image_size`).
- **Extraction layer**: `extraction_layer` (-1 ultimo, -2 penultimo…) su DINOv2/v3/I-JEPA; non applicabile a SigLIP2/RADIO.
- **Sensitivity su K** (e su eventuale rilassamento topologico) → mostrare che il *ranking degli encoder* è robusto (sostituisce la "scelta del peso giusto").
- [Opz.] **GED topologica** stile SSIG come alternativa/affianco al Jaccard d'adiacenza.
- **`[DONE infra Fase 3]`** **projection-head** allenabile (default per tutti i 5, backbone frozen, embedding cachati). **Nodo coppie positive risolto con A+ self-supervised** (non circolare): positivo = stessa pianta **degradata** (masking) + augmentation valide (flip/rot90); loss **InfoNCE** (τ, V configurabili). Scartate le alternative circolari (positivi dalla rilevanza per-asse = ciò che valutiamo). Pipeline **disaccoppiata**: embedding RAW salvati una volta, whitening/head applicati al volo da `prepare_index` → si valutano `raw/whiten/whiten768/head/head+whiten` riusando lo stesso RAW. Training su **train+valid** (test held-out). Moduli: `projection_head.py`, `projection_pairs.py`, `train_projection.py`; ordine sbatch in `COMANDI.md`. **LoRA** sul solo encoder estremo **ancora rimandata** (decisione dopo i numeri della head). Da lanciare via sbatch.

---

## 7. Discussione & Caveat (da scrivere esplicitamente — onestà metodologica)

- **Storia principale**: geometria (vista) ≫ topologia (struttura) per un encoder visivo → **motiva il ramo graph**.
- **`[DECISION]` Caveat 1 — Recall@K ≈ Precision@K per la composizione.** Con `min(K,|R|)` e classi enormi (|R|≈4000 ≫ K), `Recall@K = hits/K` = precision@K, che **cala** con K (per questo Recall@1 > Recall@100). Non è un bug: per gli assi a classe grande va letto in chiave **precision**. La topologia (classi piccole, |R|<K) resta Recall classica. → Possibile rifinitura: **rinominare** la set-metric della composizione in *Precision@K*.
- **`[DECISION]` Caveat 2 — geometria a basso range dinamico.** La similarità geometrica sta quasi sempre in [0.85, 1.0] → nDCG geometrico alto ma **poco discriminante tra encoder**. Da dichiarare: la geometria è l'asse "facile".
- **Caveat 3 — topologia sparsa.** Match esatto → 15% di piante singleton (gallery-wide); per Recall/mAP si escludono, ma **nDCG copre tutte le query**. Rilassamento (Jaccard alto / GED≤1) come opzione futura.
- **Caveat 4 — il proxy non è ground truth umana.** Dichiarare il limite + (se fatto) la validazione su un piccolo set umano.

---

## 8. Limitazioni
- Solo RPLAN (ResPlan/Maticad fuori scope in questa fase). ResPlan escluso come training corpus (no label, out-of-domain, tassonomia non allineabile).
- Lato vision (Fase 1-2) **nessun training**: encoder **frozen**; le ablation (pooling/whitening-dim/risoluzione/extraction_layer) restano training-free. **Fase 3**: si allena solo una **projection-head** sopra il frozen (backbone mai aggiornato); LoRA ancora fuori.
- Proxy di rilevanza non validato su larga scala con umani.
- Ramo graph non ancora implementato (stub).

---

## 9. Conclusioni & Future Work
- Riassunto: pipeline vision + protocollo di valutazione per-asse de-saturato + analisi per-asse degli encoder.
- Future: partial retrieval con studio del masking; benchmark 5 encoder; ramo graph (GraphSAGE+InfoNCE) + late fusion; validazione umana del proxy.

---

## 10. Struttura, figure e tabelle

### 10.a Struttura di riferimento — da `papers/examples/pippo_paper.pdf` (CVPR 2025)

Struttura estratta dal paper di esempio (26 pagine: **12 di corpo** + 5 di
reference + 6 di appendice; 8 figure e 8 tabelle nel corpo):

| § | Sezione | Pagine |
|---|---|---|
| 1 | Introduction — chiude con «we make the following contributions:» in elenco | 1-3 |
| 2 | Related Work | 3-4 |
| 3 | Method — 3.1 base · 3.2 estensione · 3.3-3.4 le due analisi · **3.5 nuova metrica** | 4-9 |
| 4 | Experiments — 4.1 Data · 4.2 Evaluation Setup and Metrics · 4.3 Results · 4.4 Ablations | 9-12 |
| 5 | Conclusion | 12 |
| — | References · Appendix A, B, … | 16-26 |

**Le quattro lezioni da imitare:**
1. **Figura 1 = teaser del risultato**, in prima pagina, non l'architettura.
   L'architettura è **una sola** figura d'insieme (Fig. 2, «Pipeline overview»).
2. **I numeri stanno nelle tabelle, non nei grafici.** 8 tabelle contro 2 soli
   grafici quantitativi: le figure servono per il qualitativo e per **una**
   analisi concettuale (Fig. 4, entropia vs γ). ⚠️ È il contrario di quello che
   fanno oggi i notebook (~40 grafici a barre).
3. **Le didascalie sono autosufficienti**: un paragrafo che rimanda alla sezione
   («…(Sec. 3.3). We overfit our multi-view model for 10K iterations…») e
   **dichiara la conclusione**, non un'etichetta.
4. Una **nuova metrica** merita una sottosezione del Metodo (§3.5): la rilevanza
   per-asse di questo progetto va lì, non in Experiments.

**Budget nostro:** 10 pagine + 2 di reference → più stretto di Pippo. Realistico:
**5-7 figure + 4-5 tabelle**, appendice per il resto.

### 10.b Figure e tabelle da produrre

⚠️ Nessuna figura si finalizza prima della **fase B** della roadmap: i numeri
attuali sono selezionati sul test e senza intervalli di confidenza.

**Figure (obiettivo: 6)**
- [ ] **F1 · teaser**: una query (completa e mascherata) con i suoi top-5 per
      **ciascun asse**, che mostra che i tre assi restituiscono piante diverse →
      giustifica tutta l'impostazione per-asse. Base:
      `src/vision/utils/retrieval_visualization.py` (già per-asse), da rigenerare.
- [ ] **F2 · pipeline overview**: i due rami + la ground truth condivisa in una
      sola figura (encoder frozen → head → whitening → FAISS; `.mat` → grafo →
      GNN → FAISS; e il blocco della rilevanza per-asse che li valuta entrambi).
- [ ] **F3 · curva di masking**: nDCG/MRR vs livello di masking, una linea per
      encoder. È il **risultato originale più forte** del progetto. Esiste già
      nei notebook (`results_partial_*.ipynb § 2`): serve solo con le bande di
      confidenza e le strategie nuove di O4.
- [ ] **F4 · la loss non predice il retrieval**: scatter loss finale (asse x) vs
      nDCG@10 (asse y), un punto per run, con la correlazione. Trasforma
      un'ipotesi smentita in evidenza. ⚠️ I dati esistono già
      (`notebooks/vision/vision_encoders_results.csv` + xlsx) ma **dinov2 manca
      del tutto** dal csv e `ijepa_mean` non c'è: 11 serie su 15 attese.
- [ ] **F5 · distribuzione delle classi di equivalenza** (composizione vs
      topologia): motiva i caveat sulla saturazione e sullo skip dei singleton.
- [ ] **F6 · robustezza alla scelta dell'ablation**: boxplot + punti di tutte le
      ablation per encoder. Esiste già (`§ 5` dei notebook) ed è **il grafico
      migliore del set**: mostra la distribuzione, quindi mostra da sé che la
      configurazione top-1 non è speciale. Sostituisce le classifiche top-12.

**Tabelle (obiettivo: 4)**
- [ ] **T1 · dataset e setup**: split, gallery, numero di query, esclusioni.
- [ ] **T2 · benchmark encoder × asse** (nDCG/Recall/mAP@10), con **CI** e il
      **floor** del ranking casuale come prima riga. Rigenerata in fase B.
- [ ] **T3 · confronto fra i rami** e fusione: vision · graph · late fusion ·
      oracolo, per asse, con test appaiato.
- [ ] **T4 · ablation**: pooling × trasformazione (vision) e OFAT (graph). La
      griglia a heatmap dei notebook (`§ 3`) è già compatta: va bene come figura
      d'appendice, ma nel corpo la versione tabellare costa meno spazio.

### 10.c Stato dei notebook — sintesi

**Inventario completo, correzioni con priorità e 21 grafici da aggiungere:
`notebooks/CHARTS.md`.** Strategia decisa: **produrne il più possibile**, la
selezione per il report avviene qui in § 10.b. Sotto solo il riassunto.

Struttura attuale: `results.ipynb` (training loss della head) +
`results_full_retrieval` / `results_partial_per_asse` /
`results_partial_self_recovery`, ognuno con le stesse 5 sezioni (top-12 ×4
metriche · andamento ×3 · heatmap ablation · confronto per-asse · boxplot
robustezza). Sorgenti: `vision_pipline.xlsx` (5 fogli) e
`vision_encoders_results.csv`.

**Da correggere prima di portarne uno nel report** (dettaglio del perché:
`current_state.md`):
1. ⚠️ **Barre con base troncata su scala `logit`** (`barh(valore − lo_lim,
   left=lo_lim)` + `set_xscale('logit')`): la lunghezza della barra non ha
   interpretazione, e differenze da 0.002 diventano visivamente enormi — proprio
   quelle che il rilievo A4 dichiara indistinguibili dal rumore. Le barre partono
   da 0; per valori vicini a 1 con differenze minime si usa un **dot plot con
   intervalli di confidenza**.
2. ⚠️ **"Score medio" = media di nDCG + Recall + mAP su tutti gli assi**: mescola
   metriche di significato diverso e media gli assi, contro la regola
   «sempre per-asse» (composizione e topologia si muovono in senso opposto). Ed è
   il criterio di **ordinamento predefinito** di tutte le classifiche.
3. ⚠️ **Le classifiche "top 12" sono leaderboard sul test** → visualizzano il
   winner's curse del rilievo A1. In fase B diventano classifiche sul valid.
4. ⚠️ **Nessuna barra d'errore** da nessuna parte (rilievo A4).
5. ⚠️ `results.ipynb` ordina gli encoder per **train loss finale**, che questo
   progetto ha dimostrato non predittiva del retrieval: come classifica è
   fuorviante, come **F4** è un risultato.
6. **Ridondanza**: 4 grafici quasi identici per sezione × 3 notebook. Nei
   notebook si **tengono** (per strategia); nel report ognuno di quei gruppi
   diventa **una** tabella.
7. ⚠️ **0 `savefig()` in 4 notebook**: 31 grafici esistono solo inline e non
   esiste `figures/`. Bloccante per la strategia "produrne molti e scegliere
   dopo" → `notebooks/CHARTS.md § 1`.

**Da tenere così com'è:** etichette diritte in fondo alle linee invece della
legenda, colore per encoder coerente fra i notebook, spine rimosse, heatmap
5-pannelli. Il gusto grafico è buono: il problema è l'inquadramento statistico.

---

## 11. Riferimenti (da completare con citazioni esatte) `[VERIFY]`
- SSIG — Vidanapathirana et al. 2023 (arXiv 2309.04357).
- DANIEL/ROBIN — Sharma et al., ICDAR 2017.
- Space Syntax — Hillier & Hanson 1984; Lee, Ostwald & Gu 2018.
- Graph2Plan; HouseGAN++; LayoutDM. `[VERIFY]`
- Encoder: DINOv2, DINOv3, SigLIP2, RADIO, I-JEPA (checkpoint esatti in `configs/vision_models/`).

---

### Log di aggiornamento
- 2026-06-27: creazione. Stato pipeline: vision retrieval + valutazione per-asse `[DONE]` (DINOv2 valutato); partial retrieval, multi-encoder, ramo graph `[TODO]`.
- 2026-06-28: Fasi 0/1 (ablation frozen) implementate + verificate (test CPU leggeri). Scoperta split: `snapshot_train/` mescola i 3 split RPLAN → `eval.split` per le query, gallery intera (§4). Decisione capacità fissa ViT-B + I-JEPA eccezione (§6.4). Ablation config-driven: pooling/whitening-dim/risoluzione/extraction_layer via override CLI + `model.variant` (§6.5). Training (projection-head/LoRA) rimandato a Fase 3 col nodo coppie-positive. Resta da indicizzare/valutare via sbatch.
- 2026-06-29: **Fase 3 (projection head) implementata.** Pipeline disaccoppiata (RAW salvato una volta; whitening/head al volo via `prepare_index`). Head A+ self-supervised (positivo = pianta degradata + flip/rot90, InfoNCE, τ/V configurabili), training su train+valid (test held-out). Moduli `projection_head/projection_pairs/train_projection`; ordine sbatch in `COMANDI.md`; job di stage `index/pairs/trainhead/eval_head_all`. LoRA ancora fuori. Smoke test CPU verdi. ⚠️ formato `embeddings/` cambiato (RAW) → rigenerare dallo Stage A. Da lanciare via sbatch.
- 2026-06-29: **Benchmark multi-encoder eseguito** (5 encoder, full, split test, n=2000): tabella in §6.4 `[DONE]`. Pattern geo≫comp>topo per tutti; terzetto DINOv2≈DINOv3≈I-JEPA appaiato su comp/topo, I-JEPA best su geometria, SigLIP2/RADIO sotto. Chiarita §6.4 la distinzione **capacità backbone** (tutti ViT-B tranne I-JEPA ViT-H) vs **dim embedding output** (RADIO 2304 / I-JEPA 1280 / altri 768). num_queries 200→2000 (stabile ≤0.008). Partial retrieval (`partial_all_job.sh`) ancora da analizzare.
