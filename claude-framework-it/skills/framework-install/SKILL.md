---
name: framework-install
description: >
  Installa e adatta il framework in un progetto: rileva se il progetto è vuoto o
  ha già del codice, fa il questionario, sceglie il roster di agenti, genera
  CLAUDE.md, gli agenti attivi, le guide e i file di stato, e verifica il
  risultato. Da usare una volta per progetto: `/framework-install`.
---

# Installazione e adattamento del framework

Sei il coordinatore: leggi un progetto, fai domande, decidi un roster, compili contenuti. Il tooling fa solo il meccanico — assemblaggio, hash, verifiche.

**Non installi nulla** (pacchetti, dipendenze, estensioni) in nessun passo. Se qualcosa sembra mancare, lo segnali e chiedi.

---

## Passo 0 — Trova e valida il sorgente

Il sorgente sta in uno di questi posti, **in quest'ordine**: `./framework/` (copiato nel progetto), `$CLAUDE_FRAMEWORK`, `~/.claude/framework/`. Prendi il **primo che esiste** — non il primo che funziona — e validalo:

```bash
cd <FW>/tools && python -m fwbuild source ..
```

Stampa root e versione, oppure cosa manca ed esce 1.

**Se esce 1, fermati qui:** niente cartelle, niente file — un sorgente sbagliato scoperto a metà lascia un progetto peggiore di uno vergine. Chiedi all'utente dov'è il framework e riprova con quel percorso. **Trovato ma incompleto è un errore, non un motivo per provare il successivo.**

Da qui `<FW>` è la root validata e `<PRJ>` la root del progetto: sostituiscili coi percorsi reali, non lasciarli letterali.

## Passo 1 — Rileva il tipo di installazione

```bash
ls -A | head -50
```

- **Progetto vuoto** (o solo configurazione): l'adattamento parte da un'**idea**, che l'utente descrive a parole → Passo 3.
- **Codebase esistente:** l'adattamento parte dal **codice** → Passo 2.

## Passo 2 — Ricognizione a costo basso (solo se c'è codice)

**Non leggere il repository tu:** delega a `explorer`. Prompt nella struttura obbligatoria:

```
TASK: mappare questo repository per adattare un framework di lavoro.

DONE QUANDO: hai consegnato, in forma compatta:
  1. linguaggi e stack, con le versioni dove dichiarate
  2. mappa "cartella → responsabilità" dei moduli reali (non generati)
  3. comandi di build, test, avvio — presi dai file di configurazione, non dedotti
  4. punti di ingresso
  5. presenza o assenza di: interfaccia utente, pipeline di dati,
     configurazione di pubblicazione, test, documentazione
  6. contratti visibili: API pubbliche, formati persistiti, schemi
  7. cosa sembra rilevante ma è generato o di terze parti

VINCOLI:
  - sola lettura, nessuna modifica
  - non aprire artefatti pesanti o cartelle di dipendenze
  - se un comando non è dichiarato da nessuna parte, dillo invece di inventarlo

DONE QUANDO: i 7 punti sopra, in forma compatta, con file:riga dove serve.
```

Repository grande → più `explorer` in parallelo su sottoalberi disgiunti: è l'unico agente a parallelismo libero.

## Passo 3 — Questionario

**Una domanda alla volta**, non un blocco unico: ogni risposta può cambiare le successive. Proponi opzioni concrete e una raccomandazione motivata dal codice o dall'idea.

### Sempre — quattro domande

**1. Campo del progetto** → profilo in `<FW>/profiles/`:

| profilo | quando |
|---|---|
| `software` | applicazioni, servizi, strumenti a riga di comando, desktop |
| `library` | librerie e pacchetti: il contratto pubblico è il prodotto |
| `web` | siti e applicazioni dove la resa visiva è parte del prodotto |
| `research` | il prodotto è evidenza riproducibile, non software che gira |
| `data` | pipeline di acquisizione, trasformazione, indicizzazione |

Se nessuno calza, chiedi all'utente di descrivere il campo e costruisci il roster a mano dal profilo più vicino.

**2. Superficie critica** — *«qual è la superficie critica di questo lavoro, cioè cosa lo rende sbagliato anche a codice perfetto?»* Determina il revisore, e se ne attiva **uno**.

Il profilo ne dichiara già una in `critical_surface`: è quella del **campo**, nota prima del progetto. Leggila all'utente come punto di partenza, non come risposta data, e falla confermare, restringere o sostituire — un progetto può averne una che il suo campo non implica.

| risposta | revisore |
|---|---|
| **Sicurezza** — qualcuno potrebbe abusarne | `security-reviewer` |
| **Validità scientifica** — le conclusioni potrebbero non reggere | `scientific-reviewer` |
| **Qualità dei dati** — potrebbero essere sbagliati a monte | `data-quality-reviewer` |
| **Normativa e licenze** — dati personali, licenze delle dipendenze, obblighi di legge | `compliance-reviewer` |
| **Prestazioni** — solo se il requisito è dichiarato e misurabile | `perf-analyst` |

Due revisori solo se il progetto ha davvero due superfici critiche distinte.

**Se la risposta non è in tabella** — contratto pubblico, accessibilità, costo operativo — **non si inventa un agente**: sarebbe un ruolo pagato da tutti per un caso solo. La superficie si scrive in due posti: la sezione *Superficie critica* di `CLAUDE.md`, e il contesto di progetto di `final-reviewer`, come una riga «qui verificato significa anche». Il punto 4 della sua checklist copre già consumatori esterni e contratti; ciò che senza quella riga non sa è **quale** superficie, qui, viene prima delle altre.

**3. Stile delle risposte in chat**, su **due assi indipendenti**:

*Forma* — telegrafica (conclusione prima, zero prosa) · sintetica ma completa (default) · esplicativa (si spiega sempre il **perché**) · discorsiva.

*Base di conoscenza assunta* — cosa dare per noto e cosa introdurre alla prima comparsa. È l'asse che conta di più, perché dice **cosa non spiegare**. Chiedilo così: *«cosa dovrei dare per scontato che sai già, e cosa preferisci che ti spieghi ogni volta?»*

**4. Autonomia** — cosa si può fare senza chiedere. Default conservativo: **nulla di tutto questo**. Commit · pubblicazione · installazione di dipendenze · esecuzioni lunghe o costose · modifiche irreversibili.

### Condizionali — solo per ciò che il profilo non installa già

**Chiedi solo di agenti che il roster non ha.** Calcolalo prima (Passo 4) e salta le domande già risolte: una domanda che non può cambiare niente insegna all'utente che il questionario è una formalità.

C'è un'interfaccia? → `frontend` · Entrano dati esterni? → `data-ingestion` ·
Ci sono misure da interpretare? → `results-analyst` · Serve letteratura o
scrittura accademica? → `literature` · Il progetto va pubblicato, e con hosting
semplice o infrastruttura definita come codice? → `deploy` **oppure** `infra`,
mai entrambi · Ci sono operazioni pesanti che lancia l'utente e non l'agente? →
va nei comandi.

Vincoli normativi e requisiti di prestazione stanno nella **domanda 2**: sono superfici critiche, non contorni del profilo.

## Passo 4 — Roster e installazione selettiva

Si installa **solo l'attivo**. Il master resta in `<FW>/agents/`: un agente non scelto non è cancellato, è *non ancora installato*, e si aggiunge più tardi già aggiornato con `framework-sync --activate`. Motivo: nome e `description` di ogni file in `.claude/agents/` entrano nel contesto del coordinatore a ogni sessione.

**Sei non si tolgono** — `explorer`, `architect`, `implementer`, `tester`, `refactorer`, `final-reviewer`: sono il ciclo del codice, e `drop` li ignora di proposito. Tutti gli altri sono opzionali e si riprendono con `--activate`.

I comandi partono da `<FW>/tools`: lì la root del framework è `..`, quella del progetto è `<PRJ>`.

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import profile
prof = profile.load(Path('../profiles/<PROFILO>.toml'))
print(profile.roster(prof, extras=[], drop=[]))
print('conflitti:', profile.check_exclusive(profile.roster(prof, [], [])))
"
```

## Passo 5 — Generazione

Si generano **due** documenti con regione kernel, non uno. La differenza è il destinatario:

| documento | sorgente del kernel | chi lo legge | costo |
|---|---|---|---|
| `CLAUDE.md` | `<FW>/method/` | **tutti**, a ogni spawn | pagato sempre |
| `.claude/shared/orchestration.md` | `<FW>/coordinator/` | solo chi delega | on-demand |

**Mai in `CLAUDE.md`:** tabella di routing, ciclo di lavoro, regole di delega, livelli di stato. Sono istruzioni che un `tester` o un `explorer` paga a ogni spawn senza poterle usare, e il doctor le rileva (`COORDINATOR_LEAK`).

### `CLAUDE.md` — sezioni di progetto

```
[REGIONE KERNEL da <FW>/method/]

## Il progetto
descrizione in una riga · mappa "path → ruolo" · vincoli DURI (violarli
invalida il lavoro, non solo il codice) · contratti, con chi li consuma

## Comandi
build, test, avvio · verifica rapida che fa l'agente · operazioni pesanti che
lancia l'utente, con cosa deve riportare

## Superficie critica
qual è la superficie critica — cosa rende il lavoro sbagliato anche a codice
perfetto — e chi la rivede. Parte da `prof.critical_surface` e dalla risposta
alla domanda 2: se coincidono si scrive una riga sola, se divergono valgono
entrambe

## Stato attuale
vuoto alla nascita — è il livello 3 dello stato auto-aggiornante

## Guide condivise
prima riga: `orchestration.md`, solo per il coordinatore e per primo se la
sessione delega. Poi **una riga per guida installata**: cosa contiene — la si
copia dalla riga sotto il titolo della guida, non la si inventa — e quando
aprirla. Un elenco di soli percorsi non è consultabile: per decidere se aprirla
bisogna già sapere cosa c'è dentro

## Stile delle risposte
forma e base di conoscenza assunta, dalle risposte al Passo 3
```

### `.claude/shared/orchestration.md` — sezioni di progetto

```
[REGIONE KERNEL da <FW>/coordinator/]

## Roster di questo progetto
tabella GENERATA dal roster reale, mai copiata: | Situazione | Agente | Modello |
una riga per ogni agente installato, nessuno escluso.
**Le colonne sono un contratto**, non una scelta di stile: il doctor legge il
nome dell'agente fra backtick nella **seconda**. Invertirle produce un roster
tutto orfano e nomi che non esistono

## Note di delega per questo progetto
operazioni che lancia l'utente e non l'agente · vincoli di parallelismo
specifici · quando saltare un passo del ciclo
```

### Assemblaggio

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import assemble
F = Path('..'); V = (F/'VERSION').read_text(encoding='utf-8').strip()
P = Path('<PRJ>')
for d in ('.claude/shared', '.claude/agents', '.claude/skills', 'docs'):
    P.joinpath(d).mkdir(parents=True, exist_ok=True)
P.joinpath('CLAUDE.md').write_text(
    assemble.build_document(F/'method', V, SEZIONI_PROGETTO), encoding='utf-8')
P.joinpath('.claude/shared/orchestration.md').write_text(
    assemble.build_document(F/'coordinator', V, SEZIONI_ROSTER), encoding='utf-8')
"
```

**Agenti attivi** — per ciascuno: leggi il sorgente con `assemble.split_source`, **compila il blocco `## Contesto di progetto`** con le direttive specifiche (ogni segnaposto dichiara cosa metterci), riassembla con `assemble.build_agent`, scrivi in `.claude/agents/`.

**Cicli di dominio** — se il profilo dichiara `cycles`, i file di `<FW>/cycles/` si accodano alla regione kernel della guida del coordinatore (`extra=assemble.cycle_files(...)`): sono orchestrazione, non esecuzione, quindi mai in `CLAUDE.md`.

**Guide** — copia da `<FW>/shared/` quelle del profilo **più quelle che gli agenti scelti citano**, compilando anche lì il blocco di progetto. Un extra porta le sue: senza, la scheda esce con un pointer morto che il doctor vede solo a installazione già scritta (`SHARED_MISSING`).

```python
sorted(set(prof.shared) | set(profile.required_guides(F, roster)))
```

**Skill di ciclo di vita** — copia `<FW>/skills/framework-doctor` e `framework-sync` in `.claude/skills/`. Senza, non sono invocabili e il doctor lo segnala (`SKILLS_MISSING`).

**`.claude/settings.json`** — serializza `Profile.settings` in JSON.

**`.claude/framework.json`** — `source`, `version`, `profile`: è come le due skill ritrovano il sorgente, e l'unico posto in cui resta scritto **di cosa** è fatta l'installazione. Senza il profilo, «rigenera i permessi del profilo del progetto» non è eseguibile. La forma **non la scrivi tu**: `source.manifest` rende il percorso relativo quando il sorgente sta dentro il progetto e assoluto solo quando sta fuori — un assoluto su un sorgente interno è la macchina di chi ha installato, e muore al primo clone.

```python
source.manifest(PRJ, FW, version, prof.name)
```

Il campo `accepted` **non si scrive all'installazione**: nasce vuoto e lo aggiunge chi decide di convivere con un avviso (→ skill `framework-doctor`).

**File di stato** — copia i tre template in `docs/` e compila **subito** ogni blocco `[DA COMPILARE — …]`: prima voce e primo passo in `TODO.md` con la data di oggi, primo obiettivo col suo criterio in `roadmap.md`. `status.md` nasce vuoto per costruzione — ci si scrive quando qualcosa si chiude. Le sezioni che possono restare vuote (in attesa, bloccati, decisioni aperte) non hanno segnaposto: portano già il testo giusto e si sostituisce quando ci sarà qualcosa. Va fatto qui: al Passo 6 un segnaposto residuo è un `PLACEHOLDER`, e `TODO.md` è il file che ogni sessione futura legge per primo.

### Nota sugli `@import`

Se `CLAUDE.md` supporta gli `@import` nella versione di Claude Code in uso, l'assemblaggio potrebbe restare virtuale. **Va verificato, non assunto:** il default è la concatenazione fisica, che non dipende da nessuna funzionalità dell'harness. Non introdurre `@import` senza averli verificati.

## Passo 6 — Verifica

```bash
cd <FW>/tools && python -m fwbuild doctor --strict <PRJ>
```

Deve stampare `OK — nessun rilievo` e uscire con 0. `--strict` rende meccanica la regola: **finché resta un rilievo, di qualunque gravità, l'installazione non è completa.** Cosa significa ogni codice: skill `framework-doctor`.
