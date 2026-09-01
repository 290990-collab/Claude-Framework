# Guida ai test — Portfolio

Il valore dei test qui è concentrato nella **logica pura di `lib/`** e nella
validità dei contenuti. La resa visiva, il motion e l'accessibilità percepita si
verificano a runtime (occhio + strumenti), non con unit test.

## Struttura

- **Unit / logica**: Vitest, test accanto al codice (`*.test.ts`) o in `test/`;
  naming `descrizione_scenario_esitoAtteso`. Esecuzione `pnpm test`.
- **E2E web** (solo se richiesto): Playwright per flussi chiave (navigazione,
  filtro progetti, apertura dettaglio) — non per la resa estetica.
- **Verifica visiva**: manuale sul dev server (viewport mobile+desktop, tema
  chiaro/scuro se previsto, `prefers-reduced-motion`); opzionale snapshot visivi
  se il progetto li adotta.

Prima di creare un setup di test, verificare che non esista già.

## Cosa si testa (in ordine di valore)

1. **Logica pura di `lib/`**: filtro per categoria/tag, ordinamento (per anno,
   parità), "progetti correlati", formattazione date/numeri. Input estremi,
   accenti/maiuscole/unicode nei titoli, tag mancanti, categoria sconosciuta,
   liste vuote, molti progetti. È il bersaglio primario.
2. **Schema dei contenuti** (Zod): round-trip di validazione; frontmatter/CMS con
   campi mancanti, in eccesso, malformati → rifiutati o normalizzati al confine,
   mai propagati rotti alle viste.
3. **Astrazione di sorgente contenuti**: il caricamento restituisce i dati
   normalizzati attesi dato un input (file MDX di prova o mock del CMS);
   contenuto corrotto/assente gestito senza crash.
4. **Utility** con logica separabile dal rendering.

NON in automatico (dichiararlo nel report, con checklist di verifica manuale): resa
visiva e layout, motion, accessibilità percepita, integrazioni reali con un CMS o
un servizio form, Core Web Vitals reali.

## Qualità dei test

- Un test mai visto fallire non dimostra nulla: per un bug, prima il test rosso,
  poi il fix (implementer), poi il verde.
- Comportamento osservabile, non dettagli interni: il test sopravvive a un refactoring.
- Test indipendenti tra loro e dall'ordine; niente stato condiviso mutabile.
- Niente sleep per "aspettare che succeda": sincronizzazione esplicita.
- Dati parlanti: un input realistico ("Progetto — Identità visiva 2024", tag
  "branding") dice più di `"test1"`.
- Mai indebolire un'asserzione per far passare: rosso = bug o test sbagliato — si
  decide, non si maschera.

## Edge case ricorrenti

Titoli con accenti, maiuscole, punteggiatura e unicode; slug con caratteri
speciali; categoria/tag mancanti o sconosciuti; anni mancanti o uguali
(ordinamento a parità); liste vuote (nessun progetto in una categoria); contenuti
troncati/malformati; campi opzionali assenti (cover, links, media); molti progetti
(le viste e i filtri reggono?).
