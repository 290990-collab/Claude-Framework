## Come si scrive un prompt di delega

La regola dei bordi — istruzioni ai margini, materiale di consultazione in mezzo
— vale qui più che altrove. Struttura obbligatoria:

```
1. TASK          una frase: cosa fare
2. DONE QUANDO   il criterio di completamento, verificabile
3. VINCOLI       i divieti duri — pochi, espliciti
4. MATERIALE     estratti con file:riga esatti (la parte lunga: sta in mezzo
                 perché si consulta, non perché conta meno)
5. DONE QUANDO   ripetuto, testuale
```

Il criterio si scrive due volte di proposito: apre e chiude. **Se un agente
sbaglia bersaglio, quasi sempre il criterio era implicito o stava in mezzo.**

Regole pratiche:

- **Mai un `file:riga` sepolto nella prosa.** Va in elenco, nel blocco materiale.
- **Vincoli pochi e duri.** Dieci vincoli equivalgono a nessun vincolo: quelli
  che contano vanno scelti, non accumulati.
- **Niente eco e niente contesto che l'agente non userà** — ciò che sta in
  `CLAUDE.md` ce l'ha già, e ogni riga in più spinge verso il centro qualcosa che
  doveva stare su un bordo.
- **Il criterio dev'essere verificabile da chi lo riceve.** «Fai un buon lavoro»
  non è un criterio; «i test in `tests/x.py` passano e la build è pulita» sì.

Per un secondo giro sullo stesso agente vale la regola 8: si continua la
conversazione esistente e si manda **solo il delta** — i finding da risolvere —
non un prompt nuovo che ridigerisce il contesto da capo.
