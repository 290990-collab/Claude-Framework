# Standard di codice

Come si struttura il codice, indipendentemente dal linguaggio, più il blocco per lo stack di questo progetto. Le convenzioni di forma — nomi, commit, commenti — stanno in `conventions.md`.

## Funzioni

- **Un livello di astrazione per funzione:** se alterna dettagli di basso livello e decisioni di alto livello, è due funzioni.
- **Poche condizioni annidate:** uscire presto sui casi degeneri lascia piatto il percorso principale.
- **Argomenti booleani che cambiano il comportamento** sono due funzioni travestite da una.
- **Restituire un valore *e* modificare stato osservabile:** separare quando possibile.
- **«Non trovato» e «non applicabile»** sono casi espliciti del valore di ritorno, mai un valore speciale ambiguo.

## Stato e mutabilità

- Immutabile per default; mutabile solo dove serve e in un ambito ristretto.
- **Nessuno stato globale modificabile:** rende i test dipendenti dall'ordine e i difetti non riproducibili.
- Nessuna struttura dati lasciata in uno stato intermedio non valido, nemmeno temporaneamente, se qualcun altro può osservarla.

## Errori

- **Errore atteso:** fa parte del contratto, sta nel tipo di ritorno o nell'eccezione dichiarata. **Errore inatteso:** propaga.
- **Si cattura solo ciò che si sa gestire:** catturare tutto e continuare trasforma un guasto in corruzione silenziosa.
- **Contesto risalendo:** quale operazione, su quale dato — mai il segreto o il dato personale.
- **Pulizia delle risorse garantita anche sul percorso di errore**, col costrutto previsto dal linguaggio.

## Dipendenze

- Ogni dipendenza è un costo permanente — manutenzione, sicurezza, aggiornamenti: per poche righe di codice si scrivono le righe.
- Le dipendenze esterne si isolano dietro un confine del progetto: sostituirle deve toccare un punto solo.
- **Nessuna installazione senza conferma esplicita dell'utente.**

## Concorrenza

- Condividere il meno possibile; dove si condivide, protocollo di accesso esplicito e documentato.
- Nessuna assunzione sull'ordine di esecuzione che non sia garantita.
- Ogni attesa ha un limite di tempo; ogni ripetizione ha un massimo.

## Leggibilità

- Il codice nuovo imita il file in cui vive: coerenza prima delle preferenze.
- Formattazione automatica dove esiste uno strumento: non si discute a mano.
- **La sola complessità ammessa è quella del problema:** funzione difficile da leggere su un problema facile = funzione sbagliata.

## In questo progetto

[DA COMPILARE — linguaggi e versioni, strumenti di formattazione e analisi statica con i comandi, convenzioni specifiche dello stack, pattern adottati e pattern esplicitamente scartati, vincoli di runtime che limitano cosa si può usare.]
