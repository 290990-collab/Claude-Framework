# Esperimenti — protocollo, ablation, operatività

Come si progetta, si lancia e si legge un esperimento qui. I **risultati** stanno
in `.claude/shared/status.md`; i **comandi completi** in `COMANDI.md` (root).

## Protocollo minimo

Un esperimento senza queste sei voci non si lancia:

1. **Ipotesi falsificabile** + **meccanismo atteso**, possibilmente **per-asse**
   ("mi aspetto che salga la topologia e *non* la geometria, perché…"). Una
   previsione per-asse rende informativo anche l'esito negativo.
2. **Baseline dichiarata** contro cui si misura. ⚠️ Il denominatore giusto
   spesso non è quello ovvio: qui la GNN a **pesi casuali** e l'add-pool delle
   feature grezze **senza rete** si sono rivelati riferimenti più onesti della
   baseline istogramma.
3. **Una variabile alla volta (OFAT)**. Più assi = più run, non un unico salto.
4. **Criterio di successo deciso prima**: quale metrica, quale asse, quale
   soglia — confrontata col rumore noto (sonda: σ ≈ 0.002-0.004).
5. **Selezione sul valid.** Le varianti si confrontano sulla **sonda**; il test
   si tocca solo per la vincente (o alla fine, per il report).
6. **Costo**: quanti job, quante ore, cosa si riusa invece di ricalcolare
   (embedding RAW, `graphs.pt`, render-cache, `pairs.npz`).

## Come si confrontano due numeri

- **Appaiato o niente**: stesse query, stessa gallery, stesse esclusioni.
  *Controllo pratico:* i conteggi di **query singleton escluse** stampati nei log
  devono coincidere (es. 10 su composizione, 313 su topologia).
- **Il riferimento è quello che credi?** ⚠️ Una cartella `save_dir` può essere
  stata **sovrascritta** da una run successiva con lo stesso `variant`: è già
  successo di misurare un "guadagno" contro una configurazione diversa da quella
  ipotizzata. Verifica data e config prima di concludere.
- **Scale non mescolate**: sonda (valid, gallery ridotta) e report finale (test,
  gallery intera) hanno **IDCG diverso** → non si confrontano fra loro. La sonda
  serve ai confronti *relativi*, che essendo su query **fisse** sono appaiati e
  quindi molto sensibili.
- **Criteri di selezione diversi = scale diverse**: una variante selezionata su
  `mean` e una su `topology` non si ordinano per `best_score`. Si confronta la
  **colonna dell'asse** che interessa.
- **Sempre per-asse**: composizione, topologia e geometria si muovono spesso in
  senso **opposto**. Una media che sale nascondendo un asse che crolla è una
  conclusione sbagliata.
- **Da 31 lug: due medie non bastano più.** Se la run ha salvato i per-query
  (`eval.perquery_dir` / `--perquery-out` / `PERQUERY_OUT`), il confronto si
  chiude con `python -m src.evaluation.significance --a A.npz --b B.npz --k 10`
  (Wilcoxon + bootstrap appaiato, join **sui nomi**). Rifiuta da solo i confronti
  non appaiati: gallery, split, `exclude_self`, seed e pesi devono coincidere.
  Il confronto vision↔graph richiede `--allow-gallery-mismatch` (67.453 vs
  67.405) e resta imperfetto finché non si restringe la gallery (fase B.3).
- **Un delta va sempre rapportato al floor**: `(score − floor)/(1 − floor)`.
  Sulla geometria lo spazio è 0.131, quindi 0.002 è l'1.5% — vedi
  `retrieval.md § Il floor`.

## Ablation (ramo graph)

`scripts/graph/03_train_gnn.sh` ha una tabella di **10 varianti OFAT**, ognuna
delle quali riporta indietro **un solo** pezzo rispetto al YAML:

```
base  noskip  nosym  nojitter  nd01  noaug  tau02  tau05  selmean  selgeom
```

```bash
sbatch scripts/graph/03_train_gnn.sh gcn ablation    # allena tutte le varianti di UN encoder
sbatch scripts/graph/04_eval_gnn.sh  gcn tau02       # valuta sul TEST solo la vincente
```

⚠️ **`COMANDI.md` (root) è l'unica fonte dei comandi**: forme complete,
dipendenze fra stage e lancio parallelo stanno lì e solo lì. Qui c'è il
*metodo*, non il ricettario.

- `--variant` è passato **dopo** i flag del YAML (argparse: vince l'ultimo) e
  namespacizza `save_dir` → le varianti non si sovrascrivono fra loro.
- In coda al job un **riepilogo** legge tutti i `training_summary.json` su disco
  e stampa la tabella encoder × variante.
- ⚠️ In **valutazione** contano solo i flag che cambiano l'**architettura** (il
  checkpoint si ricarica per costruzione): delle 10 varianti solo `noskip` lo fa
  (`--no-raw-skip`); per le altre basta `--variant`. La lista per `ablation` in
  `04` si legge **da disco** (cartelle con `encoder.pt`), così non ci sono due
  liste da sincronizzare e le varianti non allenate vengono saltate con un
  avviso.
- ⚠️ Una guardia in testa a `03` verifica che ogni nome in `ALL_VARIANTS` abbia
  una voce nella tabella dei flag e **esce con errore** altrimenti: senza, una
  lista incoerente produce un **successo apparente con una variante in meno**
  (è già successo: `selgeom` saltata, `seltopo` mai lanciata).

## Trappole operative (costate job veri)

Qui in ottica **preventiva**, prima di lanciare. La stessa casistica ordinata
per *sintomo osservato*, cioè quando qualcosa è già andato storto, sta in
`.claude/shared/debugging-playbook.md`: le due viste servono momenti diversi.

| Trappola | Cosa succede | Difesa |
|---|---|---|
| **`sage` invece di `graph_sage`** | Gli script vogliono il **basename del YAML**, non la chiave `encoder`. Con `sage` il path non esiste → encoder saltato con un avviso, job finito in 0 s che *sembra* riuscito | Usa `gcn`, `gat`, `graph_sage` |
| **GPU Blackwell sm_120** | PyTorch dell'env non la supporta: `no kernel image` al forward. ⚠️ Il percorso frozen può passare lo stesso e mascherare il problema | Constraint sbatch con allowlist di GPU (già in `03`, `04`, `vision/07`) |
| **`save_dir` sovrascritto** | Due run con lo stesso `variant` si sovrascrivono → confronto contro un riferimento che non è più quello | `variant` diverso per ogni punto di sweep |
| **Chiave YAML non tradotta** | Il ponte YAML→flag salta i booleani senza mapping esplicito → parametro **ignorato in silenzio** | Verifica sui 4 livelli (codice/argparse/YAML/ponte) |
| **Formato di un artefatto cambiato** | I vecchi `embeddings/` non sono più compatibili → vanno rigenerati (ore di GPU) | Dichiararlo prima, non dopo |
| **SLURM esegue una copia dello script** | Editare il file nel repo non altera i job già avviati (sicuro), ma un job in corso può girare con una versione diversa da quella che stai leggendo | Controllare l'orario di lancio |

## Riuso: cosa NON va mai ricalcolato

- **Embedding RAW vision** (`embeddings.npy`): una sola estrazione per (encoder,
  pooling) alimenta raw / whiten / head / head+whiten, applicati al volo da
  `prepare_index`.
- **Cache dei grafi** (`graphs.pt`): grezza, serve tutte le varianti; il filtro
  per split è in memoria.
- **Render-cache** delle viste degradate: hash su seed/frazione/augment/bordo,
  scrittura atomica, seeding deterministico **per pianta** → il rendering si
  paga una volta invece di 14. Uso: un job "che scalda" la cache, poi gli altri
  in parallelo.
- **`training_summary.json`**: criterio, best score, epoca e iperparametri di
  ogni run — risponde a molte domande senza aprire un log.

## Chi lancia cosa

Gli agenti **non lanciano job**: preparano il comando esatto, l'utente lo esegue
via `sbatch` e incolla l'output. Vale per training, valutazioni, indicizzazioni
e qualunque cosa richieda GPU o dataset intero. Gli agenti eseguono solo import
test e smoke test CPU.

## Cosa registrare dopo ogni run

1. Riga in **`.claude/TODO.md`** (stato del job: in coda / finito / letto).
2. Voce in **`.claude/shared/status.md`**: numeri, configurazione, ipotesi **confermata o
   smentita**, e il *perché*.
3. Se cambia il quadro generale, aggiornare lo **Stato attuale** di `CLAUDE.md`.
