# Guida ai dati

Per i progetti che acquisiscono, trasformano o conservano dati provenienti
dall'esterno. Un difetto qui non fa cadere niente: fa funzionare tutto con i
valori sbagliati.

## Normalizzazione

- **Deterministica**: stesso input, stesso output, sempre e fra esecuzioni
  diverse. Se dipende dall'ordine di arrivo o dall'orologio, non lo è.
- **Unità esplicite**, mai implicite nel contesto: importi come interi con la
  valuta accanto, misure con l'unità, istanti con il fuso. Il valore in virgola
  mobile non si usa per il denaro.
- **Testo normalizzato prima del confronto**: forma unicode, spazi ai bordi,
  maiuscole, caratteri invisibili. Due stringhe che appaiono identiche possono
  non esserlo.
- **Un valore mancante non è zero, non è stringa vuota, non è «sconosciuto»**:
  sono quattro cose diverse e vanno rappresentate come tali.

## Chiavi e identità

- Una chiave stabile deriva da attributi che **non cambiano**. Se deriva da un
  nome, un indirizzo o un prezzo, produrrà duplicati al prossimo aggiornamento.
- Una chiave troppo permissiva fonde entità distinte: è l'errore opposto e si
  nota molto più tardi.
- La riconciliazione fra sorgenti diverse va **verificata su casi reali**,
  inclusi i casi ambigui: due prodotti simili, due persone omonime, lo stesso
  oggetto scritto in due modi.

## Idempotenza e ripetibilità

- Rieseguire un'acquisizione non deve duplicare, incrementare, né riscrivere con
  valori parziali.
- Ogni operazione deve poter essere interrotta a metà e ripresa senza lasciare
  stato incoerente.
- Un'operazione che non è idempotente va dichiarata come tale e protetta.

## Verità e derivati

- **Una sola sorgente di verità.** Indici, cache, viste materializzate e
  aggregati sono derivati: ricostruibili, mai l'unica copia.
- Se un cambiamento impone una ricostruzione, va dichiarato con la procedura e il
  tempo previsto.
- Due punti che possono divergere divergeranno: se non c'è un modo di
  riallinearli, è un difetto di progetto.

## Input non fidato

Ogni dato esterno si valida al confine: schema, tipi, lunghezze, encoding,
intervalli. Le righe malformate si gestiscono **senza fermare tutto e senza
corrompere il resto**, e finiscono in un conteggio.

Difese esplicite: archivi e documenti costruiti per esaurire memoria o disco,
riferimenti a entità esterne, percorsi che escono dalla cartella prevista,
richieste verso indirizzi forniti dalla sorgente.

## Osservabilità

Per ogni esecuzione e ogni sorgente: quanti record letti, accettati, scartati e
**perché**. Senza questi numeri, una perdita silenziosa è invisibile — e le
perdite silenziose sono la norma, non l'eccezione.

Nessun dato personale nei log.

## Migrazioni

Compatibili con i dati già scritti · reversibili o con un percorso di ritorno
dichiarato · applicabili mentre la versione precedente del codice è ancora in
esecuzione · provate su una copia realistica, non su dati di esempio.

## In questo progetto

[DA COMPILARE — le sorgenti e cosa promettono davvero, il contratto di
acquisizione, le regole di normalizzazione adottate, quali sono le chiavi
stabili, dove sta la verità e cosa è derivato, i casi sporchi già incontrati,
come si esegue una ricostruzione.]
