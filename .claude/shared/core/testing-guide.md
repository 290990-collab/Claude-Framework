# Guida ai test

Il principio — **pochi test sensati, mai molti test deboli** — sta nel metodo.
Qui c'è il come applicarlo.

## Come si sceglie un test

Prima di scriverlo, rispondi a: **quale difetto plausibile lo farebbe fallire?**
Se non sai rispondere, il test non serve. Se la risposta è «nessuno, verifica che
il codice esista», è un test da non scrivere.

Test utile: fallisce quando il comportamento è sbagliato, passa quando è giusto,
e non cambia quando cambia solo l'implementazione. Se un refactoring a
comportamento invariato rompe il test, il test stava verificando i dettagli
interni, non il comportamento.

## Il livello giusto

| Il rischio è… | Il test va… |
|---|---|
| una regola di calcolo o trasformazione | sull'unità, con casi limite reali |
| l'interazione fra due moduli | sulla giunzione, con entrambi veri |
| un contratto verso l'esterno | sul contratto: forma, campi, compatibilità |
| il comportamento con dati reali sporchi | su un campione reale, non ideale |
| un flusso end-to-end | uno o due percorsi critici, non tutti |

L'errore più comune è testare tutto al livello più comodo — l'unità — e lasciare
scoperto il livello a cui i difetti nascono davvero.

## Invarianti prima degli esempi

Un'invariante copre infiniti casi e non invecchia:

- idempotenza: applicare due volte dà lo stesso risultato di una;
- round-trip: serializza e rileggi, ottieni l'originale;
- stabilità: input equivalenti danno output identici, anche fra esecuzioni;
- conservazione: nessun elemento perso o duplicato in una trasformazione;
- monotonia: aggiungere non può diminuire il risultato;
- gestione dell'errore: un fallimento non lascia stato parziale.

## Cosa non fare

- Test che replicano l'implementazione riga per riga: si rompono a ogni modifica
  e non trovano nulla.
- Asserzioni su messaggi di log o su formattazioni non contrattuali.
- Dipendenze dall'ordine di esecuzione o da stato lasciato da un altro test.
- Sostituti finti così permissivi da passare qualunque cosa: verificano il finto,
  non il vero.
- Attese temporali fisse al posto di una condizione: sono lente e intermittenti.
- Indebolire un'asserzione per far passare un test rosso.

## Quando un rischio non è testabile

Succede: resa visiva, prestazioni su hardware reale, integrazione con un servizio
esterno, comportamento sotto carico. In questi casi non si compensa con test
unitari che non c'entrano. Si dichiara il rischio in `UNVERIFIED` e si scrivono i
**passi di verifica manuale**, in modo che chiunque possa rifarli.

## In questo progetto

`cd framework/tools && python -m unittest discover tests -q` —
103 test, circa due secondi. `python -m pytest -q` deve dare lo **stesso**
numero: se diverge, è un difetto. A parte, `cd scripts && python -m unittest
test_transcript -q`, 16 test.

Cosa merita un test qui: i **vincoli**, non le funzioni. I test che contano sono
quelli che rompono la build quando il kernel supera il tetto di parole, quando
un'installazione reale non passa il doctor, quando un hash non torna.

**Il test end-to-end è quello che vale di più** e va tenuto vivo: installa
davvero e chiede il doctor. Un difetto reale — `roadmap.md` copiata e non
compilata — è stato trovato solo da lì.

Un test si dimostra utile reintroducendo il difetto e vedendolo diventare rosso
**su quel test e con quel messaggio**. Prima di allora è un'ipotesi.

Cosa **non** è testabile: se il metodo funzioni. Quello è D1, e i 103 test non
sono evidenza sul metodo.
