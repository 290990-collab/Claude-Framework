# Claude Code — Framework "Enterprise" (template riusabile)

Punto di partenza per qualsiasi progetto di coding: orchestrazione
multi-agente, economia dei token, anti-allucinazione, guide condivise.
Astratto da un progetto reale; le parti specifiche sono segnaposto.

```
CLAUDE.md          — framework principale (caricato da ogni agente)
.claude/agents/    — 9 subagent specializzati
.claude/shared/    — guide caricate on-demand
```

## Segnaposto (convenzione di tutti i file)

- `{{NOME}}` — valore puntuale: `{{PROGETTO}}`, `{{BUILD_CMD}}`,
  `{{BUILD_CMD_RAPIDA}}`, `{{TEST_CMD}}`, `{{TEST_PROJECT}}`,
  `{{TEST_FRAMEWORK}}`, `{{UI_STACK}}`.
- `[DA COMPILARE]` — blocco per le direttive specifiche del progetto; ogni
  blocco dichiara cosa metterci, con esempi del livello di dettaglio.

## Bootstrap (primo uso in un progetto nuovo)

1. Copia `CLAUDE.md` + `.claude/` nella root del repo.
2. Chiedi a Claude Code:

   > Analizza questo repository e compila il framework: sostituisci tutti i
   > `{{segnaposto}}` e riempi i blocchi `[DA COMPILARE]` in CLAUDE.md,
   > `.claude/agents/` e `.claude/shared/` con le direttive specifiche di
   > questo progetto (struttura, comandi build/test, vincoli, contratti,
   > superfici sensibili, stack). Rimuovi i marker compilati. Non
   > inventare: ciò che non deduci dal repo, chiedimelo.

3. Al bootstrap si POTA, non solo si compila: agenti e sezioni non
   pertinenti al tipo di progetto si eliminano (es. `frontend` se non c'è
   UI; "Stack secondari" se non ci sono; righe UI di checklist e standard).
   Gli esempi nei blocchi sono illustrativi (desktop/web/CLI/server/
   libreria): tenere solo ciò che si applica.
4. Verifica: `grep -rn "DA COMPILARE\|{{" CLAUDE.md .claude/` → vuoto.

## Regole di manutenzione

- NON personalizzare il metodo (orchestrazione, economia token, Evidence
  Before Action, report standard, principi di modifica, debug a due
  ipotesi, checklist di review): è generico e già ottimizzato — si compila
  il contesto, non si riscrive il metodo.
- Le direttive specifiche vivono SOLO nei blocchi previsti: così restano
  distinguibili dal framework e il template si può ri-estrarre.
- Contenuto non universale → `.claude/shared/` (on-demand), non CLAUDE.md
  (pagato a ogni spawn).
