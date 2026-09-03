# Metodo di lavoro

Claude Code opera qui come un **team di senior coordinati**: massima accuratezza,
minime allucinazioni, budget token come vincolo di prima classe.

Questo è il **metodo comune**: vale per chiunque lavori in questo progetto,
coordinatore o subagent, e non si personalizza. Ciò che riguarda *questo*
progetto sta nelle sezioni fuori dalla regione delimitata dai marker.

**Chi legge cosa.** Questo file è caricato in ogni contesto, quindi contiene solo
ciò che serve a tutti. Il resto sta altrove e si apre al bisogno:

- **delega** — quando spawnare, quale agente, con che prompt, come si tiene lo
  stato del progetto → `.claude/shared/orchestration.md`. Riguarda **solo il
  coordinatore**: se questa sessione delega, è il primo file da leggere.
- **mandato di un ruolo** → la sua scheda in `.claude/agents/`, che non ripete
  questo metodo.
- **dominio del task** → le guide in `.claude/shared/`, aperte solo quando il
  task ci rientra.
