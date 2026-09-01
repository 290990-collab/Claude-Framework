# Standard di codice — Portfolio

Regola sovraordinata: **il codice nuovo imita il file in cui vive**. Questi
standard valgono dove il file non dà indicazioni.

## Stack principale (TypeScript: Next.js / React)

Pattern concreti attesi nel repo (verificarli sull'uso reale, mai a memoria —
Next.js/React e le librerie evolvono in fretta):

- **TypeScript stretto**: `strict` attivo; niente `any` non giustificato; i tipi
  dei contenuti derivano dallo schema (Zod), non ridefiniti a mano.
- **Componenti**: funzionali, piccoli, una responsabilità; Server Components di
  default, Client Components (`"use client"`) solo dove servono stato/effetti/
  eventi. La logica di business non vive nei componenti ma in `lib/`.
- **Design Token First**: colori, spaziature, tipografia, motion vengono da
  `design/`; niente valori magici nei componenti. Un solo componente per ruolo
  (una card progetto, non tre).
- **Async**: `async/await`, mai `.then` annidati; ogni `await` su I/O gestisce
  l'errore o lo propaga; niente promise fire-and-forget fuori dai punti previsti.
- **Confine puro**: `lib/` non importa React/DOM/framework — solo logica di dominio
  testabile in isolamento (filtro, ordinamento, correlati, formattazione).
- **Input non fidato** (submit del form, query string, dati da CMS): validato al
  confine con lo schema (Zod) prima dell'uso; limiti di lunghezza/dimensione; mai
  eseguire né interpolare contenuti ricevuti; niente `dangerouslySetInnerHTML` su
  contenuto non fidato.
- **Immagini/media**: `next/image` con sizing esplicito; host remoti su
  `remotePatterns` ristretti (anti-SSRF); font via `next/font` (niente CLS).
- **Path e URL**: API di join, mai concatenazione di stringhe; URL esterni (CMS,
  immagini) su allowlist.
- **Segreti**: mai nel client; attenzione a `NEXT_PUBLIC_*` (finisce nel bundle);
  token solo in variabili d'ambiente/secret. Niente segreti o PII nei log.

## Stile e design system

- **Token, non hardcode**: vedi `design-guide.md`. Ogni valore di stile ha (o
  diventa) un token in `design/`.
- **Motion**: durate/easing dai token; `prefers-reduced-motion` sempre gestito;
  niente animazioni che causano CLS o bloccano l'interazione.
- **Accessibilità**: contrasto AA, focus visibile, semantica, `alt`, tastiera.

## Performance

Budget per superficie (dichiarare nel report se un cambio li mette a rischio):

- **Core Web Vitals nel verde**: LCP (immagine hero ottimizzata), CLS (font e
  media dimensionati), INP (niente lavoro pesante nel main thread).
- **Rendering**: statico/SSR dove aiuta primo caricamento e SEO; Client Components
  solo dove necessario.
- **Media**: portfolio = molte immagini/video → caricamento progressivo,
  dimensioni responsive, poster per i video, formati moderni.
- **In generale**: niente busy-polling; percorsi caldi senza allocazioni evitabili;
  strutture che non reggono i volumi reali (molti progetti) si dichiarano.

## Regole comuni

- Nomi che dicono cosa, commenti (pochi) che dicono perché.
- Funzioni/componenti corti, un livello di astrazione; 3 `if` annidati ≈ manca un
  early-return.
- Costanti/token nominati al posto di numeri/stringhe magiche ripetuti.
- Simmetria: se esistono `open`/`close`, `subscribe`/`unsubscribe`, ogni nuova
  risorsa segue lo stesso schema.
- Degradazione con grazia: mai crashare l'esperienza; ogni fallimento (contenuto
  mancante, immagine assente, CMS non raggiungibile, config corrotta) ha un esito
  visibile e recuperabile (stato vuoto/errore curato), mai silenzioso.
