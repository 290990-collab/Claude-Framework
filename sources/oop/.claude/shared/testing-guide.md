# Guida ai test — AbletonLoader

## Struttura

Non c'è ancora una suite consolidata. Quando si introducono test: progetto
xUnit `src/AbletonLoader.Tests/` aggiunto alla solution; naming
`NomeClasseTests.cs`, metodi `Metodo_Scenario_EsitoAtteso`; esecuzione
`dotnet test AbletonLoader.sln`. Prima di creare il progetto, verificare
che non esista già.

## Cosa si testa (in ordine di valore)

1. **`QuickMatch`** — matching/ranking: query vuote, case, accenti,
   caratteri speciali, cataloghi grandi, parità di punteggio.
2. **`AppConfig`** — round-trip di serializzazione; config di versioni
   precedenti (campi mancanti → default); config corrotta → niente crash,
   riparte con default segnalando.
3. **`LiveClient`** — parsing dei messaggi: troncati, encoding non-ASCII
   (nomi preset), payload oltre misura, sequenze fuori ordine. La logica di
   parsing si testa separata dal trasporto.
4. **`CatalogService`** — costruzione/filtraggio: cartelle vuote, nomi
   duplicati, path con spazi/unicode.
5. **Remote script** — solo le funzioni pure (parsing comandi, costruzione
   risposte), con l'interprete di sistema, senza API di Live.

NON in automatico (dichiararlo nel report): UI Avalonia (verifica manuale);
hook e input simulation (manuale, con antivirus attivo); integrazione con
Live reale (checklist: Live chiuso / aperto senza script / script vecchio /
flusso completo).

## Qualità dei test

- Un test mai visto fallire non dimostra nulla: per un bug, prima il test
  rosso, poi il fix (implementer), poi il verde.
- Comportamento osservabile, non dettagli interni: il test sopravvive a un
  refactoring.
- Test indipendenti tra loro e dall'ordine; niente stato condiviso mutabile.
- Niente sleep per "aspettare che succeda": sincronizzazione esplicita.
- Dati parlanti: `"preset with spaces àè.adv"` dice più di `"test1"`.
- Mai indebolire un'asserzione per far passare: rosso = bug o test
  sbagliato — si decide, non si maschera.

## Edge case ricorrenti

Path con spazi e non-ASCII (il path utente reale ne ha); nomi plugin/preset
con `/ \ : * ? " < > |` e unicode; config assente/vuota/corrotta/di
versione futura; Live spento / socket chiuso a metà messaggio; cataloghi
enormi (migliaia di preset — il matching resta reattivo?).
