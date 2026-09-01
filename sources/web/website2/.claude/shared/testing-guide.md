# Guida ai test — FindShop

## Struttura

- **Unit / dominio**: Vitest, test accanto al codice (`*.test.ts`) o in `test/`
  del package; naming `descrizione_scenario_esitoAtteso`. Esecuzione
  `pnpm turbo test` (o `pnpm --filter <pkg> test`).
- **E2E web**: Playwright (`apps/web`).
- **E2E mobile**: Detox o Maestro (`apps/mobile`) — verifica manuale/CI dedicata.
- **API**: test di contratto/integrazione con il runner nativo di NestJS su un
  DB di test.

Prima di creare un setup di test, verificare che non esista già nel package.

## Cosa si testa (in ordine di valore)

1. **Logica pura del core** (`packages/core`): matching capo↔offerta, ranking
   dei risultati, calcoli geo/distanza, normalizzazione prezzi (centesimi,
   valuta) e taglie. Input estremi, accenti/maiuscole/caratteri speciali nei
   nomi capo, parità di punteggio, volumi grandi. È il bersaglio primario.
2. **Contratti API** (`packages/shared`, Zod): round-trip di
   validazione/serializzazione; payload mancanti, in eccesso, malformati →
   rifiutati al confine, mai propagati al dominio.
3. **Adapter di ingestion**: feed reali e sporchi (CSV/XML/JSON) →
   normalizzazione corretta; righe malformate, encoding non-ASCII, campi
   mancanti, duplicati, prezzi/valute anomale → gestiti senza corrompere il
   dato né crashare la pipeline. Logica di parsing/normalizzazione testata
   separata dal trasporto.
4. **Migrazioni DB**: applicano e (dove previsto) si annullano; i dati di uno
   schema precedente restano leggibili.
5. **Servizi backend** con logica separabile da I/O e framework.

NON in automatico (dichiararlo nel report, con checklist di verifica manuale):
UI web/mobile (resa visiva, gesture, mappa), integrazioni reali con fonti dati
o provider mappe, ricerca end-to-end su indice reale.

## Qualità dei test

- Un test mai visto fallire non dimostra nulla: per un bug, prima il test
  rosso, poi il fix (implementer), poi il verde.
- Comportamento osservabile, non dettagli interni: il test sopravvive a un
  refactoring.
- Test indipendenti tra loro e dall'ordine; niente stato condiviso mutabile;
  DB di test isolato e ripulito.
- Niente sleep per "aspettare che succeda": sincronizzazione esplicita.
- Dati parlanti: un input realistico con spazi/unicode ("Nike Air Max 90",
  "giacca in lana") dice più di `"test1"`.
- Mai indebolire un'asserzione per far passare: rosso = bug o test sbagliato —
  si decide, non si maschera.

## Edge case ricorrenti

Nomi capo con accenti, maiuscole, punteggiatura e unicode; query vuote o
troppo corte; coordinate ai limiti (lat/lon fuori range, meridiano/poli),
aree senza risultati; valute e taglie eterogenee tra negozi; prezzi a zero o
negativi nei feed; feed di ingestion troncati/duplicati/di encoding diverso;
dati persistiti assenti/di versione precedente; indice o DB non raggiungibili;
volumi grandi (le prestazioni della ricerca restano accettabili?).
