# Roadmap — Portfolio

Il *cosa* e il *come* per fasi. Lo stato operativo (spunte) sta in
[TODO.md](TODO.md). Ordine pensato per ridurre il rischio: prima design system e
struttura, poi i contenuti, poi le viste, e solo dopo le rifiniture e il deploy.

## Fase 0 — Fondamenta

Scaffolding dell'app Next.js (App Router, TypeScript stretto, lint), toolchain
condivisa (pnpm, ESLint/Prettier), CI di base. `design/` con i primi **design
token** (scala tipografica, palette, spaziatura, motion). Obiettivo: `pnpm build`
verde su uno scheletro vuoto ma coerente.

## Fase 1 — Design system

Direzione visiva decisa (tipografia, griglia, palette, ritmo, tono del movimento)
appoggiandosi a `swiss-design`/`frontend-design` e, se utile, a un file Figma.
Primitive di stile e componenti base (tipografia, layout/griglia, bottoni, card,
navigazione) costruiti sui token. Regole di motion (durate, easing,
`prefers-reduced-motion`). Vedi `.claude/shared/design-guide.md`.

## Fase 2 — Contenuti e dominio

Modello di un progetto (slug, title, category ∈ {art, commercial, tech}, year,
tags, cover, media, description, links) e **schema dei contenuti** (frontmatter
MDX o schema CMS). Logica pura in `lib/`: caricamento dietro l'astrazione di
sorgente, filtro per categoria/tag, ordinamento, "progetti correlati". Contenuti
di prova per popolare le viste.

## Fase 3 — Viste

`app/`: home (hero + progetti in evidenza), lista lavori con filtro per
categoria, pagina dettaglio progetto (media, descrizione, link, correlati),
about, contatti. Motion minimale sulle transizioni e sugli stati. Stati vuoto/
caricamento/errore curati. Responsive da mobile a desktop.

## Fase 4 — Rifinitura

Accessibilità (contrasto, focus, tastiera, alt, semantica), performance (Core Web
Vitals, `next/image`, font senza CLS), SEO e social (metadati, Open Graph/Twitter,
sitemap, slug stabili). Eventuale i18n se il sito è multilingua. Micro-interazioni
e dettagli visivi.

## Fase 5 — Deploy e contenuti reali

Deploy su hosting statico/edge (Vercel/Netlify), dominio, variabili d'ambiente e
secret (analytics, servizio form contatti). Risolvere la **questione aperta #1**
(sorgente contenuti: restare su MDX statico o adottare un CMS headless) e
implementare l'adapter corrispondente dietro l'astrazione già predisposta.
Popolare i progetti reali.
