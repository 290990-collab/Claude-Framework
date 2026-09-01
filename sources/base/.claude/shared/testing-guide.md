# Guida ai test — {{PROGETTO}}

## Struttura

[DA COMPILARE] — {{TEST_FRAMEWORK}}, {{TEST_PROJECT}}, naming (es.
`NomeClasseTests`, metodi `Metodo_Scenario_EsitoAtteso`), esecuzione
`{{TEST_CMD}}`. Prima di creare il progetto di test, verificare che non
esista già.

## Cosa si testa (in ordine di valore)

[DA COMPILARE] — elenco ordinato dei bersagli REALI. Criterio di priorità:

1. **Logica pura del core** (matching, ranking, calcoli): input estremi,
   case/accenti/caratteri speciali, volumi grandi, parità di punteggio.
2. **Formati persistiti** — round-trip di serializzazione; dati di versioni
   precedenti (campi mancanti → default); dati corrotti → niente crash,
   riparte con default segnalando.
3. **Parsing di messaggi/protocolli** — troncati, encoding non-ASCII,
   payload oltre misura, sequenze fuori ordine. La logica di parsing si
   testa separata dal trasporto.
4. **Servizi con logica separabile dalla UI/dall'I/O**.
5. **Script/componenti esterni** — solo le funzioni pure, senza le API
   dell'host.

NON in automatico (dichiararlo nel report): [DA COMPILARE — cosa si
verifica solo a mano: UI; integrazioni reali, con checklist: sistema
spento / versione vecchia / flusso completo].

## Qualità dei test

- Un test mai visto fallire non dimostra nulla: per un bug, prima il test
  rosso, poi il fix (implementer), poi il verde.
- Comportamento osservabile, non dettagli interni: il test sopravvive a un
  refactoring.
- Test indipendenti tra loro e dall'ordine; niente stato condiviso mutabile.
- Niente sleep per "aspettare che succeda": sincronizzazione esplicita.
- Dati parlanti: un input realistico con spazi/unicode dice più di `"test1"`.
- Mai indebolire un'asserzione per far passare: rosso = bug o test
  sbagliato — si decide, non si maschera.

## Edge case ricorrenti

Path con spazi e non-ASCII; nomi con `/ \ : * ? " < > |` e unicode; dati
persistiti assenti/vuoti/corrotti/di versione futura; controparte
spenta/connessione chiusa a metà messaggio; volumi grandi (le prestazioni
restano accettabili?).

[DA COMPILARE] — aggiungere gli edge case specifici del dominio.
