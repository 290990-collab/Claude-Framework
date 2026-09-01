# Standard di codice — {{PROGETTO}}

Regola sovraordinata: **il codice nuovo imita il file in cui vive**. Questi
standard valgono dove il file non dà indicazioni.

## Standard dello stack principale

[DA COMPILARE] — una sezione per stack, con i pattern CONCRETI del repo sui
temi (dove applicabili):

- **Threading** (spesso la prima fonte di bug): da quali thread arrivano
  callback/eventi; come si tocca la UI se c'è (dispatcher/main thread);
  stato condiviso protetto o confinato; mai bloccare su codice async.
- **Risorse**: handle/connessioni/processi e pattern di rilascio,
  garantito anche sui percorsi d'errore.
- **Input non fidato** (file, rete, IPC, argomenti): validare lunghezze,
  caratteri nei path, formati.
- **Path**: API di join, mai concatenazione; spazi e non-ASCII gestiti.
- **Log**: con contesto; mai dati sensibili né input utente grezzo.
- **API da verificare** nell'uso reale del repo, mai dalla memoria;
  riferimenti per stringa (markup, binding, riflessione) ricontrollati a
  mano dopo ogni rename.
- **Piattaforma**: cosa resta cross-platform e dove si isola il codice
  platform-specific (pattern esistente).

## Stack secondari (script, embedded, ... — eliminare se non esistono)

[DA COMPILARE] — vincoli di runtime (interprete embedded, dipendenze,
versione del linguaggio), threading dell'host, errori difensivi (mai
crashare l'applicazione ospite), contratti versionati verso l'esterno.

## Performance

[DA COMPILARE] — budget del tipo di app (residente: idle ≈ 0% CPU; CLI:
startup rapido; server: latenza p99). In generale:

- Niente busy-polling: timer/eventi, intervalli larghi quanto la
  reattività percepita consente.
- Percorsi caldi (callback frequenti, parsing, matching): niente
  allocazioni evitabili né lavoro O(n) ripetuto per evento.
- Strutture che non reggono i volumi reali: dichiararlo nel report, non
  subirlo.
- UI (se c'è) istantanea: lavoro pesante fuori dal thread UI.

## Regole comuni

- Nomi che dicono cosa, commenti (pochi) che dicono perché.
- Funzioni corte, un livello di astrazione; 3 `if` annidati ≈ manca un
  early-return.
- Costanti nominate al posto di numeri/stringhe magiche ripetuti.
- Simmetria: se esistono `Start`/`Stop`, `Open`/`Close`, ogni nuova
  risorsa segue lo stesso schema.
- Degradazione con grazia: mai crashare l'ambiente dell'utente; ogni
  fallimento (dipendenza assente, connessione caduta, config corrotta) ha
  un esito visibile e recuperabile, mai silenzioso.
