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

`--down`, `--up`, `--activate`, `--deactivate` sono **modalità di questa skill**, non flag da shell: `fwbuild` ha `doctor`, `source`, `cost` e `report`. Il rapporto di divergenza su più repository — `python -m fwbuild report <cartella>` — è invece da shell: legge molti progetti e non ne modifica nessuno.

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
6. **Verifica** con `doctor`: deve uscire con 0.

**I conflitti si presentano, non si risolvono da soli:** su una regione modificata localmente l'utente deve vedere entrambe le versioni e decidere.

---

## `--up` — promuovere una modifica locale nel sorgente

1. **Individua la modifica:** `doctor` la segnala come `KERNEL_DRIFT`; il contenuto si ottiene confrontando la regione kernel del progetto col sorgente corrispondente.
2. **Chiedi se vale per tutti.** Un miglioramento del metodo sale, una deroga specifica di quel progetto no: la domanda va posta all'utente, non decisa.
3. **Applica al sorgente**, e la scelta della destinazione è **per destinatario**:

   | la modifica riguarda… | va in |
   |---|---|
   | ciò che vale per chiunque esegua un task | `<FW>/method/` |
   | quando delegare, a chi, con che prompt, lo stato del progetto | `<FW>/coordinator/` |
   | il mandato di un ruolo specifico | `<FW>/agents/<nome>.md` |
   | materiale di consultazione di un dominio | `<FW>/shared/` |

   Sbagliare qui costa: una regola di delega in `method/` la pagano tutti i subagent a ogni spawn senza poterla usare; una regola di esecuzione in `coordinator/` non la vedrà mai chi esegue.
4. **Incrementa `<FW>/VERSION`:** correzione → patch; regola nuova o riformulata → minor; cambio strutturale → major.
5. **Dichiara cosa è cambiato**, così chi aggiorna sa cosa riceve.
6. **Riallinea il progetto di origine** con `--down`, perché l'hash torni.

⚠️ **Una traduzione di questo sorgente è un sorgente a sé**, col proprio `VERSION`: `--up` non la raggiunge. Una regola che vale in ogni lingua va portata a mano anche là — finché non lo è, le due edizioni dicono cose diverse.

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
4. **Permessi** — rigenera `.claude/settings.json` da `Profile.settings` del profilo nuovo.

Poi aggiorna `profile` in `framework.json`. Saltarlo lascia il progetto a dichiarare un campo che non ha più: la prossima manutenzione rigenera i permessi sbagliati e nessun rilievo se ne accorge — il file dichiara, non verifica.
