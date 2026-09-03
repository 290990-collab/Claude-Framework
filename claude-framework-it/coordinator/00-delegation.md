# Orchestrazione — guida del coordinatore

Contenuto **azionabile solo da chi delega**. I subagent non lo leggono: per loro
vale ciò che sta in `CLAUDE.md`, che non contiene nulla di tutto questo proprio
per non farglielo pagare a ogni spawn.

> Da leggere a inizio sessione **se la sessione prevede delega**. Per una
> modifica da due file la tabella di routing in fondo basta.

## Chi fa cosa

Il coordinatore pianifica, delega, verifica e integra. Esegue **direttamente**
solo le modifiche piccole a basso rischio — ≤2-3 file, poche decine di righe,
nessun contratto toccato: lì delegare costa più che fare.

I subagent eseguono un task e riportano. Non spawnano nulla. Quando un report
apre una domanda fuori dal mandato di chi l'ha scritto, la domanda torna al
coordinatore: non si passa lateralmente da un agente all'altro.

## Economia dei token — le dieci regole della delega

Lista canonica e completa. Vive **solo qui**: gli obblighi di chi esegue sono
un'altra cosa e stanno in `CLAUDE.md`, non sono un sottoinsieme rinumerato di
queste.

1. **Parallelismo.** `architect` uno alla volta, mai in parallelo con altri
   agenti né rilanciato sullo stesso task: è il più costoso e ragiona
   sull'intero contesto. Gli altri agenti su modello Opus in sequenza; max 2 in
   parallelo solo su task **indipendenti** (file disgiunti, nessun output
   incrociato — altrimenti si pagano due volte le stesse letture e i risultati
   vanno riconciliati a mano). Parallelismo libero solo per `explorer`.
   Il vincolo è legato al **ruolo**, mai a un modello: un vincolo che nomina un
   modello muore col modello.
2. **Modello al task, non al ruolo.** Niente `architect` per decisioni ovvie né
   `debugger` per cause evidenti. Su lavoro meccanico e senza giudizio, declassa
   il modello dello spawn a Sonnet (override per-spawn: cambia il modello,
   l'effort della scheda resta). Solo dove non ci sono decisioni non banali: un
   modello troppo debole sbaglia e il giro a vuoto costa più del premium.
3. **Contesto pre-digerito agli agenti costosi.** `explorer` (dentro il repo) e
   `api-scout` (fuori dal repo) esplorano una volta a costo basso e consegnano
   estratti pronti — firme, righe attorno al punto, `file:riga` esatti — così
   l'agente caro legge poco a prezzo pieno. Meglio un explorer accurato in più
   che un agente caro a caccia su file interi.
4. **Passa i range, non i file.** Nel prompt vanno gli estratti e i `file:riga`
   esatti; l'agente che li riceve è tenuto a non allargare la lettura.
5. **Prompt digerito per primacy/recency.** Struttura obbligatoria in
   `20-prompt.md`. Mai seppellire un `file:riga` nella prosa.
6. **Load-on-demand, non front-loading.** Ciò che non è universale sta dietro un
   pointer che l'agente recupera se serve, non pre-caricato nel prompt.
7. **Un task per agente**, con criterio di completamento esplicito. Niente task
   ombrello «sistema tutto»: producono report vaghi e lavoro non verificabile.
8. **Continuare, non ri-spawnare.** Per un secondo giro — l'implementer dopo i
   finding del reviewer, l'explorer a cui serve un dettaglio in più — si riusa
   l'agente con il contesto intatto: ripartire da freddo ri-digerisce tutto da
   capo. È la regola che più spesso viene dimenticata, ed è fra le più care.
9. **Una sola review**: il revisore finale **oppure** una skill di review nativa,
   mai entrambe. Le skill native pesanti si lanciano solo su richiesta
   dell'utente.
10. **Niente ri-verifiche ridondanti anche per interposto agente.** L'obbligo
    vale per chi esegue; qui vale in più che non si spawna un agente per
    rifare una verifica già passata e ancora valida.
