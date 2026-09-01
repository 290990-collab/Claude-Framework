# Coding Conventions
Questo documento definisce le convenzioni di coding da seguire all'interno del progetto.
L'obiettivo è mantenere il codice:
- pulito;
- leggibile;
- semplice da mantenere;
- facilmente debuggabile;
- coerente tra moduli e contributor.

## Prefer simplicity over cleverness
Scrivere codice semplice e leggibile è preferibile rispetto a soluzioni troppo compatte o “smart”.
Evitare:
- one-liner complesse;
- nested logic inutilmente profonda;
- astrazioni premature;
- metaprogramming non necessario.
Preferire:
- esplicità;
- chiarezza;
- modularità.

## Readability first
Il codice deve essere leggibile anche dopo mesi.
Ogni funzione deve:
- avere uno scopo chiaro;
- avere input/output facilmente comprensibili.

## Small and modular functions
Preferire funzioni piccole e modulari.
Evitare funzioni monolitiche con:
- troppe responsabilità;
- troppe variabili locali;
- logica difficile da seguire.

# Training Loop Guidelines
Il training loop deve essere:
- leggibile;
- separato dalla model definition;
- separato dalla evaluation.
Separare chiaramente:
- forward pass;
- loss computation;
- backward pass;
- metrics;
- logging.

# Naming Conventions
I nomi di funzioni e variabili devono essere descrittivi.

# Comments and Documentation
## Mandatory comments for logical blocks
Ogni blocco logico significativo deve avere un commento breve ma chiaro che spieghi:
- cosa sta facendo il codice;
- perché viene fatto;
- eventuali assunzioni importanti.

## Function documentation
Ogni funzione deve includere:
- descrizione breve;
- input;
- output;
- eventuali side effects.

## Avoid obvious comments
NON scrivere commenti inutili.

Preferire commenti che spieghino:
- intenzione;
- motivazione;
- logica.

# Code Structure
## Separate responsibilities
Separare chiaramente:
- data loading;
- preprocessing;
- model definition;
- training;
- evaluation;
- visualization;
- utilities.

## Explicit error messages
Gli errori devono essere chiari e informativi.

# Deep Learning Conventions
## Tensor shapes
Documentare sempre shape importanti.
Esempio:
```python
# image_tensor: [B, C, H, W]
# embeddings: [B, D]
```

## Graph structures
Per GNN specificare sempre:
- node features;
- edge_index format;
- edge attributes;
- graph batching assumptions.
Esempio:
```python
# edge_index shape: [2, E]
# x shape: [N, F]
```

# Retrieval Pipeline Conventions
## Metrics
Documentare sempre:
- Recall@K;
- mAP;
- nDCG@K;
- similarity metric;
- normalization strategy;
- per le query parziali, il livello di masking applicato.

# Style Guidelines
# Preferred Coding Style
Il codice deve apparire:
- minimale;
- esplicito;
- scientificamente leggibile;
- facile da modificare.
- professionale

# Final Rule
Quando scrivi codice:
1. privilegia chiarezza e leggibilità;
2. commenta ogni blocco logico importante;
3. documenta input/output delle funzioni;
4. evita complessità non necessaria;
5. mantieni naming coerente;
6. scrivi codice facilmente mantenibile.