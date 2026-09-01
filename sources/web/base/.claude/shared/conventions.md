# Convenzioni — Portfolio

Regole trasversali per ogni agente e ogni modifica. (Lingua: vedi CLAUDE.md —
italiano con l'utente, inglese nel codice e nei commit; documentazione utente
nello stile dei documenti esistenti.)

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
- Non toccare artefatti generati: `node_modules/`, `.next/`, `out/`, `dist/`,
  build di deploy, coverage/report.

## File e struttura

Mappa "tipo di codice → cartella":

- Logica pura (filtro/ordinamento/correlati/formattazione, caricamento contenuti) → `lib/`.
- Design tokens e primitive di stile → `design/`.
- Componenti UI riusabili → `components/`.
- Rotte, layout, pagine, metadata → `app/`.
- Contenuti dei progetti (MDX/dati) → `content/` (letti solo via `lib/`).
- Asset statici → `public/`.

- Nuovi file: naming dei vicini (convenzione TypeScript/React e pattern esistente).
  Codice condiviso tra viste va estratto in `components/` o `lib/`, mai duplicato.
- Un solo componente per ruolo: prima di crearne uno nuovo, cerca se esiste già.

## Documentazione delle modifiche

- Cambiamenti visibili all'utente → riga nel `CHANGELOG.md` (se esiste, stile esistente).
- Cambi a un contratto (schema contenuti, slug/URL, chiavi token) → annotarlo e,
  per gli slug, predisporre il redirect.

## Qualità minima non negoziabile

- `pnpm build` passa dopo ogni task; `pnpm typecheck`/`pnpm lint` puliti.
- Nessun warning nuovo introdotto consapevolmente senza segnalarlo.
- Nessun `catch`/handler vuoto nuovo: gestire o loggare con contesto, come il file ospite.
- Niente codice morto "per dopo": o serve o non si aggiunge.
- Nessun valore di stile hardcoded dove esiste (o serve) un token.
