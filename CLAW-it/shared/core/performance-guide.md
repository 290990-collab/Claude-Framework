# Guida alle prestazioni

Come si misura e si ottimizza codice con una soglia di prestazione dichiarata. Senza soglia vale solo il primo punto dell'ordine di ottimizzazione.

## Misura

- **Nessuna affermazione di velocità senza misura:** un numero stimato a memoria o letto da un'etichetta non è un dato.
- **Percentili, non medie:** p50, p95 e p99 su più esecuzioni, con la dispersione. Il valore migliore e l'esecuzione singola non sono misure.
- **Metriche separate:** latenza, throughput, freschezza del dato, profondità delle code, successo della cache, correttezza sotto carico. «Veloce» non è una metrica.
- **Input rappresentativo:** volume e forma dei dati reali, non il caso ideale.

## Percorso caldo

- **Si scrive il percorso dall'evento allo stato visibile, a segmenti:** sorgente, ingresso, coda, cache, trasporto, resa.
- **Ogni segmento si misura da solo:** il totale dice che si perde tempo, non dove.

## Ordine di ottimizzazione

1. **Complessità prima della costante:** un `O(N²)` dove serviva `O(N log N)` conta più di qualunque micro-ottimizzazione.
2. **Via i giri di andata e ritorno non necessari.**
3. **Cache delle letture stabili, con la loro età.**
4. **Chiamate e scritture piccole raggruppate.**
5. **Calcolo vicino ai dati o a chi li usa.**
6. **Percorso caldo separato dal freddo.**
7. **Contropressione prima che una coda cresca senza limite.**

## Guardrail

- **La correttezza viene prima:** nessuna ottimizzazione toglie una validazione obbligatoria o mette a rischio l'integrità dei dati.
- **Nessun dato vecchio nascosto dietro una cache veloce:** la lettura porta la sua età, e oltre la soglia lo dice.
- **Ogni ottimizzazione ha un prezzo dichiarato:** leggibilità, memoria, complessità.
- **Log e artefatti di misura senza segreti né dati privati.**

## In questo progetto

[DA COMPILARE — le operazioni con una soglia e il suo valore, il percorso caldo scritto a segmenti, il comando che misura in modo riproducibile, le ottimizzazioni già scartate con la motivazione.]
