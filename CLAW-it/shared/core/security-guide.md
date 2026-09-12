# Guida alla sicurezza

Come si scrive codice raggiungibile da chi non dovrebbe usarlo. Sezioni in ordine di gravità.

## Input non fidato

- **Un dato esterno non diventa mai istruzione:** query parametrizzate, comandi con argomenti separati e mai composti da stringa, markup con escape del contesto, niente deserializzazione, template o valutazione a runtime di input esterno.
- **Percorsi confinati alla radice attesa,** controllati dopo aver risolto `../` e collegamenti, non prima.
- **Validazione al confine, per lista di consenso:** tipo, forma, dimensione. Ciò che non è ammesso si rifiuta, non si ripulisce.

## Segreti

- **Mai in codice, log, errori, artefatti di build o variabili esposte al client:** arrivano dall'ambiente o da un gestore di segreti.
- **Un segreto committato è compromesso anche dopo la rimozione:** si ruota.

## Autenticazione e autorizzazione

- **Controllo lato server, su ogni percorso che porta allo stesso dato:** uno solo nel client, o in un punto e non in un altro, equivale a nessuno.
- **Autorizzazione per oggetto:** essere autenticati non autorizza a leggere l'id di un altro utente.
- **Un header impostato dal client non è un'identità:** indirizzo inoltrato, ruolo o id dichiarati dalla richiesta non contano; conta l'identità autenticata o l'indirizzo reale della connessione.
- **Fail-closed:** controllo irraggiungibile o in errore → l'azione si nega, mai un ripiego senza controllo.
- **Si verifica che il controllo sia attivo:** si legge l'esito di chi imposta limiti, politiche, permessi; un fallimento silenzioso lascia zero controlli.
- **Audit anche dei rifiuti:** tentativi negati, cambi di permesso e decisioni si registrano come le operazioni riuscite, senza segreti né dati personali.

## Esposizione di dati

- **In uscita solo campi elencati,** mai l'oggetto interno serializzato per intero.
- **Errori verso l'esterno generici,** il dettaglio nel log interno.
- **Permessi minimi** su file, ruoli, token.

## Confini di fiducia

- **Richieste verso URL forniti dall'utente e redirect:** solo verso destinazioni in lista di consenso.
- **Risorse esterne e codice a runtime:** mai caricati senza lista di consenso e verifica di integrità.

## Risorse

- **Ogni input esterno ha un limite:** dimensione, numero di elementi, profondità di ricorsione, fattore di decompressione.
- **Nessuna espressione regolare con backtracking esponenziale su input esterno;** un pattern fornito dall'utente ha un limite di tempo.

## Dipendenze

- **Pacchetto nuovo solo se necessario,** coi criteri di adozione di `coding-standards.md`; nessuna versione con vulnerabilità note.
- **Versione esatta, mai un intervallo, per ciò che maneggia chiavi o token,** con integrità verificata.

## In questo progetto

[DA COMPILARE — i costrutti sicuri dello stack per query, comandi, markup e serializzazione; da dove si leggono i segreti; lo schema di autorizzazione adottato; cosa registra l'audit e dove.]
