## Il ciclo della ricerca

Si affianca al ciclo del codice, non lo sostituisce. Qui il prodotto non è «software che gira» ma **evidenza riproducibile**: un programma che gira e produce numeri sbagliati è un fallimento completo.

**Ipotesi → Protocollo → Esecuzione → Analisi → Conclusione.**

1. **Ipotesi** esplicita e **falsificabile**, col meccanismo atteso e una previsione *per dimensione* — «mi aspetto che salga X e **non** Y, perché…». Una previsione articolata rende informativo anche l'esito negativo; una generica rende inutile anche quello positivo.
2. **Protocollo** (`architect`): baseline dichiarata, **una sola variabile**, criterio di successo deciso **prima** di guardare i risultati, costo stimato, cosa si riusa invece di ricalcolare.
3. **Esecuzione:** se è pesante la lancia **l'utente**. L'agente prepara il comando esatto e scrive in `docs/TODO.md` la riga di attesa con *cosa deve rispondere* quell'esecuzione.
4. **Analisi** (`results-analyst`): confronto appaiato, delta contro rumore, lettura per dimensione, e **perché** — mai solo «è salito».
5. **Conclusione:** ipotesi **confermata o smentita**, scritta come tale in `docs/status.md`. Le smentite si registrano con la stessa cura delle conferme: non registrarle significa ripagarne il costo fra due mesi.

⚠️ **I due cicli si intrecciano**: spesso si cambia il codice **per** misurare. Allora l'`architect` produce un piano con entrambe le sezioni, e la revisione include lo `scientific-reviewer` **prima** del `final-reviewer` — «il codice è corretto» e «il numero significa quello che diciamo» sono due domande diverse.

**Non si rilancia** un'esecuzione per riavere un numero già presente in un log o in un riepilogo: si legge da lì. Vale anche per il coordinatore che delega.
