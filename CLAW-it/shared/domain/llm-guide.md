# Guida ai sistemi con LLM

Per i progetti in cui un modello linguistico produce testo, decisioni o azioni che il codice usa. Il modello non sbaglia come il codice: sbaglia in modo plausibile, e a volte perché qualcuno glielo ha chiesto.

## Fiducia

- **L'output del modello è input non fidato:** si valida come un dato esterno — schema, tipi, intervalli, valori ammessi — prima di usarlo, eseguirlo o salvarlo.
- **I limiti duri stanno nel codice, mai nel prompt:** importi, quantità, destinatari, permessi si impongono a valle dell'output, qualunque cosa il modello abbia scritto.
- **Dati esterni in un prompt che può agire sono un'iniezione:** documenti, pagine, nomi, risposte di strumenti portano istruzioni. Dove il modello agisce, entrano delimitati e filtrati, o non entrano.
- **Difese a strati indipendenti:** igiene del prompt, limiti in codice, simulazione prima dell'effetto, isolamento delle credenziali. Nessuno strato basta, e nessuno presuppone che un altro abbia tenuto.

## Agenti

- **I limiti di un agente li fissa il chiamante:** budget, permessi e strumenti si decidono prima della delega; l'agente non li alza e non ha uno strumento per farlo.
- **Strumenti stretti:** input a schema, output a forma fissa, errori che dicono come riprovare e quando fermarsi. Le operazioni ad alto rischio hanno uno strumento proprio.

## Deterministico prima

- **Il modello lavora sul residuo:** ciò che una regola, un parser o una query risolve non passa dal modello; il modello prende solo i casi che il deterministico non copre.
- **La confidenza instrada:** l'estrazione deterministica dichiara quanto è sicura; sopra soglia esce diretta, sotto va al modello o a una persona. La soglia si misura su casi reali.

## Valutazione

- **Valutazione ripetibile prima di toccare il prompt:** un insieme fisso di casi con l'esito atteso, lanciato prima e dopo ogni modifica. Senza, un prompt migliore è un'impressione.
- **Più prove, non una:** l'output varia fra esecuzioni. Si misura quante riescono su k tentativi; sui percorsi critici devono riuscire tutte.
- **Giudice in codice dove basta:** se un controllo deterministico decide l'esito, non lo si chiede a un modello.
- **Ciò che passava resta nell'insieme:** una regressione si vede solo sui casi che funzionavano.

## In questo progetto

[DA COMPILARE — dove il modello entra nel flusso e cosa può fare, quali dati esterni raggiungono i prompt, i limiti imposti in codice e dove vivono, chi fissa permessi e budget degli agenti, l'insieme di valutazione e come si lancia, le iniezioni e gli errori già visti.]
