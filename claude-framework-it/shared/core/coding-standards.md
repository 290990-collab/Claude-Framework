# Standard di codice

Regole di scrittura indipendenti dal linguaggio, più il blocco per lo stack di
questo progetto. Le convenzioni di forma (nomi, commit, commenti) stanno in
`conventions.md`; qui c'è come si struttura il codice.

## Funzioni

- **Un livello di astrazione per funzione.** Se una funzione alterna dettagli di
  basso livello e decisioni di alto livello, è due funzioni.
- Poche condizioni annidate: uscire presto sui casi degeneri lascia il percorso
  principale piatto e leggibile.
- Argomenti booleani che cambiano il comportamento sono due funzioni travestite
  da una.
- Una funzione che restituisce un valore **e** modifica stato osservabile è
  difficile da usare correttamente: separare quando possibile.
- Il valore di ritorno rappresenta anche il caso «non trovato» o «non
  applicabile» in modo esplicito, non con un valore speciale ambiguo.

## Stato e mutabilità

- Immutabile per default; mutabile dove serve davvero e in un ambito ristretto.
- Nessuno stato globale modificabile: rende ogni test dipendente dall'ordine e
  ogni difetto non riproducibile.
- Una struttura dati non si lascia in uno stato intermedio non valido, nemmeno
  temporaneamente, se qualcun altro può osservarla.

## Errori

- Un errore atteso fa parte del contratto e si rappresenta nel tipo di ritorno o
  nell'eccezione dichiarata; un errore inatteso propaga.
- Si cattura solo ciò che si sa gestire. Catturare tutto e continuare trasforma
  un guasto in corruzione silenziosa.
- Il contesto si aggiunge risalendo: quale operazione, su quale dato — mai il
  segreto o il dato personale.
- La pulizia delle risorse è garantita anche sul percorso di errore, con il
  costrutto del linguaggio previsto per quello.

## Dipendenze

- Ogni dipendenza è un costo permanente: manutenzione, sicurezza, aggiornamenti.
  Per poche righe di codice si scrivono le righe.
- Le dipendenze esterne si isolano dietro un confine del progetto, così
  sostituirle tocca un punto solo.
- **Nessuna installazione senza conferma esplicita dell'utente.**

## Concorrenza

- Condividere il meno possibile; dove si condivide, il protocollo di accesso è
  esplicito e documentato.
- Nessuna assunzione sull'ordine di esecuzione che non sia garantita.
- Ogni attesa ha un limite di tempo; ogni ripetizione ha un massimo.

## Leggibilità

- Il codice nuovo imita il file in cui vive: coerenza prima di preferenze.
- La formattazione è automatica dove esiste uno strumento: non si discute a mano.
- La complessità che resta è quella del problema, non quella aggiunta
  dall'implementazione. Se una funzione è difficile da leggere e il problema non
  è difficile, la funzione è sbagliata.

## In questo progetto

[DA COMPILARE — linguaggi e versioni, strumenti di formattazione e analisi
statica con i comandi, convenzioni specifiche dello stack, pattern adottati e
pattern esplicitamente scartati, vincoli di runtime che limitano cosa si può
usare.]
