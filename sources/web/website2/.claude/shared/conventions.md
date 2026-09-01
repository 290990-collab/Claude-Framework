# Convenzioni — FindShop

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
- Non toccare artefatti generati: `node_modules/`, `dist/`, `.next/`,
  `.expo/`, `.turbo/`, build native mobile, client Prisma generato,
  coverage/report.

## File e struttura

Mappa "tipo di codice → cartella":

- Logica di dominio pura → `packages/core`.
- Tipi/schemi condivisi (contratti API) → `packages/shared`.
- Design tokens → `packages/tokens`.
- UI web → `apps/web`; UI mobile → `apps/mobile`.
- API/servizi backend → `apps/api`; pipeline dati negozi → `apps/ingestion`.
- Infrastruttura, deploy, migrazioni → `infra/`.

- Nuovi file: naming dei vicini (convenzione TypeScript e pattern esistente del
  package). Codice condiviso tra più app va in `packages/`, mai duplicato.

## Documentazione delle modifiche

- Cambiamenti visibili all'utente → riga nel `CHANGELOG.md` (stile
  esistente).
- Cambi a un contratto versionato (protocolli, formati) → aggiornare la
  versione e annotarlo.

## Qualità minima non negoziabile

- `pnpm turbo build` (o `--filter=<app>` sul package toccato) passa dopo ogni
  task; `pnpm typecheck`/`lint` puliti.
- Nessun warning nuovo introdotto consapevolmente senza segnalarlo.
- Nessun `catch`/handler vuoto nuovo: gestire o loggare con contesto, come
  il file ospite.
- Niente codice morto "per dopo": o serve o non si aggiunge.
