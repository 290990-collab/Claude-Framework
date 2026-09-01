# Checklist di review — AbletonLoader

Riferimento esteso per `final-reviewer`. Regola base: **verificare in prima
persona, mai fidarsi dei report degli altri agenti.**

## 0. Prerequisiti (sempre, prima di tutto)

- [ ] `git status` + `git diff`: il diff reale corrisponde al dichiarato?
      File toccati non dichiarati = finding.
- [ ] Il diff fa ciò che il task chiedeva — tutto e solo quello?
- [ ] `dotnet build AbletonLoader.sln` eseguita ORA, esito alla mano.
- [ ] Se esistono test: `dotnet test` eseguito ORA.

## 1. Correttezza del codice nuovo (riga per riga)

- [ ] Null/None su ogni dereferenziazione di valori che possono mancare.
- [ ] Threading: da callback di hook o socket si tocca la UI solo via
      `Dispatcher.UIThread`? Stato condiviso protetto?
- [ ] Risorse: hook/handle/socket/processi rilasciati anche sui percorsi
      d'errore? `Dispose` coerente?
- [ ] Errori gestiti o propagati con senso; nessun `catch` vuoto nuovo;
      niente errori loggati e ignorati dove serviva reagire.
- [ ] Off-by-one, confronti di stringhe (case, cultura), encoding.
- [ ] Async: niente `.Result`/`.Wait()` nuovi, niente `async void` fuori
      dagli event handler.

## 2. Regressioni (il cuore della review)

- [ ] Per ogni simbolo modificato: `Grep` di TUTTI gli usi — C#, `.axaml`
      (binding per stringa!), Python del remote script.
- [ ] Comportamenti esistenti che passavano da quel codice: intatti?
- [ ] Protocollo app↔remote script: due lati coerenti? Versione script
      aggiornata se il protocollo è cambiato?
- [ ] `AppConfig`: una config della versione precedente si legge ancora?
      Campi rinominati/rimossi = finding grave.
- [ ] Catalogo: le scansioni esistenti restano valide o serve rigenerare?

## 3. Ambito e qualità

- [ ] Modifiche non richieste (refactoring spontanei, rename, "migliorie")
      = finding anche se corrette (viola Minimal Safe Change).
- [ ] Stile coerente col file ospite; niente commenti-cronaca.
- [ ] Niente codice morto, TODO orfani, `Console.WriteLine` di debug.
- [ ] CHANGELOG aggiornato se il cambiamento è visibile all'utente.

## 4. Sicurezza e piattaforma

- [ ] Diff su hook, input simulation, socket, path, processi,
      deserializzazione senza review di sicurezza → chiederla o segnalarlo
      nel verdetto.
- [ ] Nessun nuovo P/Invoke / permesso / superficie antivirus fuori piano.
- [ ] Nel Core nessuna API Windows-only nuova (porting macOS).
- [ ] Nessun segreto, path assoluto personale o dato sensibile in codice o
      log.

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
