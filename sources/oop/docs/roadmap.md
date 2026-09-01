# LiveLoader — Roadmap: Free, Pro, Design

Stato e specifica delle funzionalità. Tre binari: **① Free** (l'app di oggi, da
completare) · **② Pro** (a pagamento) · **③ Design UX/UI** (step successivo).

---

## ① Free — completare l'app attuale

La versione gratuita è quella funzionante oggi. Da chiudere:

- [x] **macOS milestone (runtime)** — trigger Cmd+Right-click, rilevamento Live in
  primo piano (poller UI), attivazione Live, permesso Accessibilità, fix crash
  avvio (`EventWaitHandle`), agent da barra menu (`LSUIElement`). *Da collaudare
  sul Mac.*
- [x] **Scansione Audio Units (AU)** — solo su macOS: voce "Audio Units (AU)" nel
  box di scansione, **deselezionata** di default (come VST2), riscansionabile.
  Script `1.2.0`. *Da verificare su Mac l'etichetta AU reale del browser.*
- [x] **Snappiness** — poll del Remote Script 100ms → **33ms (~30 Hz)**: comandi
  load/scan più reattivi. Budget: RAM < 80–100 MB, CPU idle < 0,8–1% (oggi ~42 MB
  / ~0,05%: ampio margine).
- [x] **Messaggio "minimizza nel tray"** — non era un bug: i miei script di test
  avevano messo `ShowStartupNotice=false` nella config locale. Ripristinato.
- [ ] **Collaudo Mac end-to-end** (build .app, permessi, scan incl. AU, menu,
  load). *Prossimo passo pratico.*
- [ ] Eventuale calibrazione posizionamento menu su Retina (punti↔pixel).

---

## ② Pro — specifica funzionale

> Tutti i trigger usano **mouse + modificatori** letti dalla maschera dell'evento
> (come l'attuale Cmd/Ctrl+Right-click): **nessun hook di tastiera**, coerente col
> vincolo antivirus. I chord vanno mappati per OS (su macOS Cmd sostituisce Ctrl).

### 2.1 Quick-launcher stile Spotlight  — ✅ implementato (v1), da collaudare in Live
- **Trigger:** `Ctrl+Alt+Right-click` (macOS: `Cmd+Alt+Right-click`). Stessa famiglia
  del menu (`Ctrl+Right-click`, senza Alt) e della futura chain mode
  (`Ctrl+Shift+Right-click`), distinti dai modificatori. Letto dalla maschera
  dell'evento, **nessun hook tastiera**.
- **Cerca su TUTTO il catalogo di Live** (plugin VST2/VST3/AU + device nativi +
  preset), non solo i preferiti — **capacità esclusiva dello spotlight**, mentre il
  menu resta la lista dei preferiti. Fonte: `catalog.json` (serve almeno una
  scansione del browser; per trovare *tutto* va scansionato tutto, incl. VST2/AU).
- **Implementazione:** motore `AbletonLoader.Core/QuickMatch.cs` (logica pura,
  12 test di disambiguazione verdi), UI `Views/QuickLauncherWindow` (finestra
  borderless al cursore, come il menu). Flag config: `QuickLauncher` (on/off) e
  `QuickLauncherAutoLoad` (auto-load sì/no). Collaudo veloce senza Live: avvio con
  `--quick-test`.
- **Auto-load senza conferma:** carica il device direttamente **solo quando la
  query risolve a UN unico device con confidenza alta** (nessuna selezione col
  mouse). In ogni altro caso resta la tendina con tutti i candidati selezionabili.
- **Disambiguazione — regola GENERALE**, valida per qualsiasi plugin/device (i
  nomi sotto sono **solo esempi illustrativi**, la logica non è cablata su
  plugin specifici):
  - **Tie-break sul formato:** se i candidati hanno lo **stesso nome e sono tutti
    plugin**, preferisci **VST3 > AU > VST2** → può auto-caricare. La differenza
    **VST vs AU è solo formato**, non ambiguità: rientra in questa regola.
  - **Ambiguità di classe:** stesso nome ma su **classi diverse** — **device
    nativo Ableton vs plugin**, oppure **nativo vs plugin vs device Max4Live** →
    **niente auto-load**, mostra la tendina.
    *(es. "OTT" di Ableton vs "OTT" di Xfer)*
  - **Ambiguità di nome:** più candidati con **nomi uguali o simili**, o uno
    **prefisso** dell'altro → **niente auto-load**, mostra la tendina.
    *(es. "serum" vs "serum 2")*
  - **Regola di chiusura:** in **qualunque** caso in cui la confidenza non basta a
    individuare un solo device, non auto-selezionare mai.
- **Note tecniche:** motore di match con punteggio di confidenza
  (exact > prefix > fuzzy) + tie-break sul formato; l'auto-load scatta solo se il
  candidato migliore è **unico e nettamente sopra** gli altri. La tendina riusa la
  UI del menu/picker esistente.

### 2.2 Rack / Chain mode — ✅ implementato e collaudato in Live (2026-07-12)
- **Trigger:** Shift aggiunto ai gesti di **apertura**: `Ctrl+Shift+Right-click`
  apre il menu in chain mode, `Ctrl+Alt+Shift+Right-click` lo Spotlight (macOS:
  Cmd al posto di Ctrl). Letto dalla maschera dell'evento, nessun hook nuovo.
- **Comportamento:** ogni selezione carica il device e la finestra **resta
  aperta** → si costruisce una catena. Indicatore: bordo accent + header/badge
  "Chain · n". Multi-track (Shift al commit) disabilitato in chain mode.
- **Chiusura:** come oggi (Esc / click fuori); alla chiusura la catena (≥2 load
  riusciti) va nei recenti come `"A --> B"` (`usage.json`, uri `chain:`+JSON).
  Click su una catena nei recenti = **replay** (load sequenziali, stop al primo
  errore).
- **Note tecniche:** load multipli sequenziali sulla stessa traccia, nessuna
  modifica al protocollo socket/remote script. Ancora da valutare: salvataggio
  della catena come preset/rack (escluso dalla v1).

### 2.3 Aggiunta a più tracce selezionate (Spotlight **e** menu)
- Stesso plugin caricato su **tutte le tracce selezionate** contemporaneamente.
- **Note tecniche:** il Remote Script oggi usa `browser.load_item` sulla traccia
  selezionata corrente → serve iterare le tracce selezionate (`song.view` /
  set di tracce evidenziate) lato script.

### 2.4 Ordinamento intelligente
- Sezione "recenti / più usati" automatica.
- **Note tecniche:** contatori d'uso + timestamp persistiti per voce.

### 2.5 Profili / layout multipli
- Set di favoriti commutabili (es. Mixing / Sound Design / Mastering) o
  **per-progetto**.

### 2.6 Backup / sync
- Export/import della configurazione; sync tra macchine (studio + laptop).

### Modello di licenza Pro (da decidere)
- **Open-core** consigliato: core MIT pubblico + componente Pro **chiuso**.
- License key via **Gumroad**. (Dettagli e stima ricavi in una nota di lavoro
  interna, fuori dal repo.)

#### Vincoli di sicurezza e unicità della copia

Principio guida: **proteggere il ricavo senza degradare l'app né l'utente
onesto**. La pirateria non è azzerabile; l'obiettivo è che copiare una
installazione Pro su un secondo PC non funzioni *per inerzia*.

- **Licenza legata alla macchina, non al file.** Il token di licenza salvato in
  `%APPDATA%\LiveLoader` è firmato (chiave asimmetrica, nel binario **solo la
  pubblica**: nessun segreto condiviso da estrarre) e lega chiave d'acquisto +
  fingerprint macchina + scadenza. Copiare la cartella su un altro computer
  produce un token la cui firma è valida ma il cui fingerprint non combacia →
  non attiva. Anti-replay con timestamp e memoria dell'ultimo istante visto
  (difesa dall'orologio spostato indietro).
- **Fingerprint a bassa invasività.** Hash salato di identificatori stabili
  (Windows: MachineGuid + serial del volume di sistema; macOS: hardware UUID).
  **Vincolo antivirus/privacy:** niente enumerazione di MAC, processi o
  dispositivi — su un exe che già installa un hook mouse è la differenza tra
  "launcher" e "profilatore". Fuori dalla macchina esce solo l'hash.
- **N attivazioni per chiave** (proposta: 2, studio + laptop) con
  **disattivazione/trasferimento** fatti dall'utente da solo. Senza quel flusso
  ogni cambio di PC o formattazione diventa assistenza manuale.
- **Su PC non autorizzato: degrado a Free, mai blocco.** L'app parte, le feature
  Pro si spengono, un messaggio spiega il perché e offre la disattivazione di un
  altro dispositivo. Non si cancella né si rende inaccessibile nulla dell'utente
  (config, layout, catalogo, preset): sono suoi e appartengono anche alla parte
  gratuita.
- **Offline è lo stato normale, non un sospetto.** Token in cache con scadenza
  (proposta 30 gg) più grace period: uno studio senza rete resta Pro. Server o
  Gumroad irraggiungibili non equivalgono a licenza invalida. Va previsto anche
  il caso "il venditore sparisce" — un backend spento non deve trasformarsi in un
  kill-switch: piano di sblocco o licenza perpetua documentato *prima* di
  vendere.
- **Revoca** per rimborsi/chargeback e chiavi diffuse pubblicamente: lista
  controllata alla riattivazione, mai in un percorso bloccante offline.
- **Niente anti-tamper aggressivo** (obfuscation, packer, anti-debug,
  self-check): sono le euristiche che fanno flaggare l'eseguibile dagli
  antivirus, ed è il rischio che questo progetto non può correre. Enforcement
  semplice, verificabile, onesto.
- **Tracciabilità della copia** (opzionale): watermark per-acquirente nel
  download per risalire alla fonte di una chiave diffusa. Costa una build o un
  packaging per ordine — da pesare contro il volume reale di vendite.
- **Privacy dichiarata**: cosa esce dalla macchina all'attivazione (hash
  fingerprint + chiave d'acquisto, nessun dato personale, nessuna telemetria) va
  scritto nel README/privacy note.

---

## ③ Design UX/UI — step successivo

Obiettivo: look **minimalista, premium, professionale, gradevole** (font,
pannelli, spaziature, micro-interazioni). Da fare dopo il completamento
funzionale.

### Da dove prendere ispirazione
- **Raycast** (raycast.com) — *il* riferimento per il quick-launcher: launcher
  stile Spotlight, elegante, risultati con azioni. Guardalo bene per la 2.1.
- **Linear** (linear.app) e **Arc / Vercel (Geist)** — minimalismo premium,
  tipografia, spaziatura, dark/light impeccabili.
- **FabFilter** — gold standard di UI audio pulita e professionale (Pro-Q ecc.).
- **Ableton** stessa — coerenza col linguaggio visivo dell'ambiente ospite.
- **Dribbble** / **Behance** — cerca: *"menu bar app"*, *"macОS app"*, *"desktop
  app dark"*, *"audio plugin UI"*, *"command palette"*.
- **Godly** (godly.website) e **Mobbin** — gallerie curate di UI premium.
- **Untitled UI** / **Radix Colors** / **Tailwind palette** — sistemi di colore e
  spaziatura pronti e coerenti.

### Letture pratiche (principi, non solo ispirazione)
- **Refactoring UI** (Adam Wathan & Steve Schoger) — il miglior libro per far
  sembrare "pro" una UI da sviluppatore: gerarchia, spaziatura, colore, ombre.
- **Apple HIG** (macOS) e **Fluent 2** (Windows) — convenzioni native per non
  sembrare "fuori posto" sui due OS.

### Font
- **Inter** (già in uso) è ottimo e neutro. Alternative premium: **Geist**
  (Vercel), o i font di sistema (SF su mac / Segoe su Win) per look nativo.
- Regola: **un solo font**, 2–3 pesi, dimensioni coerenti su una scala.
