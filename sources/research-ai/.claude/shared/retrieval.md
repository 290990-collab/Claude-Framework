# Retrieval — rilevanza, metriche, partial, benchmark

## Rilevanza architettonica ≠ similarità visiva

Un encoder su raster cattura geometria, forma e colore; per un architetto la
rilevanza è soprattutto **funzione e topologia** (quali stanze sono connesse,
come si accede, la circolazione). Due piante possono *sembrare* simili ed essere
funzionalmente diverse, o sembrare diverse (ruotate, riproporzionate) ed essere
funzionalmente identiche.

**Evidenza (SSIG, Vidanapathirana et al. 2023):** uno user study mostra che il
giudizio umano di similarità fra piante correla con una **Graph Edit Distance**
(GED) sul grafo delle stanze — non con la somiglianza di forma.
*GED = numero minimo di modifiche (aggiungi/togli/rietichetta nodi e archi) per
trasformare un grafo nell'altro*; mappa direttamente sui campi RPLAN (nodi =
`rType`, archi = `rEdge`).

Riferimenti: SSIG (arXiv 2309.04357) · DANIEL/ROBIN (Sharma et al., ICDAR 2017,
primo CBIR deep per piante) · **Space Syntax / Justified Plan Graph** (Hillier &
Hanson 1984; Lee, Ostwald & Gu 2018) per le misure configurazionali.

## I tre assi di rilevanza

Niente score fuso, niente pesi, niente soglia: la rilevanza è **scomposta in tre
assi indipendenti**, ognuno in [0,1] (`GalleryAxes` in `src/evaluation/`).

| Asse | Da cosa | Cosa misura |
|---|---|---|
| **Composizione** | `rType` → istogramma a 13 tipi | quali e quante stanze |
| **Topologia** | `rEdge` → adiacenza per **tipo** (91 coppie, permutazione-invariante) | quali stanze sono connesse |
| **Geometria** | `gtBoxNew`/`gtBox` → area+aspect del footprint + distribuzione di area per tipo | forma e scala |

## Le metriche (redesign per-asse, giugno 2026)

Ogni metrica è calcolata **contro l'intera gallery**, non solo sui top-k
recuperati: è ciò che le permette di *fallire*. K ∈ {1, 5, 10, 100}.

- **nDCG@K — primaria.** Usa la similarità graduata come gain, con IDCG
  calcolato sui migliori K dell'**intera gallery**. Niente soglia → copre tutti
  e tre gli assi, geometria compresa (che essendo continua ha *solo* nDCG).
- **Recall@K e mAP@K — secondarie**, solo sugli assi **discreti**
  (composizione, topologia): i rilevanti sono la **classe di equivalenza esatta**
  (stesso istogramma / stessa adiacenza), quindi il numero di rilevanti emerge
  dai dati. Normalizzate per `min(K, |R|)`. Le query con classe singleton sono
  **escluse e contate**. **MRR rimossa** (saturava sugli assi densi).

⚠️ **Perché il redesign.** Le metriche originali (score fuso + soglia, valutate
solo sui top-k) erano **sature e insignificanti**: il **96% delle coppie casuali**
superava la soglia 0.5, quindi Recall@5 ≈ 1.0 anche per un retriever casuale.
Due difetti che si sommavano: **ambito circolare** (nessun insieme di rilevanti
definito sulla gallery) ed **etichetta troppo permissiva**. Il problema toccava
**solo la valutazione**: score e ranking erano sempre stati reali.

**Classi di equivalenza misurate (67k piante):** composizione 721 classi, solo
**0,4% singleton** (sana e de-saturata: un retriever casuale fa ~6% di
Recall@10); topologia 15.815 classi ma **15% di piante singleton** (match esatto
sparso) → sulla topologia ci si appoggia soprattutto a nDCG. ⚠️ Sulla
composizione le classi sono enormi (mediana **3980** piante, l'8,17% della
gallery condivide la composizione di una query data): lì Recall@K si comporta di
fatto come una **precisione**, e in un batch InfoNCE da 256 circa **21 dei 255
"negativi" sono in realtà massimamente rilevanti**. Sulla topologia la classe
mediana è 16 e i falsi negativi sono 0,7 per batch.

**Raffinamenti previsti:** GED (stile SSIG) come alternativa/affianco al Jaccard
topologico; sensitivity analysis su K; metriche diagnostiche sui top-K
(room-count MAE, adjacency preservation) per spiegare *perché* un encoder vince.

## Il floor — quanto prende chi non guarda la query (misurato 31 lug 2026)

`python -m src.evaluation.random_floor`, due null: **casuale** (ranking a caso) e
**costante** (le stesse piante a tutte le query, dice se la metrica
*discrimina*). Numeri completi in `status.md §10`, script
`scripts/evaluation/01_random_floor.sh`.

**nDCG@10 del ranking casuale: comp 0.739 · topo 0.466 · geom 0.869.** Da qui tre
regole di lettura, che valgono per ogni tabella del progetto:

1. **L'nDCG per-asse è in gran parte saturo, e non per un bug**: usa gain
   *continui* su una gallery di planimetrie molto simili fra loro, quindi una
   pianta a caso ha già similarità alta con la query. Recall/mAP dello stesso
   ranking casuale stanno a 0.085 e 0.035: **lì lo spazio utile è quasi intero**.
   L'nDCG@10 da solo è la metrica meno informativa del progetto.
2. **Un punteggio si legge come frazione dello spazio disponibile**,
   `(score − floor)/(1 − floor)`: la geometria ne ha solo **0.131**, quindi il
   margine 0.002 fra i due rami è l'**1.5%** di quell'intervallo.
3. **La topologia è l'asse che discrimina** (floor 0.466, il più basso) ed è
   quello dove il training compra di più.

⚠️ Il floor **dipende dalla gallery** (l'IDCG è calcolato su di essa): va
misurato e riportato per ramo, non è un numero universale. Misurato: le due
gallery (67.453 e 67.405) danno lo stesso floor entro 0.0011.

## Partial retrieval (vision — implementato)

Query = pianta **degradata** (stanze rimosse) contro la gallery completa
invariata. Riusa tutta la pipeline: cambia solo *cosa* si passa a
`pipeline.query()`.

- **Costruzione**: mascheramento sullo **snapshot** (stesso dominio della
  gallery): affine per-immagine griglia-256→px, poi flood-fill della regione a
  bianco. ⚠️ `gtBoxNew` è `[x0,y0,x1,y1]`; `gtBox`/`footprint` ha gli assi
  **scambiati** `[y0,x0,y1,x1]` (area/aspect restano corretti, sono simmetrici).
- **Bordo aperto** (`open_boundary: true`): oltre a sbiancare l'interno si
  **cancellano i muri** che bordavano la stanza rimossa, così l'incompletezza è
  **visibile** e non si crea un appartamento completo più piccolo. Mai muri
  nuovi. Verificato: il residuo di muri delle stanze rimosse è 0,5-2,4% a piena
  risoluzione (≈1,2% a 224px, l'input reale dell'encoder) → masking onesto, la
  sagoma del footprint completo non trapela.
- **3 strategie** configurabili separatamente: `random` (frazione di stanze,
  sweep `fractions` → **curva masking-level**), `semantic` (tieni `keep_types`),
  `topology` (togli stanze foglia, `max_degree`).
- **Ground truth doppia**: (1) **self-recovery** = rank / Recall@K / MRR della
  pianta sorgente; (2) **per-asse** rispetto alla pianta **completa**. In partial
  il self **non** si esclude (la query degradata ≠ immagine originale →
  ritrovarla è un successo legittimo).
- Interruttori a due livelli: master `partial.enabled` (override CLI
  `--partial`) e per-strategia `strategies.<nome>.enabled`.

## Benchmark multi-encoder (proposto dal team, confermato dai prof)

Cinque encoder scelti per **coprire assi di rappresentazione diversi**, non come
lista di SOTA:

| Encoder | Famiglia | Ruolo | Checkpoint |
|---|---|---|---|
| DINOv2 | self-supervised | baseline self-sup standard | `facebook/dinov2-base` |
| DINOv3 | self-supervised | generazione successiva, stessa famiglia | `facebook/dinov3-vitb16-pretrain-lvd1689m` (gated) |
| SigLIP2 | vision-language | rappresentazione guidata dal linguaggio | `google/siglip2-base-patch16-224` |
| RADIO | agglomerativo | distilla DINOv2+CLIP+SAM → fonde gli assi | `nvidia/C-RADIOv2-B` |
| I-JEPA | self-sup **predittivo** | predice regioni mascherate nel latente → concettualmente vicino al partial | `facebook/ijepa_vith14_1k` |

⚠️ **Equità**: capacità fissa a **ViT-B** per tutti; I-JEPA è l'eccezione
obbligata (nessun checkpoint ViT-B ufficiale → ViT-H): il divario va
**dichiarato nel report**. Le varianti di taglia non si confrontano.

## Ablation (Fase 1 — frozen, training-free)

Tutti gli assi sono **config-driven** e si variano **uno alla volta** con
override CLI dotlist (niente editing dei YAML). `model.variant` è solo
un'etichetta che namespacizza l'output: **non auto-configura nulla**, i knob
vanno impostati esplicitamente.

| Asse | Knob | Note per-modello |
|---|---|---|
| Pooling | `model.kwargs.pooling` = natural\|mean\|gem (+`gem_p`) | CLS↔mean↔gem pieno solo su DINOv2/v3; gli altri naturale-vs-gem |
| PCA whitening | `whitening.enabled`, `whitening.dim` | `dim` = top-D componenti; neutralizza anche la differenza di larghezza nativa (I-JEPA 1280 vs 768) |
| Risoluzione | `model.kwargs.image_size` (multiplo del patch) | **SigLIP2**: legata al checkpoint → si cambia `hf_name` (-224/-256/-384) |
| Extraction layer | `model.kwargs.extraction_layer` (-1, -2, …) | solo DINOv2/v3/I-JEPA (`output_hidden_states`); non applicabile a SigLIP2 (testa di pooling solo sull'ultimo layer) né RADIO (l'API espone solo l'output finale) |

```bash
# un punto di sweep: indicizza + valuta una variante
python -m tests.test_vision_retrieval   model.variant=gem model.kwargs.pooling=gem
python -m src.vision.evaluation.evaluate model.variant=gem eval.split=test partial.enabled=false
```

## Fase 3 — projection head (vision)

Head = MLP `Linear→GELU→Linear` + L2-norm allenata **sopra l'encoder frozen**
con **InfoNCE self-supervised**: il positivo è la stessa pianta **degradata**
(masking) più augmentation valide (flip/rot90) → **nessuna circolarità** con le
label di valutazione. Training su vettori cachati, early stopping sul valid.
Risultati e conclusioni: `.claude/shared/status.md`.

## Ordine di lavoro (vision)

1. ~~Label reali dai `.mat` + mAP/nDCG~~ **fatto**
1b. ~~Redesign metriche per-asse, ambito sull'intera gallery~~ **fatto**
2. Metriche semantiche/diagnostiche sui top-K (room-count MAE, adjacency
   preservation) — **da fare**
3. ~~Masking su immagine + studio del livello di masking~~ **fatto**
4. ~~Astrazione encoder + benchmark multi-modello~~ **fatto** (5 encoder
   **misurati**, full + partial, frozen e con head). ⚠️ Il registry ne conta
   ora 8: `tipsv2` e `pecore` hanno i numeri del valid (`status.md §18`),
   `pespatial` ha le 6 run frozen su disco ma **non ancora lette** (`§19`).
   Nessuno dei tre ha il **partial** né la **head**: nella tabella del report
   vanno con la colonna vuota, non confusi coi 5 storici.
5. **Report breve per i prof** — metriche introdotte, studio del masking,
   tabella comparativa multi-encoder ← prossimo passo, insieme alle analisi
   residue (pooling gem/mean, per-asse sotto masking).
