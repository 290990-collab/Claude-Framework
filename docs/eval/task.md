# D1 — dataset dei task

Regole e formato fissati il 2026-09-01, col
[protocollo](protocollo.md). **Il dataset non è ancora completo**: mancano i
task, ed è il passo che richiede una scelta, non un comando.

---

## Da dove vengono i task

**Non si inventano.** «Rappresentativi del lavoro effettivo» non è una qualità
che si possa scrivere a tavolino: o i task vengono dal lavoro fatto, o il
confronto misura un lavoro che nessuno fa.

I transcript archiviati sono il registro di quel lavoro. Il corpus si estrae:

```bash
python scripts/transcript.py --prompts ~/.claude/projects/<progetto>
```

Al 2026-09-01 il corpus disponibile è di **230 richieste umane reali** su
quattro progetti. Le iniezioni di sistema — notifiche di task, output di
comandi, riprese di sessione — sono già scartate dall'estrattore.

## Come si sceglie

**24 task, 3 per categoria.** La stratificazione serve a non misurare il
framework solo dove è forte:

| # | categoria | cosa mette alla prova |
|---|---|---|
| 1 | ricognizione | capire un repo o una sua parte |
| 2 | modifica localizzata | cambio piccolo e circoscritto |
| 3 | bug con sintomo | dal sintomo alla causa |
| 4 | funzionalità su più file | coordinamento |
| 5 | test | scrivere o estendere una suite |
| 6 | revisione | giudizio su codice o documento esistente |
| 7 | decisione di architettura | scelta con conseguenze |
| 8 | stato e documentazione | allineare ciò che è scritto a ciò che è |

Vincoli di scelta:

- **Il task deve essere già stato fatto una volta.** Serve a sapere che è
  fattibile e quanto è costato in condizioni reali.
- **Rieseguibile da uno stato di partenza definito.** Un task che dipende da
  come è finito il precedente non è appaiabile.
- **Nessun task che il framework ha ispirato.** Prendere i task dalle sessioni
  in cui si costruiva il framework misurerebbe il framework su sé stesso.
- **Almeno due progetti diversi**, altrimenti si misura un progetto.

## Formato

Una riga per task. Il **«Fatto quando»** si scrive **prima** di eseguire, ed è
ciò su cui si dà il giudizio alla cieca.

| id | cat | progetto | stato di partenza | richiesta | Fatto quando |
|---|---|---|---|---|---|
| T01 | 2 | Claude Framework | `v1.0.0`, nessuna modifica pendente | «cambia su e giù in up and down, toccando solo il necessario» | I due nomi sono cambiati ovunque siano usati, la suite passa, e nessun file fuori da quelli che li contengono è stato toccato |
| T02 | 6 | Claude Framework | `v1.0.0` | «come valuti la qualità, correttezza e coerenza di framework/?» senza modificare nulla | Il giudizio cita almeno tre file con riga, distingue ciò che ha verificato da ciò che ha dedotto, e non ha scritto niente |
| T03 | 8 | AbletonLoader | ultimo commit su `main` | «a che punto siamo con il lavoro?» | La risposta nomina lo stato reale dei file di stato e non inventa voci che lì non ci sono |
| … | | | | | **da compilare: 21 task** |

## Cosa manca

Ventuno task, scelti dal corpus secondo le regole sopra, ciascuno col suo
«Fatto quando». È lavoro di giudizio: quali task rappresentano davvero il
lavoro, e cosa conta come riuscito. Il tooling ha fatto la parte meccanica —
estrarre il corpus e misurare le sessioni.

Finché questa tabella non è piena, **D1 non è iniziata**: eseguire prove su un
dataset scelto dopo aver visto i primi risultati è esattamente ciò che il
protocollo vieta.
