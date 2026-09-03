## Il ciclo del codice

**Capire → Progettare → Implementare → Verificare → Integrare.**

1. `explorer` individua i file rilevanti (economico, parallelizzabile);
   `api-scout` se servono firme di librerie esterne.
2. `architect` se il task tocca ≥3 file o un contratto; richieste ambigue → plan
   mode prima. Altrimenti si salta: un piano che il coordinatore scrive in tre
   righe non vale uno spawn.
3. `implementer`, **un task alla volta**: completa, verifica, passa al
   successivo. Test-first quando il comportamento desiderato è esprimibile come
   test (nuove feature, bug fix ben definiti, logica di business o di API).
   Escluso per refactoring, UI, prototipi, dipendenze, documentazione.
4. `tester` estende la copertura oltre i mini-test dell'implementer. Pochi test
   che asseriscono qualcosa di vero, mai molti test deboli.
5. Se il diff tocca la **superficie critica** dichiarata dal progetto, prima il
   revisore di quella superficie; poi `final-reviewer`, che verifica da zero
   senza fidarsi dei report.
6. Il coordinatore risolve i finding e integra. Commit solo su richiesta.

Il ciclo si salta dove non serve: per una modifica piccola a basso rischio lo
esegue direttamente il coordinatore.

## Scegliere fra agenti che sembrano vicini

| Dubbio | Discriminante |
|---|---|
| `explorer` o leggo io | Servono >2 file o non sai dove guardare → `explorer`. Sai già il path → leggi tu: spawnare costa di più |
| `explorer` o `api-scout` | Dentro il repo → `explorer`. Fuori dal repo (librerie, servizi) → `api-scout` |
| `architect` o decido io | Tocca struttura o un contratto → `architect`. Altrimenti è un piano da tre righe, e lo scrivi tu |
| `implementer` o `debugger` | La causa è nota → `implementer`. La causa è ignota → `debugger`, che consegna la diagnosi |
| `implementer` o `refactorer` | Cambia il comportamento o aggiunge → `implementer`. Comportamento osservabile invariato → `refactorer` |
| `implementer` o `frontend` | Decide il cuore del task: viste, markup, stile, movimento → `frontend`; logica e servizi con ritocchi all'interfaccia → `implementer`. Se pesa su entrambi, l'architect lo spezza in due |
| `deploy` o `infra` | Hosting semplice, un push aggiorna → `deploy`. Risorse definite come codice, ambienti multipli → `infra`. Non coesistono |
| revisore critico o `final-reviewer` | «Il codice è corretto?» → `final-reviewer`. «Questo è sicuro / valido / il dato è giusto?» → il revisore della superficie critica, **prima** |
