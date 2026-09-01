# Playbook di debug — DL, dati, HPC

**Si diagnostica con le evidenze, non con la memoria del modello.**

## Prima domanda: che tipo di guasto è?

| | **Bug di codice** | **Bug di metodo** |
|---|---|---|
| Sintomo | traceback, shape, crash, job fallito | il codice gira, i numeri escono, ma **non significano quello che crediamo** |
| Esempi | flag ignorato, path errato, device sbagliato | leakage, confronto non appaiato, metrica satura, criterio di selezione scorretto |
| Chi | `debugger` | `scientific-reviewer` |
| Costo se non visto | ore | **l'intero risultato** |

Il secondo tipo non fa rumore: se il sintomo è "il risultato non ha senso" o "il
guadagno è sparito", parti da lì.

## Metodo in 6 passi

1. **Fissa il sintomo**: cosa succede vs cosa dovrebbe, da quando, con che
   frequenza, su quale encoder/variante/split. "A volte" ≈ quasi sempre seed,
   ordine dei dati o ambiente.
2. **Fatti prima delle teorie**: output incollato dall'utente, file di summary,
   config effettivamente usata. Vietato proporre fix in questo passo.
3. **Almeno DUE ipotesi**, ciascuna con cosa la conferma, cosa la falsifica e
   come discriminarle al minor costo (preferendo una verifica CPU a un rilancio).
4. **Falsifica** la preferita: la diagnosi vale solo se spiega TUTTI i sintomi.
5. **Fix minimo sulla causa**, non sul sintomo, coi rischi di regressione. Lo
   applica l'`implementer`.
6. **Definisci la verifica**: come si dimostra che il fix funziona.

Anti-pattern vietati: fix a tentativi; sopprimere l'eccezione invece della
causa; "risolto" perché un problema intermittente non si è ripresentato una
volta; prendere il report di un altro agente come evidenza.

## Mappa sintomo → primi sospetti

| Sintomo | Primi sospetti |
|---|---|
| Job "riuscito" in pochi secondi senza fare nulla | Argomento sbagliato agli script: si passa il **basename del YAML** (`graph_sage`), non la chiave `encoder` (`sage`) → config non trovata, encoder saltato con un avviso, job che passa dritto al riepilogo. Oppure lista varianti desincronizzata dalla tabella dei flag |
| `no kernel image is available` al forward su GPU | Nodo con GPU **Blackwell sm_120** non supportata dal PyTorch dell'env → serve la constraint sbatch con allowlist di GPU. ⚠️ Il percorso "frozen" può passare lo stesso (non fa forward torch su GPU) e mascherare il problema |
| `size mismatch` ricaricando un checkpoint | Un flag di architettura non è arrivato all'eval (`raw_skip`, `hidden_dim`, `heads`, `pooling`): training ed eval devono costruire la **stessa** rete. Controlla i 4 livelli: codice ↔ argparse ↔ YAML ↔ ponte YAML→flag nello script |
| Un parametro "non ha effetto" | Chiave YAML non tradotta dal ponte, o override CLI messo **prima** dei flag del YAML (vince l'ultimo), o booleano `store_true` senza mapping esplicito → ignorato in silenzio |
| Metrica satura (tutti ≈ 1.0) | Ground truth troppo permissiva; ambito circolare (calcolata solo sui top-k invece che sull'intera gallery); oppure è un **oracolo per costruzione** (la baseline istogramma sulla composizione) |
| La loss migliora ma il retrieval peggiora | Falsi negativi di InfoNCE: i rilevanti finiti nello stesso batch vengono allontanati. Selezionare sulla sonda di retrieval, non sulla val-loss |
| Il guadagno visto sul valid sparisce sul test | Riferimento sbagliato (cartella `save_dir` **sovrascritta** da una run successiva con lo stesso `variant`) o confronto non appaiato |
| Numeri diversi "senza aver cambiato nulla" | Config diversa da quella che si crede, cache stantia, artefatto rigenerato con un formato nuovo, seed non passato |
| Tutti i modelli danno lo stesso identico numero | Sospetta i **dati**, non i modelli: duplicati esatti nel dataset, oppure un percorso che restituisce l'input invariato (es. masking con frazione 0) |
| Masking che non cancella / rendering storto | Trappola assi (`gtBoxNew` `[x0,y0,x1,y1]` vs `gtBox` `[y0,x0,y1,x1]`), affine griglia-256→pixel, flood-fill che non chiude |
| OOM o job ucciso | Batch size, gallery intera caricata in memoria, worker del DataLoader, `--mem` della sbatch |
| Risultati non riproducibili tra due run identiche | Seed non passato a *tutti* i generatori, `shuffle=True` dove l'ordine è un contratto, non-determinismo cuDNN, ordine dei file dal filesystem |

## Strumenti

- **Non** si scansiona `logs/`: si legge il file che l'utente indica.
- `training_summary.json` accanto al checkpoint (criterio, best score, epoca,
  iperparametri) risponde a molte domande senza aprire un log.
- Verifiche CPU mirate su poche piante battono qualunque rilancio di job.
- Per capire *cosa è stato davvero eseguito*: la config effettiva stampata dal
  job e la cartella `save_dir` (che contiene la variante nel path).
- ⚠️ SLURM esegue una **copia** dello script: modificare il file nel repo non
  altera i job già avviati — comodo, ma significa anche che un job in corso può
  girare con una versione diversa da quella che stai leggendo.

## Diagnosabilità by design

Il codice nuovo a rischio (I/O, cache, selezione di checkpoint, trasformazioni
applicate al volo) nasce già osservabile: stampa la config effettiva, il numero
di elementi processati/saltati e le esclusioni. In questo progetto le esclusioni
singleton stampate a ogni valutazione sono ciò che permette di verificare, a
posteriori, che due run erano appaiate.

## Quando fermarsi

Se l'evidenza non discrimina fra le ipotesi, il deliverable è: ipotesi rimaste,
evidenza mancante e strumentazione minima da aggiungere per decidere. È un esito
legittimo; una certezza inventata no.
