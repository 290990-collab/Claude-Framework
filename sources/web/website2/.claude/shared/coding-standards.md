# Standard di codice — FindShop

Regola sovraordinata: **il codice nuovo imita il file in cui vive**. Questi
standard valgono dove il file non dà indicazioni.

## Stack principale (TypeScript: web, mobile, backend)

Pattern concreti attesi nel repo (verificarli sull'uso reale, mai a memoria —
Next.js/Expo/NestJS/Prisma/Typesense evolvono in fretta):

- **TypeScript stretto**: `strict` attivo; niente `any` non giustificato; tipi
  e validazione presi dai contratti in `packages/shared` (Zod), mai ridefiniti
  a mano lato client.
- **Async**: `async/await`, mai `.then` annidati; ogni `await` su I/O gestisce
  l'errore o lo propaga; niente promise fire-and-forget fuori dai punti
  previsti; niente lavoro CPU pesante che blocca il ciclo di eventi.
- **Confine puro**: `packages/core` non importa React/Next/Nest/RN/driver DB —
  solo logica di dominio testabile in isolamento. Una funzione che non tocca UI
  né I/O vive nel core.
- **Accesso dati (backend)**: query parametrizzate via ORM (Prisma), mai
  concatenazione di SQL; niente N+1 (batch / relazioni esplicite); connessioni
  e transazioni chiuse anche sui percorsi d'errore.
- **Input non fidato** (query di ricerca, payload API, feed di ingestion):
  validato al confine con lo schema (Zod) prima di toccare dominio o DB; limiti
  di lunghezza e dimensione; mai eseguire né interpolare contenuti ricevuti.
- **Geo e prezzi**: coordinate validate (range lat/lon), distanze via PostGIS;
  prezzi in interi (centesimi) con valuta esplicita, mai float; nessuna
  assunzione di valuta/locale singola.
- **Path e URL**: API di join, mai concatenazione di stringhe; gli URL esterni
  (adapter di ingestion, provider mappe) passano da una allowlist (anti-SSRF).
- **Log**: strutturati e con contesto; MAI PII, geolocalizzazione grezza,
  token o query utente in chiaro.
- **React (web e mobile)**: la logica di business non vive nei componenti ma nel
  core / nei service; dettagli UI in `frontend`.

## Backend dati e infrastruttura

- **Migrazioni** (Prisma/SQL): ogni cambio di schema è una migrazione
  versionata e reversibile; mai modifiche a mano allo schema in produzione;
  compatibilità di lettura coi dati esistenti (default per campi nuovi).
- **Indice Typesense**: lo schema dell'indice è un contratto; un cambio impone
  reindicizzazione — segnalarlo. L'indice si rigenera dal source of truth, non
  è mai l'unica copia del dato.
- **IaC**: infrastruttura descritta come codice (vedi `infra`), niente modifica
  manuale delle risorse cloud; segreti fuori dal repo (secret manager / env).

## Performance

Budget per superficie (dichiarare nel report se un cambio li mette a rischio):

- **Web**: Core Web Vitals nel verde (LCP, CLS, INP); rendering server dove
  aiuta primo caricamento e SEO; niente lavoro pesante nel main thread del
  browser.
- **API**: latenza p95 della ricerca sotto controllo; la geo-ricerca passa
  dall'indice (Typesense), non da scansioni SQL; niente N+1.
- **Mobile**: liste virtualizzate, immagini dimensionate, niente lavoro pesante
  sul thread UI; startup rapido.
- **In generale**: niente busy-polling (eventi/webhook/intervalli ampi);
  percorsi caldi senza allocazioni evitabili né lavoro O(n) ripetuto per
  richiesta; strutture che non reggono i volumi reali si dichiarano, non si
  subiscono.

## Regole comuni

- Nomi che dicono cosa, commenti (pochi) che dicono perché.
- Funzioni corte, un livello di astrazione; 3 `if` annidati ≈ manca un
  early-return.
- Costanti nominate al posto di numeri/stringhe magiche ripetuti.
- Simmetria: se esistono `open`/`close`, `subscribe`/`unsubscribe`, ogni nuova
  risorsa segue lo stesso schema.
- Degradazione con grazia: mai crashare l'esperienza dell'utente; ogni
  fallimento (dipendenza assente, rete caduta, indice non raggiungibile, config
  corrotta) ha un esito visibile e recuperabile, mai silenzioso.
