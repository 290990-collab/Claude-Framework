# Riscrittura del Portfolio in Astro — Design

Data: 2026-07-24
Stato: approvato in brainstorming, in attesa di revisione dello spec

## Obiettivo

Riscrivere da zero il sito portfolio di Enrico Di Maria (compositore) come sito
**statico design-first** con **Astro**, sostituendo l'attuale sito vanilla
(HTML/CSS/JS con GSAP/Lenis via CDN). Obiettivi: struttura vera (componenti,
contenuti tipati), performance eccellenti, bilingue IT/EN, e bassa manutenzione
per un utente con poca esperienza web. In parallelo, **riadattare ad Astro** il
framework di lavoro multi-agente contenuto in `framework-web/` (oggi tarato su
Next.js), preservando **integralmente le direttive di economia dei token**.

Non-obiettivi (YAGNI): CMS/pannello visuale, blog/news, contenuti dinamici,
e-commerce, autenticazione, form con backend. Il sito resta una vetrina statica.

## Decisioni prese (brainstorming)

1. **Tecnologia**: Astro (ultima versione) + TypeScript, nessun framework UI.
2. **Manutenzione contenuti**: editing di file nel repo (niente CMS).
3. **Ambito**: vetrina rifinita (home, lavori, bio, contatti) — poche pagine.
4. **Bilingue**: due URL statici, `/` (IT, default) e `/en/` (EN); il toggle
   naviga tra le due. Scelta migliore per SEO e più robusta con un SSG.
5. **Font**: self-hosted via Fontsource (Inter Tight / Inter) — niente richiesta
   esterna, niente CLS, meglio per privacy.
6. **Motion**: conservare le animazioni attuali (reveal allo scroll, intro hero,
   anteprima immagine che segue il cursore) con GSAP + ScrollTrigger + Lenis,
   sempre rispettando `prefers-reduced-motion`. Sparisce la dissolvenza del
   cambio-lingua (non serve più: sono pagine distinte).

## Stack e strumenti

- **Astro** + **TypeScript** (`strict`).
- Componenti `.astro` puri (zero runtime lato client tranne il motion).
- **GSAP + ScrollTrigger + Lenis** come singola *isola* client (`src/scripts/motion.ts`),
  caricata come modulo; installati come dipendenze npm (non più CDN).
- **Fontsource** per i font self-hosted.
- **i18n**: routing per lingua di Astro (config `i18n` in `astro.config.mjs`).
- Build statica (`astro build` → `dist/`). Nessun runtime server.
- Comandi: `npm run dev` (sviluppo), `npm run build` (produzione),
  `npm run preview` (anteprima build), `astro check` (type-check dei componenti).

## Struttura del progetto

```
src/
  layouts/
    BaseLayout.astro       <head>, meta/SEO, font, header, footer, <slot/>, motion
  components/
    Header.astro           logo, nav, toggle lingua
    Hero.astro             kicker, titolo a righe, meta
    WorkList.astro         lista lavori (itera i progetti)
    WorkRow.astro          singola riga progetto
    About.astro            ritratto, bio, servizi
    Contact.astro          lead, email (mailto), piattaforme
    LangToggle.astro       IT / EN (link alle due rotte)
  content/
    config.ts              schema Zod della collection "projects"
    projects/
      titolo-del-film-uno.md   ... un file per progetto (frontmatter tipato)
  i18n/
    it.ts                  dizionario testi UI in italiano
    en.ts                  dizionario testi UI in inglese
    index.ts               helper per selezionare il dizionario per lingua
  data/
    site.ts                dati neutri: email, piattaforme, costanti di sito
  styles/
    global.css             design token (:root) + reset + stili globali
  scripts/
    motion.ts              GSAP/Lenis: reveal, intro hero, preview cursore
  pages/
    index.astro            home IT (default)
    en/
      index.astro          home EN
public/
  img/                     immagini progetti, ritratto, favicon, OG image
  (font serviti da Fontsource via import nel CSS/JS, non a mano in public)
astro.config.mjs
package.json
tsconfig.json
```

## Modello dei contenuti

### Progetti — `src/content/projects/*.md`
Frontmatter validato da uno schema Zod in `src/content/config.ts`:

- `title` (string) — titolo del film/progetto (neutro rispetto alla lingua).
- `role` (`{ it: string; en: string }`) — ruolo nelle due lingue.
- `year` (string o number) — anno.
- `cover` (string) — percorso immagine (in `public/img/` o asset importato).
- `url` (string, opzionale) — link esterno (trailer/IMDb); vuoto = nessun link.
- `order` (number, opzionale) — per l'ordinamento manuale in vetrina.

Aggiungere un progetto = aggiungere un file `.md`. Un campo errato fa fallire il
build con messaggio chiaro (validazione al confine).

### Testi UI — `src/i18n/{it,en}.ts`
Dizionari tipati con le **stesse chiavi** nelle due lingue: `logo`, `nav.*`,
`hero.kicker`, `hero.titleLines` (array di righe), `hero.metaLeft`,
`hero.metaRight`, `works.heading`, `about.heading`, `about.paragraphs` (array),
`about.servicesLabel`, `about.services` (array), `contact.heading`,
`contact.lead`, `footer.copy`, `footer.top`. Un tipo condiviso garantisce che
entrambe le lingue restino allineate.

### Contatti e dati di sito
- `email` e `platforms` (nome + url) sono dati **neutri rispetto alla lingua** e
  vivono in `src/data/site.ts` (non duplicati nei dizionari IT/EN). Email resta un
  `mailto:`. Qui stanno anche eventuali costanti di sito (URL canonico, handle social).

## Bilingue (i18n)

- Config `i18n` in `astro.config.mjs`: `defaultLocale: "it"`, `locales: ["it","en"]`,
  con l'italiano servito alla radice (`/`) e l'inglese sotto `/en/`.
- `LangToggle` linka alla stessa pagina nell'altra lingua.
- `<html lang>` corretto per lingua; `hreflang` alternate nei `<head>` per SEO.
- Nessuna logica di scambio testi lato client: ogni lingua è una pagina statica.

## Stile e design system

- I **design token** attuali migrano invariati in `src/styles/global.css` `:root`:
  colori (`--bg`, `--ink`, `--muted`, `--line`, `--surface`), font
  (`--font-display`, `--font-body`), spaziatura/griglia (`--gutter`,
  `--section-gap`), scala tipografica (`--text-xs` … `--text-hero`).
- Lo stile Swiss/International Typographic resta identico nell'aspetto.
- Stili globali (reset, tipografia base, etichette maiuscoletto ricorrenti) in
  `global.css`; stili specifici di un componente nel relativo `.astro` (scoped).
- I token restano la **fonte unica**: nessun valore hardcoded nei componenti.

## Motion

- `src/scripts/motion.ts` replica il comportamento attuale: guardia
  `prefers-reduced-motion` e presenza di GSAP; reveal allo scroll degli elementi
  `[data-reveal]`; intro della hero (righe del titolo in stagger); anteprima
  immagine che segue il cursore sulla lista lavori (solo pointer fine, desktop).
- GSAP/Lenis importati come moduli npm, non da CDN. Degradazione con grazia se il
  modulo non carica o con reduced-motion: tutto visibile, nessun movimento.
- Durate/easing coerenti; nessuna animazione che causa CLS o blocca l'interazione.

## Framework di lavoro (.claude) riadattato ad Astro

Riadattamento di `framework-web/` da Next.js ad Astro, installato nella root del
progetto (`.claude/`, `CLAUDE.md`, `docs/`).

- **Agenti** (`.claude/agents/`): `explorer`, `architect`, `frontend`,
  `implementer`, `refactorer`, `deploy`, `final-reviewer`.
  - Potati: `tester` (nessun setup di test pesante per una vetrina statica: la
    verifica è a runtime nel browser; eventuali unit test di logica pura restano
    possibili ma non hanno un agente dedicato) e `security-reviewer` (superficie
    minima: nessun form/secret/backend). Entrambe le preoccupazioni sono ripiegate
    in `final-reviewer` e in CLAUDE.md.
- **Guide condivise** (`.claude/shared/`): `design-guide` (centrale),
  `architecture-guide`, `coding-standards`, `conventions`, `debugging-playbook`,
  `review-checklist`, e `verification-guide` (verifica manuale a runtime, che
  sostituisce `testing-guide`). Tutte riscritte per Astro/vanilla-JS/CSS.
- **CLAUDE.md**: preserva **integralmente**:
  - la sezione **Economia dei token** (tutti i 10 punti, invariati);
  - il metodo Think → Design → Plan → Implement → Verify;
  - Evidence Before Action (anti-allucinazione);
  - il formato del **Report standard** dei subagent.
  Aggiorna solo la parte specifica di progetto: stack (Astro), mappa cartelle,
  contratti, comandi di build, tabella di orchestrazione (senza tester/security).
- **Contratti** del progetto (per architect/reviewer/refactorer):
  1. Schema della collection `projects` (campi del frontmatter).
  2. Chiavi dei dizionari i18n (allineate tra `it` ed `en`).
  3. Nomi dei design token CSS (usati ovunque).
  4. URL/slug delle pagine e delle lingue (`/`, `/en/`) — contratto pubblico/SEO.
  5. Classi/attributi-aggancio del motion (`[data-reveal]`, selettori GSAP).

## Deploy e README

- Build statica `dist/` → deploy su Netlify (drag della cartella o repo connesso),
  Vercel, o GitHub Pages.
- README riscritto: ora l'installazione è richiesta (Node, `npm install`,
  `npm run dev`/`build`); istruzioni per aggiungere un progetto (nuovo `.md`),
  modificare i testi (`i18n/`), cambiare colori/font (`global.css`), pubblicare.

## Migrazione dei contenuti attuali

I contenuti attuali sono segnaposto (titoli di film fittizi, immagini SVG
placeholder). Si migrano 1:1 nel nuovo modello: i 5 progetti diventano 5 file
`.md`; i testi IT/EN diventano i dizionari `i18n`; i token CSS si copiano; le
immagini restano in `public/img/`. Nessun contenuto reale viene inventato.

## Criteri di successo

- `npm run build` produce `dist/` senza errori; `astro check` pulito.
- Le due lingue rendono a `/` e `/en/` con contenuti corretti e allineati.
- Aspetto Swiss identico all'attuale; token come fonte unica dello stile.
- Motion funzionante e conforme a `prefers-reduced-motion` (verifica a runtime).
- Aggiungere un progetto richiede solo un nuovo file `.md` valido.
- `.claude/` + `CLAUDE.md` + `docs/` presenti nella root, coerenti con Astro, con
  le direttive di economia dei token preservate integralmente.

## Questioni aperte / rischi

- **Installazioni**: Node e i pacchetti npm (Astro, GSAP, Lenis, Fontsource)
  richiedono conferma esplicita dell'utente prima dell'installazione.
- **Git**: la cartella non è ancora un repository git; commit e versionamento
  vanno abilitati se/quando l'utente lo vuole.
- **`framework-web/`**: dopo il riadattamento la cartella sorgente diventa
  ridondante (e descrive lo stack sbagliato); rimozione da confermare con l'utente.
- **Contenuti reali**: titoli, immagini, bio e link reali restano da fornire;
  non vanno inventati.
