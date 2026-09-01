# Principi di ricerca — come si ragiona in questo progetto

Sono linee guida **permanenti** su *come lavorare*, non su quali competenze
avere: l'equivalente, per il deep learning, delle best practice di ingegneria
del software. Fonte: `direttive.txt` (40 principi), qui raggruppati e agganciati
a casi reali del progetto — perché un principio con un esempio si applica, uno
astratto no.

> **Principio guida.** Ogni decisione dev'essere motivata da dati, evidenze
> sperimentali o letteratura, e ogni risultato dev'essere **spiegabile,
> riproducibile e verificabile indipendentemente**.

## 1. Evidenza e onestà

1. **Evidence First** — ogni affermazione tecnica poggia su paper, esperimenti o
   metriche; mai su supposizioni.
2. **Separate Facts from Hypotheses** — risultati verificati, interpretazioni e
   idee future restano visibilmente distinti.
3. **Explicit Assumptions** — le assunzioni su problema, dati e modello si
   dichiarano.
4. **Fail Transparently** — errori, limiti e risultati negativi si riportano
   apertamente. *Qui:* la temperatura τ=0.3, motivata da una stima ragionevole,
   è stata smentita dalla misura — e il modo giusto di riportarlo è esattamente
   così.
5. **Scientific Skepticism** — ogni miglioramento è un'**ipotesi da verificare**,
   non un risultato acquisito.
6. **Fair Reporting** — si riportano punti di forza *e* debolezze.
7. **Report Like a Scientist** — il report finale copre problema, metodologia,
   esperimenti, risultati, **limiti** e sviluppi futuri.

## 2. Metodo sperimentale

8. **Baseline Before Complexity** — prima una baseline semplice, poi
   l'architettura complicata. *Qui:* la baseline training-free `hist` e la GNN a
   **pesi casuali** hanno mostrato che quasi tutto il punteggio viene
   dall'architettura, non dal training: senza quel denominatore il guadagno
   sarebbe stato sopravvalutato di 10×.
9. **Incremental Changes (OFAT)** — una sola variabile significativa per volta,
   così l'effetto è attribuibile.
10. **Ablation-Oriented Thinking** — ogni componente aggiunta dev'essere
    giustificabile da uno studio di ablazione.
11. **Measurement Over Intuition** — decidono metriche ed esperimenti, non
    l'intuizione.
12. **Compare Fairly** — stessi dati, stesso protocollo, stesse esclusioni.
    Confronti a capacità di modello dichiarata (⚠️ I-JEPA è ViT-H contro ViT-B
    degli altri: va detto, non nascosto).
13. **Respect Statistical Significance** — differenze dell'ordine del rumore non
    sono risultati finché non è mostrato il contrario.
14. **Beware of Benchmark Overfitting** — non si ottimizza per un singolo
    benchmark; il test non seleziona nulla.
15. **Error Analysis Before Improvement** — prima si analizzano gli errori, poi
    si decide la modifica.
16. **Understand Before Optimizing** — capire il comportamento del sistema
    precede il tentativo di migliorarlo.

## 3. Dati e generalizzazione

17. **Data-Centric Mindset** — prima di toccare il modello, verificare qualità,
    distribuzione e correttezza dei dati. *Qui:* il tetto di MRR 0.970 a
    masking nullo non era un limite dei modelli ma dei **duplicati esatti**
    dentro RPLAN.
18. **Avoid Data Leakage** — massima attenzione a ogni contaminazione
    train/valid/test: statistiche dal solo train, selezione sul valid.
19. **Generalization Over Memorization** — si valuta la generalizzazione, non la
    prestazione sui dati visti.
20. **Distribution Awareness** — attenzione al divario fra distribuzione di
    training e dati reali (⚠️ gli encoder sono pre-allenati su immagini
    naturali, le planimetrie RPLAN sono colormap sintetiche: il *domain gap* è
    la spiegazione principale di più risultati).
21. **Robustness First** — comportamento su rumore, input degradati e casi
    limite (è letteralmente il *partial retrieval*).
22. **Edge Cases Matter** — i casi rari e apparentemente insignificanti contano.
23. **Quantify Uncertainty** — dove possibile, stimare la confidenza.

## 4. Metriche e interpretazione

24. **Metrics Must Match the Objective** — la metrica dev'essere coerente col
    problema reale. *Qui:* la val-loss InfoNCE **non** era coerente con il
    retrieval e ne invertiva la classifica; la sonda di retrieval sì.
25. **Interpretability Matters** — spiegare *perché* il modello si comporta
    così, non solo *quanto* rende.
26. **Visualize Before Concluding** — grafici, immagini e distribuzioni prima
    delle conclusioni.
27. **Inspect the Data Frequently** — guardare campioni del dataset durante
    tutto lo sviluppo, non solo all'inizio.
28. **Literature Awareness** — confronto continuo con lo stato dell'arte, senza
    copiarlo acriticamente.

## 5. Ingegneria della ricerca

29. **Reproducibility by Default** — configurazioni, seed, versioni, dataset e
    iperparametri documentati; ogni run rieseguibile.
30. **Keep Experiments Traceable** — ogni risultato riconducibile all'esatto
    esperimento che l'ha prodotto (`variant` → `save_dir`,
    `training_summary.json`).
31. **Version Everything** — codice, config, esperimenti e risultati.
32. **Configuration over Hardcoding** — parametri nei config, mai nel codice.
33. **Modularity** — preprocessing, dataset, modello, training, valutazione e
    visualizzazione restano separati.
34. **Consistency** — convenzioni uniformi per nomi, metriche, cartelle, config.
35. **Automation Whenever Possible** — training, valutazioni, logging e
    risultati ripetitivi si automatizzano.
36. **Computational Awareness** — costo, memoria, tempo di training e inferenza
    fanno parte del design. *Qui:* la render-cache ha eliminato 13 rendering
    ridondanti su 14.
37. **Scalability** — preferire soluzioni estendibili a dataset e modelli più
    grandi.
38. **Prefer Simplicity** — fra due soluzioni equivalenti vince la più semplice
    e leggibile.
39. **Document Decisions** — le motivazioni delle scelte principali si
    registrano (è la funzione di `.claude/shared/status.md`).
40. **Ethical Awareness** — bias, privacy, usi impropri e impatto del sistema.

## Come si usano

- `architect`: 8-16 e 24 quando scrive un protocollo; 29-39 quando progetta.
- `scientific-reviewer`: 1-7, 12-14, 17-20, 24 come griglia di review.
- `results-analyst`: 2, 11, 13, 24-25 per non trasformare rumore in conclusioni.
- `implementer` / `refactorer`: 29-39.
- Tutti: 1-7 sempre.
