# Guida ai dati

Per i progetti che acquisiscono, trasformano o conservano dati esterni. Un difetto qui non fa cadere niente: fa funzionare tutto con i valori sbagliati.

## Normalizzazione

- **Deterministica:** stesso input, stesso output, anche fra esecuzioni diverse. Se dipende dall'ordine di arrivo o dall'orologio, non lo è.
- **Unità esplicite**, mai implicite nel contesto: importi come interi con la valuta accanto, misure con l'unità, istanti con il fuso. Mai virgola mobile per il denaro.
- **Testo normalizzato prima del confronto:** forma unicode, spazi ai bordi, maiuscole, caratteri invisibili. Due stringhe identiche a vedersi possono non esserlo.
- **Mancante, zero, stringa vuota e «sconosciuto» sono quattro cose diverse** e vanno rappresentate come tali.

## Chiavi e identità

- **Chiave stabile = attributi che non cambiano.** Derivarla da un nome, un indirizzo o un prezzo produce duplicati al prossimo aggiornamento.
- **Chiave troppo permissiva:** fonde entità distinte. È l'errore opposto, e si nota molto più tardi.
- **Riconciliazione fra sorgenti verificata su casi reali**, ambigui inclusi: due prodotti simili, due omonimi, lo stesso oggetto scritto in due modi.

## Idempotenza e ripetibilità

- Rieseguire un'acquisizione non deve duplicare, incrementare, né riscrivere con valori parziali.
- Ogni operazione va interrompibile a metà e ripresa senza lasciare stato incoerente.
- Un'operazione non idempotente va dichiarata come tale e protetta.

## Verità e derivati

- **Una sola sorgente di verità.** Indici, cache, viste materializzate e aggregati sono derivati: ricostruibili, mai l'unica copia.
- Un cambiamento che impone una ricostruzione si dichiara con procedura e tempo previsto.
- Due punti che possono divergere divergeranno: senza un modo di riallinearli, è un difetto di progetto.

## Input non fidato

Ogni dato esterno si valida al confine: schema, tipi, lunghezze, encoding, intervalli. Le righe malformate si gestiscono **senza fermare tutto e senza corrompere il resto**, e finiscono in un conteggio.

Difese esplicite: archivi e documenti costruiti per esaurire memoria o disco, riferimenti a entità esterne, percorsi che escono dalla cartella prevista, richieste verso indirizzi forniti dalla sorgente.

## Osservabilità

Per ogni esecuzione e ogni sorgente: quanti record letti, accettati, scartati e **perché**. Senza questi numeri una perdita silenziosa è invisibile — e le perdite silenziose sono la norma. Nessun dato personale nei log.

## Migrazioni

Compatibili con i dati già scritti · reversibili o con un percorso di ritorno dichiarato · applicabili mentre la versione precedente del codice gira ancora · provate su una copia realistica, non su dati di esempio.

## In questo progetto

[DA COMPILARE — le sorgenti e cosa promettono davvero, il contratto di acquisizione, le regole di normalizzazione adottate, quali sono le chiavi stabili, dove sta la verità e cosa è derivato, i casi sporchi già incontrati, come si esegue una ricostruzione.]
