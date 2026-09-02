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

Il framework vive in due posti: il **sorgente** (il master) e le
**installazioni** (i progetti). Questa skill è ciò che li tiene collegati.

Requisito: il sorgente deve essere raggiungibile dalla macchina. Se non lo è,
solo `doctor` è utilizzabile.

`--down`, `--up`, `--activate`, `--deactivate` sono **modalità di questa skill**,
non flag da shell: `fwbuild` ha `doctor`, `source`, `cost` e `report`. Il
rapporto di divergenza su più repository è `python -m fwbuild report <cartella>`
— quello sì da shell, perché legge molti progetti e non ne modifica nessuno.
I frammenti qui sotto partono da `<FW>/tools`, dove `<FW>` è il campo `source` di
`.claude/framework.json` (se manca, `./framework/`) e `<PRJ>` la root del
progetto. Quel campo può essere **relativo alla root del progetto**, non alla
directory da cui giri: scioglilo con `source.dereference(<PRJ>, source)`.

---

## `--down` — portare una versione nuova nel progetto

Aggiorna il metodo preservando l'adattamento.

1. **Confronta le versioni.** Quella del progetto sta nel marker della regione
   kernel; quella del sorgente in `<FW>/VERSION`.
2. **Esegui prima la diagnosi.** Se ci sono `KERNEL_DRIFT`, vanno risolti
   *prima*: aggiornare sopra una modifica locale la cancella in silenzio.
3. **Riassembla** con il metodo nuovo e le sezioni di progetto esistenti, che si
   estraggono dall'installazione corrente e si riscrivono invariate.

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

4. **Stessa operazione per `.claude/shared/orchestration.md`**, con il kernel da
   `<FW>/coordinator/`: sono due documenti versionati, non uno. Aggiornarne
   uno solo li lascia disallineati. Lì i cicli di dominio stanno **dentro** la
   regione e il progetto non registra da quale profilo è nato: vanno ripassati,
   o spariscono senza che nessun rilievo lo veda —
   `extra=assemble.installed_cycles(region.body, Path('..'))`.
5. **Stessa operazione per ogni agente installato**, con `split_source` e
   `build_agent`: il frontmatter e il blocco `## Contesto di progetto` restano
   quelli del progetto, il metodo viene dal master.
6. **Verifica** con `doctor`: deve uscire con 0.

**I conflitti si presentano, non si risolvono da soli.** Se una regione era stata
modificata localmente, l'utente deve vedere entrambe le versioni e decidere.

---

## `--up` — promuovere una modifica locale nel sorgente

È la direzione che mancava, e la sua assenza è il motivo per cui il metodo si era
biforcato in quattro versioni divergenti.

1. **Individua la modifica**: `doctor` la segnala come `KERNEL_DRIFT`; il
   contenuto si ottiene confrontando la regione kernel del progetto con il
   sorgente corrispondente.
2. **Chiedi se vale per tutti.** Un miglioramento del metodo sale; una deroga
   specifica di quel progetto no. La domanda va posta all'utente, non decisa.
3. **Applica al sorgente**, e la scelta della destinazione è **per destinatario**:

   | la modifica riguarda… | va in |
   |---|---|
   | ciò che vale per chiunque esegua un task | `<FW>/method/` |
   | quando delegare, a chi, con che prompt, lo stato del progetto | `<FW>/coordinator/` |
   | il mandato di un ruolo specifico | `<FW>/agents/<nome>.md` |
   | materiale di consultazione di un dominio | `<FW>/shared/` |

   Sbagliare qui costa: una regola di delega messa in `method/` la pagano tutti
   i subagent a ogni spawn senza poterla usare; una regola di esecuzione messa
   in `coordinator/` non la vedrà mai chi esegue.
4. **Incrementa `<FW>/VERSION`**: correzione → patch; regola nuova o
   riformulata → minor; cambio strutturale → major.
5. **Dichiara cosa è cambiato**, così chi aggiorna sa cosa sta ricevendo.
6. **Riallinea il progetto di origine** con `--down`, perché ora l'hash torni.

⚠️ **Se esiste l'overlay di traduzione**, una modifica al metodo lo disallinea.
Va annotato: una traduzione ferma a una versione vecchia diventa il nuovo
sorgente fossile.

---

## `--activate <agente>` / `--deactivate <agente>`

**Attivare** copia l'agente dal master alla **versione corrente**, compila il suo
blocco `## Contesto di progetto`, e aggiunge la riga alla tabella di routing in
`.claude/shared/orchestration.md` — mai in `CLAUDE.md`: il routing è contenuto
da coordinatore.

Attivare più tardi è *meglio* che aver tenuto un file dormiente: si prende sempre
l'ultima versione, invece di una ferma al giorno dell'installazione.

**Disattivare** rimuove il file da `.claude/agents/` e la riga dal routing. **Il
master non si tocca.** Se l'agente aveva un blocco di progetto compilato con
informazioni non ricostruibili, salvalo prima di rimuoverlo.

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
