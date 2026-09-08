## Obblighi di esecuzione

Valgono per ogni agente che riceve un task, coordinatore incluso quando lavora direttamente.

- **Niente sub-deleghe:** i subagent non spawnano altri agenti. Se serve lavoro fuori dal tuo mandato, riportalo al coordinatore.
- **Scope rigido:** esegui *solo* il task assegnato. Qualsiasi problema extra notato va nel report, MAI nel diff.
- **Lettura a range:** leggi i range `file:riga` che ricevi, non i file interi. Allarga solo se l'estratto non basta, dichiarandolo.
- **Zero ridondanza:** build/test passati e nessun file cambiato → non rieseguire.
- **Criterio di stop:** manca un criterio di completamento verificabile → chiedilo prima di procedere.
