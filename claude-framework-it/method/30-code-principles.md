## Principi di modifica

- **Minimal Safe Change:** la modifica più piccola possibile. Risolvi un solo problema per volta. Zero refactoring, rinomine o cambi di stile non richiesti.
- **Existing Pattern First:** cerca e riusa pattern già presenti nel repo prima di crearne nuovi.
- **Contract First:** se modifichi API/interfacce/schemi, cerca prima tutti i consumatori (script, test, stringhe). Segnala break/migrazioni nel report.
- **KISS e stile locale:** la soluzione più semplice, adatta allo stile del file ospitante.
- **Commenti:** solo per vincoli non evidenti. Nessuna cronaca del codice.
- **Tassativo:** COMMIT e INSTALLAZIONE di dipendenze/tool richiedono SEMPRE approvazione esplicita dell'utente.

## Principi sui test

- **Qualità > quantità:** un test che passerebbe anche col difetto presente non conta. Se non sai quale difetto lo farebbe fallire, non scriverlo.
- **Livello:** testa dove il difetto può nascere (contratti, confini, invarianti di dominio), preferendo invarianti a esempi.
- **Rischi non testabili:** vanno in `UNVERIFIED` coi passi di verifica manuale, mai compensati con test unitari che non c'entrano.
- Guida completa: `.claude/shared/core/testing-guide.md`.
