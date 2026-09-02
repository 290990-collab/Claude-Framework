# Playbook di diagnosi

Mappa sintomo → sospetti. Serve a **restringere in fretta**, non a saltare
all'ipotesi: ogni sospetto va confermato con evidenza sul flusso reale prima di
toccare una riga.

## Mappa

| Sintomo | Sospetti, in ordine |
|---|---|
| Funziona la prima volta, poi no | stato residuo in memoria o su disco · cache · connessione o risorsa non rilasciata · indice o contatore non azzerato |
| Funziona in locale, non nell'ambiente reale | differenza di configurazione o variabili d'ambiente · versione diversa di una dipendenza · percorsi relativi · permessi · fuso orario o locale del sistema |
| Fallisce solo a volte | corsa fra thread o processi · dipendenza dall'ordine · timeout troppo stretto · dati di prova non deterministici · orologio o generatore casuale non fissato |
| Fallisce solo con dati reali | volume oltre il previsto · valori nulli o assenti non contemplati · encoding · valori fuori dominio · duplicati · limiti raggiunti |
| Il test passa ma il programma no | il test verifica un sostituto finto, non il vero · ambiente del test diverso · il percorso reale non è quello testato |
| Il test fallisce ma il programma va | l'asserzione verifica un dettaglio interno cambiato · stato lasciato da un altro test · dipendenza dall'ordine di esecuzione |
| Nessun errore, risultato sbagliato | errore inghiottito da un blocco di cattura · valore di ritorno ignorato · condizione sempre vera o sempre falsa · confronto fra tipi diversi · scorciatoia logica che salta il calcolo |
| Errore lontano dalla causa | valore sbagliato prodotto molto prima e propagato · nessuna validazione al confine · un valore assente trattato come default valido |
| Lento all'improvviso | complessità che esplode oltre una soglia di dati · chiamata dentro un ciclo che prima era fuori · indice mancante · attesa di I/O seriale dove serviva parallelo · cache che ha smesso di funzionare |
| Consuma memoria senza fermarsi | struttura che cresce e non viene mai svuotata · riferimenti trattenuti · cache senza limite · risorse non chiuse |
| Va in errore solo dopo un rilascio | migrazione non applicata o applicata a metà · configurazione nuova assente nell'ambiente · dati vecchi incompatibili con il codice nuovo |

## Tecniche, in ordine di costo

1. **Leggere il codice del percorso reale** — non quello che sembra pertinente
   per nome. La maggior parte dei difetti si vede leggendo il flusso corretto.
2. **Bisezione** — sui dati (metà input), sulla storia (quale modifica l'ha
   introdotto), sul percorso (dove il valore è ancora giusto e dove non lo è più).
3. **Rendere osservabile lo stato** al confine sospetto, invece di dedurlo.
4. **Ridurre al caso minimo** che riproduce: ogni elemento eliminato che lascia
   il difetto è un elemento escluso dalla diagnosi.
5. **Confrontare due esecuzioni**, una che funziona e una no, e cercare la prima
   differenza — non l'ultima.

## Trappole

- **Cercare conferme di una sola ipotesi.** Formulane due e chiediti quale
  osservazione le distingue.
- **Confondere concomitanza e causa**: se la spiegazione non copre *tutti* i
  sintomi, non è ancora la causa.
- **Correggere il sintomo**: un controllo aggiunto per evitare l'errore, mentre
  il valore sbagliato continua a essere prodotto a monte.
- **Fix a tentativi**: costano più della diagnosi e lasciano modifiche non
  motivate nel codice.

## In questo progetto

Tutto è riproducibile in locale in secondi: nessun servizio,
nessun log, nessuno stato remoto. Se un difetto non si riproduce, il sospetto
va sull'ambiente — codepage di Windows, fine riga, cache di `__pycache__` — non
sul codice.

Il primo strumento è il doctor, non il debugger: `python -m fwbuild doctor
--strict <progetto>` nomina il difetto con un codice, e la skill
`framework-doctor` dice cosa farne.

I guasti già visti e la loro causa reale stanno nella scheda di `debugger`
installata in `.claude/agents/`: si leggono prima di indagare da zero.

**Sui difetti di parsing si guarda la stringa vera, non la si immagina.** La
regex dei tag autochiusi di `transcript.py` è stata corretta solo dopo aver
stampato l'input reale: a mente sembrava giusta.
