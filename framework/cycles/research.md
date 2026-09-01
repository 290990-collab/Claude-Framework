## Il ciclo della ricerca

Si affianca al ciclo del codice, non lo sostituisce. Qui il prodotto non è
«software che gira»: è **evidenza riproducibile**. Un programma che gira e
produce numeri sbagliati è un fallimento completo, non un successo parziale.

**Ipotesi → Protocollo → Esecuzione → Analisi → Conclusione.**

1. **Ipotesi** esplicita e **falsificabile**, con il meccanismo atteso e una
   previsione *per dimensione* — «mi aspetto che salga X e **non** Y, perché…».
   Non «proviamo se va meglio»: una previsione articolata rende informativo anche
   l'esito negativo, mentre una generica rende inutile anche quello positivo.
2. **Protocollo** (`architect`): baseline dichiarata, **una sola variabile**,
   criterio di successo deciso **prima** di guardare i risultati, costo stimato,
   cosa si riusa invece di ricalcolare.
3. **Esecuzione**: se è pesante la lancia **l'utente**, non l'agente. L'agente
   prepara il comando esatto e scrive in `docs/TODO.md` la riga di attesa con
   *cosa deve rispondere* quell'esecuzione.
4. **Analisi** (`results-analyst`): confronto appaiato, delta contro rumore,
   lettura per dimensione, e **perché** — mai solo «è salito».
5. **Conclusione**: ipotesi **confermata o smentita**, scritta come tale in
   `docs/status.md`. Le smentite valgono quanto le conferme e si registrano con
   la stessa cura: non registrarle significa ripagarne il costo fra due mesi.

⚠️ **I due cicli si intrecciano**: spesso si cambia il codice **per** misurare
qualcosa. In quel caso l'`architect` produce un piano con entrambe le sezioni, e
la revisione finale include lo `scientific-reviewer` — che va **prima** del
`final-reviewer`, perché «il codice è corretto» e «il numero significa quello che
diciamo» sono due domande diverse.

**Non si rilancia** un'esecuzione per riavere un numero già presente in un log o
in un riepilogo: si legge da lì. Vale anche per il coordinatore che delega.
