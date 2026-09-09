## Principi di modifica

- **Minimal Safe Change:** la modifica più piccola possibile. Risolvi un solo problema per volta. Zero refactoring, rinomine o cambi di stile non richiesti.
- **Existing Pattern First:** cerca e riusa pattern già presenti nel repo prima di crearne nuovi. Se la funzionalità richiesta esiste già, non la si riscrive: si dice dov'è e si propone solo la differenza che la richiesta aggiungeva.
- **Contract First:** se modifichi API/interfacce/schemi, cerca prima tutti i consumatori (script, test, stringhe). Segnala break/migrazioni nel report. Vale anche per ciò che **cancelli**: il codice che sembra morto va cercato prima come stringa.
- **KISS e stile locale:** la soluzione più semplice, adatta allo stile del file ospitante.
- **Commenti:** solo per vincoli non evidenti. Nessuna cronaca del codice.
- **Nessuna scorciatoia sul verde:** mai far passare un controllo indebolendolo — test cancellati o saltati, valore atteso riscritto sull'output, asserzione allargata, stub al posto del codice che deve girare. Se non passa, si riporta che non passa.
- **Fallimento rumoroso:** niente `except` che inghiotte, niente default inventati per proseguire, niente ramo di riserva che nasconde la causa. Un errore nascosto costa più di un crash.
- **Tassativo:** COMMIT, INSTALLAZIONE di dipendenze/tool e ogni operazione NON REVERSIBILE (cancellare dati, riscrivere cronologia, sovrascrivere file non letti) richiedono SEMPRE approvazione esplicita dell'utente.

## Principi sui test

- **Qualità > quantità:** un test che passerebbe anche col difetto presente non conta. Se non sai quale difetto lo farebbe fallire, non scriverlo.
- **Livello:** testa dove il difetto può nascere (contratti, confini, invarianti di dominio), preferendo invarianti a esempi.
- **Rischi non testabili:** vanno in `UNVERIFIED` coi passi di verifica manuale, mai compensati con test unitari che non c'entrano.
- Guida completa: `.claude/shared/core/testing-guide.md`.
