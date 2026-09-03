# Guida al design

Per i progetti in cui la qualità visiva è un requisito, non una rifinitura.
Regola sovraordinata: **coerenza prima della creatività** — un linguaggio visivo
solo, applicato ovunque.

## I token sono la fonte unica

Tutto lo stile passa da una scala dichiarata. Nessun valore scritto direttamente
in un componente.

- **Colore**: palette ristretta, definita per **ruolo semantico** (sfondo, testo,
  attenuato, accento, bordo, stati) prima che per valore. Se esistono temi, i
  ruoli sono la fonte e i colori assoluti la conseguenza.
- **Tipografia**: una o due famiglie, una scala esplicita, pesi definiti,
  interlinea e spaziatura per livello. Caricamento senza spostamento del
  contenuto.
- **Spaziatura**: una scala coerente, non margini arbitrari. Lo spazio bianco è
  uno strumento, non vuoto da riempire.
- **Griglia e punti di rottura**: dichiarati e nominati, con larghezze massime
  coerenti.
- **Movimento**: durate e curve come token, così ogni animazione parla la stessa
  lingua.
- **Raggi, ombre, bordi**: anche questi come token.

Aggiungere un token è un cambiamento consapevole: è un contratto interno usato
ovunque. Prima si cerca se ne esiste uno adatto.

## Direzione

- **Allineamento rigoroso**: ogni elemento è allineato a qualcosa. Niente
  posizioni «a occhio».
- **Gerarchia leggibile**: dimensione, peso e spazio dicono cosa conta. L'occhio
  deve sapere dove andare senza sforzo.
- **Ridurre**: poche famiglie, palette ristretta, pochi elementi per vista. Se un
  elemento non serve, si toglie.
- **Il contenuto guida la forma**, dentro un sistema unico: trattamenti diversi
  per contenuti diversi, ma stessi token e stessa griglia.

## Movimento

- **Motivato, non decorativo**: comunica continuità, gerarchia o riscontro.
- **Breve e naturale**: l'interfaccia deve sembrare reattiva, non in attesa
  dell'animazione.
- **Preferenza di movimento ridotto sempre rispettata** — non è opzionale.
- **Nessun danno**: niente spostamenti di layout, niente blocco dello scorrimento,
  niente focus rubato, niente interazione impedita durante la transizione.

## Accessibilità — requisito, non extra

Contrasto sufficiente per testo e elementi interattivi · focus visibile e ordine
di tabulazione coerente con la lettura · uso completo da tastiera · alternative
testuali che dicono la funzione, non l'aspetto · aree di tocco adeguate ·
struttura semantica corretta · nessuna informazione affidata al solo colore ·
form con etichette vere ed errori associati al campo.

## Prestazione come estetica

Nessuno spostamento di contenuto dopo il caricamento · immagini dimensionate e
servite nel formato giusto · font senza salto visivo · lavoro pesante fuori dal
percorso di rendering · risposta immediata all'interazione, anche quando il
risultato arriva dopo. Un'interfaccia lenta è un'interfaccia brutta.

## Verifica

La resa non si deduce: si guarda. Larghezze diverse, tema chiaro e scuro, testo
lungo e testo assente, stato di caricamento e di errore, movimento ridotto,
navigazione da sola tastiera. Ciò che non è stato guardato va dichiarato.

## In questo progetto

[DA COMPILARE — stack e librerie dell'interfaccia, dove vivono token e
componenti, direzione visiva già fissata, vincoli di supporto, come si avvia
l'ambiente per guardare il risultato, strumenti di design collegati.]
