<!-- FRAMEWORK:KERNEL v1.0.0 sha256:85497142 — generato, non modificare a mano -->
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
   mai entrambe. Skill native pesanti e agenti a invocazione esplicita solo su
   richiesta dell'utente.
10. **Niente ri-verifiche ridondanti anche per interposto agente.** L'obbligo
    vale per chi esegue; qui vale in più che non si spawna un agente per
    rifare una verifica già passata e ancora valida.

## Il ciclo del codice

**Capire → Progettare → Implementare → Verificare → Integrare.**

1. `explorer` individua i file rilevanti (economico, parallelizzabile);
   `api-scout` se servono firme di librerie esterne.
2. `architect` se il task tocca ≥3 file o un contratto; richieste ambigue → plan
   mode prima. Altrimenti si salta: un piano che il coordinatore scrive in tre
   righe non vale uno spawn.
3. `implementer`, **un task alla volta**: completa, verifica, passa al
   successivo. Test-first quando il comportamento desiderato è esprimibile come
   test (nuove feature, bug fix ben definiti, logica di business o di API).
   Escluso per refactoring, UI, prototipi, dipendenze, documentazione.
4. `tester` estende la copertura oltre i mini-test dell'implementer. Pochi test
   che asseriscono qualcosa di vero, mai molti test deboli.
5. Se il diff tocca la **superficie critica** dichiarata dal progetto, prima il
   revisore di quella superficie; poi `final-reviewer`, che verifica da zero
   senza fidarsi dei report.
6. Il coordinatore risolve i finding e integra. Commit solo su richiesta.

Il ciclo si salta dove non serve: per una modifica piccola a basso rischio lo
esegue direttamente il coordinatore.

## Scegliere fra agenti che sembrano vicini

| Dubbio | Discriminante |
|---|---|
| `explorer` o leggo io | Servono >2 file o non sai dove guardare → `explorer`. Sai già il path → leggi tu: spawnare costa di più |
| `explorer` o `api-scout` | Dentro il repo → `explorer`. Fuori dal repo (librerie, servizi) → `api-scout` |
| `architect` o decido io | Tocca struttura o un contratto → `architect`. Altrimenti è un piano da tre righe, e lo scrivi tu |
| `implementer` o `debugger` | La causa è nota → `implementer`. La causa è ignota → `debugger`, che consegna la diagnosi |
| `implementer` o `refactorer` | Cambia il comportamento o aggiunge → `implementer`. Comportamento osservabile invariato → `refactorer` |
| `implementer` o `frontend` | Decide il cuore del task: viste, markup, stile, movimento → `frontend`; logica e servizi con ritocchi all'interfaccia → `implementer`. Se pesa su entrambi, l'architect lo spezza in due |
| `deploy` o `infra` | Hosting semplice, un push aggiorna → `deploy`. Risorse definite come codice, ambienti multipli → `infra`. Non coesistono |
| revisore critico o `final-reviewer` | «Il codice è corretto?» → `final-reviewer`. «Questo è sicuro / valido / il dato è giusto?» → il revisore della superficie critica, **prima** |

## Come si scrive un prompt di delega

La regola dei bordi — istruzioni ai margini, materiale di consultazione in mezzo
— vale qui più che altrove. Struttura obbligatoria:

```
1. TASK          una frase: cosa fare
2. DONE QUANDO   il criterio di completamento, verificabile
3. VINCOLI       i divieti duri — pochi, espliciti
4. MATERIALE     estratti con file:riga esatti (la parte lunga: sta in mezzo
                 perché si consulta, non perché conta meno)
5. DONE QUANDO   ripetuto, testuale
```

Il criterio si scrive due volte di proposito: apre e chiude. **Se un agente
sbaglia bersaglio, quasi sempre il criterio era implicito o stava in mezzo.**

Regole pratiche:

- **Mai un `file:riga` sepolto nella prosa.** Va in elenco, nel blocco materiale.
- **Vincoli pochi e duri.** Dieci vincoli equivalgono a nessun vincolo: quelli
  che contano vanno scelti, non accumulati.
- **Niente eco e niente contesto che l'agente non userà** — ciò che sta in
  `CLAUDE.md` ce l'ha già, e ogni riga in più spinge verso il centro qualcosa che
  doveva stare su un bordo.
- **Il criterio dev'essere verificabile da chi lo riceve.** «Fai un buon lavoro»
  non è un criterio; «i test in `tests/x.py` passano e la build è pulita» sì.

Per un secondo giro sullo stesso agente vale la regola 8: si continua la
conversazione esistente e si manda **solo il delta** — i finding da risolvere —
non un prompt nuovo che ridigerisce il contesto da capo.

## Lo stato che si aggiorna da solo

Senza uno stato scritto, ogni sessione riparte a indovinare. Quattro livelli,
ognuno con il suo ritmo e il suo tetto.

**Lo scrive il coordinatore.** I subagent riportano e basta: chi scrive lo stato
deve aver visto il quadro intero, e un agente che ha visto un task solo non ce
l'ha. È anche il motivo per cui questa sezione sta qui e non in `CLAUDE.md`.

| Liv. | File | Contiene | Si aggiorna | Tetto |
|---|---|---|---|---|
| 1 | `docs/TODO.md` | dove siamo **adesso**: in corso, in attesa, prossimo passo, bloccati | a **ogni** step | ~60 righe |
| 2 | `docs/status.md` | decisioni chiuse, risultati misurati, ipotesi confermate o smentite | quando qualcosa si chiude | 1 voce |
| 3 | `CLAUDE.md § Stato attuale` | il quadro: cosa sa il progetto oggi | solo se **cambia il quadro** | ~25 righe |
| 4 | memoria persistente | fatti che valgono **fra** sessioni: chi è l'utente, direttive, decisioni | a ogni scoperta o cambio strutturale | 1 file |

**Regole:**

- **Si aggiunge o si spunta, non si riscrive.**
- **Si comprime prima di aggiungere** quando il tetto è raggiunto. La traccia
  lunga scende di livello, non gonfia quello corrente.
- **Inizio sessione:** livello 1 per primo, sempre. **Fine task:** livello 1
  sempre; livello 2 se qualcosa si è chiuso; livello 3 se una conclusione è
  cambiata.
- **Niente duplicazione fra livelli.** TODO = stato, `status.md` = risultati,
  `CLAUDE.md` = quadro, memoria = ciò che sopravvive alla sessione.
- **Operazioni lunghe o asincrone**: appena parte qualcosa che l'utente deve
  lanciare o attendere, la riga va in *In attesa* con cosa deve rispondere.
- ⚠️ Il livello 3 sta dentro la parte di progetto di `CLAUDE.md`, **fuori dalla
  regione kernel**: aggiornarlo non deve mai produrre un rilievo di drift.

**Il livello 4 va rivisitato, non solo riempito.** A ogni cambiamento
significativo — path, contratti, moduli spostati — e a ogni scoperta che chiude o
smentisce un'ipotesi, chiedersi *«questo supera una memoria?»* e, se sì,
correggerla o annotarla come superata **subito**. Anche la memoria è compatta: un
fatto per file, nessun numero duplicato dal repo, nessun path che non esiste più.
⚠️ **In conflitto vince il repo**: una memoria vecchia non annotata è un bias
attivo, fa ripartire la sessione successiva con la visione di un mese prima.
<!-- /FRAMEWORK:KERNEL -->

## Roster di questo progetto

| Situazione | Agente | Modello |
|---|---|---|
| Dove sta / chi usa X | `explorer` | haiku low |
| Design, piani multi-file, contratti | `architect` | opus xhigh |
| Scrivere codice di produzione | `implementer` | opus high |
| Estendere i test | `tester` | sonnet medium |
| Refactoring a comportamento invariato | `refactorer` | opus high |
| Bug a causa ignota | `debugger` | opus high |
| Firme di librerie esterne | `api-scout` | sonnet medium |
| Superficie raggiungibile da un attaccante | `security-reviewer` | opus high |
| Verifica finale | `final-reviewer` | opus high |
| Normativa e licenze — **solo su richiesta** | `compliance-reviewer` | opus high |
| Prestazioni — **solo su richiesta** | `perf-analyst` | opus high |

Gli ultimi due non si spawnano in autonomia: solo se l'utente li chiede.

## Note di delega per questo progetto

Le misure di prestazione su `fixtures/big.log` (2 GB) le lancia l'utente, non
l'agente: preparare il comando e attendere l'output incollato.
