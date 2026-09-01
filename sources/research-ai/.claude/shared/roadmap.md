# Roadmap — i sei obiettivi, ordinati per dipendenza

Piano di medio periodo. **Non** è lo stato: quello sta in `.claude/TODO.md`
(fase attiva) e in `.claude/shared/status.md` (risultati). La diagnosi che
motiva la fase A è in `current_state.md` (root).

Gli ID `O1…O6` sono quelli dell'utente e restano invariati; le **fasi** sono
l'ordine di esecuzione, che è diverso.

| ID utente | Obiettivo | Fase |
|---|---|---|
| O1 | Sistemare le incoerenze metodologiche (riconfermandole una per una) | **A**, **B** |
| O2 | Nuovi encoder vision: TIPS-v2, Perception Encoder (PE Core, PE Spatial) | **C** |
| O3 | Adattare l'architettura a ResPlan e CubiCasa5K (conversione immagini↔`.mat`) | **A′** (studio) → **E** (implementazione) |
| O4 | Masking: crop arbitrario + masking a livello di patch | **C** |
| O5 | Far comunicare le due pipeline **prima** degli embedding finali | **D** |
| O6 | Report da 10 pagine + 2 di reference, struttura CVPR | **A′** → continuo |

## Il principio d'ordine (perché non 1→6)

Tre regole hanno deciso la sequenza:

1. **Prima si aggiusta il metro, poi si misura.** Ogni obiettivo che produce
   numeri (O2, O4, O5) passa attraverso il protocollo di valutazione. Finché il
   protocollo sceglie sul test e non ha intervalli di confidenza, aggiungere due
   encoder significa produrre **due righe di numeri non difendibili** invece di
   una. O1 non è "debito tecnico": è il prerequisito di O2, O4 e O5.
2. **Baseline prima della complessità.** O5 (fusione intermedia) non può essere
   valutata senza la **late fusion** come denominatore — che oggi non esiste
   ancora, benché gli embedding siano già salvati e allineati.
3. **Il report non è l'ultimo passo, è il primo.** Lo scheletro di O6 decide
   *quali* esperimenti devono esistere e quali figure servono. Scritto alla fine,
   costringe a rifare run per tappare i buchi; scritto ora, guida le run.

Dipendenze essenziali:

```
A (metro) ──┬─> B (ri-valutazioni) ──┬─> C (O2 encoder, O4 masking) ──> D (O5 fusione)
            │                        └─> "config congelata per ramo" (serve a D)
A′ (studio) ┴─> E (O3 dataset)            A′ (report) ─── continuo ───> O6
```

---

## Fase A — Rimettere in sesto il metro (nessuna GPU)

**Perché adesso:** tre misure a costo quasi zero cambiano il *significato* di
tutti i numeri già ottenuti. Senza queste, non si sa nemmeno se le differenze
esistono.

1. **Riconfermare i rilievi uno per uno** prima di toccarli (richiesta esplicita
   dell'utente): vedi la tabella *Riconferma obbligatoria* più sotto. Un rilievo
   non riconfermato non si affronta.
2. **Misurare il floor**: nDCG per-asse di un ranking casuale. Dà una scala a
   tutto (un descrittore cieco alla geometria prende già 0.894).
3. **Salvare i valori per-query** in valutazione e implementare il **test
   appaiato** (Wilcoxon signed-rank o bootstrap appaiato sulle differenze). Per
   gli assi discreti, appaiare solo le query sopravvissute allo skip singleton in
   **entrambe** le run.
4. **Sensibilità ai pesi** della similarità geometrica: tre componenti da sole +
   2-3 pesature alternative. Se l'ordine vision/graph si ribalta, il claim di
   punta va abbandonato.
5. **Definire "migliore"** in modo operativo, perché O5 lo richiede:
   - *risultato più alto* = nDCG@10 sull'asse debole del ramo, senza perdere gli
     altri due, misurato sul **valid** con test appaiato;
   - *più robusto* = degradazione più piatta sotto masking crescente;
   - **decidere quale dei due** vince a parità, e scriverlo prima delle run.

**Completa quando:** floor misurato, test appaiato disponibile e applicato ai
confronti già in tabella, sensibilità nota, definizione di "migliore" scritta in
`status.md`.

## Fase A′ — In parallelo, costo quasi nullo (nessuna GPU)

Indipendente da A: si può fare mentre A gira.

1. **O6 — scheletro del report.** ✅ *fatto il 30 lug*: struttura estratta da
   `papers/examples/pippo_paper.pdf` (CVPR 2025) e lista di 6 figure + 4 tabelle
   in **`PAPER.md § 10`**, con la run che produce ciascuna. Resta da fare: il
   lavoro sui grafici secondo **`notebooks/CHARTS.md`** (infrastruttura P0 →
   correzioni P0 → 21 grafici nuovi; strategia: **produrne molti, curare dopo**)
   — ⚠️ prima di scrivere codice di grafici, caricare la skill `dataviz`; e la
   stesura del testo, che aspetta i numeri della fase B.
2. **O3 — studio di fattibilità sulla conversione, senza scrivere codice.**
   Domande da chiudere: che cosa contengono esattamente `.mat` di RPLAN vs le
   annotazioni di ResPlan e CubiCasa5K (vettoriale SVG per CubiCasa); quali dei
   campi che il progetto usa (`rType`, `rEdge`, `gtBox`, `gtBoxNew`) sono
   **ricostruibili** e quali no; se la conversione immagine→`.mat` richiede un
   modello di parsing (allora è un progetto a sé) o è deterministica dalle
   annotazioni esistenti. **Esito atteso: una raccomandazione andare/non andare**,
   con il costo. Se la risposta è "serve un parser addestrato", O3 esce dalla
   roadmap di questo report e diventa lavoro futuro.
3. **Verificare disponibilità degli encoder di O2** prima di pianificarli: pesi
   pubblici, licenza, dimensione, interfaccia (`transformers` o repo proprio),
   VRAM. ⚠️ Nessun dettaglio su TIPS-v2 e Perception Encoder va dato per noto: si
   legge la documentazione ufficiale in sessione.

**Completa quando:** indice + lista figure esistono; raccomandazione su O3
scritta; schede dei tre nuovi encoder verificate (o dichiarate non disponibili).

## Fase B — Ri-valutazioni con il protocollo corretto (GPU, nessun retraining)

Tutte ri-valutazioni: gli embedding RAW non si ricalcolano.

1. **Griglia vision su `eval.split=valid`**, scelta lì, poi test **una volta
   sola** per la vincente (chiude il rilievo alto sulla selezione su test).
2. **Whitening fittato sul solo train** e misura della differenza rispetto al
   trasduttivo attuale: si sceglie un protocollo e si usa in entrambi i rami.
3. **Gallery ristretta all'inner join** dei nomi condivisi, per rendere appaiato
   il confronto cross-ramo.
4. **Partial con `exclude_self=True`** sulle metriche per-asse, per avere la curva
   di degrado confrontabile col full (il self-recovery resta con il self dentro:
   è il suo task).
5. **I quattro smoke test** che oggi mancano (allineamento riga↔nome, contratto
   checkpoint↔`raw_skip`, valori di riferimento delle metriche, disgiunzione
   split + statistiche dal train). Proteggono tutte le fasi successive.
6. **Head vision riallenata con selezione su probe di retrieval** (unico
   training di questa fase, ed è solo la testa) → dice se «sul full la head non
   aiuta» era una conclusione o un artefatto del criterio di selezione.
7. **Congelare una configurazione per ramo** ("la migliore" secondo la
   definizione della fase A): serve come base unica per C e D.

**Completa quando:** esiste una tabella finale per-asse, per entrambi i rami,
prodotta con: selezione sul valid, protocollo di normalizzazione unico, gallery
identica, test appaiato riportato. È la tabella che va nel report.

## Fase C — Estendere, sul metro nuovo (GPU)

Le due estensioni sono indipendenti fra loro: si possono fare in parallelo.

**O2 — tre encoder in più.** TIPS-v2, PE Core, PE Spatial dentro il registry
esistente, stesso `BaseVisionEncoder`, stessi pooling. È lavoro in gran parte
meccanico: il valore sta nel fatto che il benchmark passa da 5 a 8 encoder e
include due famiglie nuove (un modello con supervisione testuale e uno con
supervisione **spaziale** densa). ⚠️ PE Spatial produce feature dense: verificare
se il pooling attuale è appropriato o se serve un pooling dedicato — e in quel
caso è una variabile in più, da isolare.

*Ipotesi da dichiarare prima:* il benchmark attuale dice che "più nuovo/più
grande" non vince, e attribuisce la cosa al domain gap. PE Spatial, essendo
addestrato con supervisione spaziale, è il primo candidato che *dovrebbe* rompere
questa regola sulla **geometria**. Se non lo fa, il domain gap è confermato più
solidamente di adesso.

**O4 — due tipi di masking nuovi.** Il masking attuale (riempimento bianco per
stanza, con bordo aperto) **resta** e diventa il termine di confronto.
1. **Crop rettangolare arbitrario**: quadrato/rettangolo bianco di dimensione e
   posizione arbitrarie, **non allineato alle stanze**. Serve a separare due cose
   che oggi sono confuse: la robustezza a *stanze mancanti* (degrado semantico) e
   la robustezza a *occlusione* (degrado puramente visivo).
2. **Masking a livello di patch**: mascherare i token dopo il patch embedding.
   *Interpretazione* del requisito, da confermare con i prof: si intende
   l'occlusione nello spazio dei token, non nei pixel.
   ⚠️ Due trappole di protocollo: (a) il numero di patch dipende dall'encoder
   (patch size e risoluzione diverse) → per confrontare encoder diversi si fissa
   la **frazione di area mascherata**, non il numero di token; (b) va deciso e
   dichiarato se i token mascherati sono *rimossi* dalla sequenza o *sostituiti*
   da un token appreso/nullo: sono due esperimenti diversi.
3. Ogni strategia va confrontata **a parità di frazione di area rimossa**,
   altrimenti le curve non sono comparabili.

**Completa quando:** benchmark a 8 encoder sul protocollo della fase B; curve di
degrado per le tre (quattro) strategie di masking a parità di area.

## Fase D — O5: far comunicare le pipeline (GPU)

Il punto più ambizioso, e quello con più modi di fallire in silenzio. Vincolo
d'ingresso: **una configurazione congelata per ramo** (fase B.7) e la definizione
di "migliore" (fase A.5).

**D.0 — la baseline, prima di tutto.** Late fusion sugli embedding già salvati:
`[√α·v ; √(1−α)·g]` con α scelto **sul valid**, inner join sui nomi. Va misurata
*e* va misurato l'**upper bound oracolo** (per query, il migliore dei due rami):
dice quanto margine esiste davvero. Senza questo numero, qualunque guadagno della
fusione intermedia non è interpretabile.

**D.1 — dove comunicare, in ordine di costo crescente.** Da valutare come
alternative OFAT, non da implementare tutte:
- **a. Fusione a livello di score** (α sui punteggi invece che sui vettori):
  quasi gratis, a volte batte la concatenazione.
- **b. Testa di proiezione congiunta**: una testa allenata con InfoNCE che vede
  entrambe le rappresentazioni e le proietta in uno spazio comune. Nessun
  cambiamento agli encoder.
- **c. Distillazione asimmetrica**: il ramo forte insegna al debole sull'asse in
  cui è forte (il graph sulla topologia, il vision sulla geometria) tramite una
  loss ausiliaria su un livello intermedio. È la risposta più diretta a
  "migliorare i risultati che peccano nella pipeline stessa".
- **d. Cross-attention fra token vision e nodi del grafo** prima del pooling: la
  più promettente e la più costosa; introduce parametri nuovi e va confrontata
  con (b) a parità di parametri, altrimenti si misura la capacità, non la
  comunicazione.

**Trappola da scrivere ora**: qualunque comunicazione che porti `rType`/`rEdge`
dentro il ramo vision **importa anche la circolarità** del ramo graph. Un
guadagno su composizione/topologia ottenuto così non è un guadagno di visione:
va dichiarato, e l'unico asse su cui il confronto resta informativo va deciso
insieme alla questione della circolarità.

**Completa quando:** late fusion + oracolo misurati; **una** variante intermedia
scelta e misurata contro entrambi, con test appaiato e lettura per-asse.

## Fase E — O3: multi-dataset (solo se lo studio A′.2 dà via libera)

Ordine consigliato, dal meno rischioso: **CubiCasa5K** prima (annotazioni
vettoriali → i campi tipo/adiacenza/box sono plausibilmente derivabili), poi
**ResPlan**. Requisiti minimi per dichiararlo fatto:
1. Un adattatore che produca la stessa struttura di `RoomMeta`, in modo che
   `relevance.py` e `metrics.py` funzionino **as-is** (se serve toccarli, il
   contratto è sbagliato).
2. La verifica che la tassonomia dei tipi di stanza sia mappabile su quella di
   RPLAN, o una mappatura dichiarata con le sue perdite.
3. **Cross-dataset retrieval** come esperimento vero e proprio (query da un
   dataset, gallery dall'altro): è il test di generalizzazione che il report
   merita, e l'unico modo di dimostrare che il metodo non è RPLAN-specifico.

## Continuo — O6: il report

Cresce insieme ai risultati, non alla fine. Budget indicativo: **10 pagine + 2 di
reference**. Regole di lavoro:
- ogni fase che chiude aggiorna la sezione corrispondente **subito**;
- ogni tabella o figura del report dichiara la run che l'ha prodotta;
- i caveat (circolarità, whitening, selezione, gallery) vanno nel testo, non
  nascosti: sono ciò che distingue un report onesto da uno vendibile;
- le ipotesi **smentite** entrano nel report: qui hanno insegnato più delle
  conferme.

---

## Riconferma obbligatoria dei rilievi (fase A.1)

L'utente ha chiesto che ogni rilievo di `current_state.md` sia **riconfermato
singolarmente** prima di essere affrontato. Metodo minimo per i rilievi alti e
medi — se la riconferma **fallisce**, il rilievo si chiude come falso allarme e
si scrive in `status.md`:

| Rilievo | Come si riconferma |
|---|---|
| A1 selezione sul test | `grep -rn 'eval.split' scripts/` → esiste almeno uno script con `valid`? |
| A2 whitening trasduttivo | seguire il chiamante di `_fit_whitening` e verificare che l'insieme passato non sia filtrato per split |
| A3 head su val-loss | leggere il blocco di early stopping e verificare che non esista un criterio alternativo dietro un flag |
| A4 nessuna incertezza | `grep -rn 'std\|bootstrap\|wilcoxon\|ttest' src/` → deve essere vuoto |
| A5 circolarità geometrica | verificare che `type_area_distribution` sia calcolabile dalle feature dei nodi; **e** ispezionare le PNG: il colore codifica `rType`? |
| A6 metrica fatta a mano | leggere `geometry_sim` e confermare che i pesi non vengano da nessuna config |
| A7 test senza assert | `grep -c assert tests/*.py` |
| B1 config ≠ vincente | leggere i tre YAML e la tabella delle varianti in `03_train_gnn.sh` |
| B2 gallery diverse | contare i nomi nei due json (non gli embedding) |
| B3 partial exclude_self | verificare che le righe passate alle metriche per-asse siano le stesse del self-recovery |
| B4 ponte booleani | aggiungere una chiave booleana finta a una **copia** del YAML e rieseguire il ponte |
| B5 `raw_skip` | costruire l'encoder con e senza il flag e confrontare la forma di `proj` |
| B6 clamp / `reduce="mean"` | il comando su `graphs.pt` già scritto in `current_state.md § B6` |

I rilievi minori (C1-C6) non richiedono riconferma formale: sono verificabili a
vista nella riga citata.

## Domande aperte che vanno decise da una persona, non da un agente

1. **Circolarità**: come si presenta il confronto fra i rami, dato che nessun
   asse è esente? (blocca la narrazione del report)
2. **Whitening**: si dichiara trasduttivo per entrambi i rami, o si passa a
   train-only per entrambi? (cambia i numeri già in tabella)
3. **"Migliore"** = più alto o più robusto? (blocca la fase D)
4. **O3**: si entra nel multi-dataset in questo report o si rimanda? (dipende
   dalla raccomandazione di A′.2)
5. **Masking a patch**: token rimossi o sostituiti? Da chiedere ai prof insieme
   alla conferma dell'interpretazione.
