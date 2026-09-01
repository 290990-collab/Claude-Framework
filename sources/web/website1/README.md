# Portfolio — Enrico Di Maria, Compositore

Sito portfolio minimalista in stile **Swiss / International Typographic Style**, ispirato a [saltandbits.com](https://saltandbits.com/en). Bilingue (IT/EN), con smooth scroll e animazioni curate (GSAP + Lenis via CDN).

**Nessuna installazione richiesta**: è un sito statico puro (HTML/CSS/JS). Niente Python, niente build.

---

## Come vedere il sito in locale

Apri un terminale in questa cartella e lancia **uno** di questi due comandi:

```powershell
# con Python (già installato)
python -m http.server 8000

# oppure con Node.js
npx serve .
```

Poi apri il browser su `http://localhost:8000` (o l'indirizzo che ti indica `serve`).

> Nota: aprire `index.html` con doppio clic funziona quasi sempre, ma un piccolo server locale è il modo corretto e identico a come funzionerà online.

---

## Come personalizzare i contenuti

### 1. Testi, progetti e link → `js/content.js`

**È l'unico file che devi modificare.** Dentro trovi, commentato:

- `email` — la tua email di contatto
- `projects` — la lista dei tuoi lavori (titolo, ruolo IT/EN, anno, immagine, link)
- `platforms` — i link a Spotify, Apple Music, SoundCloud, ecc. (sostituisci i `#`)
- `it:` e `en:` — tutti i testi del sito nelle due lingue (titolo della hero, bio, servizi, ecc.)

Per aggiungere o togliere un progetto basta aggiungere/eliminare un blocco `{ ... },` nell'array `projects`. Lo stesso vale per `platforms` e per le righe del titolo (`titleLines`).

### 2. Foto → `assets/img/`

Le immagini attuali sono segnaposto SVG. Sostituiscile così:

1. Copia le tue foto in `assets/img/` (es. `work-1.jpg`, `portrait.jpg`)
2. In `js/content.js` aggiorna i percorsi `img:` dei progetti (es. `"assets/img/work-1.jpg"`)
3. Per il ritratto della bio, aggiorna il `src` dell'immagine `portraitImg` in `index.html`

Formati consigliati: **JPG** per le foto, circa **1200×900 px** per i progetti (proporzione 4:3) e **900×1125 px** per il ritratto (4:5). Comprimile prima (es. con [squoosh.app](https://squoosh.app)) per tenere il sito veloce.

### 3. Colori e tipografia → `css/style.css`

In cima al file ci sono le **variabili CSS**: cambiando quelle cambi tutto il sito.

```css
--bg: #f4f2ee;     /* colore di sfondo */
--ink: #161614;    /* colore del testo */
--muted: #76736b;  /* testo secondario */
```

I font sono **Inter Tight** (titoli) e **Inter** (testo) da Google Fonts; per cambiarli modifica il `<link>` dei font in `index.html` e le variabili `--font-display` / `--font-body`.

### 4. Titolo e descrizione per Google → `index.html`

Aggiorna `<title>` e `<meta name="description">` in cima al file.

---

## Struttura del progetto

```
Portfolio/
├── index.html          → struttura della pagina
├── css/style.css       → tutto lo stile (variabili in cima)
├── js/content.js       → ★ I TUOI CONTENUTI (modifica questo)
├── js/main.js          → animazioni e logica (non serve toccarlo)
├── assets/img/         → le tue foto
└── README.md           → questa guida
```

---

## Come pubblicarlo online (gratis)

**Opzione A — Netlify Drop (più semplice):**
vai su [app.netlify.com/drop](https://app.netlify.com/drop) e trascina l'intera cartella `Portfolio` nella pagina. Fine: hai un URL pubblico. Potrai poi collegare un dominio tuo (es. `enricodimaria.com`).

**Opzione B — GitHub Pages:**
crea un repository su GitHub, carica questi file e attiva *Settings → Pages → Deploy from branch*.

---

## Note tecniche

- Le animazioni usano [GSAP](https://gsap.com) (reveal allo scroll, intro della hero, anteprima immagini che segue il cursore) e [Lenis](https://github.com/darkroomengineering/lenis) (smooth scroll), caricate via CDN: serve una connessione internet la prima volta che si apre la pagina.
- Il sito rispetta `prefers-reduced-motion`: chi ha le animazioni ridotte nel sistema operativo vede tutto senza movimento.
- La lingua scelta viene ricordata dal browser (localStorage); al primo accesso usa la lingua del browser del visitatore.
