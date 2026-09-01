# Guida all'architettura — Portfolio

Topologia: una singola app **Next.js** (App Router). Le viste in `app/` compongono
componenti da `components/`, che leggono lo stile dai token di `design/` e i dati
dei progetti da `lib/`, il quale li carica dietro un'**astrazione di sorgente**
(oggi statico MDX, domani eventualmente un CMS). Nessun backend complesso: al
massimo route API leggere (es. submit del form di contatto).

## Confini e responsabilità

- `lib/` — logica **pura** e riusabile: caricamento/normalizzazione dei progetti
  (dietro l'astrazione), filtro per categoria/tag, ordinamento, "progetti
  correlati", formattazione (date/numeri). **Nessuna dipendenza da React/DOM/
  framework**: il cuore testabile in isolamento. Una funzione che non tocca UI né
  I/O di rendering vive qui.
- `design/` — design tokens e primitive di stile; nessuna logica.
- `components/` — presentazione e interazione; consumano i dati da `lib/` e lo
  stile dai token. Nessuna logica di dominio nei componenti.
- `app/` — rotte, layout, metadata, composizione delle viste. Orchestra, non
  duplica la logica di `lib/`.
- `content/` — i progetti come dati/MDX; letti solo tramite l'astrazione di
  sorgente in `lib/`, mai direttamente dalle viste.
- `public/` — asset statici.

Regola pratica: una funzione che non tocca UI, rendering o rete probabilmente va
in `lib/`. Un valore di stile va in `design/`. Un dato di progetto passa da `lib/`.

## I contratti (cambiarli = decisione architetturale)

1. **Schema dei contenuti** — i campi di un progetto (slug, title, category ∈
   {art, commercial, tech}, year, tags, cover, media, description, links…),
   definiti come frontmatter MDX o schema CMS + validazione (Zod). Cambiarli
   impone di aggiornare TUTTI i contenuti esistenti e le viste che li leggono.
2. **Slug/URL dei progetti** — formato persistito pubblico: link condivisi e SEO.
   Cambiare uno slug rompe i link esterni → serve un redirect (lato deploy).
3. **Chiavi dei design token** — contratto interno usato ovunque nei componenti;
   rinominarle rompe lo stile in silenzio (il compilatore aiuta poco con le
   stringhe). Migrazione = aggiornare tutti gli usi.
4. **Astrazione di sorgente contenuti** — l'interfaccia tra `lib/` e la sorgente
   (statico vs CMS) che tiene aperta la questione #1: un nuovo backend la
   implementa senza toccare viste e logica a valle.

Input da fonti esterne (submit del form di contatto, dati da un CMS, immagini
remote) = confine di fiducia: validati (schema, lunghezze, range), mai eseguiti,
host esterni su allowlist (`next/image` `remotePatterns`, fetch CMS) — anti-SSRF.

## Decisioni vincolanti già prese

- **`lib/` puro**: nessuna dipendenza da React/DOM/framework nella logica.
- **Design coerente dai token**: niente stile hardcoded; `design/` è la fonte unica.
- **Sorgente contenuti non decisa (questione aperta #1)**: la logica resta dietro
  l'astrazione; nessuna scelta incastra su statico o CMS.
- **Accessibilità e performance come requisiti**: WCAG AA e Core Web Vitals nel
  verde non sono rifiniture opzionali.
- **Multilingua-ready**: niente hardcode di lingua, formati data/numero; i18n dal
  layer apposito anche partendo da una sola lingua.
- **Superficie sensibile minima**: a parità di risultato vince l'alternativa che
  espone meno segreti e meno dati (attenzione a `NEXT_PUBLIC_*` e agli analytics).

## Valutare una proposta di design (per l'architect)

1. Quali contratti tocca? (nessuno = rischio molto più basso)
2. Cosa succede ai link esistenti e alla SEO se cambiano gli slug?
3. Regge la coerenza del design system (token, un solo linguaggio visivo)?
4. Degrada con grazia se un contenuto o una risorsa esterna (immagine, CMS)
   è assente o cambia?
5. Aggiunge superficie sensibile (secret, input non fidato, tracciamento)?
6. Regge accessibilità, performance e reduced-motion?
7. Qual è l'alternativa più semplice che risolve il 90% del problema? (KISS)
