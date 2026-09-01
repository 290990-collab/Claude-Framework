# Checklist di revisione

Materiale di consultazione per chi rivede. Due blocchi **separati e non fusi**:
il primo vale in ogni progetto, il secondo è di questo progetto. Tenerli distinti
è ciò che permette di aggiornare il framework senza perdere le voci specifiche —
e viceversa.

---

## Blocco generico — correttezza (valido ovunque)

### Ambito

- Le modifiche fanno **tutto** ciò che il task chiedeva?
- Fanno **solo** quello? Lavoro extra non richiesto è un rilievo, anche se è
  buon codice: allarga la superficie di rischio senza mandato.
- Un solo problema affrontato per volta, o più cose intrecciate nello stesso
  cambiamento?

### Valori e confini

- Valori nulli o assenti: gestiti dove possono arrivare, o assunti presenti?
- Collezioni vuote, stringa vuota, zero, valore negativo: cosa succede?
- Indici e intervalli: primo e ultimo elemento, intervallo di un solo elemento,
  intervallo vuoto.
- Conversioni numeriche: troncamenti, superamento dei limiti, virgola mobile usata
  dove serve precisione esatta.
- Testo: encoding dichiarato, caratteri fuori dall'alfabeto latino, lunghezze
  massime, normalizzazione prima del confronto.
- Date e orari: fuso orario esplicito, ora legale, confronti fra istanti con
  rappresentazioni diverse.

### Errori

- Ogni errore è gestito o propagato **consapevolmente**? Nessun blocco di cattura
  vuoto o che nasconde l'eccezione originale.
- Un errore a metà lavoro lascia stato parziale? Se sì, è recuperabile?
- I messaggi di errore dicono abbastanza per diagnosticare, senza rivelare
  dettagli interni o dati sensibili.

### Risorse e concorrenza

- File, connessioni, blocchi: rilasciati anche sul percorso di errore?
- Strutture condivise fra thread o processi: accesso protetto, o corsa possibile?
- Lavoro lungo eseguito dove non blocca ciò che deve restare reattivo.
- Cicli su risorse esterne: c'è un limite, un timeout, un tentativo massimo?

### Regressioni e contratti

- Per ogni simbolo o comportamento modificato: chi lo usa? Cercato anche dove il
  compilatore non guarda — markup, configurazioni, script in altri linguaggi,
  riferimenti per stringa, documentazione.
- I formati già scritti su disco si rileggono ancora?
- I consumatori esterni restano compatibili? Se no, la migrazione è prevista?
- Le firme pubbliche cambiate hanno tutti i lati aggiornati?

### Test

- Esistono, girano, e **fallirebbero** se il difetto tornasse?
- Asseriscono il comportamento o solo che il codice non esplode?
- Coprono il livello a cui il difetto può nascere, non solo l'unità più comoda?

### Verifiche eseguite

- Build eseguita, non dedotta. Test eseguiti, non dedotti. Output reale alla mano.
- Ciò che non è stato verificato è dichiarato come tale, con i passi per farlo.

---

## Blocco di progetto

Verifiche obbligatorie qui: memoria costante durante il follow (un accumulo si vede solo su file grandi); comportamento su file ruotato; encoding non UTF-8; output su pipe oltre che su terminale; codici di uscita invariati.
