---
name: framework-sync
description: >
  Allinea un'installazione con il framework sorgente: porta giù una versione
  nuova del metodo preservando l'adattamento, promuove su una modifica locale
  perché il prossimo progetto la erediti, attiva o disattiva un agente. Da usare
  quando esce una versione nuova o quando una modifica locale merita di diventare
  generale.
---

# Sincronizzazione con il sorgente

Collega il **sorgente** (il master) alle **installazioni** (i progetti). Requisito: il sorgente dev'essere raggiungibile dalla macchina; se non lo è, solo `doctor` è utilizzabile.

`--down`, `--up`, `--upgrade`, `--activate`, `--deactivate` sono **modalità di questa skill**, non flag da shell: `fwbuild` ha `doctor`, `source`, `cost` e `report`. Il rapporto di divergenza su più repository — `python -m fwbuild report <cartella>` — è invece da shell: legge molti progetti e non ne modifica nessuno.

I frammenti partono da `<FW>/tools`. `<PRJ>` è la root del progetto; `<FW>` è il campo `source` di `.claude/framework.json` (se manca, `./framework/`), che può essere **relativo alla root del progetto**, non alla directory da cui giri: scioglilo con `source.dereference(<PRJ>, source)`.

---

## `--down` — portare una versione nuova nel progetto

Aggiorna il metodo preservando l'adattamento.

1. **Confronta le versioni:** quella del progetto sta nel marker della regione kernel, quella del sorgente in `<FW>/VERSION`.
2. **Diagnosi prima.** I `KERNEL_DRIFT` vanno risolti *prima*: aggiornare sopra una modifica locale la cancella in silenzio.
3. **Riassembla** col metodo nuovo e le sezioni di progetto esistenti, estratte dall'installazione corrente e riscritte invariate.

```bash
cd <FW>/tools && python -c "
from pathlib import Path
from fwbuild import assemble, kernel
p = Path('<PRJ>/CLAUDE.md')
text = p.read_text(encoding='utf-8')
region = kernel.parse(text)
sezioni = text[region.end:].lstrip('\n')          # l'adattamento, invariato
version = Path('../VERSION').read_text(encoding='utf-8').strip()
p.write_text(assemble.build_document(Path('../method'), version, sezioni), encoding='utf-8')
"
```

4. **Stessa operazione su `.claude/shared/orchestration.md`**, col kernel da `<FW>/coordinator/`: i documenti versionati sono **due**, aggiornarne uno solo li lascia disallineati. Lì i cicli di dominio stanno **dentro** la regione e il progetto non registra da quale profilo è nato: vanno ripassati con `extra=assemble.installed_cycles(region.body, Path('..'))`, o spariscono senza che nessun rilievo lo veda.
5. **Stessa operazione su ogni agente installato**, con `split_source` e `build_agent`: frontmatter e blocco `## Contesto di progetto` restano del progetto, il metodo viene dal master.
6. **Aggiorna `version` in `.claude/framework.json`**, lasciando `source`, `profile` e `accepted` come sono. Nessun passo lo faceva: il manifesto restava a dichiarare la versione di prima, ed è l'unica leggibile senza aprire un documento generato. Il doctor ora lo vede (`VERSION_MISMATCH`).
7. **Verifica** con `doctor`: deve uscire con 0.

**I conflitti si presentano, non si risolvono da soli:** su una regione modificata localmente l'utente deve vedere entrambe le versioni e decidere.

---

## `--up [cosa]` — promuovere una modifica locale nel sorgente

**Precondizione: il progetto dev'essere allineato al sorgente.** Se `version` in `.claude/framework.json` non è quella di `<FW>/VERSION`, prima `--down`, poi la promozione. Da un progetto rimasto indietro la regione locale differisce dal sorgente per **due** motivi — la tua modifica, e quella che un altro progetto ha già promosso — e il passo 1 non li distingue: promuovere in blocco cancella la seconda in silenzio. Allineato vuol dire che base e sorgente coincidono, ed è la sola condizione in cui un confronto a due alberi è corretto.

`[cosa]` nomina **una** modifica. Senza argomento, elenca ciò che è promovibile e procedi **una cosa alla volta**: il passo 2 va posto caso per caso, e una promozione in blocco quella domanda non la può porre.

1. **Individua la modifica:** `doctor` la segnala come `KERNEL_DRIFT`; il contenuto si ottiene confrontando la regione kernel del progetto col sorgente corrispondente. **Il drift non vede i file nuovi:** una regione kernel ce l'hanno solo `CLAUDE.md`, `orchestration.md` e le schede agente, quindi elenca anche i file che stanno in `.claude/shared/` o `.claude/agents/` del progetto e mancano dal sorgente. Una guida aggiunta a mano è promovibile e nessun rilievo la nomina.
2. **Chiedi se vale per tutti.** Un miglioramento del metodo sale, una deroga specifica di quel progetto no: la domanda va posta all'utente, non decisa.
3. **Applica al sorgente**, e la scelta della destinazione è **per destinatario**:

   | la modifica riguarda… | va in |
   |---|---|
   | ciò che vale per chiunque esegua un task | `<FW>/method/` |
   | quando delegare, a chi, con che prompt, lo stato del progetto | `<FW>/coordinator/` |
   | il mandato di un ruolo specifico | `<FW>/agents/<nome>.md` |
   | materiale di consultazione di un dominio | `<FW>/shared/` |

   Sbagliare qui costa: una regola di delega in `method/` la pagano tutti i subagent a ogni spawn senza poterla usare; una regola di esecuzione in `coordinator/` non la vedrà mai chi esegue.
4. **Registra la base, se non c'è già**, **prima** di toccare `VERSION`:

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   F = Path('..')
   if upgrade.read_record(F) is None:
       print(upgrade.write_record(F, (F/'VERSION').read_text(encoding='utf-8').strip(),
                                  '<EDIZIONE>', '<URL del repository>'))
   "
   ```

   Da qui in avanti `VERSION` non è più un numero pubblicato, e senza questa riga nessuno sa più da quale release il sorgente veniva: è la sola cosa che rende recuperabile il tuo lavoro al prossimo aggiornamento (→ `--upgrade`). **Se il record c'è già non si tocca:** la base resta quella, per quante promozioni tu faccia.
5. **Incrementa `<FW>/VERSION`:** correzione → patch; regola nuova o riformulata → minor; cambio strutturale → major.
6. **Dichiara cosa è cambiato**, così chi aggiorna sa cosa riceve.
7. **Riallinea il progetto di origine** con `--down`, perché l'hash torni.

⚠️ **Una traduzione di questo sorgente è un sorgente a sé**, col proprio `VERSION`: `--up` non la raggiunge. Una regola che vale in ogni lingua va portata a mano anche là — finché non lo è, le due edizioni dicono cose diverse.

---

## `--upgrade` — portare una release nuova sopra un sorgente modificato

Serve solo a chi ha usato `--up`: un sorgente intatto si aggiorna sostituendolo. L'assenza di `upstream.json` **è** quella risposta, non un guasto.

1. **Prendi la release nuova** dove non disturba, e da lì `<NEW>` è la cartella di edizione dentro il clone:

   ```bash
   git clone <repo> <NEW>   # oppure: git -C <clone esistente> pull
   ```

2. **Ricostruisci la base**, cioè l'edizione com'era alla release da cui il tuo sorgente veniva. `upgrade.base_version(<FW>)` dà il numero; nel clone, la base è il commit in cui `VERSION` di quell'edizione valeva quel numero, estratto dove non tocca niente:

   ```bash
   git -C <NEW> log --format=%H -- <EDIZIONE>/VERSION   # dal più recente
   git -C <NEW> show <commit>:<EDIZIONE>/VERSION        # finché non corrisponde
   git -C <NEW> worktree add --detach <BASE> <commit>
   ```

   **Base sbagliata, confronto inutile:** se nessun commit corrisponde — repository sbagliato, storia troncata, numero mai pubblicato — fermati e chiedi. Non ripiegare su `VERSION`: quella è la risposta giusta solo quando `upstream.json` manca.

3. **Classifica**, senza scrivere niente:

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   plan = upgrade.classify(Path('<BASE>/<EDIZIONE>'), Path('<FW>'), Path('<NEW>/<EDIZIONE>'))
   for nome in ('theirs', 'yours', 'conflict'):
       print(nome, len(getattr(plan, nome)), getattr(plan, nome)[:20])
   "
   ```

   | esito | cosa vuol dire | cosa si fa |
   |---|---|---|
   | `same` | tu e la release dite la stessa cosa — anche quando la tua aggiunta è arrivata a monte identica | niente |
   | `theirs` | l'hai lasciato com'era e a monte è cambiato | si copia dalla release |
   | `yours` | l'hai cambiato tu e a monte no | **si tiene il tuo** |
   | `conflict` | cambiato da tutti e due, in modo diverso | lo decide l'utente |

4. **Mostra il piano prima di applicarlo**, coi conteggi e i percorsi in conflitto. `same`, `theirs` e `yours` sono meccanici: si applicano copiando dalla release i primi, non toccando i secondi.
5. **Un conflitto per volta:** leggi le tre versioni — base, tua, nuova — e proponi una fusione che tenga la tua aggiunta *dentro* il testo nuovo, non accanto. Se la tua modifica è già coperta dal testo nuovo, si prende quello e lo si dice. Nessun conflitto si risolve senza mostrare all'utente cosa perde.
6. **`VERSION` non è un conflitto:** si prende quella della release. Un sorgente che dichiara un numero mai pubblicato è ciò che ha creato il problema.
7. **Riscrivi il record** con la release appena presa: è la base del prossimo aggiornamento.

   ```bash
   cd <FW>/tools && python -c "
   from pathlib import Path
   from fwbuild import upgrade
   F = Path('..')
   print(upgrade.write_record(F, (F/'VERSION').read_text(encoding='utf-8').strip(),
                              '<EDIZIONE>', '<URL del repository>'))
   "
   ```

8. **Chiudi con `--down` sui progetti**, che ora sono indietro di una versione, e con `doctor` su ciascuno.

⚠️ Il sorgente si aggiorna **sul posto**: prima di applicare, copialo da parte. È l'unica operazione della skill che tocca il master, e non ha un annulla.

---

## `--activate <agente>` / `--deactivate <agente>`

**Attivare** copia l'agente dal master alla **versione corrente**, compila il suo blocco `## Contesto di progetto` e aggiunge la riga alla tabella di routing in `.claude/shared/orchestration.md` — mai in `CLAUDE.md`: il routing è contenuto da coordinatore.

Forma obbligatoria della riga, perché il doctor la legge:

```
| Situazione | `nome-agente` | Modello |
```

Il nome sta fra backtick nella **seconda** colonna. Altrove, quell'agente risulta `ROSTER_ORPHAN` e la tabella cita un `ROSTER_MISSING` che non esiste.

Attivare più tardi è *meglio* di un file dormiente: si prende sempre l'ultima versione, non una ferma al giorno dell'installazione.

**Disattivare** rimuove il file da `.claude/agents/` e la riga dal routing. **Il master non si tocca.** Se il blocco di progetto conteneva informazioni non ricostruibili, salvalo prima.

Controlla sempre i conflitti dopo un'attivazione:

```bash
cd <FW>/tools && python -c "
from fwbuild import profile
import pathlib
present = sorted(p.stem for p in pathlib.Path('<PRJ>/.claude/agents').glob('*.md'))
print('conflitti:', profile.check_exclusive(present) or 'nessuno')
"
```

Chiudi sempre con `doctor`.

---

## Cambio di campo

Un progetto non resta dov'è nato: una libreria si fa una demo, uno strumento diventa un servizio. Il campo sta in `profile` dentro `.claude/framework.json`, unico posto che lo sa. Nessuna modalità apposta: sono le stesse quattro operazioni dell'installazione, sul profilo nuovo.

1. **Roster** — `--activate` per ciò che il campo nuovo implica, `--deactivate` per il resto. Controlla i conflitti dopo.
2. **Guide** — copia quelle del profilo nuovo più quelle che gli agenti attivati citano (`profile.required_guides`), e aggiungi la riga in `CLAUDE.md § Guide condivise`: cosa contiene la guida, presa dalla riga sotto il suo titolo. Il doctor pretende che il percorso sia citato (`SHARED_ORPHAN`), non che la riga sia scritta bene: quella è responsabilità di chi installa.
3. **Cicli** — riassembla la guida del coordinatore accodando quelli del campo nuovo (`assemble.cycle_files`), o senza se ne toglie. Stanno **dentro** la regione kernel: nessun rilievo li vede sparire.
4. **Permessi** — rigenera `.claude/settings.json` da `Profile.settings` del profilo nuovo, **unendolo** al file esistente: il `deny` del campo vecchio se ne va, ciò che ha aggiunto l'utente resta. Una rigenerazione secca cancella permessi che nessun profilo ha mai scritto.

Poi aggiorna `profile` in `framework.json`. Saltarlo lascia il progetto a dichiarare un campo che non ha più: la prossima manutenzione rigenera i permessi sbagliati e nessun rilievo se ne accorge — il file dichiara, non verifica.
