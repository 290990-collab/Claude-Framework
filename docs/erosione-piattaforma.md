# Erosione di piattaforma — check ricorrente

**Documento vivo.** Si riesegue a ogni release di Claude Code, non una volta
sola. Chiude [D8](../UPDATE.md).

## Perché

Il rilievo è [P3](../UPDATE.md): Claude Code assorbe questa superficie a ogni
release — subagent nativi, skill, `model:`/`tools:` nel frontmatter, memoria,
hook. Un framework il cui valore è «file di metodo + roster» viene eroso dal
basso, e la differenziazione deve stare dove la piattaforma non andrà:
**verifica dell'installazione** e **sincronizzazione fra molti repo**.

Il rischio non è che la piattaforma faccia una cosa meglio: è che il framework
continui a **pagarla in parole** dopo che è diventata gratis. Ogni riga che
duplica una funzionalità nativa è costo puro, e il costo si paga a ogni spawn.

**Premessa epistemica.** La colonna «cosa fa la piattaforma» viene da conoscenza
pregressa, non da fonti verificate al momento della scrittura. È esattamente il
motivo per cui questo è un check ricorrente e non una conclusione: la mappa
qui sotto va **riverificata**, non ereditata.

Dalla passata del 2026-09-02 (seconda) la riga sul frontmatter degli agenti fa
eccezione: è l'unica letta da una fonte, e la fonte è annotata. Le altre restano
conoscenza pregressa.

## Come si esegue

Quindici minuti, in quest'ordine.

1. **Leggi le note di rilascio** di Claude Code dall'ultima passata registrata
   in fondo. Serve una sola domanda per ogni voce nuova: *questa cosa il
   framework la fa già in prosa?*
2. **Per ogni riga della mappa**, aggiorna la colonna «piattaforma» con quello
   che hai appena letto, non con quello che ricordi.
3. **Dove il verdetto diventa `duplica`**, togli. Non «semplifica»: togli, e
   misura il kernel dopo (`python -m fwbuild cost` su un'installazione, oppure
   la suite, che ha i due tetti come test).
4. **Registra la passata** in fondo, anche quando non cambia niente. Una
   passata senza esito è un dato: dice che la superficie è ferma.

Il verdetto ha tre valori soli:

| verdetto | significa |
|---|---|
| `si appoggia` | la piattaforma lo fornisce e il framework lo **usa**, senza reimplementarlo. Va bene così |
| `duplica` | la piattaforma lo fornisce e il framework lo **ridice** in prosa. Da togliere |
| `scoperto` | la piattaforma non lo fornisce. È qui che vive il valore, ed è la riga da guardare quando cambia |

## La mappa — passata del 2026-09-02

| superficie | cosa fa la piattaforma | cosa fa il framework | verdetto |
|---|---|---|---|
| Definizione degli agenti | file in `.claude/agents/` con **diciassette** campi di frontmatter — oltre a `name`/`description`/`model`/`tools`: `disallowedTools`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental` | scrive quei file, non un formato proprio; ne usa cinque (`name`, `description`, `model`, `effort`, `tools`, `color`) | `si appoggia` — verificato il 2026-09-02 |
| Skill | `SKILL.md` con frontmatter, invocabili per nome | `framework-install`, `framework-doctor`, `framework-sync` sono skill normali | `si appoggia` |
| Permessi | `.claude/settings.json`, `allow`/`deny` per strumento | li genera dal profilo, uguali su tutti e cinque | `si appoggia`, **con un confine da dire**: un `deny` su `Read` non copre `Bash(cat .env)`. Dove il segreto conta, la guardia meccanica è la lista `tools` dell'agente, non i permessi |
| Contesto comune | `CLAUDE.md` caricata a ogni spawn | ne governa la **dimensione**, con due tetti che rompono la build e un rilievo del doctor sull'installato | `scoperto` |
| Verifica dell'installazione | niente di equivalente | `fwbuild doctor`, sedici codici di rilievo | `scoperto` — è il prodotto |
| Allineamento fra repo | niente di equivalente | `fwbuild report`, `framework-sync --up/--down` | `scoperto` — è il prodotto |
| Stato fra sessioni | memoria nativa e `CLAUDE.md` | tre file in `docs/` (`TODO`, `status`, `roadmap`) più le regole che li aggiornano | **da sorvegliare**: se la memoria nativa arriva a coprire i tre livelli, questa diventa la prima riga a passare a `duplica` |
| Scelta dell'agente a cui delegare | il coordinatore sceglie dalle `description` | dieci regole di delega più una tabella di routing | **da sorvegliare**: prosa che vale finché la scelta nativa resta grossolana |
| Formato del report fra agenti | niente di equivalente | schema `CONF`/`SMENTIRE`/`ASSUMED`/`UNVERIFIED` | `scoperto` |
| Vincoli meccanici sul comportamento | hook | **non usati**: i vincoli stanno in prosa | `scoperto`, ma è la riga in cui *aggiungere* costa meno che scrivere — un hook rende meccanico ciò che la prosa chiede e basta |
| `@import` in `CLAUDE.md` | dipende dalla versione | la skill dice di **verificare, non assumere**, e resta sulla concatenazione fisica | `si appoggia` (con la verifica già scritta) |
| Distribuzione | plugin e marketplace | installazione via skill più copia del sorgente | **da sorvegliare**: se il framework diventasse un plugin, il Passo 0 di `framework-install` cambierebbe forma |

**Cosa dice questa passata.** Niente da togliere: nessuna riga è a `duplica`. Le
tre righe da sorvegliare sono quelle da rileggere per prime la prossima volta —
lo stato fra sessioni è la più esposta, perché è l'unica dove il framework
mantiene file propri per una cosa che la piattaforma sta imparando a fare.

## Registro delle passate

| data | versione di Claude Code | esito |
|---|---|---|
| 2026-09-02 | non registrata — da annotare alla prossima | prima passata: mappa costruita, nessuna riga a `duplica`, tre da sorvegliare |
| 2026-09-02 | non registrata | seconda passata, su fonte: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents). Niente a `duplica`. Due correzioni al framework: `effort` **esiste** (la riga lo dava per non documentato, e la regola 2 della delega ci si appoggia legittimamente); `color` ammette otto valori e sei schede ne dichiaravano uno inventato — corretto, con un test che lo tiene. Da guardare alla prossima: `hooks` e `permissionMode` nel frontmatter, che renderebbero meccanico ciò che oggi è mandato |
