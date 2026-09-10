# Orchestrazione — guida del coordinatore

Contenuto azionabile **solo dal coordinatore**. I subagent NON leggono questo file.

> Da leggere a inizio sessione **se la sessione delega**. Per una modifica da due file basta la tabella di routing in fondo.

## Chi fa cosa

- **Coordinatore:** pianifica, delega, verifica e integra.
- **Esecuzione diretta:** modifiche piccole (≤2-3 file, poche decine di righe, nessun contratto toccato) si eseguono direttamente: delegare costa di più.
- **Subagent:** eseguono il task e riportano al coordinatore. Non spawnano subagent né comunicano lateralmente: una domanda fuori mandato torna al coordinatore.

## Economia dei token — le dieci regole della delega

Lista canonica e completa, vive **solo qui**. Gli obblighi di chi esegue stanno in `CLAUDE.md` e sono un'altra cosa, non un sottoinsieme rinumerato di queste.

1. **Parallelismo per ruolo** — il vincolo è del ruolo, mai di un modello: un vincolo che nomina un modello muore col modello.
   - `architect`: max 1 alla volta. Mai in parallelo, mai rilanciato sullo stesso task.
   - Altri agenti ad alto reasoning: in sequenza. Max 2 in parallelo SOLO su task e file completamente disgiunti.
   - `explorer`: parallelismo libero.
2. **Agente e modello al task, non al ruolo:** niente `architect` per decisioni ovvie né `debugger` per cause evidenti. Per task meccanici, privi di decisioni o a basso rischio, declassa il modello dello spawn a uno più leggero (l'effort della scheda resta). Un modello troppo debole sbaglia, e il giro a vuoto costa più del premium.
3. **Pre-digerire il contesto:** prima `explorer` (repo) o `api-scout` (librerie, servizi, docs) a costo basso per estrarre `file:riga` e firme precise, poi passa gli estratti agli agenti costosi. **Scansionare non è lavoro del contesto principale:** compito ampio, risposta stretta, nessun giudizio delegato («di N file, quali toccano X» → una tabella) va a `explorer` anche quando farlo da sé sembra più rapido, perché il coordinatore costa di più per token e si tiene il rumore per tutta la sessione. Resta a te ciò di cui il **giudizio** è il prodotto, non la scansione che lo precede.
4. **Passa range, non file:** nel prompt solo estratti e `file:riga` esatti; chi li riceve non allarga la lettura.
5. **Struttura del prompt:** tassativa, sezione «Come si scrive un prompt di delega». Istruzioni ai bordi, dati ed estratti al centro.
6. **Load-on-demand:** passa i pointer a risorse e guide. L'agente le apre se e quando servono.
7. **Un task per agente,** con criterio di completamento verificabile. Zero task ombrello («sistema X»).
8. **Riuso della sessione, mai ri-spawn:** per iterare sullo stesso task manda il delta allo STESSO agente senza chiuderlo. Ripartire da freddo ridigerisce tutto e costa il doppio.
9. **Una sola review:** il revisore finale **oppure** una skill di review nativa, mai entrambe. Le skill native pesanti si lanciano solo su richiesta dell'utente.
10. **Zero ri-verifiche inutili:** non spawnare agenti per rieseguire build/test appena passati se nulla è cambiato.
