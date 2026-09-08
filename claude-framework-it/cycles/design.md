## Il ciclo del design

Si inserisce nel ciclo del codice fra *Capire* e *Progettare*. Qui la resa visiva è parte del prodotto: un'interfaccia corretta e brutta non è un successo parziale, è un prodotto che smentisce sé stesso.

**Capire → Direzione → Progettare → Implementare → Verificare (funzionale *e* visivo) → Integrare.**

Il passo aggiunto è il secondo:

**Direzione** (`frontend`, prima di qualunque markup): griglia, scala tipografica, palette, ritmo dello spazio, tono del movimento. Si decide **prima** del primo componente e si esprime in token, non in aggettivi. Richieste ambigue → plan mode o brainstorming prima.

Regole del ciclo:

- **Mai saltare al markup prima della direzione:** un componente scritto senza sistema diventa il sistema, per inerzia.
- **La verifica visiva non è opzionale e non è automatica:** build e test verdi non dimostrano che si veda bene. Si guarda a runtime; ciò che non è stato guardato torna in `UNVERIFIED` con le istruzioni per guardarlo. Un task di interfaccia chiuso senza quella riga non è chiuso.
- **Il test unitario copre la logica pura**, non la resa: test sul markup danno falsa sicurezza e si rompono a ogni ritocco.
- **Accessibilità e prestazione sono requisiti del ciclo**, non una revisione finale: entrano nella direzione.

Dettaglio operativo su token, movimento e accessibilità: `.claude/shared/domain/design-guide.md`.
