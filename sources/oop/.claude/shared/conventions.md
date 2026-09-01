# Convenzioni — AbletonLoader

Regole trasversali per ogni agente e ogni modifica. (Lingua: vedi CLAUDE.md
— italiano con l'utente, inglese nel codice e nei commit; documentazione
utente come il documento esistente.)

## Commit

- Solo su richiesta esplicita dell'utente.
- Messaggi in inglese, imperativi, prima riga ≤ 72 caratteri, stile di
  `git log --oneline` ("Fix ...", "Add ...").
- Un commit = un cambiamento logico; mai refactoring e feature insieme.
- Mai `--no-verify`, push forzati o amend di commit già pushati.

## Ambito

- Solo ciò che è richiesto; il resto si segnala nel report.
- Refactoring = task separato (`refactorer`).
- Niente aggiornamenti di dipendenze NuGet/versioni non richiesti.
- Non toccare `dist/`, `publish/` e artefatti generati.

## File e struttura

- Logica riusabile → `src/AbletonLoader.Core/`; UI e integrazione OS →
  `src/AbletonLoader.App/` (`Services/`, `Views/`); lato Live →
  `remote-script/LiveLoader/`; build → `build/`, installer →
  `installer/`.
- Nuovi file: naming dei vicini (PascalCase per C#, pattern esistente per
  il resto).

## Documentazione delle modifiche

- Cambiamenti visibili all'utente → riga nel `CHANGELOG.md` (stile
  esistente).
- Cambi al protocollo app↔remote script → aggiornare la versione dello
  script e annotarlo.

## Qualità minima non negoziabile

- `dotnet build AbletonLoader.sln` passa dopo ogni task.
- Nessun warning nuovo introdotto consapevolmente senza segnalarlo.
- Nessun `catch` vuoto nuovo: gestire o loggare con contesto, come il file
  ospite.
- Niente codice morto "per dopo": o serve o non si aggiunge.
