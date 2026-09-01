# Guida al design — Portfolio

La guida centrale di questo progetto **design-first**. Il design non è
decorazione applicata alla fine: è deciso prima del markup e vincola tutto ciò
che segue. Regola sovraordinata: **coerenza prima della creatività** — un
linguaggio visivo solo, applicato ovunque.

## Design tokens = fonte unica

Tutto lo stile passa dai token in `design/`. Nessun valore magico nei componenti.

- **Colore**: palette ridotta (fondo, testo, accento, stati). Definire i ruoli
  semantici (`bg`, `fg`, `muted`, `accent`, `border`) oltre ai valori grezzi. Se
  c'è tema chiaro/scuro, i ruoli sono la fonte, non i colori assoluti.
- **Tipografia**: poche famiglie (idealmente 1-2), una scala tipografica esplicita
  (es. modulare), pesi definiti, line-height e letter-spacing per livello.
  Font caricati senza layout shift (`next/font`).
- **Spaziatura**: una scala coerente (es. multipli di 4/8); niente margini
  arbitrari. Lo spazio bianco è uno strumento di design, non vuoto da riempire.
- **Griglia e breakpoint**: griglia dichiarata, breakpoint nominati, container con
  larghezze massime coerenti.
- **Motion**: durate ed easing come token (es. `fast`, `base`, `slow`;
  `ease-out`, `ease-in-out`), così ogni animazione parla la stessa lingua.
- **Raggi, ombre, bordi**: anche questi come token, per coerenza.

Aggiungere un token è un cambiamento consapevole (è un contratto interno usato
ovunque): riusa un token esistente prima di crearne uno nuovo.

## Direzione estetica

Appoggiati alle skill `swiss-design` e `frontend-design` per la direzione. Principi
guida per un portfolio:

- **Griglia e allineamento rigoroso**: tutto è allineato a qualcosa; niente
  posizioni "a occhio".
- **Gerarchia chiara**: dimensione, peso e spazio dicono cosa conta; l'occhio sa
  dove andare.
- **Spazio bianco generoso**: il contenuto respira; il lavoro (arte, progetti)
  è il protagonista, non l'interfaccia.
- **Ridurre**: poche famiglie tipografiche, palette ristretta, pochi elementi per
  vista. Se un elemento non serve, si toglie.
- **Il contenuto guida la forma**: un progetto artistico e uno tecnico possono
  meritare trattamenti diversi, ma dentro lo stesso sistema (stessi token, stessa
  griglia).

## Movimento (minimale)

- **Motivato, non gratuito**: entrata di sezioni al primo scroll, hover sui
  progetti, transizioni di pagina/route. Il movimento comunica (continuità,
  gerarchia, feedback), non intrattiene.
- **Sottile e veloce**: durate brevi, easing naturale (dai token). Il sito deve
  sembrare reattivo, non "in attesa dell'animazione".
- **`prefers-reduced-motion` SEMPRE**: chi lo imposta riceve una versione senza
  movimento (o con dissolvenze minime). Non è opzionale.
- **Niente danni**: nessuna animazione che causa layout shift (CLS), blocca lo
  scroll, ruba il focus o impedisce l'interazione.
- La libreria (es. Framer Motion) va verificata nell'uso reale del repo; le durate/
  easing vengono dai token, non hardcodate nel componente.

## Accessibilità (requisito, non extra)

- Contrasto testo/fondo conforme WCAG AA (verificare le coppie di colore reali).
- Focus visibile su ogni elemento interattivo; ordine di tab logico.
- Semantica HTML corretta (heading in ordine, `nav`, `main`, `figure`…).
- `alt` che descrive davvero l'immagine di un progetto (non "immagine").
- Target tattili adeguati; nessuna informazione veicolata dal solo colore.
- Media: video con controlli, niente autoplay con audio.

## Performance (è estetica)

- Immagini dei progetti via `next/image` (sizing esplicito, lazy, formati moderni).
- Font senza CLS; evitare FOUT/FOIT vistosi.
- Core Web Vitals nel verde (LCP, CLS, INP); niente lavoro pesante nel main thread.
- Media pesanti (portfolio = molte immagini/video): caricamento progressivo,
  dimensioni responsive, poster per i video.

## Figma e Framer

- **Figma (MCP)**: per portare un design Figma in codice usa la skill
  `figma-design-to-code` prima di `get_design_context`; per il verso opposto le
  skill `figma-use`/`figma-generate-*`. I tool richiedono l'autorizzazione del
  connettore (via `/mcp`): se manca, i tool non funzionano — segnalalo, non
  inventare l'output. Quando importi da Figma, mappa i valori sui **token** del
  progetto invece di hardcodare i valori grezzi del file.
- **Framer**: sezioni/prototipi nati in Framer si integrano nel codice sui token e
  sui componenti esistenti; non ricreare un secondo design system parallelo.

## Checklist rapida per una vista nuova

- [ ] Ogni valore di stile viene da un token in `design/`?
- [ ] Riuso componenti esistenti invece di crearne varianti?
- [ ] Griglia e allineamento rispettati; gerarchia leggibile?
- [ ] Motion motivato, dai token, con `prefers-reduced-motion`?
- [ ] Contrasto, focus, tastiera, `alt`, semantica a posto?
- [ ] Immagini via `next/image`; niente CLS; responsive mobile→desktop?
- [ ] Stati vuoto/caricamento/errore curati?
