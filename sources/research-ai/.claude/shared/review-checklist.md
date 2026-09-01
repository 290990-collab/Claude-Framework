# Checklist di review

Riferimento esteso per `final-reviewer` (parti 0-3) e `scientific-reviewer`
(parte 4). Regola base: **verificare in prima persona, mai fidarsi dei report
degli altri agenti.**

⚠️ **Git è vietato nel progetto**: non c'è `git diff`. Il perimetro è la lista
di file dichiarati modificati dal coordinatore — e il primo controllo è che non
ne siano stati toccati altri.

## 0. Prerequisiti

- [ ] I file modificati sono quelli dichiarati? (file toccati e non dichiarati =
      finding)
- [ ] Le modifiche fanno ciò che il task chiedeva — tutto e **solo** quello?
- [ ] Import dei moduli toccati + smoke test CPU esistenti, ESEGUITI ora.
- [ ] Ciò che richiede GPU/sbatch è dichiarato come non verificabile qui, col
      comando esatto per l'utente.

## 1. Correttezza del codice nuovo

- [ ] Shape e ordine degli assi; niente broadcasting accidentale.
- [ ] Device coerente (CPU/GPU), `no_grad`/`detach` dove servono, `eval()` dove
      il modello non deve allenarsi.
- [ ] Normalizzazioni applicate **una volta sola** e nell'ordine giusto
      (head → whitening → L2; clip prima dello z-score).
- [ ] Indici e nomi allineati; niente ordinamenti impliciti del filesystem.
- [ ] Valori mancanti gestiti (pianta senza record `.mat`, grafo vuoto, classe
      singleton).
- [ ] Nessun `except` silenzioso nuovo; errori con contesto.
- [ ] Seed passati davvero a tutti i generatori usati.

## 2. Coerenza fra i quattro livelli (il punto debole di questo progetto)

- [ ] **codice ↔ argparse ↔ chiavi YAML ↔ ponte YAML→flag negli script**: un
      parametro presente in tre di questi quattro viene ignorato **in silenzio**.
- [ ] I booleani hanno il mapping esplicito (`store_true` / coppia negativa),
      altrimenti il ponte li salta.
- [ ] Training ed eval costruiscono la **stessa** architettura (altrimenti il
      checkpoint non si ricarica).
- [ ] Le liste che devono restare sincronizzate (varianti di ablation, encoder
      noti) hanno una guardia che fallisce, non un `warning`.

## 3. Regressioni, artefatti, riproducibilità

- [ ] Per ogni simbolo/chiave/nome modificato: `Grep` di TUTTI gli usi, inclusi
      `.sh`, YAML, `COMANDI.md`, e i nomi che compongono `save_dir`.
- [ ] Gli artefatti già su disco (`embeddings.npy`, `graphs.pt`, `pairs.npz`,
      `head.pt`, `encoder.pt`, `geom_stats.npz`) restano leggibili? Se no, la
      **rigenerazione** (ore di GPU) è dichiarata esplicitamente?
- [ ] La modifica può cambiare una metrica già riportata? Se sì è dichiarato?
- [ ] Nessun path assoluto d'utente, nessun iperparametro hardcodato.
- [ ] Documentazione allineata: `.claude/shared/*.md`, *Stato attuale* di
      CLAUDE.md, `.claude/TODO.md`, `COMANDI.md` se cambiano i comandi.
- [ ] Niente codice morto, TODO orfani, `print` di debug residui.

## 4. Validità scientifica (`scientific-reviewer`)

- [ ] **Leakage**: statistiche dal solo train? selezione sul valid? il test non
      ha scelto niente? (controllo: test normalizzato col train ha media *vicina*
      ma non esattamente 0)
- [ ] **Confronto appaiato**: stesse query, gallery, esclusioni, protocollo. Le
      esclusioni singleton nei log coincidono?
- [ ] **Riferimento valido**: la run di confronto è davvero quella
      configurazione, o la cartella è stata sovrascritta?
- [ ] **Baseline giusta**: oltre alla baseline ovvia, esiste il denominatore
      onesto (pesi casuali, componente disattivata, feature grezze)?
- [ ] **Metrica**: può fallire? un sistema banale che punteggio prende? è quella
      coerente con l'obiettivo, o si sta ottimizzando un proxy che diverge?
- [ ] **Scale non mescolate**: sonda (valid, gallery ridotta) e report finale
      (test, gallery intera) non si confrontano tra loro.
- [ ] **Attribuzione**: una sola variabile per confronto; varianti selezionate
      con criteri diversi non si ordinano tra loro.
- [ ] **Significatività**: il delta è sopra il rumore noto? è dichiarato?
- [ ] **Per-asse**: composizione/topologia/geometria riportate separatamente; una
      media che nasconde un asse in calo è una conclusione sbagliata.
- [ ] **Caveat dichiarati**: circolarità sugli assi composizione/topologia,
      divario di capacità fra encoder, duplicati nel dataset, limiti dei dati.
- [ ] **Claim vs numeri**: il testo afferma esattamente quanto i numeri letti
      mostrano, né più né meno.

## Verdetto

- **APPROVATO** — test eseguiti di persona, nessun finding rilevante.
- **APPROVATO CON RISERVE** — finding minori elencati, nulla che blocchi.
- **RESPINTO** — almeno un finding grave, motivato con `file:riga` e scenario.

Un verdetto senza test eseguiti di persona non è un verdetto.
