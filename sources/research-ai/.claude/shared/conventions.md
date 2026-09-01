# Convenzioni — codice e documentazione

Regola sovraordinata: **il codice nuovo imita il file in cui vive**. Queste
convenzioni valgono dove il file non dà indicazioni. Lingua: italiano con
l'utente, **inglese** in codice, identificatori e commenti.

## Obiettivo dello stile

Codice **pulito, leggibile, semplice da mantenere, facilmente debuggabile e
coerente tra moduli e contributor** — la cartella è condivisa da tre persone e
il codice sopravvive al progetto sotto forma di report.

- **Semplicità > astuzia**: niente one-liner criptiche, nesting inutile,
  astrazioni premature, metaprogrammazione non necessaria.
- **Leggibilità a mesi di distanza**: ogni funzione ha uno scopo chiaro e
  input/output comprensibili.
- **Funzioni piccole e modulari**: niente funzioni monolitiche con troppe
  responsabilità.
- **Errori espliciti**: messaggi che dicono cosa è mancato e dove.

## Separazione delle responsabilità

Restano separati: **data loading · preprocessing · definizione del modello ·
training · valutazione · visualizzazione · utility**. Il training loop è
leggibile e distinto da modello e valutazione, con forward, loss, backward,
metriche e logging chiaramente riconoscibili.

## Documentazione nel codice

- **Docstring per ogni funzione**: descrizione breve, input, output, eventuali
  side effect (file scritti, stato modificato).
- **Un commento per blocco logico significativo**: cosa fa, **perché**, quali
  assunzioni. Niente commenti che ripetono la riga successiva.
- **Shape sempre documentate**:
  ```python
  # image_tensor: [B, C, H, W]
  # embeddings:   [B, D]  (L2-normalized)
  ```
- **Per i grafi**, dichiarare sempre node features, formato di `edge_index`,
  attributi degli archi e assunzioni di batching:
  ```python
  # x:          [N, 19]  one-hot type (13) + geometry (6)
  # edge_index: [2, E]   undirected (symmetrized)
  # edge_attr:  [E, 10]  one-hot RPLAN relation
  ```
- **Nel retrieval**, documentare metrica di similarità, strategia di
  normalizzazione, K usati e — per le query parziali — il **livello di masking**.

## File e struttura

| Tipo di codice | Dove |
|---|---|
| Lettura ground truth RPLAN, metriche, rilevanza | `src/data/`, `src/evaluation/` (**condivisi**, usati as-is) |
| Pipeline vision | `src/vision/{data,models,training,evaluation,utils}/` |
| Pipeline graph | `src/graph/{models,training,evaluation}/` + moduli di primo livello |
| Iperparametri e preset | `configs/` (mai nel codice) |
| Job HPC | `scripts/{vision,graph}/`, numerati nell'ordine di esecuzione |
| Smoke test | `tests/` |

- Nuovi file: naming dei vicini; nuovi moduli espongono `main()` sotto
  `if __name__ == "__main__"` e si lanciano con `python -m`.
- Artefatti generati (`embeddings/`, `results/`, `logs/`, `wandb/`) non si
  modificano a mano e non si versionano.
- `umask 002` / `chmod g+w`: tutto resta scrivibile dal gruppo.

## Principi di modifica (estensione di CLAUDE.md)

In `CLAUDE.md` restano i tre non negoziabili — *Minimal Safe Change*, *numeri
invariati salvo mandato*, *Contract First*. Qui il resto:

- **Existing Pattern First.** I due rami sono gemelli per costruzione (registry
  di encoder, `save_dir` namespacizzato, un YAML per modello, script numerati).
  Prima di inventare, guarda come l'ha risolto l'altro ramo: consistenza prima
  di creatività.
- **Niente refactor cross-ramo.** `src/vision/` e `src/graph/` restano
  autonomi; il codice condiviso è solo `src/data/` e `src/evaluation/`, usati
  **as-is**. La duplicazione degli helper di accumulo per-asse è **deliberata**,
  non un difetto: unificarli legherebbe i due rami proprio dove devono poter
  divergere.
- **La ridondanza non è un difetto in assoluto**: prima di segnalarla, chiedersi
  *chi la paga*. Nei documenti di contesto (`CLAUDE.md`, `.claude/**`) si paga a
  ogni spawn → un fatto in un posto solo, altrove un puntatore. Nel codice il
  problema non è la ripetizione ma la **divergenza** (due copie che si scollano,
  es. lo stesso dict di flag in due script). Altrove — grafici, notebook,
  analisi, bozze — è **opzionalità gratuita** e si tiene.
- **Configuration over Hardcoding.** Ogni iperparametro sta in un YAML o in un
  flag, mai nel codice; nessun path assoluto d'utente (`$HOME`/`~` dinamico).
- **Riproducibilità.** Seed espliciti e passati a tutti i generatori;
  `shuffle=False` dove l'ordine indice↔nome è un contratto; statistiche di
  normalizzazione dal **solo train**; ogni run rintracciabile (`variant`
  namespacizza `save_dir`).
- **KISS e stile locale**: a parità di risultato vince la soluzione più
  semplice, e il codice nuovo imita il file in cui vive.

## Ambito delle modifiche

- Solo ciò che è richiesto; il resto si segnala nel report.
- Refactoring = task separato (`refactorer`).
- Niente aggiornamenti di dipendenze non richiesti (l'env è condiviso: romperlo
  blocca tre persone).
- **Git è vietato** nel progetto: nessun commit, nessun comando git.

## Documentazione delle modifiche

- Cambiamento sostanziale di codice → aggiornare il `.md` corrispondente in
  `.claude/shared/`.
- Risultato nuovo o ipotesi risolta → riga in `.claude/shared/status.md` **e** aggiorno
  dello *Stato attuale* in `CLAUDE.md`.
- Nuovo comando o nuova dipendenza tra job → `COMANDI.md`.

## Qualità minima non negoziabile

- I moduli toccati **importano** e i loro smoke test CPU passano.
- Nessun `except` nudo o silenzioso nuovo: o si gestisce, o si logga col
  contesto, o si lascia propagare.
- Niente codice morto "per dopo"; niente `print` di debug residui.
- Niente numeri magici ripetuti: costanti nominate.
- Nessun path assoluto d'utente, nessun segreto, nessuna chiave in codice o log.
