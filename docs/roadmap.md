# Roadmap

Il **cosa** e il **come**: obiettivi, in che ordine e perché in quell'ordine. Lo
stato di avanzamento non sta qui — sta in [TODO.md](TODO.md).

> Ordinata per **dipendenza**, non per priorità percepita: ciò che sblocca altro
> viene prima. Un obiettivo senza criterio di completamento non è un obiettivo.

## Obiettivi

### 1. D1 — misurare il metodo

**Perché:** è il cancello di tutto il resto. La tesi centrale del framework —
«`CLAUDE.md` è pagata a ogni spawn, quindi separare per destinatario fa
risparmiare» — oggi è un argomento, non un numero. D2, D5, D6 e D7 senza quel
numero sono opinioni.
**Fatto quando:** almeno 20 coppie A/B eseguite secondo
[eval/protocollo.md](eval/protocollo.md), e `docs/eval/esito.md` scritto col
verdetto sul criterio **già fissato** — mediana della riduzione ≥35% *e* tasso
di successo di A non inferiore — pubblicato anche se negativo.
**Dipende da:** —. D0 è chiusa: lo strumento di misura esiste e ha i suoi test.
**Rischi:** il dataset richiede giudizio, non un comando, ed è il pezzo fermo da
più tempo; 40 sessioni sono un costo reale; il criterio non si può ritoccare
dopo aver visto i primi risultati, ed è esattamente la tentazione che il
protocollo esiste per impedire.

### 2. D2 — ablation e potatura

**Perché:** scoprire quale parte del metodo è inerte e **tagliarla**. È il
risultato più prezioso possibile, ed è ciò che oggi non si sa.
**Fatto quando:** ogni sezione del metodo ha un delta misurato, e ciò che non ne
ha uno è stato rimosso — non marcato come «da rivedere».
**Dipende da:** 1.
**Rischi:** l'esito atteso è scomodo. Buona parte della prosa potrebbe non
guadagnarsi il posto, e la regola dice che allora esce.

### 3. D9 e D10 — errore multi-step e divagazione

**Perché:** sono le due questioni che toccano il cuore, cioè i file di metodo. È
anche dove sbagliare costa di più: ogni riga aggiunta a `method/` la paga ogni
agente a ogni spawn, per sempre.
**Fatto quando:** per ciascuna è deciso **dove** va scritta — e quindi chi la
paga — con l'osservabile fissato **prima** della prosa, come in D1.
**Dipende da:** —, per la discussione. 1, per l'implementazione: nessuna sezione
nuova di metodo prima che D1 chiuda.
**Rischi:** in entrambi i casi la cura sbagliata somiglia a quella giusta —
verificare di più è divagazione istituzionalizzata, e «l'utente può sbagliare»
diventa facilmente «l'utente ha di solito torto».

### 4. Pubblicazione

**Perché:** un framework che nessuno può installare non è un prodotto.
**Fatto quando:** licenza dichiarata, procedura di disinstallazione, CI che
esegue la suite, e un'installazione riuscita su una macchina che non è questa.
**Dipende da:** 1 e 2 — non si pubblica prosa non misurata — più la decisione
sulla licenza, oggi aperta.
**Rischi:** D7 (traduzione in inglese) va fatta prima o subito dopo, e va fatta
**solo** a potatura avvenuta: tradurre prima significa tradurre anche ciò che
verrà buttato.

## Fuori ambito, di proposito

- **Stack RAG, indicizzazione del codice, servizi, interfaccia.** `claude-os` li
  ha e sono fatti bene, ma sono un **secondo prodotto con un secondo ciclo di
  manutenzione**: 24.600 righe non misurate sono peggio di 1265 parole non
  misurate.
- **Spingere il metodo come prodotto in sé.** È prosa: si copia in una
  settimana. Il pezzo difendibile è il tooling che si accorge quando il metodo
  si rompe.
- **Tradurre in inglese prima di aver potato.** Si tradurrebbe anche la prosa
  inerte, e la si difenderebbe due volte.
