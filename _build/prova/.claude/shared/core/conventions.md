# Convenzioni

Regole trasversali di forma. Il metodo di lavoro sta altrove: qui c'è solo come
si scrivono le cose.

## Commit

- **Solo su richiesta esplicita dell'utente.**
- Messaggi in inglese, imperativi, prima riga ≤ 72 caratteri: `Fix …`, `Add …`,
  `Remove …`.
- Un commit = un cambiamento logico. Mai refactoring e funzionalità insieme: il
  primo nasconde il secondo in revisione.
- Il corpo spiega **perché**, non cosa: il cosa è nel diff.
- Mai riscrivere una storia già condivisa, mai forzare un invio, mai saltare i
  controlli automatici.

## Ambito di una modifica

- Solo ciò che è richiesto; il resto si segnala nel report invece di farlo.
- Refactoring, aggiornamenti di dipendenze e riformattazioni di massa sono task
  separati: mescolati ad altro rendono il diff illeggibile.
- Non toccare artefatti generati: si rigenerano, non si modificano a mano.

## Nomi

- Un nome dice **cosa è o cosa fa**, non come è implementato. Un nome che
  contiene il tipo o la struttura invecchia al primo cambiamento.
- Coerenza prima di eleganza: se il progetto chiama una cosa in un modo, la si
  chiama così ovunque. Due nomi per lo stesso concetto costano più di un nome
  imperfetto.
- Niente abbreviazioni non standard nel dominio.
- I file nuovi seguono la convenzione dei vicini, non una preferenza personale.

## Commenti

- Spiegano **vincoli non evidenti**: perché questa scelta invece di quella ovvia,
  quale caso limite ha imposto una riga strana, quale riferimento esterno impone
  un formato.
- Mai cronaca di ciò che la riga sotto già dice.
- Un commento che descrive codice cambiato è peggio di nessun commento: si
  aggiorna insieme al codice o si toglie.
- Codice commentato «per dopo» non si lascia: o serve, o si elimina.

## Documentazione

- I cambiamenti visibili all'utente vanno annotati dove il progetto li annota.
- Un contratto versionato che cambia impone di aggiornare la versione e dirlo.
- La documentazione che descrive comportamento va verificata contro il codice
  reale prima di scriverla: è il punto in cui le due cose divergono in silenzio.

## Qualità minima non negoziabile

- La build passa dopo ogni task.
- Nessun avviso nuovo introdotto consapevolmente senza segnalarlo.
- Nessuna gestione di errore vuota aggiunta: gestire o propagare, con contesto.
- Niente codice morto «per dopo»: o serve ora, o non si aggiunge.

## In questo progetto

Lingua: codice e commit in inglese. Struttura: logica riusabile in `src/logtail/core/`, interfaccia a riga di comando in `src/logtail/cli/`. `dist/` e `*.egg-info/` sono generati. I cambiamenti visibili all'utente vanno in `CHANGELOG.md`.
