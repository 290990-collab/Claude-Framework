# Checklist di review — FindShop

Riferimento esteso per `final-reviewer`. Regola base: **verificare in prima
persona, mai fidarsi dei report degli altri agenti.**

## 0. Prerequisiti (sempre, prima di tutto)

- [ ] `git status` + `git diff`: il diff reale corrisponde al dichiarato?
      File toccati non dichiarati = finding.
- [ ] Il diff fa ciò che il task chiedeva — tutto e solo quello?
- [ ] `pnpm turbo build` eseguita ORA, esito alla mano.
- [ ] Se esistono test: `pnpm turbo test` eseguito ORA.

## 1. Correttezza del codice nuovo (riga per riga)

- [ ] Null/None su ogni dereferenziazione di valori che possono mancare.
- [ ] Async: ogni `await` su I/O gestisce o propaga l'errore; niente promise
      non attese o blocco del ciclo di eventi; stato condiviso coerente.
- [ ] Risorse: handle/connessioni/processi rilasciati anche sui percorsi
      d'errore? Rilascio coerente col pattern del repo?
- [ ] Errori gestiti o propagati con senso; nessun handler vuoto nuovo;
      niente errori loggati e ignorati dove serviva reagire.
- [ ] Off-by-one, confronti di stringhe (case, cultura), encoding.
- [ ] Async: niente attese bloccanti nuove su codice asincrono, niente
      fire-and-forget fuori dai punti previsti.

## 2. Regressioni (il cuore della review)

- [ ] Per ogni simbolo modificato: `Grep` di TUTTI gli usi — inclusi markup,
      riferimenti per stringa/riflessione, script di altri linguaggi.
- [ ] Comportamenti esistenti che passavano da quel codice: intatti?
- [ ] Contratti tra componenti (vedi `architecture-guide.md`): tutti i lati
      coerenti? Versione incrementata se il contratto è cambiato?
- [ ] Formati persistiti: i dati della versione precedente si leggono
      ancora? Campi rinominati/rimossi = finding grave.
- [ ] Dati rigenerabili (cache/indici): restano validi o serve rigenerare?

## 3. Ambito e qualità

- [ ] Modifiche non richieste (refactoring spontanei, rename, "migliorie")
      = finding anche se corrette (viola Minimal Safe Change).
- [ ] Stile coerente col file ospite; niente commenti-cronaca.
- [ ] Niente codice morto, TODO orfani, print/log di debug residui.
- [ ] CHANGELOG aggiornato se il cambiamento è visibile all'utente.

## 4. Sicurezza e piattaforma

- [ ] Diff sulle superfici sensibili dichiarate (vedi CLAUDE.md e
      `security-reviewer`) senza review di sicurezza → chiederla o
      segnalarlo nel verdetto.
- [ ] Input esterno (query, payload API, feed di ingestion) validato al
      confine (Zod); nessuna query SQL concatenata; URL esterni su allowlist.
- [ ] Authz verificata sugli endpoint che toccano dati di un tenant/negozio;
      nessun dato di altri tenant esposto.
- [ ] Vincoli di core puro e multi-region rispettati (vedi
      `architecture-guide.md`): niente hardcode di valuta/lingua/locale.
- [ ] Nessun segreto, path assoluto personale, PII o geolocalizzazione grezza
      in codice o log.

## 5. Test

- [ ] I test nuovi asseriscono comportamento significativo (fallirebbero
      col bug?), non solo "non esplode".
- [ ] Nessuna asserzione indebolita o test disabilitato per far passare.
- [ ] Il non coperto in automatico è elencato come verifica manuale?

## Verdetto

- **APPROVATO** — build+test verificati di persona, nessun finding rilevante.
- **APPROVATO CON RISERVE** — finding minori elencati, nulla che blocchi.
- **RESPINTO** — almeno un finding grave, motivato con file:riga e scenario
  concreto.

Un verdetto senza build eseguita di persona non è un verdetto.
