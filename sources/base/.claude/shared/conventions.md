# Convenzioni — {{PROGETTO}}

Regole trasversali per ogni agente e ogni modifica. (Lingua: vedi CLAUDE.md
— italiano con l'utente, inglese nel codice e nei commit; documentazione
utente nello stile dei documenti esistenti.)

## Commit

- Solo su richiesta esplicita dell'utente.
- Messaggi in inglese, imperativi, prima riga ≤ 72 caratteri, stile di
  `git log --oneline` ("Fix ...", "Add ...").
- Un commit = un cambiamento logico; mai refactoring e feature insieme.
- Mai `--no-verify`, push forzati o amend di commit già pushati.

## Ambito

- Solo ciò che è richiesto; il resto si segnala nel report.
- Refactoring = task separato (`refactorer`).
- Niente aggiornamenti di dipendenze/versioni non richiesti.
- Non toccare artefatti generati: [DA COMPILARE — cartelle di output del
  progetto, es. `dist/`, `publish/`].

## File e struttura

[DA COMPILARE] — mappa "tipo di codice → cartella" del progetto (es.
logica riusabile → `<modulo core>`; UI/integrazione OS → `<modulo app>`;
script embedded → `<path>`; build → `<path>`, installer → `<path>`).

- Nuovi file: naming dei vicini (convenzione del linguaggio e pattern
  esistente).

## Documentazione delle modifiche

- Cambiamenti visibili all'utente → riga nel `CHANGELOG.md` (stile
  esistente).
- Cambi a un contratto versionato (protocolli, formati) → aggiornare la
  versione e annotarlo.

## Qualità minima non negoziabile

- `{{BUILD_CMD}}` passa dopo ogni task.
- Nessun warning nuovo introdotto consapevolmente senza segnalarlo.
- Nessun `catch`/handler vuoto nuovo: gestire o loggare con contesto, come
  il file ospite.
- Niente codice morto "per dopo": o serve o non si aggiunge.
