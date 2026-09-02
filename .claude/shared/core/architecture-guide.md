# Guida all'architettura

Confini, contratti e direzione delle dipendenze. Materiale di consultazione per
chi progetta o rivede una modifica strutturale.

## Confini

Un confine ben posto risponde a tre domande senza aprire il codice: **cosa fa
questa unità, come la si usa, da cosa dipende.** Se per rispondere devi leggere
l'implementazione, il confine non è un confine.

Segnali che un confine manca o è nel posto sbagliato:

- un file che cresce e non si riesce a dire in una frase di cosa si occupa;
- due unità che devono essere modificate sempre insieme;
- un'unità che sa come è fatta un'altra internamente;
- una modifica interna che rompe chi la usa;
- lo stesso concetto rappresentato in modo diverso in due punti.

**Ciò che cambia insieme sta insieme.** Si divide per responsabilità, non per
categoria tecnica: separare per «tipo di file» produce unità che non si possono
capire né modificare da sole.

## Direzione delle dipendenze

La logica di dominio non dipende da ciò che le sta intorno: non conosce
l'interfaccia, il database, il formato di trasporto, il fornitore esterno. Sono
loro a dipendere da lei.

La prova pratica: **la logica si può esercitare senza avviare nulla.** Se per
testare una regola serve un server, un browser o una connessione, la regola è
accoppiata a un dettaglio.

Quando la direzione naturale sarebbe sbagliata, si inverte con un'interfaccia
definita dal lato che la usa — non dal lato che la implementa.

## Contratti

Un contratto è tutto ciò su cui qualcun altro fa affidamento: firme pubbliche,
formati persistiti, protocolli, schemi, nomi di chiavi, URL, codici di errore,
e **comportamenti osservabili** anche non documentati.

Prima di cambiarne uno:

1. Qual è il contratto, esattamente?
2. Chi lo usa? Cerca ovunque, incluso ciò che il compilatore non vede.
3. Rompo compatibilità o comportamento osservabile?
4. Se sì: c'è una migrazione? Serve una versione? Serve un periodo in cui
   funzionano entrambi?

Un contratto cambiato in silenzio non è un risparmio di tempo: è un guasto
rinviato a quando nessuno ricorderà il perché.

## Decisioni rimandate

Quando una scelta non è ancora presa — quale fornitore, quale formato, quale
sorgente — la si tiene **dietro un'interfaccia** invece di indovinare. Il costo è
un livello di indirezione; il beneficio è che la decisione, quando arriva, tocca
un solo punto.

Vale solo per le decisioni **realmente aperte**. Astrarre ciò che non cambierà
mai è complessità pura.

## Stato

Meno stato condiviso c'è, meno modi ci sono di essere incoerenti. Dove serve:
una sola fonte di verità, le altre copie dichiaratamente derivate e
ricostruibili. Due punti che possono divergere divergeranno.

## In questo progetto

Tre moduli, con confini che non si attraversano:

| modulo | responsabilità | confine |
|---|---|---|
| `framework/` | il pacchetto installabile | **non cita nulla fuori da sé** |
| `framework/tools/fwbuild/` | assemblare, verificare, risolvere il sorgente | non contiene metodo: solo meccanica |
| `scripts/` | strumenti di lavoro non distribuiti | può citare tutto, non è distribuito |

Il confine che conta più di ogni altro è **dentro** il pacchetto: `method/` va a
tutti e si paga a ogni spawn, `coordinator/` va solo a chi delega. Il doctor lo
verifica (`COORDINATOR_LEAK`), ma solo su titoli letterali noti: la disciplina
non è tutta automatizzabile.

`fwbuild` è deliberatamente diviso fra parti **pure** (`source.resolve` riceve i
candidati) e parti **impure** (`cli._bases` li costruisce): è ciò che rende la
ricerca del sorgente testabile senza dipendere da dove sta il framework.
