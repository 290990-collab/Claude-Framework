# D1 — protocollo dell'eval del metodo

**Scritto il 2026-09-01, prima di qualunque prova.** Il criterio è fissato in
questo file e non si tocca dopo aver visto un risultato: è la regola che
[research-principles.md](../../framework/shared/domain/research-principles.md)
impone agli altri, applicata a sé.

---

## Ipotesi

Il framework riduce il **costo in contesto** di un task, a parità di esito.

Falsificabile: se la riduzione mediana è sotto la soglia, o se il tasso di
successo peggiora, l'ipotesi è smentita e si scrive che è smentita.

## Le due condizioni

| | cosa c'è |
|---|---|
| **A — framework** | installazione completa: kernel comune, `orchestration.md`, roster del profilo, guide, `settings.json` |
| **B — baseline** | `CLAUDE.md` con le **sole sezioni di progetto** — *Il progetto*, *Comandi*, *Superficie critica* — senza regione kernel. Nessun agente in `.claude/agents/`, nessuna guida in `.claude/shared/`, nessun `settings.json` di profilo |

**Perché B è fatta così.** Se la baseline non sapesse del progetto, si
misurerebbe «sapere del progetto», non il metodo. La variabile isolata è il
**metodo**, non la conoscenza: le due condizioni sanno le stesse cose e
lavorano in modo diverso.

## Metriche

Tutte da `python scripts/transcript.py --csv <progetto>`.

- **Primaria — token di contesto per task**: somma su **tutti i rami**
  (coordinatore + ogni subagent) di `input + cache_creation + cache_read`.
- **Secondarie**: `output`, interventi umani, numero di spawn, contesto
  caricato agli spawn, turni, chiamate a tool.

**Perché non un costo in euro.** I quattro tipi di token si pagano a tariffe
diverse, e le tariffe cambiano. Il CSV li tiene **separati apposta**: un costo
si ricava dopo, coi prezzi del giorno, senza rifare le prove.

## Successo di un task

Il campo **«Fatto quando»** scritto in [task.md](task.md) **prima** di
eseguire.

Il giudizio è **alla cieca**: chi valuta vede l'output finale e il criterio, non
la condizione che l'ha prodotto.

## Criterio — deciso ora

1. **Primario.** Mediana di `(token B − token A) / token B` **≥ 35%**, su
   **N ≥ 20** task appaiati.
2. **Guardia.** Tasso di successo di A **non inferiore** a quello di B.

Devono valere **entrambi**. Primario superato e guardia no ⇒ esito **negativo**:
un metodo che costa meno e riesce meno non ha vinto niente.

Se il primario fallisce ma il tasso di successo di A è nettamente migliore,
quella è **un'altra affermazione**. Si registra come osservazione e si progetta
una prova apposta: **non si rimodella questo criterio sui dati**.

## Appaiamento

- Stesso task, **stesso stato di partenza** del repository.
- **Sessione nuova per ogni condizione.** Una cache calda sposta i token da
  `cache_creation` a `cache_read` e falsa il confronto.
- Ordine alternato — A/B su un task, B/A sul successivo — così l'ordine non
  coincide con quanto l'operatore ha imparato del task.
- **Una variabile alla volta.** Nessun'altra differenza fra le due sessioni.

## Cosa invalida una coppia

| motivo | come si verifica |
|---|---|
| `version` di Claude Code diversa fra le due condizioni | campo `version` del transcript |
| `model` diverso | campo `message.model` |
| `effort` diverso | campo `effort` |
| interruzione, errore di rete, `/compact` a metà | annotazione dell'operatore |
| «Fatto quando» modificato dopo aver visto un risultato | la coppia è nulla, e il task esce dal dataset |

I primi tre stanno **nel transcript**: sono verificabili, non dichiarati.

## Layout

```
docs/eval/
  protocollo.md   questo file — il criterio, fissato prima
  task.md         il dataset, col «Fatto quando» di ciascun task
  risultati/      un CSV per prova, grezzo, mai modificato a mano
  esito.md        l'analisi — si scrive dopo, e si scrive comunque
```

## Esecuzione

1. Scegli i task secondo la regola in [task.md](task.md).
2. Per ciascuno: due sessioni nuove, una per condizione, ordine alternato.
3. Dopo ognuna:
   ```bash
   python scripts/transcript.py --csv ~/.claude/projects/<progetto> \
     > docs/eval/risultati/<task>-<A|B>.csv
   ```
4. Giudizio alla cieca sul «Fatto quando».
5. `esito.md`, **anche se negativo**.

## Pubblicazione

Il risultato si pubblica in entrambi i casi. Un eval che esce solo quando
conferma non è un eval: è marketing con i numeri.
