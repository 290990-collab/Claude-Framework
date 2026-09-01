# Guida ai test — smoke test CPU e invarianti

Qui i test **non** misurano quanto è bravo il modello (lo dicono le metriche,
dopo un job sbatch): verificano che la **pipeline sia corretta e riproducibile**.
Un test da 10 secondi su CPU che cattura un disallineamento indice↔nome vale più
di una run da 3 ore.

## Struttura ed esecuzione

- I test stanno in `tests/`, si lanciano con `python -m tests.<nome>` dopo
  `source ~/floorplan-env/bin/activate`.
- ⚠️ **`tests/test_vision_retrieval.py` non è un test**: è l'entrypoint storico
  di **indicizzazione** del ramo vision (gira su GPU sul cluster). Non
  trasformarlo in un test e non lanciarlo per "provare".
- Un test valido qui: **CPU**, pochi campioni, seed fisso, nessun download di
  pesi, nessuna scrittura in `embeddings/` reali (usare una directory
  temporanea).

## Cosa si testa (in ordine di valore)

1. **Invarianti numeriche** — embedding L2-normalizzati (norma ≈ 1); shape
   `[B, D]` / `[num_grafi, out_dim]`; gradienti che fluiscono dove devono
   (e **non** dove il modello è frozen); singolo grafo `batch=None` → `[1, D]`.
2. **Contratti su disco** — riga `i` di `embeddings.npy` ↔ riga `i` di
   `names.json`; `shuffle=False` rispettato; salva → ricarica → stessi valori;
   un checkpoint si ricarica **solo** con la stessa forma di architettura e
   viene **rifiutato** con una forma diversa (è il test che protegge dal flag
   dimenticato in un ponte YAML→flag).
3. **Determinismo e cache** — stesso seed → stesso output; una cache restituisce
   bit-identico ciò che ricalcolerebbe (chiave della cache = tutti i parametri
   che influenzano il contenuto).
4. **Assenza di leakage** — statistiche calcolate sul train e applicate al test
   danno media **vicina ma non esattamente** 0; una media esattamente 0 è la
   firma di un leakage.
5. **Invarianze dichiarate dalle augmentation** — se un'augmentation dichiara
   un'invarianza, il test la verifica *esattamente*: rotazione e riflessione non
   cambiano area/aspect né one-hot né archi; 4 rotazioni = identità;
   la decisione è per-grafo, non per-nodo.
6. **Trasformazioni della pipeline** — whitening/head applicati **una volta
   sola** e in ordine; `prepare_index` su raw/whiten/head/head+whiten produce
   forme coerenti; PCA con `dim` ridotta restituisce la larghezza attesa.
7. **Casi limite del dominio** — PNG senza record `.mat` (dev'essere saltato,
   non far crashare); `mask_fraction=0` → immagine originale intatta; grafo con
   self-loop spurio; classe di equivalenza singleton (query esclusa **e
   contata**); stanza rimossa che svuota il grafo.

## NON testabile in automatico

Valori reali delle metriche, qualità visiva dei rendering, tempi e memoria su
GPU, comportamento sul dataset intero, ricarica di pesi pretrained che richiede
rete. Vanno **elencati nel report come verifica manuale o da sbatch**, con il
comando esatto.

## Qualità dei test

- Un test mai visto fallire non dimostra nulla: per un bug, prima il test rosso,
  poi il fix, poi il verde.
- Comportamento osservabile, non dettagli interni: il test sopravvive a un
  refactoring.
- Test indipendenti dall'ordine, senza stato condiviso mutabile.
- Niente `sleep`: sincronizzazione esplicita.
- Dati parlanti: una pianta reale con la sua vera composizione dice più di un
  tensore di zeri — ma il test deve restare veloce.
- Mai indebolire un'asserzione per farla passare: rosso = bug o test sbagliato,
  si decide, non si maschera.
