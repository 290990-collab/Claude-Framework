# Convenzioni

Regole trasversali di forma. Il metodo di lavoro sta altrove: qui c'è solo come si scrivono le cose.

## Commit

- **Solo su richiesta esplicita dell'utente.**
- Messaggi in inglese, imperativi, prima riga ≤ 72 caratteri (`Fix …`, `Add …`, `Remove …`).
- Un commit = un cambiamento logico. Nessun refactoring mescolato a nuove funzionalità.
- Il corpo spiega il **perché**, non il cosa (il cosa è nel diff).
- Mai riscrivere storie condivise, mai forzare un push, mai saltare i controlli automatici.

## Ambito di una modifica

- Solo ciò che è richiesto; il resto si segnala nel report invece di eseguirlo.
- Refactoring, aggiornamenti dipendenze e formattazioni di massa sono task separati.
- Non toccare artefatti generati: si rigenerano, non si modificano a mano.

## Nomi

- Un nome esprime **cosa è o cosa fa**, non come è implementato (evitare tipi/strutture nei nomi).
- Coerenza prima dell'eleganza: usa la terminologia già presente nel progetto.
- Nessuna abbreviazione non standard nel dominio.
- I nuovi file seguono la convenzione di naming dei file adiacenti.

## Commenti

- Spiegano **vincoli non evidenti**: motivi di scelte non ovvie, casi limite o formati imposti dall'esterno.
- Mai descrivere ciò che il codice sottostante già esprime.
- Aggiornare o rimuovere i commenti contestualmente alle modifiche del codice.
- Eliminare il codice commentato inutilizzato: o serve ora, o si rimuove.

## Documentazione

- I cambiamenti visibili all'utente vanno annotati nei registri stabiliti dal progetto.
- Qualsiasi modifica a un contratto versionato impone l'aggiornamento della versione e la relativa segnalazione.
- La documentazione comportamentale va verificata contro il codice reale prima di essere scritta.

## Qualità minima non negoziabile

- La build deve passare dopo ogni task.
- Nessun nuovo avviso introdotto senza segnalazione.
- Nessuna gestione di errore vuota: gestire o propagare fornendo contesto.
- Nessun codice morto per usi futuri: o serve ora, o non si aggiunge.

## In questo progetto

[DA COMPILARE — lingua di codice e commenti, mappa "tipo di codice → cartella", convenzioni di naming specifiche, dove si annotano i cambiamenti visibili, quali cartelle contengono artefatti generati da non toccare.]
