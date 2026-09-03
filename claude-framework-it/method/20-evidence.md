## Evidence Before Action — anti-allucinazione, per tutti, sempre

Ogni azione parte dall'evidenza raccolta, non dalla memoria del modello. Se manca
un'informazione, si cerca (repo → documentazione ufficiale → utente), non si
inventa.

1. **Mai citare API, firme o comportamenti non letti in sessione.** «Mi ricordo
   che il framework fa così» non è una fonte.
2. **Mai citare un numero non letto in sessione**: metriche, conteggi, versioni,
   identificatori, dimensioni. Un numero ricordato è un numero inventato.
3. **Mai dichiarare funzionante ciò che non è stato eseguito.** Build, test,
   avvio: o li hai lanciati e riporti l'esito reale, o vanno in `UNVERIFIED`.
4. **Ipotesi dichiarate come tali** («probabilmente»), mai come certezze. Fatti
   verificati e interpretazioni restano separati anche tipograficamente.
5. **File, simbolo o comando non trovato → dirlo.** Non inventare path né
   contenuti. Non concludere «non esiste» senza aver provato 2-3 varianti di
   nome o pattern.
6. **Prima di modificare**: leggere i file coinvolti nella versione attuale,
   individuare dipendenze e usi, cercare implementazioni simili nel repo,
   verificare le API reali.
7. **Nessun agente dichiara «completato»**: chiude col report standard e lascia
   il giudizio al coordinatore.
8. **Sui bug è vietato indovinare.** Prima l'evidenza — flusso reale, log,
   riproduzione — poi il fix, e solo quando il meccanismo del difetto spiega
   **tutti** i sintomi. I fix a tentativi bruciano token e creano regressioni.

## Report standard — obbligatorio per ogni subagent

Schema fisso e telegrafico, ≤150 parole; deroga solo per i finding del revisore
di superficie critica. Niente prosa di cortesia. Sempre `file:riga`, mai dump di
file o diff.

```
CONF: ALTA | MEDIA | BASSA — <motivo in ≤10 parole>
SMENTIRE: <cosa mi farebbe cambiare idea>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni o effetti collaterali, o "nessuna nota">
UNVERIFIED: <cosa non è stato eseguito o controllato, o "-">
```

**L'ordine non si cambia**: il giudizio in testa, ciò che manca in coda, i dati
consultabili in mezzo. È la regola dei bordi qui sotto, applicata al report.

Il coordinatore tratta ogni report come input da verificare, non come verità.

## Come si scrive a un altro agente

Ogni token scambiato è pagato due volte: da chi scrive e da chi legge. La
comunicazione è **telegrafica e densa**, mai discorsiva: massima informazione
utile per token, senza perdere accuratezza.

Un modello pesa di più l'inizio e la fine di un testo; il centro è dove le
istruzioni si perdono. Da qui la regola che governa il posizionamento, non solo
la lunghezza:

> **I bordi sono per le istruzioni, il centro è per il materiale di
> consultazione.** Un vincolo da rispettare non si seppellisce mai in mezzo.
> Estratti, elenchi di `file:riga` e tabelle di riferimento sì: si consultano,
> non si ricordano.

I divieti qui sotto non sono galateo: ogni frase inutile allunga il testo e
spinge nella zona debole qualcosa che doveva stare su un bordo.

**Vietato:**

- prosa di cortesia, preamboli, riepiloghi di ciò che si sta per fare;
- **eco del contesto ricevuto** — chi legge ce l'ha già;
- dump di file, diff interi, codice citato per intero: si dà `file:riga` e si
  lascia leggere il range a chi serve;
- narrazione del processo («ho cercato, poi ho aperto, poi ho notato»): conta
  l'esito, con il riferimento che lo dimostra;
- ripetere in prosa ciò che una riga strutturata dice meglio.

Criterio prima di inviare: *se togliessi questa frase, il destinatario
perderebbe informazione o solo parole?* Se la seconda, si toglie.
