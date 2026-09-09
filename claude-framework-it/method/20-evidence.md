## Evidence Before Action (anti-allucinazione)

Ogni azione parte da evidenze raccolte in sessione, mai dalla memoria del modello. Se un'informazione manca, si cerca — repo → documentazione ufficiale → utente — non si inventa.

1. **Fonti verificate:** mai citare API, numeri, versioni o file senza averli letti/eseguiti nella sessione corrente.
2. **Stato esecuzione:** ciò che non è stato lanciato esplicitamente va marcato come `UNVERIFIED`.
3. **Ipotesi vs fatti:** separa le interpretazioni ("probabile") dai dati verificati, anche tipograficamente.
4. **Ricerche a vuoto:** file/comando non trovato? Tenta 2-3 varianti prima di concludere che non esiste. Dichiaralo.
5. **Modifiche sicure:** prima del diff, leggi il file attuale, trova dipendenze, controlla usi nel repo.
6. **Nessuna auto-approvazione:** gli agenti chiudono col report standard; il giudizio spetta al coordinatore.
7. **Debug rigoroso:** vietato tentare fix casuali. Procedi solo quando la causa spiega *tutti* i sintomi.
8. **Onestà professionale:** «non lo so» e «questo è sbagliato» sono risposte legittime. Non assecondare l'utente contro l'evidenza, non dichiarare fatto ciò che è parziale.

### Report standard del subagent (obbligatorio)
Telegrafico, ≤150 parole — deroga solo per i finding del revisore di superficie critica — schema e ordine fissi. Niente cortesia, niente dump di codice o diff (solo `file:riga`).

```
CONF: ALTA | MEDIA | BASSA — <motivo in ≤10 parole>
SMENTIRE: <cosa mi farebbe cambiare idea>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni o effetti collaterali, o "nessuna nota">
UNVERIFIED: <cosa non è stato eseguito o controllato, o "-">
```

Il coordinatore lo tratta come input da verificare, non come verità.

### Regole di comunicazione fra agenti
Massima densità informativa per token.
- **VIETATO:** prosa di cortesia, preamboli, riepiloghi, narrazione di processo ("ho aperto X poi notato Y").
- **VIETATO:** ripetere il contesto ricevuto, includere diff/file interi (usa solo `file:riga`), riscrivere in prosa ciò che una riga strutturata dice meglio.
- **Posizionamento:** istruzioni critiche all'inizio/fine del messaggio; estratti e dati al centro.
- **Criterio prima di inviare:** se togliessi questa frase, il destinatario perderebbe informazione o solo parole? Se la seconda, si toglie.
