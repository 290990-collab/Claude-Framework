## Principi di modifica

- **Minimal Safe Change** — la modifica più piccola che risolve il problema; un
  solo problema per task. Niente refactoring non richiesti, rename inutili,
  spostamenti di file, cambi di stile o di comportamento non chiesti. Il
  refactoring è un task separato.
- **Existing Pattern First** — prima di scrivere codice nuovo, cercare nel repo
  qualcosa da riusare o estendere. Consistenza prima della creatività.
- **Contract First** — prima di cambiare una funzione, un'API, un formato
  persistito o uno schema: qual è il contratto? chi lo usa (ricerca testuale
  inclusi markup, script in altri linguaggi e riferimenti per stringa)? rompo
  compatibilità o comportamento osservabile? Se sì: dichiararlo nel report e
  gestire la migrazione.
- **KISS** — a parità di risultato vince la soluzione più semplice.
- **Stile locale** — il codice nuovo imita il file in cui vive.
- **Niente commenti-cronaca** — i commenti spiegano vincoli non evidenti, non
  cosa fa la riga successiva.
- **Commit solo su richiesta esplicita** dell'utente, mai in autonomia.
- **Nessuna installazione senza conferma esplicita** — pacchetti, dipendenze,
  estensioni, tool, modelli, via qualunque gestore. Vale per ogni agente con
  accesso alla shell, anche quando l'installazione sembra ovvia o implicita.

## Principio sui test — pochi e sensati, mai molti e deboli

Il numero di test non è una metrica. Una suite grande può dare falsa sicurezza
mentre il difetto vero sta a un livello più alto: un'incoerenza di architettura,
un contratto sbagliato, un comportamento corretto in ogni unità e sbagliato
nell'insieme. Centinaia di test unitari verdi non lo vedono.

- **Un test che passerebbe anche col difetto presente non conta.** È il criterio
  con cui si giudica una suite, non la copertura di riga. Se non sai quale
  difetto plausibile lo farebbe fallire, non lo scrivi.
- **Si testa al livello a cui il difetto può nascere**, preferendo invarianti a
  esempi e coprendo i confini dichiarati — contratti, formati persistiti, casi
  limite reali del dominio.
- **Un rischio non esprimibile come test** va in `UNVERIFIED` con i passi di
  verifica manuale, mai compensato con test unitari che non c'entrano.

Livelli, invarianti e cosa non scrivere: `.claude/shared/core/testing-guide.md`.
