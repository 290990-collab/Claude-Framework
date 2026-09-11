# Orchestrazione — guida del coordinatore

Contenuto azionabile **solo dal coordinatore**. I subagent NON leggono questo file.

> Da leggere a inizio sessione **se la sessione delega**. Per una modifica da due file basta la tabella di routing in fondo.

## Chi fa cosa

- **Coordinatore:** pianifica, delega, verifica e integra.
- **Esecuzione diretta:** modifiche piccole (≤2-3 file, poche decine di righe, nessun contratto toccato) si eseguono direttamente: delegare costa di più.
- **Subagent:** eseguono il task e riportano al coordinatore. Non spawnano subagent né comunicano lateralmente: una domanda fuori mandato torna al coordinatore.

## Economia dei token — le dieci regole della delega

Lista canonica e completa, vive **solo qui**. Gli obblighi di chi esegue stanno in `CLAUDE.md` e sono un'altra cosa, non un sottoinsieme rinumerato di queste.

1. **Parallelismo per ruolo e per costo** — il vincolo nomina ruoli e fasce di costo, mai un modello: un vincolo che nomina un modello muore col modello.
   - `architect`, e ogni agente che decide per l'intero lavoro: uno solo. Mai in parallelo, mai rilanciato sullo stesso task: due controllori collidono.
   - Modello leggero: parallelismo libero.
   - Modello intermedio: pochi insieme, solo se il parallelo accorcia davvero il percorso.
   - Modello di punta: in sequenza. Due insieme solo se il task lo esige — giudizi indipendenti su file disgiunti — mai per fare prima.
   - Il parallelo non abbassa il costo, lo concentra: la finestra d'uso dell'utente si esaurisce prima e il lavoro si interrompe a metà.
2. **Agente e modello al task, non al ruolo:** niente `architect` per decisioni ovvie né `debugger` per cause evidenti. Il modello della scheda è il default e lo spawn lo sposta: più leggero per task meccanici, privi di decisioni o a basso rischio; di punta per un esecutore che deve prendere decisioni che nessuno ha preso sopra (l'effort della scheda resta). Un modello troppo debole sbaglia, e il giro a vuoto costa più del premium: un modello leggero regge «trova ed elenca», non «classifica».
3. **Pre-digerire il contesto:** ciò che un comando raccoglie per intero (ricerca, test, doctor) non si chiede a un modello. Poi `explorer` (repo) o `api-scout` (librerie, servizi, docs) a costo basso per estrarre `file:riga` e firme precise, e gli estratti vanno agli agenti costosi. **Scansionare non è lavoro del contesto principale:** compito ampio, risposta stretta, nessun giudizio delegato («di N file, quali toccano X» → una tabella) va a `explorer` anche quando farlo da sé sembra più rapido, perché il coordinatore costa di più per token e si tiene il rumore per tutta la sessione. Resta a te ciò di cui il **giudizio** è il prodotto, non la scansione che lo precede.
4. **Passa range, non file:** nel prompt solo estratti e `file:riga` esatti; chi li riceve non allarga la lettura.
5. **Struttura del prompt:** tassativa, sezione «Come si scrive un prompt di delega». Istruzioni ai bordi, dati ed estratti al centro.
6. **Load-on-demand:** passa i pointer a risorse e guide. L'agente le apre se e quando servono.
7. **Un task per agente,** con criterio di completamento verificabile. Zero task ombrello («sistema X»). Si spezza solo ciò che non entra in un contesto: la profondità è un esito, non un piano.
8. **Riuso della sessione, mai ri-spawn:** l'agente che ha il contesto di un task — lo stesso o uno successivo sugli stessi file — si riprende col delta, e non si chiude finché quel contesto serve: ripartire da freddo ridigerisce tutto. Riprenderlo paga però l'intera sua trascrizione: un delta di poche righe lo applica il coordinatore.
9. **La revisione minima che serve:** un revisore, un giro — il revisore finale **oppure** una skill di review nativa, mai entrambe; le native pesanti solo su richiesta dell'utente. I finding li corregge chi ha il quadro — il coordinatore, o l'agente ancora aperto che ha scritto quel codice — mai uno spawn nuovo. Le correzioni le verifica il coordinatore coi test e sul delta. Secondo giro solo per un rilievo che blocca e la cui correzione cambia il piano: stesso revisore, solo il delta; se blocca ancora, decide l'utente.
10. **Zero ri-verifiche inutili:** non spawnare agenti per rieseguire build/test appena passati se nulla è cambiato.
