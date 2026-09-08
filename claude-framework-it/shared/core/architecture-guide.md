# Guida all'architettura

Confini, contratti e direzione delle dipendenze. Materiale di consultazione per chi progetta o rivede una modifica strutturale.

## Confini

Un confine ben posto risponde a tre domande senza aprire il codice: **cosa fa questa unità, come la si usa, da cosa dipende.** Se serve leggere l'implementazione, non è un confine.

Segnali che un confine manca o è nel posto sbagliato:

- un file che cresce e di cui non si dice in una frase di cosa si occupa;
- due unità sempre da modificare insieme;
- un'unità che sa come è fatta un'altra internamente;
- una modifica interna che rompe chi la usa;
- lo stesso concetto rappresentato in modo diverso in due punti.

**Ciò che cambia insieme sta insieme:** si divide per responsabilità, mai per categoria tecnica. Separare per «tipo di file» produce unità che non si capiscono né si modificano da sole.

## Direzione delle dipendenze

- **La logica di dominio non conosce ciò che le sta intorno** — interfaccia, database, formato di trasporto, fornitore esterno. Sono loro a dipendere da lei.
- **Prova pratica:** la logica si esercita senza avviare nulla. Se per testare una regola serve un server, un browser o una connessione, la regola è accoppiata a un dettaglio.
- **Inversione:** dove la direzione naturale sarebbe sbagliata, l'interfaccia la definisce il lato che la usa, non il lato che la implementa.

## Contratti

Contratto = tutto ciò su cui qualcun altro fa affidamento: firme pubbliche, formati persistiti, protocolli, schemi, nomi di chiavi, URL, codici di errore, e **comportamenti osservabili** anche non documentati.

Prima di cambiarne uno:

1. Qual è il contratto, esattamente?
2. Chi lo usa? Cerca ovunque, incluso ciò che il compilatore non vede.
3. Rompo compatibilità o comportamento osservabile?
4. Se sì: migrazione? versione nuova? periodo in cui funzionano entrambi?

Un contratto cambiato in silenzio è un guasto rinviato a quando nessuno ricorderà il perché.

## Decisioni rimandate

Una scelta non ancora presa — quale fornitore, formato, sorgente — si tiene **dietro un'interfaccia** invece di indovinarla: costa un livello di indirezione, e quando la decisione arriva tocca un punto solo. Vale solo per le decisioni **realmente aperte**: astrarre ciò che non cambierà mai è complessità pura.

## Stato

Meno stato condiviso, meno modi di essere incoerenti. Dove serve: **una sola fonte di verità**, le altre copie dichiaratamente derivate e ricostruibili. Due punti che possono divergere divergeranno.

## In questo progetto

[DA COMPILARE — mappa dei moduli con la responsabilità di ciascuno, i confini che non vanno attraversati, i contratti dichiarati e chi li consuma, le decisioni rimandate di proposito e cosa le tiene aperte, le scelte architetturali già prese che non si riaprono senza mandato.]
