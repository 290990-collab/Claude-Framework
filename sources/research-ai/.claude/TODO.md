# TODO — stato operativo vivo

**Ultimo aggiornamento:** 13 ago 2026 — `tipsv2` e `pecore` estratti e valutati
sul valid: **`tipsv2/gem448/whiten` è il nuovo migliore vision** (§18). Ora
anche `pespatial` è estratto e valutato, ma i suoi 6 `.npz` sono **da leggere**.

> **Primo** file a inizio sessione, **ultimo** a fine task: dice dove siamo
> *adesso*. Regole in `CLAUDE.md § Stato che si aggiorna da solo`. Tetto ~60
> righe: si comprime prima di aggiungere, la traccia va in `status.md`.

## In corso

**Piano dei sei obiettivi: `.claude/shared/roadmap.md`** (ordine per dipendenza,
non 1→6). Qui solo la fase attiva.

- [x] **Fase A.1-A.4 chiusa** (30-31 lug) — riconferme 11/13, floor misurato,
      strumenti in `src/evaluation/` + 16 test → `status.md §8-10`. Criterio A.4
      **fissato prima**: il claim geometria regge se in tutte e 6 le pesature il
      segno del delta è invariato e il CI 95% esclude 0.
- [ ] **A.5 — definire "migliore"** (più alto vs più robusto): decisione umana,
      blocca la fase D.
- [x] **A1 ri-verificato (13 ago)** → `status.md §9.1`: risolto in pratica (si
      sceglie sul valid), **non nel codice**. 4 residui: `vision/{04..07}` ancora
      `eval.split=test` senza override; test letto 3 volte; l'oracolo per-asse
      **0.830/0.662/0.948** ancora citato in `CLAUDE.md` e §1 (sul valid la
      geometria è 0.9473); default dei due YAML non è `valid`.
- [ ] **Fase B — i fix** dei rilievi riconfermati (nessuno ancora applicato).
      Aperti dall'audit vision (`status.md §12`): `gem_pool` clampa il 50,7%
      delle componenti (tocca il 0.948 di `ijepa/gem/whiten`); register token
      DINOv3 dentro `mean`/`gem`; whitening fittato su tutta la gallery (viola
      «solo train»). Restano CPU: **M3** (geometria ricalibrata come variante di
      `geometry_variants`) e lo spettro PCA reale.
- [ ] **Fase A′ — costo ~zero, in parallelo.** ✅ scheletro report (`PAPER.md §10`).
      ✅ **3 encoder nuovi** (11-13 ago): `tipsv2`, `pecore`, `pespatial` →
      **`status.md §17`**. ✅ **valid per-query di tipsv2 (12 run) e pecore (6)**
      → **`status.md §18`**: `tipsv2/gem448/whiten` 0.8433/0.6896/0.9347 batte
      `siglip2/mean/whiten` di +0.0140 comp e **+0.0297 topo** (CI escludono 0);
      geometria ancora a `ijepa/gem/whiten` 0.9473. **448 > 224 in 6 coppie su
      6** → ablation §17 chiusa. `pecore` sotto siglip2 su tutti e tre gli assi.
  - ✅ **`pespatial` estratto e valutato** (13 ago, 3 RAW 67.453×768 + 6 run
    `frozen`) → **`status.md §19`**. ⚠️ **Zero numeri letti**: i `.npz` sono
    artefatti pesanti, serve il tuo ok. Da verificare anche l'appaiamento
    (firma gallery/seed/query), non ancora controllato come per §18.
    **Ipotesi scritta prima di leggere**: coppia controllata con `pecore`
    (stesso ViT-B/16, stessa norm., stessi 224px, cambia solo contrastivo →
    denso) → deve vincere **sulla geometria**, l'unico asse non circolare.
  - ⚠️ **Floor costante, causa trovata** (§18.4): il `.txt` dà la media sui 5
    seed, il `.npz` il **solo seed 0** — §10 e §13 leggevano file diversi.
    Nessun numero è sbagliato, ma sul costante ±1 sorteggio = **±8 punti** di
    "spazio utile". **Serve la tua decisione**: denominatore = floor `random`
    (raccomandato, mc_std 0.0007) o costante con banda ±mc_std dichiarata.
  - ⚠️ Griglia RAW ora a **26 feature**, tutte estratte (verificato simulando i
    loop + `ls` su `embeddings/vision/`): `02_perquery_vision_valid.sh` senza
    argomenti fa **104 run** (erano 56 pre-registrate) e **riscrive** i .npz già
    prodotti → lanciarlo sempre con l'encoder esplicito.
  - Nessuno dei 3 nuovi ha **head** né **partial**: nel report vanno con la
    colonna vuota, non mescolati ai 5 storici.
  - ⚠️ `scripts/evaluation/*` non ha `--constraint`: il valid può finire su un
    nodo Blackwell e crashare. Rilanciare, oppure estendere la whitelist.
  - Restano: studio O3 conversione immagini↔`.mat` → **andare/non andare**;
    grafici (`notebooks/CHARTS.md`, ⚠️ caricare la skill `dataviz`).

## In attesa dell'utente (job sbatch)

- [x] **griglia vision VALID completa 56/56** → `status.md §13`. ⚠️ Il miglior
      geometria è `ijepa/gem/whiten`, **non** dinov3 (che primeggia sul partial).
      **Nessun vincitore unico**: 14 run su 56 sono sulla frontiera di Pareto →
      è esattamente la decisione A.5.
- [x] **TEST vision (8-9 ago)** — primario pre-registrato `siglip2/mean/whiten`
      **0.8259 / 0.6537 / 0.9356** (`status.md §14`), poi 2 varianti in più: la
      selezione **non si replica** (§14.1). ⚠️ Il report deve dichiarare tutte e
      tre e dire quale era scelta prima. **Non lanciarne altre**: test a quota 3.
- [x] **graph per-query su TEST e VALID** — `gcn/tau02` domina senza ambiguità,
      `gat/nosym` miglior geometria (0.9453), appaiamento verificato → `§16`.
- [x] **vision per-query sul VALID**: la cartella ha **80** run (74 verificate
      appaiate — gallery `22d91dcf`, seed 42, 2000 query — **+6 di `pespatial`
      del 13 ago, appaiamento da verificare**). I candidati alla fusione ci sono
      tutti.

## Prossimo passo consigliato

**Coppia D.0 scelta sul valid**: il candidato vision è `tipsv2/gem448/whiten`
(+ `ijepa/gem/whiten` se si vuole la geometria: r = 0.654 per-query sull'asse,
la coppia più complementare del ramo — `status.md §18.3`). Contro
`graph gcn/tau02` serve `--allow-gallery-mismatch`, e resta imperfetto fino a
B.3. Decisione A.5 (più alto vs più robusto) ancora aperta e ancora bloccante.

## Bloccato / in attesa di decisione

Le 5 decisioni in `roadmap.md § Domande aperte`. Le urgenti: **circolarità**
(nessun asse è esente → blocca la narrazione del report) e **il colore delle PNG
codifica `rType`?** (se sì tocca anche il vision).

- [ ] **Due verifiche ferme**: serve l'ok sugli artefatti pesanti per **B6**
      (`graphs.pt`) e per la domanda sulle PNG (una PNG + il suo `.mat`). Idem
      per verificare M1/M2/M4a-b sui `.npz` reali (comando in `status.md §12`).
- [ ] **Committare il lavoro di luglio** (solo l'utente): finché non lo fai,
      `.claude/archive/CLAUDE-2026-07-29-full.md` è l'unica copia della
      cronologia di Fase 1. Dopo, l'archivio si elimina.
- [ ] **Re-indicizzare** `current_state.md` nella knowledge graph (rigenerata il
      30 lug, quindi anteriore all'audit).
- [ ] Due incoerenze note: `--constraint` anti-Blackwell ora su **10 script su
      16** (esteso ai vision il 13 ago); scoperti restano i 4 di
      `scripts/evaluation/` e `graph/0{1,2}`. E `graph/../axis_metrics.py:100`
      stampa ancora `Recall` (allineamento cross-ramo **da decidere**).
- [ ] Voci vecchie che la roadmap riassorbe: complementarità vision↔graph dagli
      embedding salvati = **baseline D.0**; `temperature: 0.2` nei YAML → **B1**;
      **partial** sul ramo graph → fase C.
