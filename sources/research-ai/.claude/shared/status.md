# Stato — risultati, decisioni, ipotesi smentite

Cronologia **compatta** di ciò che è stato misurato e deciso. Fonte dei numeri:
`vision_pipline.xlsx` (vision), log e `training_summary.json` dei job (graph),
`spiegazione_metriche_e_risultati_grafi.md` (versione discorsiva per il report).

> **Come si aggiorna** (economia dei token): si **aggiunge** una voce quando un
> risultato è letto o un'ipotesi è risolta — non si riscrive il file. Ogni voce:
> *data · configurazione · numeri · conclusione (confermata/smentita) · perché*.
> Quando una sezione supera ~40 righe, si comprimono le voci vecchie in una riga
> di sintesi, tenendo per intero solo l'ultima misura di ogni cosa. Lo storico
> integrale pre-29 lug 2026 è in `.claude/archive/CLAUDE-2026-07-29-full.md`.

**Setup di riferimento** (comune a tutti i numeri qui sotto, salvo diversa
indicazione): gallery = intero `snapshot_train/`; query = **2000 campionate dal
test split**; metriche per-asse contro l'intera gallery; nDCG@10 riportato come
`composizione / topologia / geometria`.

---

## 1. Ramo vision

**Benchmark completo (lug 2026)** — 5 encoder × pooling (natural/gem/mean) ×
trasformazione (raw/whiten/head/head+whiten) = 28 combinazioni per contributo,
full e partial.

- **Full retrieval: la head NON aiuta.** Frozen `whiten` (larghezza nativa) ≥
  head e head+whiten (256d) su ogni asse e modello, per ~0.01 di nDCG. Atteso:
  la head comprime e il suo obiettivo è il masking, non il full.
- **Partial self-recovery: la head è un guadagno grande e crescente col
  masking** — che è esattamente il suo scopo. dinov3/natural, MRR: f=0.5
  0.535 → 0.835; f=0.75 **0.205 (frozen-whiten) → 0.668 (head)**, ~3×.
  dinov2/natural: f=0.5 0.594 → 0.742; f=0.75 0.258 → 0.490. Con raw puro
  siglip2/radio/ijepa collassano già a f=0.25; il solo whitening li recupera in
  gran parte.
- **Head pura vs head+whiten dipende dal modello**: per dinov3/siglip2 la head
  pura è pari o migliore già a masking medio; per radio/ijepa il whiten-dopo-head
  aiuta; **a f=0.75 la head pura vince quasi ovunque** → default head+whiten,
  head pura per incompletezza estrema.
- **Ranking partial con head (f=0.5, natural):** dinov3 > dinov2 > radio >
  siglip2 > ijepa. La strategia `topology` (togli foglie) è quasi satura per
  tutti; i casi duri sono `random` pesante e `semantic`.
- **Migliori numeri full per asse** (fra tutte le combinazioni): **C 0.830 ·
  T 0.662 · G 0.948** (geometria: ijepa/gem/whiten; topologia: dinov3/natural/
  whiten). Media migliore: ijepa/natural/whiten 0.8077.
- ⚠️ **Tetto a f=0.0: MRR 0.970 identico per tutti gli encoder** → limite dei
  **dati**, non dei modelli: a masking nullo la query è il PNG originale intatto
  e RPLAN contiene duplicati esatti (3% dei file) e quasi-duplicati.
- Primo giro (giu 2026, n=200): geometria > composizione > topologia per
  **tutti** gli encoder; cluster di testa DINOv2 ≈ DINOv3 ≈ I-JEPA entro il
  rumore, SigLIP2 sotto, RADIO ultimo → *più recente/più grande non vince*:
  domina il **domain gap** (colormap sintetiche vs immagini naturali). 16 GB di
  VRAM bastano per tutti.

**Da analizzare ancora:** confronto sistematico pooling gem/mean; metriche
per-asse-vs-pianta-completa sotto masking.

---

## 2. Ramo graph — la scoperta che ha riscritto il metodo

**(a) Primi giri, selezione su val-loss (17-18 lug).** 50 epoche: GCN
0.931/0.781/0.939, SAGE 0.912/0.759/0.942, GAT 0.892/0.726/0.942 vs baseline
`hist` 1.000\*/0.643/0.894 (\*oracolo per costruzione). Nessun early stopping →
`epochs` alzato a 150-200. **Allenare 3× più a lungo non ha dato nulla**: GCN
+0.003, GAT invariato, **SAGE peggiorato** (0.912→0.904, 0.759→0.746).

**(b) Diagnosi (27 lug).** La classifica per val-loss è l'**inverso** di quella
per retrieval: GAT ha la loss migliore (2.08) e l'nDCG peggiore; GCN la loss
peggiore (2.73) e l'nDCG migliore. **Causa:** InfoNCE è *instance
discrimination* — in un batch da 256 molte piante condividono composizione e
topologia con la query (classi enormi: solo 0,4% di singleton sulla
composizione, mediana 3980 piante) e la loss le tratta da **negativi**,
allontanando attivamente proprio ciò che la valutazione considera rilevante.
Ottimizzare meglio la loss può quindi **peggiorare** il retrieval.

**(c) Fix — `RetrievalProbe`.** Mini-retrieval sul **valid** (gallery fissa
campionata, self escluso) che gira ogni `probe_every` epoche e guida
best-checkpoint ed early stopping al posto della val-loss (che resta come sola
diagnostica). Protocollo **identico** alla valutazione finale: gli helper sono
condivisi (`axis_metrics.py`), così la metrica che *seleziona* e quella che
*giudica* sono lo stesso codice. Costo 2,6 s/epoca (~20%).

**(d) Conferma empirica (job 74096).** **GAT raggiunge il massimo di retrieval
all'epoca 3** (mean nDCG@10 sonda 0.8446) e poi **peggiora in modo monotono per
20 epoche** (0.8284) **mentre la val-loss continua a migliorare** (2.952 →
2.235). Per asse: composizione 0.890→0.858 e topologia 0.714→0.695 **calano**,
geometria 0.927→0.932 **sale** — esattamente la previsione, perché
composizione/topologia hanno grandi classi di equivalenza e la geometria no.
SAGE stesso profilo, più mite (picco a epoch 41).

**(e) Risultati con selezione su nDCG (27 lug, 74121 + 74184).** Picchi: GCN
epoch 12, SAGE 40, GAT 3; lo stop cade sempre a picco+20 e **non è prematuro**
(0/20 epoche successive superano il picco). Test: **GCN 0.934/0.789/0.938
(media 0.8870)**, SAGE 0.916/0.766/0.943 (0.8750), GAT 0.915/0.761/0.938
(0.8713). Il guadagno segue il danno previsto: GCN +0.001 (era su un plateau),
SAGE +0.010, **GAT +0.016** (il più danneggiato). Effetto maggiore sulle
metriche di **ordine**: GAT composizione mAP@10 0.401→0.525 (+31% rel.),
Recall@1 0.643→0.722. ⚠️ Trade-off reale: la **geometria peggiora** un filo
(GAT −0.008) — è l'asse continuo senza classi di equivalenza, quindi non soffre
di falsi negativi e continuava a migliorare allenando.

**(f) Ablation pesi casuali (28 lug) — quasi tutto viene dall'ARCHITETTURA.**
Misurato con la sonda (valid, gallery 5000, 500 query, nDCG@10):
**add-pool delle feature grezze, senza alcuna rete = 0.884/0.625/0.906 (media
0.8050)**; GNN a **pesi casuali** 0.799-0.809; GNN allenate GCN 0.8615, SAGE
0.8425, GAT 0.8411. Cioè **un sistema mai allenato è già al ~93% di quello
allenato**, e tutto il training vale **+0.056**. Causa: con l'one-hot dei tipi,
l'`add`-pool **è** l'istogramma delle stanze → la composizione arriva gratis e
la geometria quasi. Scomposto per asse, il training compra **essenzialmente la
topologia**: GCN da casuale ad allenato fa C +0.056, **T +0.100**, G +0.012.
→ Le poche epoche **non sono un errore**: su grafi 4-8 nodi con 2 layer,
imparare a propagare a 1-2 hop richiede poche centinaia di passi.
→ Il **denominatore onesto** non è solo la baseline `hist`, è la GNN a pesi
casuali: va riportato nel report.

**(g) Fix 1+2 (28 lug).** *(1)* Augmentation riscritte sul principio "*ogni
augmentation dichiara un'invarianza, da confrontare con la ground truth*":
flip/rot sono invarianze **vere** (i tre assi sono esattamente invarianti) →
guadagno puro; `node_drop` è **falsa** sul full ma vera sul partial → si dosa
sapendolo. `node_drop` 0.1→0.2 (grafi effettivamente perturbati 51%→75%),
`feat_mask` reso **per-cella** invece che per-colonna-globale (che spostava lo
spazio uniformemente invece di creare difficoltà). *(2)* **`raw_skip`**:
add-pool delle feature grezze concatenato prima della proiezione → composizione
e geometria garantite per costruzione, capacità della rete libera per la
topologia. **Test (74714 vs 74184):** media **GCN 0.8870→0.9130 (+0.026)**,
SAGE +0.005, **GAT −0.023**. La composizione sale per tutti (GCN 0.934→0.971,
mAP@10 0.632→0.847, Recall@1 0.793→0.922) ma sulla topologia i tre divergono:
GCN +0.039, SAGE invariata, **GAT −0.087**. ⚠️ **Meccanismo:** con `raw_skip` la
composizione diventa alta e gratis dalla prima epoca, quindi il criterio `mean`
è dominato dalla componente regalata e il picco arriva **prestissimo** (GAT e
SAGE a epoch 5, GCN a 35) — cioè *prima* che la topologia si sviluppi. Skip +
criterio `mean` si combinano male → giustifica `select_criterion: topology` e
`probe_every: 1`.

---

## 3. Ablation OFAT (28 lug, job 74839 / 74840 / 74856)

9 varianti su 10 per encoder (`selgeom` mai lanciata: lista desincronizzata, poi
sanata con una guardia). ⚠️ **Si leggono sulla colonna topologia della sonda**,
non su `best_score`: `selmean` è selezionata su un criterio diverso, quindi il
suo punteggio è su un'altra scala.

| Encoder | Migliore | Topologia (sonda) | vs `base` |
|---|---|---:|---:|
| gcn | **`tau02`** (`nd01` pari) | 0.800 | +0.030 |
| sage | **`nd01`** | 0.747 | +0.031 |
| gat | **`nosym`** | 0.703 | +0.012 (al limite del rumore) |

σ della sonda ≈ 0.002-0.004.

**Verifica sul TEST delle vincitrici (job 74885-74887, 74931-74933):**
gcn `base` 0.965/0.788/0.939 → **`tau02` 0.972/0.826/0.940**; sage `base`
0.935/0.726/0.933 → `nd01` 0.940/0.759/0.934; gat `base` 0.927/0.697/0.938 →
`nosym` 0.907/0.743/0.946.

- ✅ **La sonda predice il test**: Δ topologia sonda→test = gcn +0.030→+0.038,
  sage +0.031→+0.033, gat +0.012→+0.046 — segno sempre giusto, magnitudo quasi
  identica su gcn/sage. Il protocollo "ablation sul valid, test solo per le
  finaliste" è **validato**; non serve ingrandire `probe_gallery`.
- **Classifica test (media nDCG@10):** `gcn/tau02` **0.913** > `gcn/base` 0.897 >
  `sage/nd01` 0.878 > `sage/base` 0.865 ≈ `gat/nosym` 0.865 > `gat/base` 0.854 >
  baseline `hist` 0.846. Ordine encoder invariato **GCN > SAGE > GAT**.
- Valore vero rispetto alla baseline: la **topologia** — nDCG 0.826 vs 0.643 ma
  soprattutto **Recall@1 0.558 vs 0.027 (20×)**.
- ⚠️ `gat/nosym` ha la **geometria più alta di tutto il ramo graph (0.946)**,
  contro 0.948 del miglior encoder vision: sull'unico asse **senza circolarità**
  i due rami sono ormai pari.
- **Bilancio onesto della giornata del 28 lug su gcn ≈ zero** (topologia 0.826 vs
  0.828 del mattino): il guadagno vero erano i fix 1+2; il secondo giro di
  tuning è stato una regressione che l'ablation ha individuato e annullato.
- **Da fare:** riportare `temperature: 0.2` in `gcn.yaml`/`graph_sage.yaml` (gat
  resta 0.3 con flip/rot a 0) e provare la **combinazione** τ0.2 + `node_drop
  0.1`, che l'OFAT per costruzione non copre.

---

## 4. Confronto appaiato vision vs graph e attese sulla fusione (28 lug)

Stesse 2000 query, stessa gallery, stesse metriche — verificato: entrambi i log
riportano le identiche esclusioni singleton (10 composizione, 313 topologia).

**nDCG@10 — vision best per asse C 0.830 / T 0.662 / G 0.948** vs **graph GCN
0.934 / 0.789 / 0.938** (SAGE geometria 0.943, gat/nosym 0.946).

1. **Sulla geometria vince il vision (0.948 vs 0.946)** ed è **l'unico asse dove
   il confronto è alla pari**: è il dato più onesto della tabella.
2. Sulla topologia il miglior encoder visivo (0.662) supera di pochissimo la
   baseline `hist` (0.643), che le adiacenze **non le guarda affatto** →
   leggere la connettività dai pixel è genuinamente difficile (muro pieno vs
   passaggio = pochi pixel).
3. Il grafo rappresenta le stanze come **bounding box**: una stanza a L e una
   rettangolare con lo stesso box sono per lui identiche. Muri, aperture e forma
   del contorno sono informazione che **solo il vision** ha — e che **nessuno
   dei tre assi attuali misura**.

⚠️ **Aspettativa realistica per la fusione.** Prendendo il meglio per asse fra
tutti i sistemi (C 1.000 `hist`, T 0.789 GCN, G 0.948 vision) si arriva a media
**0.912 contro 0.887 del solo GCN**: **+0.025, quasi tutto dalla composizione
della baseline**; il contributo specifico del vision vale **+0.005÷0.010**. Sulle
metriche attuali la fusione **sposta poco**, e questo va detto nel report invece
di promettere un salto di nDCG. Il valore va cercato nel **partial** (i rami
falliscono in modo diverso: il vision degrada coi pixel rimasti, il grafo è
nativamente robusto al node-drop) e nell'applicabilità reale.

**Implementazione consigliata:** *concatenazione pesata* `[√α·v ; √(1−α)·g]` su
embedding L2-norm → il prodotto scalare **è già** `α·simV + (1−α)·simG`, quindi
basta **un solo indice FAISS e una sola ricerca**. Prima normalizzare la scala
degli score per ramo; confrontare con **RRF** (fusione per rango, scale-free) come
baseline. ⚠️ Prima di costruire: misurare la complementarità dagli embedding già
salvati (sovrapposizione top-10, correlazione nDCG per-query, upper bound
oracolo), con **inner join sui nomi** (67.405 vs 67.453).

**Due regimi da dichiarare:** (A) su RPLAN coi `.mat` la fusione è **parzialmente
auto-avverante** su C/T; (B) col grafo estratto dall'immagine la circolarità
sparisce e la complementarità è piena — fuori scope Fase 1, ma è la direzione in
cui la fusione ha senso pieno.

---

## 5. Ipotesi smentite dalla misura (da riportare così come sono)

| Ipotesi | Esito | Perché |
|---|---|---|
| "La val-loss InfoNCE indica la qualità del retrieval" | ❌ **Invertita** | InfoNCE allontana i rilevanti finiti nello stesso batch |
| "Allenare più a lungo migliora" | ❌ | 50→150 epoche: +0.003 su GCN (rumore), SAGE **peggiora** |
| "τ più alto (0.3-0.5) smorza i falsi negativi e aiuta" | ❌ | τ 0.2→0.3 costa **0.038 di topologia** su gcn; τ=0.5 è la peggiore su tutti e tre. La stima dell'8,17% misurava la composizione, ma la topologia ha classi mediane di 16 → ammorbidire la pressione distrugge il segnale che serve |
| "Encoder più recenti/grandi vincono" | ❌ | Cluster di testa entro il rumore, RADIO ultimo: domina il domain gap |
| "La projection head migliora anche il full retrieval" | ❌ | Sul full frozen+whiten ≥ head; la head serve al **partial** (dove vale fino a 3×) |
| "Il tetto di MRR 0.970 è un limite dei modelli" | ❌ | È un limite dei **dati** (duplicati esatti nel 3% dei PNG) |
| "Il guadagno delle ablation svanisce sul test" | ❌ (era un artefatto) | Il riferimento era una cartella **sovrascritta**, non la configurazione ipotizzata |

Confermate invece: la sonda di retrieval come criterio di selezione; `raw_skip`
sulla composizione; le simmetrie flip/rot su gcn/sage (ma **non** su gat).

---

## 6. Incidenti operativi

- **GPU Blackwell sm_120** non supportata dal PyTorch dell'env: job vx07
  65653-65657 morti con `no kernel image` al forward della head; rilancio
  riuscito su GPU compatibile (67424, 67448, 67451-67453). Da allora tutti gli
  script sensibili portano la constraint con allowlist.
- **Job 74848 finito in 0 s**: passato `sage` invece di `graph_sage` (gli script
  vogliono il basename del YAML) → encoder saltato con avviso, successo
  apparente.
- **Job 74096 scartato**: partito mentre il codice veniva modificato → giro misto
  GCN-vecchio / GAT-SAGE-nuovo. Rifatto da 74121.
- **`selgeom` mai lanciata**: `ALL_VARIANTS` e la tabella dei flag erano
  desincronizzate → 9 varianti su 10, con successo apparente. Sanata con una
  guardia che ora fallisce.
- **31 lug — le 4 run del floor uccise dal login node**: `ulimit -t` = **600 s
  di CPU** su `ailb-login-02`; `random_floor` ne consuma ~180 s per seed
  (misurati 196.0 / 178.0 / 161.2 s) e muore durante il 4°, con un `Killed`
  muto. Non è memoria (110 GB liberi). Regola: **ogni job CPU su scala dataset
  va su nodo di calcolo**, anche se non usa la GPU.

---

## 7. Prossimi passi

1. **Late fusion vision+graph** — miglior rapporto valore/sforzo: gli
   `embeddings.npy` + `names.json` allineati dei 4 sistemi sono **già salvati**.
   Prima misurare la complementarità, poi implementare.
2. **Modalità partial sul ramo graph** (gemella del vision), dove la robustezza
   nativa al node-drop dovrebbe pagare.
3. **Cambiare l'obiettivo, non allenare di più**: testa di proiezione stile
   SimCLR (loss su una proiezione usa-e-getta, retrieval sulla rappresentazione a
   monte) — attacca i falsi negativi alla fonte. Poi **GIN** (bias induttivo
   giusto per la topologia), dropout su GAT, scheduler lr, batch più grande.
4. **Combinazione τ0.2 + `node_drop` 0.1** (l'OFAT non la copre).
5. **`GraphModelManager`** (config-loader vero: a quel punto i ponti YAML→flag
   negli script diventano superflui).
6. **Decidere la questione circolarità** (oracle dichiarato / solo geometria /
   grafo estratto dall'immagine) — vedi `.claude/shared/architecture.md`.
7. **Report per i prof**: metriche introdotte, studio del livello di masking,
   tabella comparativa multi-encoder, confronto fra i rami coi caveat.

---

## 8. Audit metodologico della codebase (30 lug) — nessuna run, solo lettura

Diagnosi completa in **`current_state.md`** (root). Qui solo ciò che chiude o
apre un'ipotesi; i dettagli non si duplicano.

**Chiuso in positivo (verificato, non più da sospettare):**
- Le **2000 query sono davvero le stesse** nei due rami: verificato per
  costruzione (stesso `sorted()`, stesso predicato di filtro, stesso
  `Random(42).sample`) *e* sui due json (`names.json` ⊂ `image_paths.json`,
  solo-vision = 48, solo-graph = 0). Il claim di §4 regge.
- **IDCG e self coerenti** in entrambi i rami e in entrambe le modalità: nessuna
  deflazione sistematica dell'nDCG.
- **Esclusioni singleton identiche per costruzione** (le 48 piante extra del
  vision hanno `valid=False`): il 10/313 dei log non era una coincidenza.
- Nessun leakage nel training della head (coppie da `train`+`valid`).

**Aperto o contraddetto (da decidere prima del report):**
- ⚠️ **«La geometria è l'unico asse alla pari» non è supportata dal codice**: la
  GT geometrica è funzione di `rType`/`gtBoxNew`, che il grafo riceve in input.
  Cambia la § circolarità di `CLAUDE.md` e l'argomento sulla fusione.
- ⚠️ **Selezione sul test** nel ramo vision (nessuno script valuta su `valid`):
  i massimi per-asse, **0.948 compreso**, sono max su ~60 config lette sul test.
- ⚠️ **Whitening vision fittato su tutta la gallery** (contiene valid+test),
  mentre il graph normalizza col solo train: protocolli diversi fra i rami.
- ⚠️ **La head vision è ancora selezionata sulla val-loss InfoNCE**, il criterio
  smentito in §2: la conclusione «sul full la head non aiuta» non è difendibile
  finché non si riallena con selezione su probe.
- ⚠️ **Nessuna stima di incertezza e per-query mai salvati**: ogni Δ ≤ 0.005 —
  incluso 0.948 vs 0.946 — è indistinguibile dal rumore finché non c'è un test
  appaiato. Il **floor** (ranking casuale) non è mai stato misurato.

## 9. Fase A.1 — riconferma dei rilievi, uno per uno (30 lug, nessuna GPU)

Metodo: grep + letture a range + **esecuzione** per i punti verificabili solo
così. Esito: **11 confermati, 1 ridimensionato, 1 non verificato**.

**Confermati** (evidenza letta o eseguita in sessione):
- **A1** nessuno script vision valuta su `valid`; `eval.split=test` in
  `scripts/vision/{04,05,06,07}_eval_*.sh:33-34`. Il consumatore gestisce `valid`
  correttamente: manca l'invocazione, non il meccanismo.
- **A2** whitening su tutta la gallery, **nessun flag** train-only esiste.
- **A3** `train_projection.py:108-109` monitora solo `vl < best_val`; grep di
  `probe|ndcg|monitor` in codice e config → **zero hit**: nessun criterio
  alternativo dietro un flag.
- **A4** unico hit di `std` in `src/` è `graph/transforms.py:142` (z-score sulle
  feature, **non** incertezza); nessun per-query persistito.
- **A6** `sim = (area_sim + aspect_sim + dist_sim) / 3.0`, pesi hardcoded,
  `GalleryAxes.__init__` senza parametro di pesi → **nessun punto di iniezione**.
- **A7** `grep -c assert tests/*.py` → **0, 0, 0** (115 righe totali).
- **B1** su disco oggi: `temperature: 0.3`, `node_drop: 0.2`,
  `flip_prob/rot_prob: 0.5` — nessuno dei tre è la variante vincente misurata.
- **B2** 67.405 nomi graph, 67.453 vision, |vision∖graph| = **48**,
  |graph∖vision| = **0**, e l'ordine della lista vision filtrata coincide
  esattamente con quello graph (inner join pulito, non un disallineamento).
- **B3** partial `exclude_self=False` anche sulle metriche per-asse, full
  `exclude_self=True`.
- **B4** riprodotto: YAML con `amp: true`/`foo_flag: false` in più → output del
  ponte **byte-identico**, exit code 0 in entrambi i casi.
- **B5** riprodotto: `proj.weight` **(128,147)** con `raw_skip=True`,
  **(128,128)** senza; in eval `load_state_dict` a nudo, errore generico.

**Ridimensionato — A5 (parziale).** `type_area_distribution` **è** ricostruibile
dalle node feature (somma aree per tipo / totale). Ma `footprint_area` e
`footprint_aspect` derivano da `rec.gtBox`, che **non** è nelle feature dei nodi:
il grafo ha i box delle singole stanze, non il bbox globale. Quindi la GT
geometrica non è interamente calcolabile dall'input del grafo. ⚠️ Resta da
verificare se `gtBox` coincide con l'unione dei `gtBoxNew`: se sì, A5 torna
pieno. La formulazione «di grado, non di natura» va comunque corretta.

**Non verificato:** **B6** (clamp degli id di relazione e `reduce="mean"` su
`edge_attr`) richiede di leggere `graphs.pt`; e la domanda «il colore delle
stanze nelle PNG codifica `rType`?» richiede una PNG + il `.mat` corrispondente.
Entrambi sono artefatti pesanti: servono l'ok dell'utente.

### 9.1 — A1 ri-verificato il 13 ago: **risolto in pratica, non nel codice**

⚠️ **Il criterio della tabella non discrimina più.** «`grep -rn 'eval.split'
scripts/` → esiste almeno uno script con `valid`?» oggi passa
(`scripts/evaluation/02_perquery_vision_valid.sh:96`), ma quello script è **nato
per chiudere A1** (lo dichiara alle righe 5-8): il rivelatore trova la propria
toppa. La riconferma va fatta sulla sostanza.

**Risolto** — la selezione vision **non** avviene più sul test: 80 `.npz` in
`results/perquery/vision_valid/`, la vincente è scelta lì (§13, §18) e il test è
letto dopo (§14). Meccanismo consumatore intatto:
`src/vision/evaluation/evaluate.py:90-98` e `:468`. Il graph non era toccato da
A1 (probe sul valid) e ora ha anche i per-query del valid (§16).

**Residui aperti (4):**
1. Le quattro griglie storiche hardcodano ancora `eval.split=test` e **non hanno
   passthrough** di override: `scripts/vision/{04,05,06,07}_eval_*.sh:40-42`.
   Chi le rilancia torna a selezionare sul test senza accorgersene.
2. Il test è stato letto **3 volte, non una** (§14.1) — la condizione di chiusura
   di A1 («leggere il test una volta sola») è violata; mitigata solo dalla
   pre-registrazione del primario, che va dichiarata nel report.
3. **La metà "oracolo per-asse" di A1 è ancora viva nei documenti**: §1:43-45 e
   `CLAUDE.md § Stato attuale` citano **C 0.830 · T 0.662 · G 0.948**, tre
   configurazioni diverse ciascuna massimizzata **sul test** (luglio). Sul valid
   lo stesso `ijepa/gem/whiten` fa **0.9473**: è quello il numero citabile.
4. `configs/graph_retrieval.yaml:20` ha `split: test` come default e
   `configs/vision_retrieval.yaml:55` ha `split: null` (= gallery intera): il
   default di entrambi i rami non è `valid`.

Nessun residuo richiede una run: 1 e 4 sono edit di script/config, 2 e 3 sono
scrittura del report.

## 10. Il floor misurato (A.2) — 31 lug, `results/random_floor/`

2000 query del test, 5 seed di ranking, `exclude_self=True`. **nDCG@10:**

| null | gallery | comp | topo | geom |
|---|---|---|---|---|
| casuale | vision (67.453) | 0.7388 | 0.4658 | 0.8689 |
| costante | vision | 0.7690 | 0.4960 | 0.8729 |
| casuale | graph (67.405) | 0.7399 | 0.4664 | 0.8696 |
| costante | graph | 0.7372 | 0.4716 | 0.8700 |

**Spazio utile** `(score − floor)/(1 − floor)`, floor casuale della propria
gallery: geometria **vision 0.948 → 60%**, graph 0.940 → 54%, `hist` 0.894 →
**19%**; topologia graph 0.826 → **67%**, `hist` 0.643 → 33%; composizione graph
0.972 → 89%.

**Conclusioni.**
1. **L'nDCG per-asse è la metrica meno informativa che il progetto abbia**:
   il floor casuale è 0.74 (comp) e 0.87 (geom). Recall/mAP dello stesso ranking
   casuale stanno a 0.085 e 0.035: lì lo spazio utile è quasi intero.
2. **La geometria ha solo 0.131 di spazio**: il margine 0.002 fra i due rami è
   **1.5%** di quell'intervallo. Il claim resta indecidibile senza test appaiato.
3. **La topologia è l'asse che discrimina** (floor 0.466, il più basso) ed è
   quello dove il training compra di più: 67% contro il 33% di `hist`.
4. **Il null costante non inganna la metrica**: nessun vantaggio sistematico sul
   casuale (graph: 0.7372 vs 0.7399 su comp). ⚠️ Ma la sua `mc_std` è 10-100×
   più grande (0.025 vs 0.0007), perché è un solo sorteggio per seed: alcune
   scelte fisse vanno molto meglio di altre.
5. **Le due gallery danno lo stesso floor** (Δ ≤ 0.0011): le 48 piante in più
   non spostano il pavimento — ma quel Δ è dello stesso ordine del margine 0.002.
6. ⚠️ **`recall_at_k` normalizza per `min(k, R)`** (`metrics.py:73`): quando la
   classe di rilevanti ha ≥ k elementi **è Precision@k**, non Recall. Il nome
   nelle tabelle è fuorviante e va dichiarato nel report. A k=1 coincide con mAP
   per costruzione (`:96` stessa normalizzazione): riportarle entrambe a k=1 non
   aggiunge nulla.

## 11. Griglia vision sul VALID (B.1) — 31 lug, job 76919, analisi PARZIALE

> ⚠️ **SUPERATA dalla §13** (8 ago): la griglia è **completa, 56/56, dinov3
> incluso** — i file a disco sono del 6 ago, quindi il job è stato rilanciato con
> successo. Restano validi gli effetti misurati (confermati su 14 coppie invece
> di 5); **cambia il vincitore** e cade la premessa «dinov3 manca».

19 run su 56 a disco (`results/perquery/vision_valid/`), job ancora in corso.
**dinov2** completo (3 pooling × 4), **siglip2** quasi; **dinov3 fallito in
blocco** (`GatedRepoError` 401, repo gated + nessun token HF) → il job chiuderà a
44/56 e il miglior encoder del progetto **manca dalla selezione**.

**Appaiamento verificato**: tutte le run hanno gallery `22d91dcff041` (67.453),
`split=valid`, `query_seed=42`, 2000 query, e **la stessa firma di skip**
(comp 6, topo 311, geom 0 — geometria è continua: `num_relevant=-1`, quindi
Recall/mAP non esistono su quell'asse). Confronto appaiato lecito senza riserve.

**Tre effetti misurati** (nDCG@10, delta appaiati, CI 95% bootstrap, Wilcoxon):

1. **Il whitening compra topologia, su tutti i modelli**: +0.033/+0.040/+0.035
   (dinov2 gem/mean/natural), +0.015/+0.024 (siglip2), CI sempre lontano da 0.
   Su composizione l'effetto **cambia segno per encoder**: +0.005…+0.009 su
   dinov2, **−0.004…−0.005 su siglip2** (p<0.002). Su geometria è ~0.
2. **La head aiuta la composizione e paga in topologia/geometria.** Contro
   `raw`: comp +0.007…+0.008 (ns su gem), topo **−0.016** (dinov2/gem) o ns,
   geom −0.005…0. Unica eccezione **siglip2/natural**, dove migliora tutto.
3. **Sopra il whitening la head è un danno netto**: `head+whiten` < `whiten` in
   **tutte e 4** le coppie disponibili, su **tutti e tre** gli assi
   (topo −0.004…−0.009, geom −0.002…−0.004, p ≤ 2e-3). Coerente con A3: quella
   head è selezionata sulla val-loss InfoNCE.

**Chi vince (sul valid, parziale).** Per asse: comp `siglip2/natural/head`
0.8353 · topo `dinov2/natural/whiten` 0.6600 · geom `dinov2/gem/whiten` 0.9393.
In frazione di spazio utile (floor **del test**, proxy: 0.7388/0.4658/0.8689) →
**37% / 36% / 54%**: la geometria resta l'asse dove il vision copre di più.
Media dei tre assi: `dinov2/natural/whiten` 40.0% ≈ `siglip2/gem/whiten` 39.8%.

⚠️ **Due cautele.** (a) Il floor è misurato sulle query del **test**: per
normalizzare il valid serve `01_random_floor.sh --split valid` (oggi `--split
test` è cablato alla riga 50). (b) `dinov2/natural/whiten` vs
`siglip2/gem/whiten` è **indistinguibile** su composizione e geometria (CI
include 0 su 5 confronti su 7): vince solo su nDCG topo (+0.0073), e su
Recall/mAP topo l'ordine si **inverte** (siglip2 avanti, ma ns). Senza la
decisione A.5 su cosa significa "migliore", la griglia non elegge un vincitore.

---

## 12. Audit del ramo vision (6 ago 2026) — sola lettura + misure CPU

Misure fatte in sessione sui `.mat` reali (80.729 record) e su
`embeddings/vision/*/image_paths.json` (nessun `.npy` letto, nessuna GPU).

**Struttura della gallery (verificata).** 67.453 righe = test 10.127 · train
47.126 · valid 10.152; 48 righe (0,07%) senza `.mat`; 0 stem duplicati. Le **14**
gallery vision hanno **ordine identico** → l'appaiamento dentro il ramo è
garantito. ⚠️ `snapshot_train/` copre l'84% dei `.mat` (67.453/80.729): il test
ufficiale ha 12.110 piante, in gallery ce ne sono 10.127.

**Gli assi NON sono indipendenti** (359.940 coppie, 60 query × 6.000 righe).
Pearson fra i gain: comp↔topo **0.69**, comp↔geom **0.30**, topo↔geom 0.27, e
comp↔`dist_sim` **0.53**. Smentisce `relevance.py:6` («TRE segnali
indipendenti»): "vince su 2 assi su 3" non è evidenza indipendente.

**Perché la geometria ha il floor a 0.869 — causa meccanica.** `footprint_area`
∈ [0.193, 0.684] (std 0.060) → `area_sim = 1−|Δa|` ha media **0.933**, min
0.569: un terzo del gain è quasi costante. `geometry_sim` totale: media 0.849,
std 0.060, p1–p99 = [0.707, 0.955]. Il floor non è un caso, è la definizione del
gain. Inoltre area/aspect misurano il **bounding box**, non la pianta.

**"Recall" sulla composizione è Precision@k.** Classe di equivalenza mediana
≈3.990 righe (p90 15.140): nel **98,5%** delle query num_rel ≥ 10, quindi
`min(k,num_rel)=k` e la formula degenera in |top-k ∩ rel|/k. A k=100 vale ancora
per il 90%. Topologia: 59% a k=10, e **27,3% di query singleton escluse** →
Recall/mAP topologia si misurano solo sulle topologie comuni (bias ottimistico,
ma uguale per tutti i modelli → confronto appaiato salvo).

**Due difetti negli encoder (verificati nel sorgente).**
1. `base.py:24` — `gem_pool` fa `clamp(min=1e-6)` su token post-LayerNorm:
   misurato, **50,7%** delle componenti azzerate. Il "GeM" del progetto è la
   media della sola parte positiva. ⚠️ Tocca il numero di punta del ramo:
   geometria 0.948 = `ijepa/gem/whiten`.
2. `dinov2.py:72` (ereditato da `DINOv3Encoder`) — `patches = hidden[:, 1:, :]`.
   In transformers 5.8.1 `modeling_dinov3_vit.py:90` concatena
   `[CLS, register, patch]` e usa `num_prefix = 1 + num_register_tokens`
   (riga 596): per DINOv3 i register entrano in `mean`/`gem`. Non tocca
   `dinov3/natural` (topo 0.662). Resta da leggere `num_register_tokens` del
   checkpoint (gated, non letto).

**Whitening fittato sulla gallery intera** (`retrieval_model.py:137`), quindi
anche su test e valid → contraddice il vincolo «statistiche dal solo train».
Effetto atteso piccolo (1 query su 67k) ma il claim va corretto o il fit
ristretto alle 47.126 righe train. Con `dim: null` + `eps=1e-6` l'amplificazione
delle direzioni a varianza nulla arriva a **1000×**: lo spettro reale non è
stato letto (serve l'ok su un `.npy`).

### 12.1 — M1/M2/M4a-b applicati (6 ago). Numeri invariati.

Correzioni di **lettura**, non di calcolo: nessuna media cambia, cambia cosa
c'è scritto sopra la colonna. Verificato sui dati sintetici che le medie
restino identiche (`_accumulate_axes` non toccato).

- **nuovo** `src/evaluation/metric_diagnostics.py` — post-hoc dai `.npz`
  `perquery/1`: regime precision (`#rel >= k`), copertura della media
  (`num_relevant == 0`), correlazione fra gli assi. Nessuna GPU.
- `metrics.py` — docstring: il `min(k,·)` fa degenerare `recall_at_k` in
  Precision@k. Nome della funzione e chiave `"recall"` del contratto
  **invariati** di proposito (li usa il ramo graph e i 51 file già scritti).
- `relevance.py` — «TRE segnali indipendenti» → «distinti», con le correlazioni
  misurate e la saturazione della geometria dichiarate nel docstring.
- `vision/evaluation/evaluate.py` — colonna `Recall` → `Rec/Prec`, **nuova
  colonna `cop.`** (copertura, derivata dalle lunghezze delle liste di accumulo:
  nessun parametro nuovo), avviso nel report partial che quelle tabelle non sono
  confrontabili col full + caso «run che non rimuove nulla».
- `tests/test_metric_diagnostics.py` — 11 test, fra cui l'invariante che conta:
  copertura calcolata **in linea** e **post-hoc** devono coincidere. 11/11 verdi,
  `test_perquery` 16/16 (nessuna regressione).

**Non verificato**: il modulo non ha ancora girato sui `.npz` reali (serve l'ok
sugli artefatti). Comando pronto:

    python -m src.evaluation.metric_diagnostics \
        --perquery results/perquery/vision_valid/*.npz --k 10
    python -m src.evaluation.metric_diagnostics \
        --gallery embeddings/vision/dinov2/natural/image_paths.json

**Decisione aperta**: `src/graph/evaluation/axis_metrics.py:100` stampa ancora
`Recall` senza copertura — stessa metrica, stesso difetto. Non toccato per la
regola «niente refactor cross-ramo»: l'allineamento (6 righe, identiche) va
deciso, altrimenti le tabelle dei due rami divergono nel report.

---

## 13. Griglia vision sul VALID — COMPLETA (56/56), analisi dell'8 ago

I `.npz` in `results/perquery/vision_valid/` sono datati **6 ago 18:26-21:52**:
il job è stato rilanciato e chiuso, **dinov3 compreso**. Supera la §11 e la voce
del TODO che dava dinov3 per fallito.

**Appaiamento: una sola firma su 56 run** — gallery `22d91dcff041` (67.453),
`split=valid`, seed 42, 2000 query identiche per nome, skip (comp 6, topo 311).
Confronto appaiato lecito senza riserve.

**Floor usato**: il null **`constant`** (0.7942/0.5144/0.8703), non il `random`:
sulla composizione il constant è **+0.055** sopra il random, quindi è lui il
riferimento onesto. ⚠️ È misurato sul **test** (proxy per il valid, come da §11).

> ⚠️ **Rettifica 13 ago (§18.4)**: quei tre numeri sono il **solo ranking-seed 0**
> (`constant_vision_test.npz`, `run_tag=constant_floor/seed0`), non la media sui
> 5 seed, che è **0.7690/0.4960/0.8729** (§10 e il `.txt`). Sul null costante il
> seed sposta il floor di ±0.025 sulla composizione, quindi **tutte le
> percentuali di spazio utile qui sotto sono da leggere come una realizzazione,
> non come una stima**: comp 19.9% → **28.7%** con la media dei 5 seed, **36.9%**
> col floor `random`. L'ordine delle run non cambia (il denominatore è comune),
> cambia solo la scala. Convenzione consigliata e da decidere: §18.4.

**Non esiste un vincitore: 14 run su 56 sono sulla frontiera di Pareto.** La
frontiera è una curva di scambio **geometria ↔ composizione**, da
`ijepa/gem/whiten` (geom 0.9473, comp 0.8229) a `siglip2/natural/head`
(comp 0.8353, geom 0.9315). Migliori per asse: comp `siglip2/natural/head`
0.8353 (19.9% dello spazio utile) · topo `dinov3/natural/whiten` 0.6623 (30.5%)
· geom `ijepa/gem/whiten` 0.9473 (59.4%).

⚠️ **La media dello spazio utile è fuorviante**: `ijepa/gem/whiten` è primo
(33.4%) ma nei test appaiati **perde su composizione e topologia** contro tutti
e tre i suoi inseguitori, con CI che escludono 0 (vs `siglip2/mean/whiten`:
comp −0.0064, topo −0.0149, geom +0.0114; p ≤ 3e-7). Vince la media solo grazie
all'asse più saturo.

**Tre effetti ora misurati su tutte e 14 le coppie (encoder × pooling):**

1. **Il whitening compra topologia, 14/14 senza eccezioni**: +0.0305 medio
   (comp +0.0016, geom +0.0034). È l'effetto più forte e sistematico del
   benchmark: `whiten` è il contributo migliore sulla topologia in **14 casi
   su 14**.
2. **La head da sola aiuta solo la composizione** (+0.0018) e paga topologia
   (−0.0090) e geometria (−0.0015).
3. **Sopra il whitening la head è un danno netto su tutti e tre gli assi**
   (comp −0.0013, topo −0.0092, geom −0.0040), 14 coppie su 14. Conferma A3:
   quella head è selezionata sulla val-loss InfoNCE.

**Le metriche concordano in grande e divergono in testa.** Spearman fra i
ranking delle 56 run: nDCG~Recall +0.96, nDCG~mAP +0.96 (entrambi gli assi
discreti). Ma il **vincitore cambia**: su topologia nDCG dice
`dinov3/natural/whiten`, Recall e mAP dicono `siglip2/mean/whiten`; su
composizione nDCG dice `siglip2/natural/head`, Recall/mAP dicono
`siglip2/mean/head`. Sulla profondità invece il verdetto tiene
(Spearman @10~@100 = +0.93; `dinov3/natural/whiten` primo a k=1, 10 e 100).

**Diagnostica delle metriche sui dati veri** (`metric_diagnostics`, prima
esecuzione reale del modulo): composizione copertura **99.7%**, regime precision
**97.8%**, classe di equivalenza mediana **5.007** (p90 15.251) → "Recall@10"
su quell'asse è Precision@10 quasi ovunque. Topologia: copertura **84.5%**
(311 query singleton escluse), regime precision 72.5%, classe mediana 38.
⚠️ Corregge le stime della §12, che venivano da una sotto-gallery di 20.000
righe (davano 27.3% di query escluse e mediana ~3.990).

### 13.1 — La variante per il test: `siglip2/mean/whiten` (8 ago)

Confronti appaiati fra i tre candidati di testa sulla topologia (nDCG@10, CI 95%
bootstrap, Wilcoxon, Holm sui 3 assi). **A = `siglip2/mean/whiten`:**

| vs | composition | topology | geometry |
|---|---|---|---|
| `dinov3/natural/whiten` | **+0.0048** (p 5.7e-5) | −0.0025 (ns, p .135) | **+0.0016** (p 5.8e-4) |
| `dinov2/natural/whiten` | **+0.0038** (p 2.4e-3) | −0.0001 (ns, p .988) | **+0.0008** (p 4.2e-2) |

**Verdetto**: siglip2/mean/whiten vince composizione e geometria contro entrambi
i rivali di testa ed è **indistinguibile** da loro sulla topologia. Regge anche
su Recall/mAP topo (vs dinov3: −0.0005 / −0.0015, entrambi ns).

⚠️ **Smentita una conclusione intermedia dell'8 ago**: «il candidato è
`dinov3/natural/whiten` perché primo sulla topologia». Quel primato è
**+0.0024 su nDCG, non significativo** (p .135–.22). dinov3 batte davvero
*dinov2* su Recall/mAP topo (+0.0097 / +0.0078, p ≤ 1.3e-3) ma **non** siglip2.
Ordinare per la stima puntuale di un asse senza il test appaiato porta alla
variante sbagliata: è il caso da citare nel report.

**Due proprietà che la rendono la scelta difendibile**: (a) non usa la head →
immune al rilievo A3 (head selezionata sulla val-loss InfoNCE) e non va rifatta
se la head si riallena; (b) usa `whiten`, il contributo migliore sulla topologia
in 14/14 combinazioni.

⚠️ Se invece A.5 decide «massimo su un asse», la risposta cambia:
`ijepa/gem/whiten` per la geometria (0.9473, +0.0114 su siglip2, p 4.7e-124).

**Comando (una volta sola, il test non sceglie nulla):**

    sbatch scripts/evaluation/03_perquery_vision_test.sh siglip2 mean whiten

Artefatti presenti: `embeddings/vision/siglip2/mean/{embeddings.npy,
image_paths.json}`. Output atteso:
`results/perquery/vision_test/vision_siglip2_mean_whiten_full_test.npz`.

---

## 14. TEST del ramo vision — `siglip2/mean/whiten` (8 ago, una volta sola)

`results/perquery/vision_test/vision_siglip2_mean_whiten_full_test.npz`, scritto
l'8 ago 12:17. Integrità verificata: `split=test`, `exclude_self=True`, seed 42,
2000 query, gallery `22d91dcff041` (67.453), schema `perquery/1`. **Un solo file
nella cartella**: il test non ha visto altre varianti.

**nDCG@10 = 0.8259 / 0.6537 / 0.9356** (comp / topo / geom).
Recall@10 0.2875 / 0.2148 · mAP@10 0.2126 / 0.1705.

**Generalizza**: rispetto al valid della stessa variante (query diverse, non
appaiato) comp −0.0034, topo −0.0061, geom −0.0004. La selezione sul valid non
ha prodotto overfitting.

**Contro i null, appaiato** (le query di test coincidono con quelle dei due
floor — verificato per nome). Contro il null più forte (`constant`):
comp +0.0317, topo **+0.1393**, geom +0.0653, tutti con p ≤ 6e-63. In frazione
di spazio utile: **15.4% / 28.7% / 50.3%** (valid: 17.0/29.9/50.6 → coerente).

⚠️ **L'nDCG nasconde il risultato vero.** Sulle metriche d'ordine il margine sul
null `constant` è di un altro ordine di grandezza: composizione Recall@10 2.0×,
mAP@10 2.3×; **topologia Recall@10 54.9×, mAP@10 92.5×** (0.1705 contro 0.0018).
Da riportare così nel report: il +0.14 di nDCG topologia e il ×92 di mAP sono lo
stesso fatto, ma solo il secondo si legge.

**Contro il ramo graph** (⚠️ gallery diverse, 67.453 vs 67.405, `--allow-gallery-
mismatch`: confronto imperfetto fino a B.3):

| B | composition | topology | geometry |
|---|---|---|---|
| `gcn/tau02` | −0.1463 | −0.1721 | **−0.0049** (p 2e-18) |
| `hist` (training-free) | −0.1739 (oracolo) | **+0.0109** (p 4e-3) | **+0.0419** |

Il vision batte la baseline training-free del graph su topologia e geometria, e
perde contro la GNN allenata su tutti e tre gli assi. Su composizione e topologia
il confronto è **viziato per costruzione** (la GT deriva da `rType`/`rEdge`, che
sono l'input del graph): l'unico asse quasi alla pari è la geometria, e lì il
graph vince di 0.0049.

⚠️ **Conseguenza della decisione A.5, da scrivere nel report.** La variante
scelta è la più *robusta*, non la più forte sulla geometria: `ijepa/gem/whiten`
faceva 0.948 sul test (§1, benchmark di luglio), cioè **sopra** lo 0.9405 del
graph. Scegliere la robustezza è costato al vision l'unico asse dove poteva
battere il graph. **Questo NON autorizza a cambiare variante adesso**: sceglierla
guardando il test è esattamente il rilievo A1. Se si vuole il confronto per-query
anche su ijepa, va dichiarato come analisi secondaria e riportato accanto, non al
posto, di questo numero.

### 14.1 — Due varianti in più sul test (9 ago): la selezione NON si replica

Lanciate `dinov2/natural/whiten` e `dinov3/natural/whiten` sul test (file del
9 ago 15:25). **File integri**: 2000 query, `n_ret` = 100 ovunque, 0 query
degenerate, gallery `22d91dcff041`, `split=test`, seed 42, `argv` coerenti.
Nessun errore tecnico. (La rapidità è attesa: l'eval ricarica `embeddings.npy`
dalla cache e non ri-estrae.) dinov3 gira: il `GatedRepoError` è chiuso.

**nDCG@10 sul test**: dinov2 0.8262/0.6590/0.9350 · dinov3 0.8243/**0.6618**/
0.9342 · siglip2 0.8259/0.6537/**0.9356**.

**Il confronto si ribalta fra valid e test** (A = siglip2, delta appaiati, Holm):

| vs | asse | VALID | TEST |
|---|---|---|---|
| dinov2 | comp | **+0.0038** (p 2.4e-3) | −0.0003 (**ns**) |
| dinov2 | topo | −0.0001 (ns) | **−0.0053** (p 4.4e-3) |
| dinov3 | comp | **+0.0048** (p 5.7e-5) | +0.0015 (**ns**) |
| dinov3 | topo | −0.0025 (ns) | **−0.0081** (p 1.9e-5) |
| dinov3 | geom | **+0.0016** (p 5.8e-4) | +0.0014 (p 1.1e-2) |

Il vantaggio di siglip2 sulla **composizione sparisce** e il pareggio sulla
**topologia diventa sconfitta significativa**. Regge solo la geometria vs dinov3.
`dinov3` vs `dinov2` sul test: **tutto ns dopo Holm**.

**Causa: drift valid→test asimmetrico.** siglip2 comp −0.0034 / topo −0.0061;
dinov2 +0.0007/−0.0010; dinov3 −0.0002/−0.0005. Il margine con cui siglip2 era
stato scelto (≈0.004) è **dello stesso ordine del suo drift fra split**: era in
buona parte rumore dello split di validazione, non un'proprietà del modello.

**Conclusione (smentisce §13.1 nella parte narrativa, non nel numero):** le tre
varianti di testa sono **equivalenti entro il rumore**; nessuna è "la migliore".
Il numero primario resta `siglip2/mean/whiten` **perché pre-registrato in §13.1
prima di vedere il test**, non perché vinca.

⚠️ **Debito metodologico**: ora sul test ci sono 3 varianti. Non invalida il
primario (scelta documentata e datata prima), ma **il report deve dichiararle
tutte e tre** e dire che il primario era pre-registrato. Riportarne una sola
sarebbe cherry-picking. Da qui in avanti ogni ulteriore variante sul test
peggiora il bilancio: fermarsi a queste tre.

---

## 15. Complementarità vision↔graph e baseline D.0 (9 ago, dai `ret_rows`)

Analisi **post-hoc dai file per-query**, nessun job lanciato. ⚠️ Calcolata sui
file di **test**: è **esplorativa**, non un risultato pre-registrato. La scelta
della coppia va rifatta sul valid (per il graph i per-query del valid **non
esistono**: serve `04_perquery_graph.sh` con `eval.split=valid`).

**I due rami recuperano piante quasi disgiunte.** Top-10 per query, join per
nome: **Jaccard 0.036**, in media **0.60/10** piante in comune, e nel **67.8%**
delle query **zero** risultati condivisi. La diversità c'è, ed è enorme.

**Ma la diversità è utile su UN solo asse.** Oracolo per-query (scegliere per
ogni query il ranking migliore dei due) su `siglip2/mean/whiten` + `gcn/tau02`:

| asse | vision | graph | oracolo | guadagno | query in cui vision > graph |
|---|---|---|---|---|---|
| composition | 0.8259 | 0.9722 | 0.9728 | +0.0006 | **2.0%** |
| topology | 0.6537 | 0.8258 | 0.8288 | +0.0030 | **6.0%** |
| geometry | 0.9356 | 0.9405 | 0.9485 | **+0.0080** | **40.5%** |

⚠️ **La premessa «il vision è forte dove il graph è debole» non regge**: il graph
non è debole da nessuna parte. Domina composizione e topologia — dove è un upper
bound **per costruzione**, essendo la GT derivata da `rType`/`rEdge` che sono il
suo input — ed è alla pari sulla geometria. **L'unico asse con complementarità
sfruttabile è la geometria.**

**La fusione funziona (baseline D.0).** RRF (k=60) sui nomi, ranking fusi e
rivalutati sulla gallery vision, asse geometria, 2000 query:

    vision 0.9356 · graph 0.9405 · **RRF 0.9437** · oracolo 0.9485

**+0.0032 sopra il miglior singolo**, batte entrambi nel **35.8%** delle query, e
resta **−0.0048 sotto l'oracolo** → una fusione pesata/supervisionata ha ancora
margine. È il primo numero reale di late fusion del progetto.

**Conseguenza per la scelta della coppia**: il vision da fondere **non** è il
migliore in composizione (inutile: il graph fa 0.9722 e `hist` 0.9998) ma il
migliore in **geometria** → `ijepa/gem/whiten` (0.9473 sul valid), non
`siglip2/mean/whiten` (0.9356). Lato graph: `gcn/tau02` per il sistema completo,
ma il miglior graph in geometria è **`gat_nosym` (0.9464)**, non gcn.

---

## 16. VALID per-query del ramo graph (10 ago) — 7 run, gallery intera

`results/perquery/graph_test/*_full_valid.npz`, scritti il 10 ago 10:35-10:48.
Colma il buco dichiarato in §15 (per il graph i per-query del valid non
esistevano). **Appaiamento verificato**, non assunto: gallery `0c24cfc05e18`
(67.405) e `names` **identici** su tutti e 7 i file, `split=valid`, `mode=full`,
`exclude_self=True`, seed 42, 2000 query, `geometry_weights` uguali, e soprattutto
le query saltate **coincidono riga per riga** (6 sulla composizione, 311 sulla
topologia: dipendono dalla GT, non dal modello).

**nDCG@10 e frazione di spazio utile** (⚠️ floor = ranking casuale misurato sul
**test** §10, usato come proxy: il floor sul valid non è mai stato misurato):

| run | comp | util | topo | util | geom | util |
|---|---:|---:|---:|---:|---:|---:|
| `hist` (training-free) | 0.9999 | 100%\* | 0.6428 | 33% | 0.8927 | 18% |
| `gat/base` | 0.9281 | 72% | 0.6997 | 44% | 0.9381 | 53% |
| `gat/nosym` | 0.9085 | 65% | 0.7441 | 52% | **0.9453** | **58%** |
| `sage/base` | 0.9372 | 76% | 0.7304 | 50% | 0.9336 | 49% |
| `sage/nd01` | 0.9421 | 78% | 0.7622 | 55% | 0.9342 | 50% |
| `gcn/base` | 0.9677 | 88% | 0.7940 | 61% | 0.9391 | 53% |
| **`gcn/tau02`** | **0.9741** | **90%** | **0.8298** | **68%** | 0.9408 | 55% |

\*oracolo per costruzione.

**Le tre ablation OFAT sono confermate con test appaiato** (Wilcoxon + bootstrap
10k, Holm sui 3 assi). Tutte e tre comprano topologia, con delta simili:
`tau02−base` **+0.0358** [+0.0335,+0.0382], `nosym−base` **+0.0444**
[+0.0403,+0.0485], `nd01−base` **+0.0318** [+0.0294,+0.0344]; p Holm ≤ 8e-82.
⚠️ Le tre varianti sono **ritorni allo stato precedente** (τ 0.2, `node_drop`
0.1, flip/rot spente): le tre modifiche del 28 lug restano quindi smentite anche
a gallery intera. Sulla sonda i delta erano +0.030/+0.012/+0.031 → **la sonda
sottostimava gat** (+0.012 vs +0.044 reale), gli altri due sono quasi identici.

**`nosym` è l'unico trade-off vero**: paga −0.0196 di composizione (−7.5% dello
spazio) per +0.0444 di topologia e +0.0073 di geometria — e resta il **miglior
geometria del ramo**, battendo `gcn/tau02` di 0.0045 (p 6.7e-24). Conferma la
scelta della coppia per D.0 indicata in §15, ora **sul valid** come richiesto.

**`gcn/tau02` domina tutto il resto**: vs `sage/nd01` +0.0320/+0.0676/+0.0066, vs
`gat/nosym` +0.0656/+0.0857/−0.0045, tutti p ≤ 2e-24. **Nessuna ambiguità di
scelta sul ramo graph** (a differenza del vision, §13/§14.1): l'unico asse che
perde è la geometria, dove il divario vale 3.5% dello spazio utile.

**Contro `hist`**: comp −0.0259 (l'oracolo), topo **+0.1870** (+35% dello
spazio), geom **+0.0481** (+37%). Sulle metriche d'ordine il divario topologico è
di un altro ordine: **mAP@10 0.3508 vs 0.0148 (24×)**, Recall@10 0.4117 vs
0.0464 (8.9×). ⚠️ `significance` marca questi due come non affidabili perché
coprono 1689/2000 query (84.5% < 90%): l'avviso riguarda la **copertura**, non
l'appaiamento — le 311 query escluse sono le stesse in tutti i file (singleton
topologici). Il claim vale per l'84,5% delle query, e le escluse sono
plausibilmente le più difficili.

**Bias di selezione stimato.** Confronto cella per cella col test già pubblicato
(§3, job 74885-74887/74931-74933; il test **non** è stato riaperto): il valid è
sopra di **+0.001…+0.006** su comp/topo e di ±0.001 sulla geometria, su tutte e 6
le run. È l'entità dell'overfitting da selezione con la probe: piccola, di segno
costante, e da dichiarare nel report.

**Aperto:** il floor sul **valid** non esiste (le % di spazio utile sopra sono
approssimate); e la geometria separa i modelli di appena 0.0117 fra il peggiore e
il migliore (9% dello spazio) → su quell'asse la classifica interna al ramo è
quasi priva di potere discriminante.

---

## 17. Tre encoder vision nuovi (11-13 ago) — implementati, **zero numeri**

Estensione del ramo vision da 5 a **8 encoder registrati**. Nessuno dei tre ha
ancora un embedding su disco: qui c'è solo ciò che è stato **misurato in smoke
test CPU** e le decisioni prese. Finché non gira `01_extract_raw.sh`, ogni
confronto con i 5 storici è vuoto.

| Nome | Checkpoint | D | Provenienza | Risoluzione |
|---|---|---|---|---|
| `tipsv2` | `google/tipsv2-b14` | 768 | `transformers` + `trust_remote_code` | nativa **448**, 224 legale |
| `pecore` | `vit_pe_core_base_patch16_224.fb` | 768 (1024 su `natural`) | **timm** | **224 bloccata** |
| `pespatial` | `vit_pe_spatial_base_patch16_512.fb` | 768 | **timm** | nativa 512, default **224** |

Tutti e tre apache-2.0 e **non gated** (a differenza di DINOv3).

**Decisioni.**
1. **TIPSv2 gira a due risoluzioni** (448 nativa + 224 come gli altri): la
   risoluzione entra nel nome della variante (`tipsv2/natural448`), altrimenti le
   due estrazioni si sovrascrivono. Meccanismo generale in `_common.sh`
   (`resolutions_for`), i 5 encoder storici restano a variante = pooling e i loro
   comandi sono **invariati** (verificato: 98/98 identici).
2. **PE-Core e PE-Spatial si caricano da timm**, non da `transformers`: i repo
   `facebook/PE-*` pubblicano un `.pt` grezzo utilizzabile solo col pacchetto
   `perception_models` di Meta.
3. **PE-Spatial: scelta la B16-512, non la G14-448.** Misurato: la gigantic ha
   **0 prefix token** → nessun CLS, `natural` collasserebbe su `mean` e la
   griglia perderebbe una colonna. La B16 è anche la **coppia controllata** di
   `pecore` (stesso ViT-B/16, stessa norm. 0.5×3): l'unica variabile che cambia è
   l'obiettivo di training, contrastivo vs denso.

**Due claim del pretrained_cfg smentiti dalla misura.**
- PE-Spatial `fixed_input_size=True` **non** blocca la risoluzione: timm
  ricampiona il `pos_embed` (1025 → 197 token da 512 a 224) e il CLS a 224
  correla 0.956 con quello a 512 → default 224, allineato alla griglia.
- PE-Spatial `model(images)` **non** è il pooling naturale: con
  `global_pool="avg"` è la media dei patch (cos 1.0000 con la media esplicita).
  Usarlo per `natural` avrebbe reso `natural ≡ mean` **senza errori**, cioè una
  colonna della griglia sprecata in silenzio.

**Effetto sulla griglia (attenzione).** `select_models` in `_common.sh` elenca
ora **8** nomi (`pespatial` incluso dal 13 ago, §19): le feature RAW passano da
14 a **26** e `02_perquery_vision_valid.sh` lanciato **senza argomenti** da 56 a
**104 run**, che **riscrivono** i .npz già prodotti (§13). Va sempre lanciato
con l'encoder esplicito.

**Aperto:** l'ablation 448 vs 224 di TIPSv2 e il layer intermedio di PE-Core
(il paper sostiene che le feature migliori non sono all'ultimo layer) si
decidono **sul valid**, non sul test. → 448 vs 224 **chiuso** in §18.

---

## 18. VALID per-query di `tipsv2` e `pecore` (13 ago) — 18 run nuove

`results/perquery/vision_valid/`, file del 13 ago 10:34-11:24. **tipsv2**: 12 run
(3 pooling × {224, 448} × {raw, whiten}); **pecore**: 6 (3 pooling × {raw,
whiten}); **`pespatial`: zero, non ancora estratto**. Nessuna variante `head`:
quelle esistono solo per i 5 encoder storici. La cartella passa a **74 run**.

**Appaiamento verificato**: gallery `22d91dcf` (67.453), `split=valid`, seed 42,
2000 query — **firma identica alle 56 della §13**, quindi i confronti con lo
storico sono appaiati senza riserve e i vecchi `.npz` non sono stati riscritti.

### 18.1 TIPSv2 è il primo salto reale della griglia vision

Migliore assoluto **`tipsv2/gem448/whiten` = 0.8433 / 0.6896 / 0.9347**. Batte
tutti sui due assi non saturi; la geometria resta a `ijepa/gem/whiten` (0.9473).

| A = `tipsv2/gem448/whiten` vs | comp | topo | geom |
|---|---|---|---|
| `siglip2/mean/whiten` (variante del test) | **+0.0140** | **+0.0297** | −0.0013 |
| `ijepa/gem/whiten` (miglior geometria) | **+0.0204** | **+0.0446** | −0.0126 |
| `tipsv2/gem224/whiten` (risoluzione) | **+0.0095** | **+0.0171** | −0.0013 |

Tutti con CI 95% che esclude 0 e p Holm ≤ 2e-5. Il +0.0297 di topologia è
**dieci volte** il margine che in §13.1 separava i tre candidati di testa
(+0.0024, non significativo): è il primo delta vision che non è rumore.
Massimi per asse aggiornati: comp `tipsv2/mean448/raw` **0.8509** (era
`siglip2/natural/head` 0.8353) · topo `tipsv2/gem448/whiten` **0.6896** (era
`dinov3/natural/whiten` 0.6623) · geom `ijepa/gem/whiten` 0.9473 **invariato**.

**Tre effetti misurati dentro tipsv2.**
1. **448 > 224 sistematico** su comp (+0.0065…+0.0138) e topo
   (+0.0115…+0.0200) in **6 coppie su 6**, geometria piatta (±0.004). La
   risoluzione nativa del checkpoint vale più di qualunque scelta di pooling
   → l'ablation della §17 è chiusa: **si usa 448**.
2. **Il whitening qui è uno scambio, non un regalo**: +0.0193 topo ma −0.0069
   comp e −0.0046 geom. Diverge dal pattern §13 (whiten migliore su tutto in
   14/14): il massimo di composizione è una run **`raw`**.
3. **`gem` > `mean` > `natural`(CLS)** a 448+whiten su tutti e tre gli assi
   (+0.0021…+0.0049, CI esclude 0). Piccolo ma coerente.

### 18.2 PE-Core sta sotto la media, ma misura il whitening

Migliore `pecore/mean/whiten` = 0.8264 / 0.6517 / 0.9342: **perde su tutti e tre
gli assi** contro `siglip2/mean/whiten` (−0.0029 / −0.0082 / −0.0018, p Holm
≤ 2.1e-5). Le sue tre run `raw` sono le **peggiori delle 74** (`mean/raw`
0.8058 / 0.5758 / 0.9108).

Da qui l'unico risultato interessante: su `pecore` il whitening vale
**+0.0205 / +0.0759 / +0.0234** — l'effetto più grande del benchmark (media §13
sulle 14 coppie: +0.0305 sulla topologia). Interpretazione, **non verificata**:
lo spazio contrastivo CLIP-like di PE-Core è fortemente anisotropo e senza
decorrelazione poche direzioni dominano il coseno.

### 18.3 Frontiera di Pareto e ricadute

**12 run non dominate su 74** (erano 14 su 56): **4 sono tipsv2**
(`gem448/whiten`, `gem224/whiten`, `gem448/raw`, `mean448/raw`), le altre 8 sono
`ijepa` (6) e `dinov3` (2). **siglip2 e dinov2 escono dalla frontiera**; pecore
non ci entra mai. La curva di scambio resta la stessa della §13 — geometria ↔
(composizione+topologia) — ma con un estremo nuovo e più alto.

Spazio utile sopra il floor **costante** (0.7690/0.4960/0.8729, §10, misurato sul
test come proxy): `tipsv2/gem448/whiten` = 32.2% / **38.4%** / 48.6% contro il
33.0% di topologia del miglior storico.

⚠️ Sul floor citato dalla §13 vedi la rettifica in **§18.4**.

**Complementarità per D.0** (per-query, stesse 2000 query): `tipsv2/gem448/whiten`
vs `ijepa/gem/whiten` correlano **r = 0.654 sulla geometria** (la più bassa
misurata) e ijepa vince su **74.9%** delle query di quell'asse pur essendo dietro
sugli altri due. È la coppia più complementare disponibile nel ramo vision.
⚠️ L'oracolo per-query (0.9503 geom, +0.0030) è il tetto di un **selettore**
per-query, non della fusione a punteggi: non è un bound su RRF.

### 18.4 Il floor costante: due numeri veri, due grandezze diverse (13 ago)

**Causa trovata, nessun numero inventato.** `random_floor.py` produce due
artefatti che *non contengono la stessa cosa*:

- il **`.txt`** (`print_floor_table`, `:430`) stampa la **media sui 5 ranking
  seed** → costante vision @10 = **0.7690/0.4960/0.8729** (= §10);
- il **`.npz`** (`recorder.write`, `:434`) salva le per-query del **solo primo
  seed**, `run_tag=constant_floor/seed0` → **0.7942/0.5144/0.8703**, cioè
  esattamente i valori della §13. Verificato ricalcolando dal file.

La §10 ha letto il `.txt`, la §13 il `.npz`. Entrambe corrette, mai confrontate.

**Perché il difetto è invisibile sul null `random` e feroce sul `constant`**: nel
random ogni query ha un sorteggio suo, i 2000 si mediano e il seed sparisce
(seed0 0.7396 vs media 0.7388, mc_std 0.0007). Nel costante il sorteggio è **uno
solo, condiviso da tutte le query**: la mc_std sale a 0.025 sulla composizione
(già notato in §10.4) e il seed 0 è una realizzazione a **+1 mc_std** esatto.

**Effetto sul denominatore** (asse composizione, best 0.8353): floor seed0 →
20.0% di spazio utile; media 5 seed → 28.7%; media −1 mc_std → 35.7%; floor
`random` → 36.9%. **±1 sorteggio = ±8 punti percentuali.**

**Meccanismo dell'ambiguità sul disco**: `random_floor.py:433` mette il seed nel
nome di default (`..._seed0.npz`), ma `01_random_floor.sh:75` passa `--out
results/random_floor/<null>_<ramo>_test.npz` e **lo toglie**. Il file su disco non
dichiara di essere un seed solo (lo dicono solo il `run_tag` nel meta e il
commento `:23` dello script).

**Decisione da prendere (A.5-adiacente, blocca le percentuali del report).**
Raccomandato: **denominatore = floor `random`** (mc_std 0.0007 → percentuali
stabili e riproducibili), e null `constant` riportato **sempre come media ±
mc_std sui 5 seed**, nel suo ruolo proprio — dire se un asse discrimina — mai
come singolo numero al denominatore. In alternativa si tiene il costante come
denominatore, ma allora va scritta accanto la banda ±1 mc_std, perché una
percentuale con ±8 punti di rumore non è riportabile da sola.
⚠️ Il seed 0 non è una scelta conservativa: alza il floor su comp/topo e lo
**abbassa** sulla geometria (0.8703 < 0.8729). Sbaglia in due direzioni.

**Aperto, costo zero se accorpato**: i floor esistono **solo sul test** e i
confronti sul valid li usano come proxy (§11, §13, §18). Se si decide di
misurarli anche sul valid, è quel momento — e solo quello — che conviene
rimettere il seed nel nome del `.npz` in `01_random_floor.sh` (una riga, ma tocca
`scripts/**` e i path già citati in `COMANDI.md`: serve mandato esplicito).

---

## 19. `pespatial` in griglia ed estratto (13 ago) — **zero numeri letti**

Chiude la parte implementativa aperta in §17. Due decisioni e due job, nessuna
metrica: i `.npz` esistono ma **non sono stati aperti** (artefatti pesanti,
serve l'ok dell'utente). Tutto ciò che segue è metadato di filesystem.

**Decisione 1 — `pespatial` entra in `select_models`** (`_common.sh:14`), a
**224 soltanto**: la variante 512 resta fuori per scelta esplicita, quindi
`resolutions_for` e `poolings_for` lo lasciano al caso di default (`native`, 3
pooling — il CLS c'è, a differenza della G14 scartata in §17). Effetto
verificato simulando i loop: feature RAW **23 → 26**, griglia valid senza
argomenti **92 → 104** run.

**Decisione 2 — primo giro solo `frozen`.** Il gruppo `head` caricherebbe un
`head.pt` che per `pespatial` non esiste: quelle 6 run fallirebbero.

**Artefatti su disco.**

| Cosa | Evidenza |
|---|---|
| RAW, 3 varianti | `embeddings/vision/pespatial/{natural,gem,mean}/`, 13 ago 11:39-11:58 |
| forma | 207.215.744 B = header 128 + **67.453 × 768 × 4** → gallery intera, 768d su tutti e tre i pooling (come atteso da §17) |
| valid per-query | 6 `.npz` `vision_pespatial_<pool>_{raw,whiten}_full_valid.npz` → la cartella passa da 74 (§18) a **80** |

**Non verificato**: i valori delle metriche, e l'appaiamento (firma gallery /
seed / n. query) che in §18 era stato controllato per `tipsv2` e `pecore`.
Vanno letti prima di qualunque confronto con la griglia storica.

**Ipotesi da falsificare quando si leggeranno** (scritta *prima*, per non
adattarla al risultato): `pespatial` è la coppia controllata di `pecore` —
stesso ViT-B/16, stessa norm., stessa risoluzione 224, cambia **solo**
l'obiettivo di training (contrastivo → denso). Se l'allineamento denso serve al
retrieval di planimetrie, `pespatial` deve battere `pecore` **sulla geometria**,
che è l'unico asse non circolare (`CLAUDE.md`, vincolo 5). Un vantaggio solo su
composizione/topologia non sosterrebbe la tesi.
