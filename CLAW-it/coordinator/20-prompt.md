## Come si scrive un prompt di delega

Regola dei bordi, tassativa: **istruzioni operative ai margini, dati e materiale di consultazione al centro.**

### Struttura obbligatoria

```
1. TASK:        [una frase: cosa fare]
2. DONE QUANDO: [criterio di completamento verificabile]
3. VINCOLI:     [divieti duri, pochi e specifici]
4. MATERIALE:   [estratti ed elenco di file:riga esatti]
5. DONE QUANDO: [ripetuto identico al punto 2]
```

Il criterio apre e chiude di proposito: se un agente sbaglia bersaglio, quasi sempre era implicito o stava in mezzo.

### Regole tassative

- **Zero `file:riga` nella prosa:** vanno solo in elenco, nel blocco MATERIALE.
- **Vincoli essenziali:** pochi e duri. Dieci vincoli equivalgono a nessun vincolo.
- **Zero eco:** non ripetere ciò che è già in `CLAUDE.md`. Passa solo il delta del task.
- **Criterio oggettivo:** verificabile da chi lo riceve («i test in `tests/x.py` passano e la build è pulita»), non «fai un buon lavoro».
- **Secondo giro (regola 8):** per correzioni o iterazioni continua la sessione esistente mandando SOLO i finding. Mai ricreare il prompt da capo.
