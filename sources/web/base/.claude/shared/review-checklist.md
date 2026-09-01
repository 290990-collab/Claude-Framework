# Checklist di review — Portfolio

Riferimento esteso per `final-reviewer`. Regola base: **verificare in prima
persona, mai fidarsi dei report degli altri agenti.** Progetto design-first: si
verifica correttezza del codice **e** coerenza col design system.

## 0. Prerequisiti (sempre, prima di tutto)

- [ ] `git status` + `git diff`: il diff reale corrisponde al dichiarato?
      File toccati non dichiarati = finding.
- [ ] Il diff fa ciò che il task chiedeva — tutto e solo quello?
- [ ] `pnpm build` (e `pnpm typecheck`/`pnpm lint`) eseguiti ORA, esito alla mano.
- [ ] Se esistono test: `pnpm test` eseguito ORA.

## 1. Correttezza del codice nuovo (riga per riga)

- [ ] Null/undefined su ogni accesso a valori che possono mancare (contenuti,
      campi opzionali di un progetto).
- [ ] Async: ogni `await` su I/O gestisce o propaga l'errore; niente promise non
      attese; niente lavoro pesante nel main thread.
- [ ] Server vs Client Component corretto; niente `window`/`document` lato server.
- [ ] Errori gestiti o propagati con senso; nessun handler vuoto nuovo.
- [ ] Off-by-one, confronti di stringhe (case, accenti), encoding dei titoli.
- [ ] Contenuti mancanti/malformati gestiti (stato vuoto/errore), non crash.

## 2. Design system e visivo (cuore del progetto)

- [ ] Valori di stile presi dai **token** (`design/`), non hardcoded.
- [ ] Nessun componente duplicato (una card progetto, non varianti multiple).
- [ ] Coerenza tipografica, di spaziatura e di griglia col resto del sito.
- [ ] Motion: dai token, motivato, `prefers-reduced-motion` gestito, niente CLS.
- [ ] Stati vuoto/caricamento/errore curati.

## 3. Accessibilità e performance

- [ ] Contrasto AA, focus visibile, navigazione da tastiera, semantica HTML.
- [ ] `alt` significativi sulle immagini dei progetti.
- [ ] Immagini via `next/image` (sizing), font via `next/font` (niente CLS).
- [ ] Nessun lavoro pesante nel main thread; niente overflow orizzontale.

## 4. Regressioni (verifica attiva)

- [ ] Per ogni simbolo/token/slug modificato: `Grep` di TUTTI gli usi — inclusi
      MDX, className, riferimenti per stringa.
- [ ] Comportamenti/viste esistenti che passavano da quel codice: intatti?
- [ ] Contratti (schema contenuti, slug/URL, chiavi token, astrazione sorgente):
      tutti i lati coerenti?
- [ ] **Slug cambiati senza redirect = finding grave** (link e SEO rotti).
- [ ] Schema contenuti cambiato senza aggiornare i contenuti esistenti = finding.

## 5. Ambito e qualità

- [ ] Modifiche non richieste (refactoring spontanei, rename, ridisegni) = finding
      anche se corrette (viola Minimal Safe Change).
- [ ] Stile coerente col file ospite; niente commenti-cronaca.
- [ ] Niente codice morto, TODO orfani, print/log di debug residui.
- [ ] CHANGELOG aggiornato se il cambiamento è visibile all'utente (se esiste).

## 6. Sicurezza e piattaforma

- [ ] Diff sulle superfici sensibili dichiarate (secret/`NEXT_PUBLIC_*`, form/input
      non fidato, fetch esterni, privacy) senza review di sicurezza → segnalarlo.
- [ ] Input esterno (submit form, query, dati CMS) validato al confine (Zod);
      niente `dangerouslySetInnerHTML` su contenuto non fidato; host esterni su allowlist.
- [ ] Nessun segreto, path assoluto personale o PII in codice o log; niente segreto
      dietro `NEXT_PUBLIC_*`.
- [ ] Vincoli di `lib/` puro e multilingua-ready rispettati.

## 7. Test

- [ ] I test nuovi asseriscono comportamento significativo (fallirebbero col bug?),
      non solo "non esplode".
- [ ] Nessuna asserzione indebolita o test disabilitato per far passare.
- [ ] Il non coperto in automatico (resa visiva, motion, a11y percepita) è elencato
      come verifica manuale?

## Verdetto

- **APPROVATO** — build (+test) verificati di persona, nessun finding rilevante.
- **APPROVATO CON RISERVE** — finding minori elencati, nulla che blocchi.
- **RESPINTO** — almeno un finding grave, motivato con file:riga e scenario concreto.

Un verdetto senza build eseguita di persona non è un verdetto.
