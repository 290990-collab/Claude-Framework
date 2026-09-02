---
name: framework-doctor
description: >
  Verifica l'integrità di un'installazione del framework: segnaposto non
  compilati, roster incoerente con la tabella di routing, guide mancanti, drift
  della regione kernel, file di stato assenti. Da usare quando qualcosa non torna,
  dopo modifiche a mano al framework, o prima di aggiornarlo.
---

# Diagnosi di un'installazione

```bash
cd <FW>/tools && python -m fwbuild doctor --strict <PRJ>
```

`<FW>` è il campo `source` di `.claude/framework.json`; se il file manca,
`./framework/`. Quel campo può essere **relativo alla root del progetto** —
`source.dereference(<PRJ>, source)` lo scioglie. `<PRJ>` è la root del progetto.
I sottocomandi di `fwbuild` sono **quattro**: `doctor`, `source`, `cost` e
`report`. Le modalità di `framework-sync` (`--down`, `--up`, `--activate`,
`--deactivate`) sono invece di quella skill, non flag da shell.

Un'installazione completa stampa `OK — nessun rilievo`. Senza `--strict` l'uscita
è 0 anche con soli avvisi: usalo sempre, in CI e a mano.

`--json` stampa gli stessi rilievi più la misura di `CLAUDE.md` in una struttura
sola, per la CI: l'exit code non cambia.

## Come si legge ogni rilievo

### `PLACEHOLDER` — ERRORE

Un blocco `[DA COMPILARE]` o un `{{segnaposto}}` è rimasto non compilato.
L'agente che lo legge riceve istruzioni al posto di direttive.

**Cosa fare:** apri il file, leggi cosa il segnaposto chiede di scrivere, e
compilalo con le direttive reali del progetto. Se l'informazione non c'è,
chiedila all'utente — non inventarla.

### `ROSTER_MISSING` — ERRORE

Un agente è citato nella tabella di routing di `.claude/shared/orchestration.md`
(o di `CLAUDE.md`, se quella guida non c'è) ma il file non esiste
in `.claude/agents/`. Il coordinatore proverà a delegare a qualcosa che non c'è.

**Cosa fare:** o installi l'agente (`framework-sync --activate <nome>`, che
prende la versione corrente dal master), o togli la riga dalla tabella.

### `ROSTER_ORPHAN` — AVVISO

Il file dell'agente esiste ma non compare nella tabella di routing. L'agente
esiste, costa contesto a ogni sessione, e non verrà mai scelto.

**Cosa fare:** o lo aggiungi alla tabella, o lo disattivi
(`framework-sync --deactivate <nome>`). Nessuna eccezione: un agente installato
che non è in tabella o è di troppo, o la tabella è incompleta.

### `SHARED_MISSING` — ERRORE

Un file installato — `CLAUDE.md`, un agente, una guida — punta a una guida che
non è stata installata. Un pointer rotto è peggio di un pointer assente:
l'agente ci prova e non trova nulla. Il rilievo dice **da quale file** parte.

Caso particolare: **`.claude/shared/orchestration.md` assente** mentre esistono
agenti installati. È la guida del coordinatore — senza, chi delega non ha né le
regole di delega né la tabella di routing, e il doctor non può nemmeno
verificare il roster.

**Cosa fare:** copia la guida da `<FW>/shared/` e compilane il blocco di
progetto, oppure togli il pointer. Per `orchestration.md`, rigenerala assemblando
`<FW>/coordinator/` e aggiungendo la tabella di routing del progetto.

### `SHARED_ORPHAN` — AVVISO

Una guida è installata in `.claude/shared/` e nessun file la cita. È contesto che
il progetto si porta dietro e non apre mai: costo senza uso, l'inverso esatto di
`SHARED_MISSING`.

**Cosa fare:** o la citi da dove serve — le guide generiche si elencano in
`CLAUDE.md § Guide condivise`, quelle di ruolo le punta l'agente che le usa — o
la togli dall'installazione.

### `COORDINATOR_LEAK` — AVVISO

`CLAUDE.md` contiene una sezione che appartiene alla guida del coordinatore: le
regole di delega, il ciclo di lavoro, il template del prompt, i livelli di stato,
la disambiguazione fra agenti.

**Perché è un problema.** `CLAUDE.md` è caricato in **ogni** contesto, compreso
quello di ogni subagent. Un `explorer` su Haiku che va a cercare una funzione
paga il ciclo del codice e i quattro livelli di stato, e non può usarne nulla —
non delega e non scrive lo stato. Su una sessione con dieci spawn è puro sperpero
sul file più caro del sistema.

**Cosa fare:** sposta la sezione in `.claude/shared/orchestration.md` e lascia in
`CLAUDE.md` al massimo un pointer di una riga. Se il contenuto serve davvero a
chi esegue e non solo a chi delega, allora riscrivilo come obbligo di esecuzione
— è un'altra cosa, e sta in `<FW>/method/`.

⚠️ Il check confronta i **titoli**, non il senso: la stessa sezione riformulata
sotto un altro titolo non lo fa scattare. Sulla fuga di contenuto vale la
lettura, il rilievo copre solo i sei titoli noti.

### `KERNEL_MISSING` — ERRORE

I marker della regione kernel sono spariti da un file che ne ha una per
costruzione — `CLAUDE.md`, `orchestration.md`, un agente. **È più grave di un
drift:** con i marker sparisce il controllo, e il metodo riscritto a mano
diventa indistinguibile da quello generato. Non scatta se **nessun** file
tracciato ha marker: quella è l'installazione senza tracking, ed è una scelta.

**Cosa fare:** riassembla il file con `framework-sync --down`, dopo aver
confrontato il contenuto attuale col sorgente — dentro potrebbe esserci una
modifica che vale la pena promuovere.

### `KERNEL_DRIFT` — AVVISO, e non è un errore

La regione kernel è stata modificata a mano. **Questa è informazione, non un
guasto.** Il framework non vieta di modificare il metodo: rende la modifica
visibile.

**La domanda giusta da porre all'utente è una sola:**

> «Hai modificato il metodo in `<file>`. È un miglioramento che vale per tutti i
> progetti — quindi lo promuovo nel sorgente — o è una deroga specifica di questo
> progetto?»

- **Miglioramento** → `framework-sync --up`: risale nel sorgente, incrementa
  la versione, e il prossimo progetto nasce con dentro. È la direzione che nei
  framework precedenti non esisteva, ed è il motivo per cui il metodo si era
  biforcato in quattro versioni diverse.
- **Deroga locale** → si annota nel progetto perché il prossimo che legge il
  rilievo sappia che è voluta.

Non «correggere» mai un drift riscrivendoci sopra senza aver posto quella
domanda: butteresti via una modifica che qualcuno aveva ragione di fare.

### `VERSION_MISMATCH` — AVVISO

Le regioni kernel del progetto non dichiarano tutte la stessa versione, oppure il
progetto è a una versione diversa dal sorgente. **Nessun altro rilievo lo vede:**
su un metodo vecchio l'hash torna, perché torna su quello vecchio. È la
biforcazione fra progetti, cioè il difetto che il framework esiste per evitare.

**Cosa fare:** `framework-sync --down`, su **entrambi** i documenti versionati e su
ogni agente installato. Uno scarto fra un singolo agente e il resto è normale
subito dopo un `--activate`, che prende il master corrente: si chiude con lo
stesso `--down`.

### `SETTINGS_MISSING` — AVVISO

`.claude/settings.json` non c'è, ma il progetto ha agenti installati. È il file
che porta i permessi del profilo — fra cui il divieto di leggere `.env`, chiavi e
certificati: senza, quel divieto non è in vigore e nessuno se ne accorge.

**Cosa fare:** rigeneralo serializzando `Profile.settings` del profilo del
progetto, come al Passo 5 dell'installazione.

### `SKILLS_MISSING` — AVVISO

`framework-doctor` o `framework-sync` non sono in `.claude/skills/`: esistono nel
sorgente ma non sono invocabili in questo progetto. Nessuno se ne accorge finché
non servono — cioè quando qualcosa è già andato storto.

**Cosa fare:** copiale da `<FW>/skills/` in `.claude/skills/`. Non serve
adattarle: sono file di framework, si copiano alla lettera.

### `STATE_MISSING` — ERRORE

Manca uno fra `docs/TODO.md`, `docs/status.md`, `docs/roadmap.md`.

**Cosa fare:** copia il template mancante da `<FW>/templates/`. Senza il
livello 1, ogni sessione riparte a indovinare.

### `FABLE` — ERRORE

È stato generato `model: fable`. Quel modello non è disponibile: l'agente non
parte.

**Cosa fare:** sostituire con `model: opus`. Per `architect`, `effort: xhigh`.

### `EXCLUSIVE` — ERRORE

`deploy` e `infra` sono installati insieme. Coprono lo stesso spazio con
posture opposte — pubblicazione semplice contro infrastruttura definita come
codice — e la sovrapposizione produce routing ambiguo.

**Cosa fare:** scegli quale descrive davvero questo progetto e disattiva l'altro.

### `TOKEN_BUDGET` — AVVISO

Le sezioni di progetto di `CLAUDE.md` hanno superato in parole la regione
kernel. Il tetto che rompe la build sta sul **sorgente** e vincola solo il
metodo; `CLAUDE.md` assemblata è invece ciò che ogni subagent paga a **ogni
spawn**, e la parte che l'installazione scrive non aveva nessuna soglia — ed è
la sola che cresce, perché cresce col progetto.

La soglia è il kernel stesso, cioè l'unica grandezza nota: *il progetto non
scrive più del metodo*. Non viene da una misura di efficacia — non ne esiste
una — è una scelta a giudizio, e va trattata come tale. Sotto il tetto che il
framework si dà per il solo metodo il rilievo tace: su un file piccolo il
rapporto è vero e irrilevante.

**Cosa fare:** non tagliare a caso. Sposta in `.claude/shared/` ciò che serve a
pochi agenti e lasciane il pointer, togli quello che il repository già dice da
sé (struttura ricavabile, comandi già in un `Makefile` o in `package.json`), e
tieni in `CLAUDE.md` solo ciò che un agente non può dedurre: vincoli duri,
contratti con chi li consuma, superficie critica. Se dopo il taglio il file
resta sopra soglia perché il progetto è davvero grande, è un avviso da
accettare consapevolmente, non un errore.

Per tradurlo in una cifra: `python -m fwbuild cost <PRJ> --spawns N --devs N`.

### `REPORT_FORMAT` — AVVISO

Lo schema del report installato porta ancora la confidenza come percentuale. È
il formato precedente: una precisione finta nel campo che il coordinatore legge
per primo, mentre la confidenza auto-riportata da un modello è mal calibrata.

Nessun altro rilievo lo vede: l'hash della regione kernel torna, perché torna su
quel testo lì, e la versione dichiarata è quella con cui il progetto è nato.

**Cosa fare:** `framework-sync --down`. Il formato attuale è categorico e porta
con sé il falsificatore (`SMENTIRE`), che è ciò che rende leggibile un giudizio
senza numeri.

## Più progetti insieme

```bash
cd <FW>/tools && python -m fwbuild report <cartella-di-repository>
```

`doctor` risponde «questa installazione regge?». `report` risponde a una domanda
che il singolo non si pone e chi ha quaranta repository sì: **quante versioni del
metodo sono in giro, e dove**. Cerca `.claude/framework.json` sotto i percorsi
dati (due livelli, `--depth` per cambiarli), chiama il doctor su ognuno e mette
in fila versione, rilievi e dimensione della `CLAUDE.md`.

Il riferimento è la versione del **sorgente** da cui giri, non la più diffusa:
la maggioranza non è un riferimento. `--strict` esce 1 se un progetto diverge o
ha rilievi; `--json` dà lo stesso rapporto per la CI.

## Dopo la diagnosi

Riporta all'utente: quanti rilievi per gravità, cosa hai corretto, cosa richiede
una sua decisione. I `KERNEL_DRIFT` si elencano sempre, anche quando tutto il
resto è pulito: sono la parte utile del rapporto.
