# Principi di ricerca

Per i progetti il cui prodotto non è «software che gira» ma **evidenza
riproducibile**. Linee guida permanenti su *come si ragiona*, non su quali
competenze avere.

> **Principio guida.** Ogni decisione è motivata da dati, esperimenti o
> letteratura; ogni risultato è spiegabile, riproducibile e verificabile da altri.

## Evidenza e onestà

1. **Evidence first** — ogni affermazione tecnica poggia su una misura, una
   fonte o un esperimento. Mai su una supposizione plausibile.
2. **Fatti, interpretazioni e idee restano separati**, anche tipograficamente.
   La confusione fra i tre è il modo più comune di scrivere qualcosa di falso
   senza mentire.
3. **Assunzioni esplicite** su problema, dati e modello: quelle taciute sono
   quelle che si rivelano sbagliate.
4. **I risultati negativi si riportano.** Un'ipotesi smentita è informazione
   acquisita: nasconderla significa ripagarne il costo più avanti.
5. **Scetticismo verso i propri miglioramenti**: un guadagno è un'ipotesi da
   verificare, non un risultato acquisito.
6. **Si riportano forze e debolezze.** Un lavoro che espone solo i propri punti
   forti non è valutabile.

## Metodo sperimentale

7. **Baseline prima della complessità.** Prima il riferimento semplice — anche
   banale, anche casuale — poi l'architettura elaborata. Senza il denominatore
   giusto, un guadagno può essere sopravvalutato di un ordine di grandezza.
8. **Una variabile alla volta.** Se cambi due cose insieme, l'effetto non è
   attribuibile e l'esperimento è sprecato.
9. **Ogni componente aggiunta va giustificata da un'ablazione**: se toglierla non
   cambia nulla, non serviva.
10. **Il criterio di successo si decide prima** di guardare i risultati. Deciderlo
    dopo è scegliere la conclusione.
11. **Misura contro intuizione**: decidono le metriche, non la sensazione che una
    cosa «dovrebbe» funzionare meglio.
12. **Confronti equi**: stessi dati, stesso protocollo, stesse esclusioni,
    capacità dei modelli dichiarata quando differisce.
13. **Rispetta la significatività**: differenze dell'ordine del rumore non sono
    risultati finché non è mostrato il contrario.
14. **Analisi degli errori prima del miglioramento**: capire *come* sbaglia
    precede il tentativo di farlo sbagliare meno.
15. **Capire prima di ottimizzare.**

## Integrità dei dati

16. **L'insieme di test non seleziona nulla.** Iperparametri, varianti e
    checkpoint si scelgono sull'insieme di validazione; il test si tocca una
    volta, per il numero finale.
17. **Statistiche di normalizzazione dal solo insieme di addestramento.**
18. **Attenzione alla circolarità**: se il modello riceve in ingresso ciò che la
    verità di riferimento misura in uscita, su quella dimensione il risultato è
    un limite superiore, non una prestazione. Va dichiarato ogni volta.
19. **Non si ottimizza per un singolo benchmark**: ciò che ne risulta misura il
    benchmark, non il problema.

## Riproducibilità

20. **Semi e sorgenti di casualità fissati e dichiarati.**
21. **Configurazione fuori dal codice**, versionata insieme al risultato che ha
    prodotto.
22. **Ogni numero riportato deve essere rintracciabile**: quale configurazione,
    quale esecuzione, quale file. Un numero senza provenienza non è citabile.
23. **Non si rilancia un esperimento** per riavere un numero che esiste già in un
    log o in un riepilogo.

## In questo progetto

**L'ipotesi corrente** è una sola, ed è quella di
[D1](../../../docs/eval/protocollo.md): il framework riduce il **costo in
contesto** di un task, a parità di esito. È falsificabile per costruzione — se
la riduzione mediana è sotto soglia, o se il tasso di successo peggiora,
l'ipotesi è smentita e si scrive che è smentita.

**Insiemi.** `docs/eval/task.md`: 24 task previsti, stratificati in 8 categorie,
estratti dai transcript reali e mai inventati. Ne sono compilati 3. Due
condizioni: **A** installazione completa, **B** `CLAUDE.md` con le sole sezioni
di progetto — B sa del progetto quanto A, così la variabile isolata è il
**metodo** e non la conoscenza.

**Metrica primaria:** token di contesto per task = `input + cache_creation +
cache_read`, sommati su tutti i rami. **Cosa nasconde:** `cache_read` è circa il
95% dei totali grezzi, quindi un «totale token» misura il caching, non il
metodo. Nessuna cifra in euro: le quattro tariffe sono diverse e cambiano, e il
CSV le tiene separate apposta.

**Baseline:** la condizione B. Non esiste una baseline esterna.

**Circolarità note e dichiarate:** i task escono dai transcript dell'utente, e
quelli delle sessioni in cui si costruiva il framework sono **esclusi apposta**
— altrimenti si misurerebbe il framework su sé stesso. Il rumore delle misure
non è ancora stimato: è ciò che il pilota sui primi task deve dare.

**Le esecuzioni pesanti le lancia l'utente**, non un agente: ogni coppia sono due
sessioni nuove di Claude Code, in ordine alternato, perché una cache calda
sposta i token da `cache_creation` a `cache_read` e falserebbe il confronto.

**I risultati si scrivono** in `docs/eval/risultati/<id-task>-<A|B>.csv`, grezzi,
mai modificati a mano. L'analisi va in `docs/eval/esito.md`, e si pubblica
**anche se negativa**.
