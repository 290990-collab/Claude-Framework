# Orchestrazione — guida del main agent

Contenuto **azionabile solo dal coordinatore**: come delegare, con che modello,
in che ordine, e come spendere bene i token. I subagent non lo leggono (non
spawnano nulla): per loro vale ciò che resta in `CLAUDE.md`.

> Da leggere a inizio sessione **se la sessione prevede delega**. Per un task da
> due file la tabella di routing in `CLAUDE.md` basta.

## Economia dei token — regole di delega

1. **Parallelismo.** `architect` **mai** in parallelo con altri agenti né
   rilanciato sullo stesso task: è il più costoso e ragiona sull'intero
   contesto. Gli altri Opus in sequenza; max 2 in parallelo solo su task
   **indipendenti** (file disgiunti, nessun output incrociato — altrimenti si
   pagano due volte le stesse letture e i risultati vanno riconciliati a mano).
   Parallelismo libero solo per `explorer`.
2. **Modello al task, non al ruolo.** Niente `architect` per decisioni ovvie né
   `debugger` per cause evidenti. Su lavoro meccanico e senza giudizio, declassa
   il modello dello spawn a Sonnet (override per-spawn: cambia il modello,
   l'effort dell'agente resta). ⚠️ Solo dove non ci sono decisioni non banali:
   un modello troppo debole sbaglia e il giro a vuoto costa più del premium.
3. **Contesto pre-digerito agli agenti costosi.** L'`explorer` (Haiku) esplora
   una volta e consegna estratti pronti — firma della funzione, righe attorno al
   punto, `file:riga` esatti — così l'Opus legge poco a prezzo pieno. Meglio un
   explorer accurato in più che un agente caro a caccia su file interi.
4. **Prompt digerito per primacy/recency**: task + criterio di completamento in
   cima → vincoli → estratti e `file:riga` → criterio ripetuto in fondo. Mai
   seppellire un `file:riga` nella prosa.
5. **Un task per agente**, con criterio di completamento esplicito. Niente task
   ombrello ("sistema tutto"): producono report vaghi e lavoro non verificabile.
6. **Continuare, non ri-spawnare.** Per un secondo giro (es. `implementer` dopo
   i finding del reviewer) si riusa l'agente con il contesto intatto: ripartire
   da freddo ri-digerisce tutto da capo.
7. **Una sola review**: `final-reviewer` **oppure** `/code-review`, mai entrambe.
   Le skill native pesanti solo su richiesta esplicita dell'utente.
8. **Niente ri-verifiche ridondanti**: smoke test appena passato + nessun file
   cambiato = non si rilancia "per sicurezza".

## Il ciclo del codice

**Capire → Progettare → Implementare → Verificare → Integrare.**

1. `explorer` individua i file rilevanti (economico, parallelizzabile).
2. `architect` se il task tocca ≥3 file o un contratto; richieste ambigue →
   plan mode prima. Altrimenti si salta.
3. `implementer`, **un task alla volta**: completa, verifica, passa al
   successivo.
4. `tester` estende la copertura (invarianti, casi limite) oltre i mini-test
   dell'implementer.
5. `final-reviewer` verifica da zero senza fidarsi dei report. Se il task ha
   cambiato *cosa* o *come* si misura, prima `scientific-reviewer`.
6. Il main agent risolve i finding e integra.

Il main agent esegue **direttamente** le modifiche piccole a basso rischio
(≤2-3 file, poche decine di righe, nessun contratto, nessuna conseguenza sui
numeri): lì delegare costa più che fare.

## Il ciclo della ricerca

**Ipotesi → Protocollo → Run → Analisi → Conclusione.**

1. **Ipotesi** esplicita e falsificabile, con il meccanismo atteso e possibilmente
   una previsione **per-asse** ("mi aspetto che salga la topologia e *non* la
   geometria, perché…"). Non "proviamo se va meglio": una previsione per-asse
   rende informativo anche l'esito negativo.
2. **Protocollo** (`architect`): baseline dichiarata, **una sola variabile**
   (OFAT), criterio di successo deciso *prima*, costo in job/ore, cosa si riusa
   invece di ricalcolare. Dettaglio: `.claude/shared/experiments.md`.
3. **Run**: la lancia l'**utente** via sbatch. L'agente prepara il comando
   esatto e la riga di attesa in `.claude/TODO.md`.
4. **Analisi** (`results-analyst`): confronto appaiato, delta vs rumore, lettura
   per-asse, e *perché* — mai solo "è salito".
5. **Conclusione**: ipotesi **confermata o smentita**, scritta come tale in
   `.claude/shared/status.md`. Qui le smentite (val-loss ≠ retrieval, τ=0.3, "allenare di più")
   hanno insegnato più delle conferme.

⚠️ I due cicli si intrecciano: spesso si cambia il codice **per** misurare
qualcosa. In quel caso l'`architect` produce un piano con entrambe le sezioni, e
la review finale include lo `scientific-reviewer`.

## Scegliere fra agenti che sembrano vicini

| Dubbio | Discriminante |
|---|---|
| `architect` vs `results-analyst` | Il primo decide **cosa misurare** (prima della run), il secondo dice **cosa è emerso** (dopo). Un'analisi che suggerisce il prossimo esperimento passa la palla all'architect, non lo improvvisa |
| `debugger` vs `scientific-reviewer` | Il programma si rompe → `debugger`. Il programma gira ma il **risultato non ha senso** → `scientific-reviewer` |
| `implementer` vs `refactorer` | Cambia il comportamento o aggiunge qualcosa → `implementer`. Comportamento **e numeri** invariati → `refactorer` |
| `final-reviewer` vs `scientific-reviewer` | "Il codice è corretto?" vs "questo numero significa quello che diciamo?" |
| `explorer` vs leggere da sé | Se servono >2 file o non sai dove guardare → `explorer`. Se sai già il path → leggi tu, spawnare costa di più |
