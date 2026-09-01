# Potenziale economico — FindShop

Analisi strategica del modello di business. I dati di mercato qui sono **ordini
di grandezza**, non cifre verificate: prima di un pitch vanno sostituiti con
fonti aggiornate. Il *cosa/come* di prodotto sta in [roadmap.md](roadmap.md).

## Sintesi

Potenziale **alto** ma **vincolato** da una sola leva: costo e legalità
dell'acquisizione dei dati di inventario dei negozi. Non è un rischio
tecnologico (la ricerca geo la fa qualunque motore), è un rischio di **business
development e legale**. Chi possiede il dataset inventario+prezzo in tempo reale
per negozio vince; tutto il resto è replicabile.

## Il problema e l'opportunità

Il consumatore di abbigliamento si comporta secondo il pattern **ROPO**
(Research Online, Purchase Offline): cerca online, compra in negozio. Oggi manca
il pezzo "quale negozio *vicino a me* ha *questo* capo, ora, a *questo* prezzo".
Google Shopping e i local inventory ads ci arrivano vicino ma sono generalisti e
pay-to-play; nessuno è verticale su **moda + geolocalizzazione + prezzo**. È lo
spazio che FindShop occupa.

## Mercato (framing TAM → SOM)

- **TAM** — il retail abbigliamento in Italia è nell'ordine delle decine di
  miliardi di €/anno (mercato grande e maturo).
- **SAM** — FindShop non vende vestiti: vende **traffico qualificato e dati** ai
  retailer. Il mercato indirizzabile reale è la loro spesa in
  advertising/lead-gen/local marketing, più eventuali fee sui volumi
  intermediati: una frazione del TAM, ma su una base enorme.
- **SOM** — Italia, poche città/categorie pilota: piccolo, ma sufficiente a
  validare le unit economics prima di scalare.

## Modelli di ricavo (in ordine di realismo)

1. **Lead-gen / commissione per visita o click qualificato** verso il negozio
   (pay-per-result): basso attrito, allineato al valore generato.
2. **Abbonamento SaaS per il negozio**: presenza, gestione catalogo/prezzi,
   analytics ("cosa cercano vicino a te e non trovano"). Ricavo ricorrente, il
   pezzo più prezioso, più un **setup una-tantum** per l'integrazione dei dati
   del negozio (spesso eterogenei).
3. **Promoted listings / ranking sponsorizzato**: scala con l'audience.
4. **Affiliazione** su click-to-reserve / click-to-buy dove il negozio ha e-commerce.
5. **Dati aggregati e anonimi di domanda locale** venduti a brand/retailer:
   margine altissimo, ma solo con volumi e densità di dati — e solo con consenso
   esplicito e nessun profilo individuale (vincolo GDPR).
6. **Consumer premium** (avvisi disponibilità/prezzo/taglia): marginale
   all'inizio, utile per la retention.

Mix sano: **2 (ricorrente) + 1/3 (variabile sul traffico)**; il **5** diventa la
leva ad alto margine quando la densità di dati è sufficiente.

## Il moat è anche il rischio n.1

Il fossato difendibile è il **dataset inventario+prezzo in tempo reale**, non
l'app né la ricerca. È la "questione aperta #1":

- **Con** feed strutturati (accordi catene, integrazioni POS/e-commerce tipo
  Shopify/Google Merchant) le unit economics reggono e il moat cresce da solo.
- **Senza**, ricostruire il dato negozio-per-negozio (a mano o via scraping) fa
  esplodere il **costo di acquisizione del dato** e apre un rischio legale (ToS).

L'architettura ad **adapter pluggabili** scelta a livello tecnico è quindi anche
**de-risking economico**: si parte dalle fonti più facili e si aggiungono le
altre senza riscrivere la pipeline.

## Chicken-and-egg (due lati) e go-to-market

Servono negozi (dati) per attrarre utenti, e utenti per convincere i negozi.
Mosse che funzionano:

- **Partire densi, non larghi**: una città, una categoria, fino a saturazione.
- **Seed dei dati** con le fonti più accessibili (retailer con e-commerce/feed
  già pronti) per dare valore all'utente *prima* di firmare le catene.
- **Monetizzare i negozi dopo** aver mostrato traffico reale, non prima.

## Pilota candidato: Modena

Modena è un buon banco di prova: città di media dimensione (facile da saturare),
centro storico con retail concentrato, città universitaria (popolazione giovane
e sensibile alla moda), territorio benestante in un distretto della moda
(Emilia-Romagna). Impostazione proposta:

- **Una categoria** ad alta ricercabilità e forte domanda giovane (es. sneakers /
  streetwear), non l'intero abbigliamento.
- **Prime fonti dati realistiche**: boutique e retailer del centro con
  e-commerce/feed già pronti + eventuali catene con integrazione POS; import
  manuale per il seed iniziale della demo.
- **Obiettivo del pilota**: densità sufficiente a rendere la ricerca *utile* in
  centro, così da avere un caso di traffico reale con cui aprire il dialogo
  commerciale con le catene.

## Rischi principali

- **Acquisizione dati** (costo + legalità): il rischio dominante.
- **Livello di dettaglio del dato** (es. quantità disponibile in tempo reale):
  molto più difficile di presenza+prezzo; per l'MVP trattarla come opzionale/
  best-effort, non requisito.
- **Freschezza del prezzo/disponibilità**: un dato vecchio distrugge la fiducia;
  la sync deve essere credibile.
- **Cold start** su entrambi i lati del marketplace.
- **Concorrenza di piattaforma** (Google) se il verticale si dimostra grande.

## Metriche da validare nel pilota

Copertura (quota di negozi/stock reale indicizzato in centro), freschezza del
dato, ricerche con risultato utile / ricerche totali, tasso di click-to-store,
costo di acquisizione del dato per negozio, disponibilità dei retailer a pagare.

---

Ultimo aggiornamento: 2026-07-24
