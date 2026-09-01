# LiveLoader — TODO operativo

Checklist dei punti ancora da eseguire. **Va letta a inizio task e aggiornata a
ogni step di modifica** (spuntare le voci fatte, aggiungere le nuove, aggiornare
la riga qui sotto). Qui c'è **solo lo stato**: il *cosa/come* sta in
`roadmap.md`, la cronologia dettagliata delle implementazioni nei messaggi di
commit git.

**Ultimo aggiornamento:** 2026-08-01 — chiusi in ① **accento personalizzabile**
(i 3 colori vanno bene) e la **scrollbar in tema chiaro**; il **1440p**, non
collaudabile perché quello schermo non c'è, è stato **sostituito da 7 test**
(307 totali verdi) che ne fissano baseline, nitidezza e assenza di clamp sui 5
fattori. In ③: **spotlight −18%** (410×344, proporzionale) e **bordo d'accento
della chain mode a 2px** in popup e spotlight, **entrambi collaudati in Live
dall'utente**; artefatti in `dist/` (portable + installer 1.0.0 win-x64)
**rigenerati** con dentro queste modifiche. **Indagato il bug macOS più grave**
(scansione plugin), **fix rimandato per decisione dell'utente**: servono **due**
difetti per spiegarlo — (A) la scansione automatica non può fallire visibilmente
e "vuoto" vale "riuscito", difetto **non macOS-specifico**; (B) causa radice al
~70%, i chunk della risposta sono contati **in item e non in byte** e sfondano il
limite UDP di macOS (9216 B; misurati 26 chunk su 63 oltre soglia sul catalogo
reale). Fix **non applicato**: tocca il contratto socket, e prima serve un
controllo sul log di Live sul Mac. Dettagli in ⑤. Prima (stesso giorno):
aggiunta la sezione **⑧ Audit di
debugging a sezioni**: audit di correttezza/robustezza condotto **modulo per
modulo** (unità il più indipendenti possibile) e poi **sulle interfacce** fra i
moduli, invece che sull'app intera in un colpo solo — così ogni passata resta
abbastanza stretta da scendere nel dettaglio. Elencati 7 moduli e 6 interfacce,
nessuna passata ancora fatta. Prima (stesso giorno): **Collaudato in Live e chiuso** il glitch
del popup ancorato in basso; accettata la fascia trasparente sopra il menu corto.
Rimosse entrambe le diagnostiche temporanee di `PopupMenuWindow` (`SwipeDiag` e
`AnchorDiag`): la prima faceva anche danno, perché scriveva su file a ogni evento
del trackpad dentro il gestore dell'input, ed era **quella** la causa degli
"swipe persi" — in Release non se ne perde uno. Build Debug/Release e 297 test
verdi dopo la pulizia. Il fix: la finestra ora **non si muove e non si ridimensiona mai**
per tutta la vita del menu (`FreezeHeightToTallestLayout` la fissa al layout più
alto prima di mostrarla, `Root` allineato al bordo ancorato, pannelli in cache).
La causa di fondo, dopo tre fix parziali: `Position` arriva allo schermo subito
mentre il contenuto si aggiorna al frame dopo, quindi **ogni** spostamento lascia
un frame disallineato. Come effetto collaterale gli switch sono molto più rapidi
(`SWITCH`→`SLIDE-GO` da 7-42 ms a 1-11 ms). Costi accettati e da collaudare in ①.
Prima (stesso giorno): aggiunte due sezioni: **⑥ Audit di
sicurezza completo**, dichiarato **gate di rilascio** (superfici già mappate:
socket UDP 19845 su loopback *senza autenticazione*, comandi che potrebbero
accettare path arbitrari, scritture in ProgramData e dentro il bundle di Live,
`Process.Start` su URL, hook, config JSON, packaging non firmato, dipendenze e
telemetria di Avalonia Accelerate, rete futura della licenza), e **⑦ Robustezza
agli aggiornamenti di Live** (le minor della 12 hanno retto fino alla 12.4.2;
l'obiettivo è reggere una major: elencato cosa è già version-agnostic e cosa si
romperebbe, più il piano per il giorno X). Prima (stesso giorno): chiuso il
**residuo** di scatto del
popup ancorato in basso, misurato con una diagnostica temporanea (`AnchorDiag`,
log in `%APPDATA%\LiveLoader\anchor-diag.log`, **da rimuovere** → ④): durante lo
slide i due pannelli stavano nella stessa cella e il `Grid` misurava il massimo
dei due, quindi passando a un layout più corto la finestra si stringeva solo alla
rimozione del vecchio — 249 px di salto 180 ms dopo lo switch. Ora il pannello
uscente vive in un `Canvas` (DesiredSize 0,0): la finestra prende subito
l'altezza finale, e il layer d'uscita viene compensato in Y così non schizza →
ricollaudo in ①. Prima (stesso giorno): **Primo collaudo su Mac reale** (Apple
Silicon, Live Lite 12.4.2): l'app **parte** dal kit cross-build, ma il collaudo
funzionale non passa → nuova sezione **⑤ Bug aperti macOS** con i problemi
registrati e non ancora indagati (icona assente sulla Scrivania, semafori sopra il
logo, esito sbagliato di "Install remote script" quando macOS nega i permessi,
scansione plugin che non scansiona — il più grave —, spinner decentrato, glifi
♥/→ non renderizzati per catena font Segoe UI/Manrope assente su macOS). Nello
stesso giro: **4K con scaling OS al 200% verificato OK** (①, resta scoperto solo
il 1440p). Prima (stesso giorno): corretto il **salto del popup ancorato in
basso** al cambio layout: la finestra è `SizeToContent` e cresce verso il basso a
`Position` ferma, quindi passando a un layout più alto si allungava sotto il
cursore e solo a fine slide risaliva. Il riancoraggio è ora agganciato a
`WindowBase.Resized` (notifica di piattaforma, prima del layout sul contenuto,
altezza letta da `e.ClientSize`) invece che al termine dell'animazione → collaudo
in ①. Prima (stesso giorno): aggiunta in ② la voce **sblocco Pro via
donazione sopra soglia** (importo libero, chiave consegnata solo oltre la soglia
utile; piattaforma+soglia da decidere insieme, consegna chiave, sotto-soglia,
anti-abuso, UX): decide solo il trigger d'acquisto, l'infrastruttura resta quella
del "Modello di licenza Pro". Rigenerati gli artefatti in `dist/` (portable +
installer 1.0.0 win-x64) per il collaudo su secondo schermo; per il Mac serve
ancora una build su macOS. Prima (2026-07-31): aggiunta in ③ la voce **audit design di
tutti i popup** (ricognizione a occhio di ogni finestra secondaria + fix mirati
dove stonano rispetto ai token di `App.axaml`; `MessageDialog`, costruito in C#,
è il più a rischio). Prima (stesso giorno): aggiunti in ② i **vincoli di sicurezza
della licenza Pro** (attivazione e limite macchine, fingerprint, comportamento
su PC non autorizzato = degrado a Free mai blocco, offline/grace, **unicità della
copia** via token firmato legato alla macchina, revoca, limite anti-tamper per il
vincolo antivirus, privacy, test): spec estesa in `roadmap.md §"Modello di
licenza Pro"`, nessuna implementazione iniziata. Prima (stesso giorno):
chiusi in Live i collaudi **layout
multipli (§2.5)**, **responsività dello swipe orizzontale** e **Shift+verticale
col trackpad**: il bug del 3° layout non si ripresenta e le tarature attuali dei
gesti (`GestureCooldownMs`, `DetentGapMs`) vanno bene così. Tutta l'area gesti è
collaudata → `SwipeDiag` è ora da rimuovere (④). Riscritto poi lo **UI scaling**:
da scatti assoluti + Auto a soglie a un modello **relativo** (baseline per-schermo
+ moltiplicatore 80-120%, con snap alla griglia dei pixel del device) — chiude ③
"porzione fissa di schermo", collaudato sul 1080p (al 100% la finestra è identica
a prima, com'è per costruzione). In ① restano Mac,
sync export/import, accento e la scrollbar su tema chiaro. Ancora prima:
overflow del popup chiuso con cap al 49% dello
schermo + scroll proprio, cambio layout su Shift+verticale, posizione stabile tra
layout di altezze diverse, e anti-skip estratto in `GestureStepper` (Core) con 14
test di regressione.

---

## ① Verifiche in sospeso (collaudi)

- [x] **Preset (catalogo / spotlight / picker)** — collaudati in Live (2026-07-11).
- [x] **Quick-launcher in Live** — §2.1 end-to-end + fix focus `AttachThreadInput` (2026-07-11).
- [x] **Multi-track load (§2.3, script 1.4.1)** — collaudato in Live (2026-07-11).
- [x] **Recenti/più usati (§2.4)** — collaudato in Live (2026-07-11).
- [x] **Chain mode (§2.2)** — collaudato in Live (2026-07-12).
- [x] **Fix anti-freeze hook** — verificato in uso reale (2026-07-18): nessun
      freeze one-shot, menu e spotlight si riaprono sempre. Trade-off noto: primo
      Ctrl+RClick su finestra Live con class name atipico può essere ignorato
      (cache fredda), il successivo funziona. Se ricapita: strumentare
      `WinIsLiveForeground` (fgHwnd/class/verdetto) e il foreground attorno a `ActivateLive`.
- [x] **Popup progresso scansione (script 1.5.0)** — verificato in Live (2026-07-18).
- [x] **Factory reset** — verificato (2026-07-18).

- [ ] **Collaudo Mac end-to-end** — build .app, permesso Accessibilità, scan
      (incl. AU), menu Cmd+RClick, spotlight Cmd+Alt+RClick, load, calibrazione
      posizionamento su Retina (→ roadmap ①). **Bloccante:** serve il .dmg,
      producibile solo su macOS — job `macos` di `.github/workflows/release.yml`
      (richiede push su GitHub, oggi senza remote) o `build/make-macos-app.sh` sul
      Mac (richiede .NET 8 SDK).
      **Aggiramento predisposto (2026-08-01):** il .dmg non serve per *provare*
      l'app. I binari `osx-arm64` sono cross-buildabili da Windows
      (`dotnet publish -r osx-arm64 --self-contained`); il bundle `.app` si
      assembla poi sul Mac con `sips`/`iconutil`, già presenti in macOS, senza
      .NET SDK. Kit così preparato su chiavetta (`D:\LiveLoader-Test`) con script
      `crea-app.sh`. **Vincolo scoperto:** su Apple Silicon un binario non firmato
      viene ucciso all'avvio → serve firma ad-hoc (`codesign --force --deep -s -`),
      quindi gli Xcode Command Line Tools sul Mac.
      **Primo avvio reale fatto (2026-08-01, Mac Apple Silicon, Ableton Live Lite
      12.4.2): l'app parte** — il percorso cross-build + `crea-app.sh` + firma
      ad-hoc funziona. Il collaudo funzionale però **non è passato**: problemi
      aperti elencati in ⑤. Questa voce resta aperta finché ⑤ non è chiusa.
- [x] **Layout multipli (§2.5) — ricollaudo** dopo fix bug 3° layout (Id mancante
      sui layout creati a runtime, corretto con factory `AppConfig.CreateLayout`):
      collaudato in Live (2026-07-31). NB storica: le config salvate prima del fix
      hanno Id vuoto — `MigrateLayouts` li riassegna al riavvio, ma le voci finite
      nel layout sbagliato vanno reinserite a mano.
- [x] **Responsività swipe orizzontale layout (§2.5)** — confermata nell'uso reale
      in Live (2026-07-31); taratura attuale buona, nessuna micro-taratura di
      `GestureCooldownMs` necessaria. Costanti in
      [PopupMenuWindow.axaml.cs](../src/AbletonLoader.App/Views/PopupMenuWindow.axaml.cs)
      (GestureCooldownMs, ReaccelFactor, ReaccelMin, ReversalMin, `_lockSign`).
      Se il tema tornasse fuori: **due tentativi di fix falliti** ("valle con
      persistenza", "boundary/prova di nuovo tocco") sono documentati nel commento
      in `PopupMenuWindow.axaml.cs` — **non ritentarli alla cieca**; la soluzione
      definitiva (anche per futuri swipe verticali) sono gli eventi tocco nativi
      WM_POINTER. Collaudo gesti chiuso → `SwipeDiag` **rimossa** il 2026-08-01
      (faceva anche danno: I/O su file a ogni evento, vedi voce sotto).
- [x] **Riancoraggio popup su cambio altezza** — **collaudato in Live e chiuso**
      (2026-08-01): nessuno scatto in nessuno dei due versi, metà alta invariata, e
      la fascia trasparente non dà fastidio nell'uso (accettata così).
      **Fix definitivo: la finestra non si muove più.** `FreezeHeightToTallestLayout`
      misura tutti i layout prima di mostrare il menu e fissa `AnchorHost.MinHeight`
      (nuovo `Panel` nell'axaml) al più alto, clampato al cap; `Root` è allineato al
      bordo ancorato. Da lì `posY` e l'altezza restano costanti per tutta la vita del
      popup — verificato su 46 s e decine di switch: ogni `ANCHOR` è `noop`.
      Motivo di fondo, da non dimenticare: **`Position` arriva allo schermo subito,
      il contenuto al frame dopo**, quindi ogni spostamento della finestra lascia un
      frame disallineato che nessun riordino di chiamate elimina. I tre interventi
      precedenti (riancoraggio su `Resized`, pannello uscente in un `Canvas` fuori
      dalla misura, `UpdateLayout()` sincrono in `SwitchTo`) restano e servono, ma da
      soli non bastavano.
      Effetti collaterali noti e accettati: (a) sopra il menu corto c'è una fascia
      trasparente (≈246×280 px nel caso misurato) che **inghiotte i click** — il
      popup si chiude comunque (`OnGlobalPress` testa `Root`, non la finestra), ma
      il click non arriva a Live; se un giorno desse fastidio serve intercettare
      `WM_NCHITTEST` a livello Win32, che Avalonia non espone; (b) i pannelli sono
      in **cache** per la vita del popup; (c) l'apertura costa la costruzione di
      tutti i layout (+56 ms misurati con 4 layout a freddo).
      `AnchorDiag` rimossa a collaudo chiuso.
- [x] **Swipe persi durante il cambio layout** — segnalato e **chiuso** il
      2026-08-01: **erano un artefatto della strumentazione**. In Debug `SwipeDiag`
      apre/scrive/chiude il file di log a ogni evento del trackpad (~40/s) dentro il
      gestore dell'input; in **Release** (dove i call-site spariscono a compile time)
      **non si perde più uno swipe** — verificato dall'utente. Motivo in più per
      rimuoverla (→ ④). Sotto resta l'analisi, valida se il tema si ripresentasse.
      **Non era una regressione**: misurato su `swipe-diag.log`, il tasso
      di accettazione del movimento vero (`mag>1.2`) oscilla fra 7% e 70% in tutte
      le sessioni, incluse quelle precedenti ai fix (00:47→9%, 01:27→7%; dopo i fix
      21%). **Il collo di bottiglia NON è `GestureStepper`** (i 539
      `swallow-reversal-weak` stanno tutti sotto 0.98, cioè sono code inerziali
      scartate correttamente): su 186 eventi di movimento vero, **93 finiscono in
      `swallow-busy` e 41 in `swallow-cooldown`** — il 72% cade nella finestra cieca
      di ~300 ms che segue ogni step (slide 165 ms + `GestureCooldownMs` 300 ms),
      dove l'analisi anti-skip è del tutto bypassata.
      Prima di tarare: **rimisurare in Release**, perché in Debug `SwipeDiag` scrive
      su file a ogni evento (~40/s) dentro il gestore dell'input.
      Se confermato, la strada NON è ritoccare le soglie dello stepper (due
      tentativi falliti, vedi voce sopra) ma la finestra cieca: accodare il gesto
      che arriva durante lo slide invece di scartarlo, e/o accorciare cooldown e
      durata dell'animazione.
- [ ] **Sync layout export/import** — verificare resa visiva dei due pulsanti +
      avviso rosso a schermo, UX dei file-picker OS e round-trip cross-PC con file
      spostato (il merge è coperto dai test Core, il layer file da `SyncFile`).
- [x] **UI scale relativa (nuovo modello)** — build, 297 test ed exe verificati
      (2026-07-31). **Neutralità sul 1080p confermata a occhio**: al 100% la
      finestra è identica a prima, quindi la baseline è davvero 1.0 esatto e chi
      era già a 100% non subisce cambiamenti. Fattori non-default provati a 110%:
      nitidezza sostanzialmente invariata, sfocatura percepibile solo cercandola —
      atteso, perché a 1.1 solo i multipli di 10 DIP cadono su pixel interi.
      Set di fattori **confermato così**: nessun set alternativo sta sulla griglia
      su tutti gli schermi (a baseline 1.25 anche ×1.25 esce), servirebbero tacche
      per-schermo con passi disomogenei — scartato.
      **4K con ridimensionamento OS al 200%: verificato OK** (2026-08-01, su un
      secondo PC Windows). **Il 1440p non è collaudabile** — quello schermo non è
      disponibile — quindi **il collaudo visivo è sostituito da test**: la
      garanzia si ottiene per calcolo, non a occhio (2026-08-01). **Fatto:** 7
      test in
      [UiScalingTests.cs:239-296](../src/AbletonLoader.Tests/UiScalingTests.cs),
      **307 test totali verdi**. Coprono 2560×1440 agli scaling OS 1.0/1.25/1.5,
      la **work area** reale (con taskbar, ~2560×1400) oltre allo schermo pieno,
      e la verifica che nessuno dei 5 fattori 80-120% venga clampato da
      `MaxFittingScale` — se lo fosse, l'impostazione utente non farebbe nulla su
      quello schermo. Valori fissati: baseline **1.25** a scaling OS 100%,
      **1.0** sia a 125% sia a 150% (sotto il 100% di area DIP scatta il pavimento).
      Garanzie codificate: scala effettiva sulla griglia 0.25 (nitidezza) e
      nessun clamp. **Precisazione emersa scrivendo i test:** il pavimento a 1.0
      vale sul **baseline**, non sul prodotto `baseline × fattore` — al fattore
      80% la scala scende sotto 1.0 di proposito, come già sul 1080p. **Nota di
      merito, non un bug:**
      il 1440p prende baseline **1.25 e non 1.333** (snap alla griglia,
      razionale in [UiScaling.cs:30-33](../src/AbletonLoader.Core/UiScaling.cs)),
      cioè la finestra è ~6% più piccola della frazione esatta di schermo: è la
      scelta "nitidezza prima della frazione", non una svista.
- [x] **Footer riorganizzato** — "Test connection" spostato in basso a sinistra
      (PRIMA di dot e stato: il testo di stato si allunga alla connessione e
      trascinerebbe con sé un pulsante messo dopo) e controllo **UI scale** portato
      da Settings al footer a destra. Build, finestra reale e verifiche a occhio
      tutte fatte (2026-07-31): tendina aperta dal footer, footer a scala 80/120%
      su una riga sola, label "UI scale" leggibile anche in tema chiaro.
- [x] **Accento personalizzabile** — **verificato a occhio dall'utente
      (2026-08-01): i 3 colori (Arancio/Oro/Viola) vanno bene in tutti i punti**,
      l'override runtime delle risorse (`App.ApplyAccent`) fa il suo lavoro.
      Residuo separato, non di questa voce: in **tema chiaro** il contorno
      d'accento della **chain mode** si legge male → portato a 2px (③).
- [x] **Popup menu con troppi plugin (overflow)** — implementato e collaudato in
      `--menu-test` e in Live (2026-07-31): cap, scroll, scrollbar, stabilità della
      posizione tra layout di altezze diverse e **Shift+verticale col trackpad**
      (`DetentGapMs` va bene com'è, nessuna ritaratura). Come funziona:
      - Popup cappato al **49% dell'area utile** dello schermo su cui si apre
        (`MaxScreenFraction`); oltre, la lista scorre. **Il ≤50% è un vincolo,
        non una scelta estetica**: regge l'ancoraggio a bordo fisso (sotto).
        Alzarlo fa tornare gli scatti di posizione.
      - **Posizione stabile tra i layout**: il bordo ancorato al cursore è deciso
        una volta sola dalla posizione del cursore (metà bassa dello schermo →
        ancora il bordo inferiore e il menu cresce in alto; metà alta →
        viceversa), **non** dall'altezza del layout. Scorrendo layout di altezze
        diverse la finestra non si sposta.
      - La scrollbar ha un **ControlTheme proprio** in `Window.Resources` (solo
        Track + Thumb): quello di Fluent lasciava traccia e pulsanti di
        paginazione visibili come un binario scuro, e i setter puntuali non li
        raggiungevano tutti.
      - **Scroll verticale** (rotellina *e* trackpad, senza modificatori) =
        scorrimento continuo della lista.
      - **Shift + verticale** = cambio layout, uno per gesto (stesso anti-skip
        dello swipe orizzontale, che resta invariato). Simmetrico: su →
        successivo, giù → precedente, niente wrap ai bordi.
      - Il cambio layout **a fine lista** è stato deliberatamente **escluso**:
        con Shift come modificatore esplicito sarebbe scattato per sbaglio ogni
        volta che si scorre fino in fondo.
      - `DetentGapMs` in
        [PopupMenuWindow.axaml.cs](../src/AbletonLoader.App/Views/PopupMenuWindow.axaml.cs)
        è l'euristica che distingue lo scatto della rotellina dallo swipe del
        trackpad sullo stesso asse Y (nel dubbio assume trackpad): valore attuale
        confermato in uso reale, toccarlo solo se emergono falsi scatti.
      - Resa della scrollbar verificata in **entrambi** i temi: scuro già prima,
        **chiaro confermato OK dall'utente il 2026-08-01**. Voce chiusa senza
        residui.

## ② Feature Pro (→ roadmap.md §2)

- [x] **§2.2 Rack / Chain mode** — implementata e collaudata (2026-07-12).
      Persistenza catene come preset/rack: rimandata.
- [x] **§2.3 Multi-track load** — implementata (script 1.4.1) e collaudata.
- [x] **§2.4 Ordinamento intelligente** — implementata (usage.json/frecency) e collaudata.
- [x] **§2.5 Profili / layout multipli** — implementata; bug 3° layout corretto e
      ricollaudata in Live (2026-07-31), swipe orizzontale incluso.
- [ ] **§2.6 Backup / sync** — export/import layout implementato (→ verifica in ①);
      resta sync config completa tra macchine.
- [ ] **Sblocco Pro via donazione (importo libero sopra soglia)** — capire come
      *consegnare e attivare* le feature Pro dopo una donazione di importo a
      scelta dell'utente, purché **sopra una soglia minima utile** (soglia = il
      lordo che, tolte le commissioni di piattaforma e di incasso, lascia netto
      almeno l'importo minimo fissato; cifra e conti nella nota interna, qui solo
      lo stato). Da decidere, nell'ordine:
      - **Deciso (2026-08-01):** importo **consigliato/preselezionato 10** (£/$/€)
            *netti* e **minimo accettato pari a 2 netti**, cioè **3 lordi** una volta
            tolte le commissioni. Il lordo esatto da mettere sui due campi dipende
            dalla piattaforma → conti nella nota interna.
      - [ ] **Impedire la donazione sotto soglia** — non basta "non consegnare la
            chiave": sotto il minimo la donazione **non deve proprio essere
            possibile**. Va verificato *quale piattaforma lo permette davvero*
            (importo minimo imposto lato piattaforma, non solo suggerito) — è un
            criterio di scelta della piattaforma, non un dettaglio di
            configurazione. Se nessuna lo impone, ripiego da decidere: prodotto a
            **prezzo fisso** (3) con possibilità di pagare di più, invece della
            donazione libera.
      - [ ] **Piattaforma e soglia insieme** — la soglia dipende dalle commissioni
            della piattaforma scelta, quindi non è decidibile prima di essa. Serve
            che la piattaforma permetta di conoscere l'importo della singola
            donazione (per confrontarlo con la soglia) e di **imporre il minimo**
            (punto sopra).
      - [ ] **Consegna della chiave** — automatica (notifica/webhook o API della
            piattaforma → generazione del token → email all'acquirente) oppure
            manuale finché i volumi sono bassi. Fallback obbligatorio: se
            l'automazione non parte, l'utente non deve restare senza chiave.
      - [ ] **Donazione sotto soglia** — resta una donazione: ringraziamento, niente
            chiave, nessun addebito aggiuntivo e nessun messaggio che la faccia
            sembrare un pagamento fallito.
      - [ ] **Anti-abuso** — una sola chiave per transazione; rimborso/chargeback →
            revoca (voce già presente sotto).
      - [ ] **UX in app** — dove si inserisce la chiave, cosa vede chi non ce l'ha,
            e quale testo/link porta alla pagina di donazione.
      - **Nota:** questo punto decide solo il *trigger* di acquisto (donazione
        libera invece di prezzo fisso). Tutta l'infrastruttura — attivazione,
        fingerprint, token firmato, offline/grace, revoca — è quella della voce
        "Modello di licenza Pro" qui sotto e non va duplicata.
- [ ] **Modello di licenza Pro** — decidere open-core + license key (Gumroad).
      Spec e razionale in [roadmap.md §"Modello di licenza Pro"](roadmap.md).
      Sotto-punti (nessuno ancora iniziato):
      - [ ] **Attivazione e limite macchine** — decidere N attivazioni per chiave
            (proposta: 2, studio + laptop) e il flusso di **disattivazione/trasferimento**
            autonomo dall'utente. Senza trasferimento, ogni cambio PC diventa
            assistenza manuale.
      - [ ] **Fingerprint macchina** — identificatore stabile e a bassa invasività
            (hash salato di MachineGuid + serial del volume di sistema; su macOS
            hardware UUID). **Vincolo AV/privacy:** niente enumerazione di MAC,
            processi o dispositivi — assomiglia a profilazione e riaccende i falsi
            positivi; esce dalla macchina solo l'hash, mai dati grezzi.
      - [ ] **Comportamento su un PC non autorizzato** (copia dell'app o della
            chiave su un altro computer, o attivazione oltre il limite): **degrado
            a Free**, non blocco. L'app parte, le feature Pro si disattivano, un
            messaggio spiega il perché e offre "disattiva un altro dispositivo".
            **Mai** cancellare config/preset/catalogo dell'utente, mai rendere
            inutilizzabile la parte gratuita.
      - [ ] **Offline e resilienza** — l'app deve funzionare senza rete: token di
            licenza in cache con scadenza (proposta 30 gg) + grace period prima del
            degrado. Server/Gumroad irraggiungibili ≠ licenza invalida. Prevedere
            l'uscita di scena del venditore (kill-switch involontario): piano di
            sblocco/licenza perpetua.
      - [ ] **Unicità della copia** — il file di licenza in `%APPDATA%\LiveLoader`
            deve essere **non trasferibile**: token firmato (Ed25519/RSA, nel binario
            solo la **chiave pubblica** — nessun segreto condiviso estraibile) che
            lega chiave d'acquisto + fingerprint macchina + scadenza; verifica della
            firma prima di ogni uso. Copiarlo su un altro PC non deve validare.
            Anti-replay: timestamp/nonce e difesa dall'orologio spostato indietro
            (memorizzare l'ultimo istante visto).
      - [ ] **Revoca** — rimborsi/chargeback e chiavi diffuse pubblicamente:
            lista di revoca controllata alla riattivazione (mai bloccante offline).
      - [ ] **Limite anti-tamper (vincolo, non TODO)** — niente obfuscation,
            anti-debug, packer o self-check invasivi: sono esattamente le euristiche
            che fanno flaggare l'exe dagli antivirus, sullo stesso eseguibile che già
            installa un hook mouse. L'enforcement resta semplice e onesto; chi vuole
            piratare ci riesce comunque.
      - [ ] **Tracciabilità della copia (opzionale, da decidere)** — watermark
            per-acquirente nel download per risalire alla fonte di una chiave
            diffusa. Valutare costo/beneficio: richiede build o packaging per ordine.
      - [ ] **Privacy** — dichiarare nel README/privacy note *cosa* esce dalla
            macchina all'attivazione (hash fingerprint + chiave, niente PII, niente
            telemetria) e la base giuridica.
      - [ ] **Test** — validatore di licenza coperto da unit test in Core: firma
            errata, token scaduto, fingerprint di un'altra macchina, orologio
            spostato indietro, server irraggiungibile (deve restare Pro nel grace).

## ③ Design UX/UI (→ roadmap.md §③)

- [x] **Restyling spotlight** — riferimento Raycast. Verificato (2026-07-18).
- [x] **Polish menu popup e MainWindow** — gerarchia, spaziature, ombre,
      coerenza dark/light. Verificato (2026-07-18).
- [x] **Spotlight più compatto (−18%)** — **fatto e collaudato in Live
      dall'utente** (2026-08-01): 500×420 → **410×344** (×0.82), con padding,
      raggi, ombra, font e margini ricalcolati **dagli originali**, non applicati
      in cascata. NB storica: una prima passata era stata fatta al −22%
      (390×328), poi corretta a −18% su indicazione dell'utente — i valori
      attuali sono ricalcolati da capo dai 500×420, non dal 22%.
      Due deviazioni deliberate dal ×0.82, entrambe per leggibilità: i `FontSize`
      secondari (hint, badge, path) tenuti a **10** invece del naturale 9.02, e
      `FontSize=12` esplicito sul nome della riga, che altrimenti erediterebbe
      ~14, cioè più della casella di ricerca a 13. **Non scalati perché globali** (stanno in `App.axaml`,
      non nel file dello spotlight): `sectionHeader` 10.5 e soprattutto
      `ListBoxItem MinHeight 38`
      ([App.axaml:455](../src/AbletonLoader.App/App.axaml)) — le righe della
      lista restano quindi proporzionalmente più alte del pannello ridotto:
      **da guardare all'uso reale**, si tocca solo accettando l'impatto su
      MainWindow. Debito minore introdotto: `Root.Margin` (XAML) e
      `ShadowMargin` (code-behind
      [QuickLauncherWindow.axaml.cs:25-28](../src/AbletonLoader.App/Views/QuickLauncherWindow.axaml.cs))
      sono due valori da tenere in pari.
      Deciso il 2026-08-01: il popup
      Ctrl+Alt+RClick va reso il **18% più piccolo**, proporzionalmente (non solo
      la finestra: anche padding, raggi, font e margini), partendo da
      `Width="500" Height="420"`
      ([QuickLauncherWindow.axaml:6](../src/AbletonLoader.App/Views/QuickLauncherWindow.axaml))
      → 390×328, arrotondando a interi. **Scelto di scalare i valori di design e
      non di aggiungere un fattore al `LayoutTransform` di `UiScale`**: il testo
      scritto a 12 è più nitido dello stesso testo a 16 scalato 0.78 da una
      trasformazione, coerentemente col principio "nitidezza prima della
      frazione" già adottato per lo UI scaling; in più `UiScale.Apply` è condiviso
      da tutte le finestre e non va toccato per una sola. Da controllare che
      nessun testo trabocchi alle scale 80-120%.
- [x] **Contorno chain mode più leggibile in tema chiaro** — **fatto** (2026-08-01):
      `BorderThickness = 2` **solo in chain mode** in entrambe le finestre
      ([PopupMenuWindow.axaml.cs:137-145](../src/AbletonLoader.App/Views/PopupMenuWindow.axaml.cs),
      [QuickLauncherWindow.axaml.cs:63](../src/AbletonLoader.App/Views/QuickLauncherWindow.axaml.cs)),
      stato normale invariato. Il timore sul popup è rientrato: i 2px sono
      impostati nel costruttore, **prima** di `BuildScaffold` e di ogni misura,
      quindi il chrome calcolato da `FreezeHeightToTallestLayout` li comprende già
      — ancoraggio in alto e in basso riverificati a video, nessun salto.
      **Residuo da giudicare all'uso:** in tema chiaro con accento **Wisteria** i
      2px si leggono ma restano tenui su fondo quasi bianco. Se non bastasse, la
      leva è il **colore** (globale, tocca tutta l'app), non lo spessore → altro
      task, non allargare questo.
      Situazione originaria: in chain mode il
      bordo d'accento non si stacca dal fondo chiaro. Entrambi i punti legano
      **solo** il `BorderBrush` e lasciano lo spessore a 1 preso dallo stile:
      [PopupMenuWindow.axaml.cs:138](../src/AbletonLoader.App/Views/PopupMenuWindow.axaml.cs)
      e [QuickLauncherWindow.axaml.cs:55](../src/AbletonLoader.App/Views/QuickLauncherWindow.axaml.cs).
      Fix: spessore **2px solo in chain mode**, stato normale invariato.
      Attenzione sul popup menu: l'altezza è congelata da
      `FreezeHeightToTallestLayout` prima di mostrare la finestra, un bordo più
      spesso cambia le misure → verificare che non rientrino i disallineamenti
      chiusi in ①. Se 2px non bastassero, **non** toccare il colore d'accento
      (è globale): sarebbe un altro task.
- [ ] **Audit design di tutti i popup** — passare in rassegna ogni finestra
      secondaria e sistemare quello che stona rispetto al linguaggio visivo di
      MainWindow/popup menu (token di `App.axaml`, tipografia, spaziature, raggi,
      ombre, stati hover/focus, coerenza dark/light, resa alle scale UI 80-120%):
      [PopupMenuWindow](../src/AbletonLoader.App/Views/PopupMenuWindow.axaml),
      [QuickLauncherWindow](../src/AbletonLoader.App/Views/QuickLauncherWindow.axaml),
      [PluginPickerWindow](../src/AbletonLoader.App/Views/PluginPickerWindow.axaml),
      [ScanProgressWindow](../src/AbletonLoader.App/Views/ScanProgressWindow.axaml),
      [StartupNoticeWindow](../src/AbletonLoader.App/Views/StartupNoticeWindow.axaml),
      [ToastWindow](../src/AbletonLoader.App/Views/ToastWindow.axaml),
      [MessageDialog](../src/AbletonLoader.App/Views/MessageDialog.cs) (costruito in
      C#, non XAML: è il più a rischio di divergenza). Prima un giro di ricognizione
      a occhio sull'app reale, poi fix solo dove serve — non un restyling.
- [ ] **Estrarre un design system riutilizzabile** — dai token e stili di questa
      app (centralizzati in `App.axaml`: palette antracite/avorio + accenti,
      tipografia Manrope e scala size, spaziature/raggi/ombre, varianti bottone
      accent/ghost/danger, card `modalCard`/`popIn`, temi light/dark, motion)
      ricavare un design system riusabile in altri programmi/plugin. Doppio strato:
      (a) **token neutri** (JSON/YAML) come fonte unica + doc col *perché* delle
      scelte; (b) **libreria risorse Avalonia** riusabile (dizionari + ControlTheme).
      NB: richiede una passata di audit/consolidamento dei valori oggi inline/sparsi.
      Opz.: export verso Figma.
- [x] **Finestra a porzione fissa di schermo** — **adottata** (2026-07-31, → ① per
      la verifica a occhio). Lo scaling assoluto a scatti con Auto a soglie è stato
      sostituito da un modello **relativo**: una baseline per-schermo fa occupare
      alla finestra la stessa frazione che occupa su 1920×1080, e l'impostazione
      utente è un moltiplicatore 80/90/100/110/120% sopra di essa
      (`UiScaling.BaselineScale`/`Factors`/`ParseFactor`). Conseguenze volute: su
      1080p il 100% è *esattamente* la scala di prima; su schermi grandi le scale
      troppo piccole spariscono da sole (su 4K il minimo è 0.8 × 2.0 = 1.6), che è
      il clamp inverso che prima mancava.
      - **Snap alla griglia dei pixel** (`SnapToDeviceGrid`, griglia 0.25): la
        baseline viene arrotondata sulla scala **effettiva sul device**
        (`scala × scaling OS`), perché è quella che decide se un bordo da 1px cade
        su un pixel intero. Priorità esplicita: nitidezza prima della precisione
        della frazione. 1440p → 1.25 (non 1.333), 4K@150% → 1.333 (eff 2.0, già
        intera). Griglia 0.25 e non 0.5 perché 125/150/175% sono i passi DPI
        standard di Windows.
      - **Lo snap non viene riapplicato dopo il fattore utente**: con griglia 0.25
        collasserebbe 90/100/110% sullo stesso valore. Quindi il default è sempre
        allineato alla griglia, le altre scelte sono una deviazione deliberata.
      - Contratto: `AppConfig.UiScale` cambia significato (era assoluto, ora
        relativo). Migrazione silenziosa — i valori legacy (`"Auto"`, `"150"`, …)
        non parsano più e ricadono su 1.0, senza riscrivere la config.
      - Non rifatto: `MaxFittingScale` è ora continua e snappata per difetto; su
        1080p il tetto scende da 1.65 a 1.5 (i fattori arrivano a 1.2, ci stanno).

## ④ Pubblicazione

- [x] **Rename del prodotto** — AbletonLoader → **LiveLoader** (2026-07-16),
      verificato (2026-07-18).
- [ ] **URL reali** — GitHubUrl/DonateUrl in MainWindow.axaml.cs,
      `.github/FUNDING.yml`, link Donate nel README, AppURL nell'installer .iss.
- [ ] **README pubblico** — descrizione, screenshot/GIF, install per OS, setup
      Control Surface, troubleshooting, build from source, donazioni.
- [ ] **Rimozione v1 WPF** (`app/`, gitignorata) a collaudo v2 completato.
- [ ] **Pulizia diagnostiche e avvii speciali (prima del rilascio)** — togliere
      **tutto** il codice di sviluppo. Inventario (riverificare con un grep a fine
      lavoro):
      - ~~`SwipeDiag` e `AnchorDiag` in `PopupMenuWindow.axaml.cs`~~ — **fatto**
        (2026-08-01): entrambi i blocchi e tutti i call-site rimossi a collaudo
        chiuso; build Debug/Release e 297 test verdi dopo la rimozione.
      - Residuo minore: `GestureStepper.DebugState` (Core) ora non ha più chiamanti
        — era usato solo da `SwipeDiag`. Lasciato perché è API pubblica accanto a
        `LastDecision`, che i test usano; valutare se toglierlo.
      - DevTools F12: `AttachDeveloperTools()` (`#if DEBUG`) in [App.axaml.cs](../src/AbletonLoader.App/App.axaml.cs) + package `AvaloniaUI.DiagnosticsSupport` in [AbletonLoader.App.csproj](../src/AbletonLoader.App/AbletonLoader.App.csproj).
      - Argomenti speciali `--menu-test` e `--quick-test` in [App.axaml.cs](../src/AbletonLoader.App/App.axaml.cs).
        NB scoperto il 2026-08-01: **nessuno dei due attiva la chain mode**, che
        resta raggiungibile solo con Live in primo piano — chi deve collaudarla
        a occhio non perda tempo a cercarla lì.
      - Ogni altro `[Conditional("DEBUG")]`, log di diagnostica o probe temporaneo.

## ⑤ Bug aperti macOS (primo collaudo reale, 2026-08-01)

Osservati su **Mac Apple Silicon + Ableton Live Lite 12.4.2**, app assemblata dal
kit cross-build (`crea-app.sh`). **Nessuno ancora indagato**: sotto c'è il
sintomo riportato e, dove il codice suggerisce già un sospetto, un'**ipotesi da
verificare** — non una diagnosi. Prima di toccare qualcosa serve riprodurre sul
Mac, che è l'unico posto dove si vedono.

- [ ] **Icona dell'app assente sulla Scrivania** — il `.app` sulla Scrivania
      mostra l'icona generica; nel Dock e nella barra dei menu in alto l'icona
      c'è. *Ipotesi:* l'`.icns` generato da `crea-app.sh` (iconset con sole
      dimensioni 1×, senza varianti `@2x`) o la cache icone del Finder. **Potrebbe
      essere un difetto del kit di test, non dell'app** — da distinguere prima di
      cercare nel codice; il job `macos` del workflow di release genera l'icns
      allo stesso modo (`build/make-macos-app.sh`), quindi se è lì il problema
      riguarda anche il rilascio.
- [ ] **Semafori macOS sovrapposti al logo** — i pulsanti chiudi/min/max di macOS
      stanno in alto a **sinistra** e finiscono sopra il badge logo+nome della
      titlebar custom. Su Windows i pulsanti sono a destra, quindi il problema è
      solo macOS. Titlebar in
      [MainWindow.axaml:8-44](../src/AbletonLoader.App/Views/MainWindow.axaml)
      (`ExtendClientAreaToDecorationsHint`, badge nella Grid riga 0): serve un
      padding sinistro condizionale su macOS (o spostare il badge), non un
      restyling.
- [ ] **"Install remote script": esito sbagliato quando macOS nega i permessi** —
      sequenza osservata: click su Install → macOS blocca l'accesso alla cartella
      e chiede il permesso nelle Impostazioni → **prima ancora di concederlo**
      compare il dialog con "Script installed to: …" *e sotto* "Failed: …", e lo
      stato in finestra dice **"installed in 1 location(s)"** benché lo script non
      fosse installato. Concessi i permessi, un secondo Install ha funzionato.
      Tre cose da separare:
      - lo **stato** conta le copie trovate/scritte ma evidentemente non riflette
        la realtà su macOS
        ([MainWindow.axaml.cs:496](../src/AbletonLoader.App/Views/MainWindow.axaml.cs));
      - il **messaggio** mescola successo e fallimento senza dire che la causa è
        un permesso negato: il suggerimento di rimedio esiste **solo per Windows**
        ("esegui come amministratore",
        [MainWindow.axaml.cs:1450-1451](../src/AbletonLoader.App/Views/MainWindow.axaml.cs)),
        su macOS manca l'equivalente ("consenti l'accesso alla cartella e riprova");
      - va capito **quale** delle destinazioni risultava "installed" e perché Live
        non vedeva lo script.
- [ ] **Scansione plugin che non scansiona** — su Mac i plugin non risultano
      scansionati, il popup di scansione dichiara di averli scansionati e
      **ricompare a ogni avvio** (segno che il catalogo resta vuoto/non
      persistito). È il problema più grosso dei cinque: senza catalogo l'app su
      Mac non fa nulla.
      **Indagato il 2026-08-01** (diagnosi da codice, *nulla eseguito sul Mac*).
      Servono **due difetti** per spiegare i tre sintomi:
      - **A — amplificatore, certo dal codice, indipendente dalla causa radice:**
        la scansione automatica **non può fallire visibilmente** e "vuoto" conta
        come "riuscito". `items is null` → `(false,0,0)` ma **nessuno consuma quel
        `false`** sul percorso automatico
        ([CatalogService.cs:113](../src/AbletonLoader.App/Services/CatalogService.cs));
        `ScanFinished` parte dal `finally` (`:137-142`) sia in successo sia in
        fallimento, e i datagrammi di progress sono piccoli e arrivano → **la
        barra sale al 100% e la card si chiude senza un messaggio** (sintomo 2);
        `empty = _knownCount == 0` rifà lo scan a ogni avvio (`:78,84`) →
        sintomo 3; una lista vuota verrebbe persistita e timbrata come scansione
        riuscita (`:122-129`). **Questo difetto è indipendente da macOS e va
        corretto comunque**: è il motivo per cui il guasto è invisibile.
      - **B — causa radice, ipotesi al ~70%, macOS-specifica:** i datagrammi di
        risposta superano il limite UDP di macOS. Lo chunking è a **numero di
        item** (`CHUNK = 60`), **mai misurato in byte**
        ([__init__.py:403-408](../remote-script/LiveLoader/__init__.py)); misurato
        sul catalogo Windows reale (3758 item): 63 chunk, mediana 9043 B, **26 su
        63 sopra 9216 B**, che è il `net.inet.udp.maxdgram` di default su macOS
        (Windows arriva a 65507 — ecco perché lì funziona). `sendto` fallisce con
        EMSGSIZE e `_reply` **inghiotte l'eccezione**
        ([__init__.py:192-198](../remote-script/LiveLoader/__init__.py)); l'app
        aspetta *tutti* i chunk → timeout 8 s → scan fallito
        ([LiveClient.cs:184-187](../src/AbletonLoader.Core/LiveClient.cs)).
      - **Falsificata:** "lo script non era installato" — il popup all'avvio nasce
        solo dal percorso che richiede un ping riuscito
        ([App.axaml.cs:105-106](../src/AbletonLoader.App/App.axaml.cs)), quindi lo
        script rispondeva.
      - **Ancora aperte al ~15% ciascuna:** cartella dati macOS non scrivibile
        (`~/Library/Application Support/LiveLoader`,
        [AppConfig.cs:93-99](../src/AbletonLoader.Core/AppConfig.cs), errore
        inghiottito da `CatalogService.cs:133-135`) e scansione che torna 0 item.
      - **Difetto C, certo e separato, morde DOPO il fix:** `au` è **spento di
        default** ([AppConfig.cs:57-60](../src/AbletonLoader.Core/AppConfig.cs),
        [PluginPickerWindow.axaml.cs:59](../src/AbletonLoader.App/Views/PluginPickerWindow.axaml.cs))
        — su macOS i plugin sono Audio Unit, quindi il picker li nasconderebbe
        comunque.
      - **Un solo controllo sul Mac decide fra le tre ipotesi**, da fare prima di
        scrivere il fix: in `~/Library/Preferences/Ableton/Live 12.4.2/Log.txt`
        cercare `LiveLoader` → `scansione [...]: N elementi` (N grande =
        trasporto/B; N = 0 = scansione a vuoto) e l'eventuale `errore nella
        risposta: ... Message too long` / `[Errno 40]`, che confermerebbe B
        direttamente. Poi: `sysctl net.inet.udp.maxdgram` (atteso 9216),
        `ls -l ~/Library/Application\ Support/LiveLoader/`, e **quale** popup
        dichiarava successo (la card che si chiude da sola o il dialogo "Scan
        complete … the catalog holds N", e con quale N).
      - **Fix proposto, non applicato** (tocca il **contratto socket** → richiede
        bump `VERSION` dello script e reinstallazione): chunking a byte con cap
        ~8000 B invece che a 60 item, log esplicito su EMSGSIZE, e il difetto A
        corretto **insieme** — senza A il prossimo guasto di trasporto tornerebbe
        invisibile.
      - **Rimandato per decisione dell'utente (2026-08-01):** l'indagine è
        chiusa e va conservata così com'è; il fix si affronta in un giro
        successivo. **Non rifare la diagnosi da zero** — riparti da qui e dal
        controllo sul log di Live elencato sopra.
- [ ] **Spinner del popup di scansione decentrato** — il cerchio che ruota non è
      centrato nel quadrato che dovrebbe contenerlo
      ([ScanProgressWindow.axaml](../src/AbletonLoader.App/Views/ScanProgressWindow.axaml)).
      Cosmetico; da verificare se si vede anche su Windows o solo su macOS.
      → confluisce nell'audit design dei popup (③).
- [ ] **Glifi icona non renderizzati** — il cuore di "Donate ♥"
      ([MainWindow.axaml:336](../src/AbletonLoader.App/Views/MainWindow.axaml)) e le
      frecce "→" del testo "One-time setup in Live"
      ([MainWindow.axaml:314](../src/AbletonLoader.App/Views/MainWindow.axaml)) non
      si vedono correttamente. *Ipotesi forte:* sono **caratteri Unicode**, non
      icone vettoriali, e la catena font è
      `Segoe UI, Manrope, sans-serif`
      ([MainWindow.axaml:12](../src/AbletonLoader.App/Views/MainWindow.axaml)) —
      **Segoe UI non esiste su macOS** e Manrope probabilmente non ha U+2665/U+2192,
      quindi si finisce su un fallback che li rende male o non li rende. Da
      decidere: sostituirli con path/glifi di un font incluso nel bundle, invece di
      dipendere dai font di sistema. Vale la pena un grep di tutti i caratteri non
      ASCII usati come icona, non solo questi due.

## ⑥ Audit di sicurezza completo (gate di rilascio)

- [ ] **Audit di sicurezza dell'intera superficie** — **bloccante per la
      pubblicazione**: l'app non deve poter essere usata come *vettore* contro il
      PC/Mac di chi la installa. Da fare con `security-reviewer` su tutta la
      superficie, non solo sul diff, e da rifare prima di ogni release che tocchi
      i punti sotto. Superfici reali già individuate, in ordine di rischio:
      - [ ] **Socket UDP del remote script** — `127.0.0.1:19845`
            ([remote-script/LiveLoader/__init__.py:54,123,175](../remote-script/LiveLoader/__init__.py)),
            `recvfrom` senza alcuna autenticazione e risposta rimandata al mittente
            del datagramma. Loopback **non è** un confine di fiducia: qualunque
            processo locale (anche non privilegiato, anche di un altro utente
            loggato) può pilotare Live. Da valutare: token condiviso
            app↔script generato all'installazione, controllo del mittente,
            rifiuto dei datagrammi che non arrivano da loopback.
      - [ ] **Comandi accettati dallo script** — passare in rassegna *ogni* comando
            del protocollo e verificare che nessuno permetta di far leggere,
            scrivere o caricare a Live un path arbitrario scelto dal mittente
            (path traversal, file fuori dalla User Library, URI del browser
            inventati). È il punto in cui un comando "innocuo" diventa esecuzione
            di codice altrui dentro Live.
      - [ ] **Scritture privilegiate di `ScriptInstaller`** — scrive dentro
            `ProgramData\Ableton\...\MIDI Remote Scripts` e, su macOS, **dentro il
            bundle `/Applications/Ableton Live *.app`**
            ([ScriptInstaller.cs:95-120](../src/AbletonLoader.Core/ScriptInstaller.cs)).
            Verificare: nessun path costruito da input non fidato, nessun
            follow di symlink/junction, permessi risultanti sui file scritti,
            comportamento se una di quelle cartelle è scrivibile da utenti non
            admin (sarebbe un vettore di privilege escalation *verso* Live).
      - [ ] **Path dedotti da file di Live** — la User Library viene letta con
            regex da `Library.cfg`
            ([ScriptInstaller.cs:63-70](../src/AbletonLoader.Core/ScriptInstaller.cs)):
            è input esterno, va trattato come non fidato (path assoluti strani,
            UNC, `..`).
      - [ ] **`Process.Start` con `UseShellExecute`** — apertura di URL
            ([MainWindow.axaml.cs:1460-1466](../src/AbletonLoader.App/Views/MainWindow.axaml.cs))
            e di cartelle: verificare che l'argomento sia sempre una costante o un
            path validato, mai una stringa che l'utente/un file può influenzare
            (con `UseShellExecute` una stringa arbitraria è esecuzione di comandi).
      - [ ] **Hook mouse e simulazione input** — confermare che l'hook resti
            *passivo* fuori da Live, che non registri né persista nulla, e che non
            esistano percorsi in cui un click sintetico possa finire su una
            finestra diversa da quella prevista (elevazione/UAC).
      - [ ] **File di configurazione e catalogo** — JSON in `%APPDATA%\LiveLoader`:
            deserializzazione senza type-handling polimorfico, comportamento su
            file corrotto o ostile (nessun crash, nessun path eseguito), e nessun
            dato sensibile in chiaro.
      - [ ] **Packaging** — installer Inno (dove scrive, con quali permessi,
            cosa lascia alla disinstallazione), autostart
            ([Autostart.cs](../src/AbletonLoader.Core/Autostart.cs)), e il fatto
            che oggi gli eseguibili **non sono firmati** (Windows: SmartScreen;
            macOS: solo firma ad-hoc) — la firma è anche una difesa contro la
            distribuzione di build manomesse col nostro nome.
      - [ ] **Dipendenze (supply chain)** — inventario delle librerie e delle
            versioni, controllo di vulnerabilità note, e verifica che nessuna
            faccia rete a nostra insaputa (`dotnet list package --vulnerable
            --include-transitive`). Nota nota: Avalonia Accelerate Community
            **richiede telemetria** — capire cosa invia e dichiararlo.
      - [ ] **Rete futura (licenza Pro)** — quando esisterà: TLS obbligatorio,
            validazione del certificato, nessun segreto nel binario, timeout e
            fallimento *chiuso verso l'utente* (mai bloccante, → ②).
      - **Perché è un gate e non un "nice to have":** la licenza MIT include la
        clausola "AS IS" senza garanzia, che è la difesa standard e serve — ma è
        una difesa contrattuale, non un lasciapassare: non copre condotta
        gravemente negligente e non ha effetto sugli obblighi verso i dati
        personali degli utenti (GDPR) se un domani l'attivazione Pro trasmette
        qualcosa. Tradotto: il modo serio di non avere problemi è non spedire il
        buco, non contarci sul disclaimer. **Non è un parere legale** — se il
        progetto inizia a incassare, la consulenza singola citata nella nota
        interna copre anche questo.

## ⑦ Robustezza agli aggiornamenti di Ableton Live

- [ ] **Reggere una futura major (Live 13) oltre alle minor** — **stato attuale:
      le minor interne alla 12 (12.1, 12.2, …, fino a 12.4.2) hanno retto** senza
      interventi. L'obiettivo è che regga anche un salto di major, per quanto
      dipende da noi. Quello che *già* è indipendente dalla versione (verificato
      nel codice, da non rompere):
      - scoperta delle preferenze per versione via regex `^Live (\d+(?:\.\d+)*)$`
        con ordinamento sulla più recente
        ([ScriptInstaller.cs:49-53](../src/AbletonLoader.Core/ScriptInstaller.cs));
      - cartelle installate cercate come `Live *` / `Ableton Live *.app`
        ([ScriptInstaller.cs:101,113](../src/AbletonLoader.Core/ScriptInstaller.cs));
      - rilevamento finestra per class name **con fallback** su
        `ProcessName.StartsWith("Ableton Live")`
        ([LiveWindowDetector.cs:48,114,236](../src/AbletonLoader.App/Services/LiveWindowDetector.cs));
      - import del ControlSurface con fallback `ableton.v2` → `_Framework`
        ([__init__.py:47-49](../remote-script/LiveLoader/__init__.py)).
      Quello che invece **si romperebbe** con una major, da presidiare:
      - [ ] **API Python del browser** — `browser.load_item`, gli URI degli item
            e `get_application().get_document()`
            ([__init__.py:252,473,522,538](../remote-script/LiveLoader/__init__.py)):
            è la parte che Ableton può cambiare senza preavviso. Ogni chiamata
            all'API di Live dovrebbe essere in un punto solo e degradare con un
            messaggio chiaro ("questa versione di Live non è supportata"), non
            con un'eccezione muta dentro Live.
      - [ ] **Interprete Python di Live** — una major può cambiarne la versione:
            tenere il codice sul sottoinsieme compatibile e **niente dipendenze
            esterne** (vincolo già in CLAUDE.md), verificare che non entrino
            costrutti troppo recenti.
      - [ ] **`Live.Base.Timer`** — già con fallback su `update_display`
            ([__init__.py:135-139](../remote-script/LiveLoader/__init__.py)):
            confermare che il fallback sia davvero esercitato e non solo scritto.
      - [ ] **Piano operativo per il giorno X** — cosa fare quando esce una major:
            (1) installare la beta/nuova versione, (2) eseguire una checklist di
            fumo (install script, connessione, scan, load, multi-track, chain),
            (3) se il protocollo cambia, alzare la versione dello script e gestire
            il mismatch app↔script con un messaggio, mai con un crash.
      - [ ] **Messaggio di incompatibilità esplicito** — se lo script non riesce a
            parlare con Live (API sparita, versione ignota), l'utente deve leggere
            *perché*; oggi il rischio è un silenzio identico a "non ho scansionato
            nulla" (vedi ⑤, scansione su Mac).

## ⑧ Audit di debugging a sezioni

Audit di **correttezza e robustezza** (bug latenti, stati impossibili, errori
inghiottiti, race, risorse non rilasciate, casi limite non gestiti) —
**non** di sicurezza: quella è ⑥, stesse superfici ma lente diversa, e le due
non vanno duplicate né fuse.

**Metodo — il punto della sezione:** l'app intera in un colpo solo è troppo
grande perché una passata resti profonda; si finisce a scremare la superficie.
Quindi si procede a **sezioni il più indipendenti possibile**: un modulo alla
volta, con un audit stretto e dettagliato che lo tratta come se fosse l'unica
cosa esistente; solo dopo si fa una passata dedicata alle **interfacce** fra i
moduli, che è dove i bug veri si nascondono (assunzioni che i due lati non
condividono). Un modulo per task, criterio di completamento esplicito,
un `file:riga` per ogni finding. I moduli sotto sono elencati **dal più
isolato al più intrecciato**: partire dai primi tiene le passate pulite.

### Passata 1 — moduli

- [ ] **Core / logica pura** — `QuickMatch`, `UsageStore`, `ChainUsage`,
      `GestureStepper`, `UiScaling`, `LayoutAvailability`, `Models`. È la
      parte già coperta dai 297 test: l'audit cerca ciò che i test **non**
      dicono (input degeneri, ordinamenti instabili, overflow di contatori,
      unicode, collezioni mutate durante l'iterazione).
- [ ] **Core / persistenza** — `AppConfig`, `SyncFile`, `LayoutSync`: scrittura
      atomica o no, comportamento su file corrotto/troncato/con permessi negati,
      migrazioni (`MigrateLayouts`, `UiScale` legacy), accessi concorrenti da
      due istanze dell'app.
- [ ] **Core / sistema** — `ScriptInstaller`, `Autostart`: cartelle assenti,
      più versioni di Live installate, scritture parzialmente riuscite (vedi ⑤,
      il bug "installed in 1 location(s)"), disinstallazione.
- [ ] **Core / `LiveClient`** — lato app del socket: timeout, risposte
      parziali o fuori ordine, datagrammi persi, script assente o di versione
      diversa, scan progress interrotto a metà.
- [ ] **remote-script `__init__.py`** — lato Live: eccezioni che non devono
      mai uscire verso Live, stato interno fra un comando e l'altro, comandi
      ricevuti mentre un altro è in corso, set/documento cambiato sotto i piedi.
- [ ] **App / input e OS** — `HookService`, `InputSimulator`,
      `LiveWindowDetector`, `MacInterop`: rientranza dell'hook, thread su cui
      girano le callback, disinstallazione dell'hook su crash, cache del
      rilevamento finestra (il trade-off "cache fredda" già noto in ①).
- [ ] **App / orchestrazione e UI** — `MenuFlow`, `CatalogService`,
      `SyncService`, `UiScale`, `Program`/`App.axaml.cs` e le View: chi possiede
      il thread UI, `async void`, finestre non chiuse, handler non
      disiscritti, ordine di costruzione allo startup (vincolo "runtime UI").

### Passata 2 — interfacce fra i moduli

- [ ] **App ↔ remote script (socket UDP)** — il contratto principale: ogni
      comando e ogni risposta, versione dello script vs versione attesa
      dall'app, cosa succede a ogni mismatch. Nessun silenzio: vedi ⑦
      "messaggio di incompatibilità esplicito".
- [ ] **App ↔ Core (config e catalogo)** — chi scrive, chi legge, quando si
      ricarica; stato in memoria che diverge da quello su disco.
- [ ] **Hook → MenuFlow → View** — la catena input→azione: eventi che arrivano
      mentre un menu è già aperto o in chiusura, doppi trigger, riordino.
- [ ] **View ↔ risorse/tema/scala** — `UiScale.Apply`, `App.ApplyAccent`,
      risorse theme-scoped: i punti dove il fallimento è runtime e silenzioso.
- [ ] **Core ↔ filesystem e OS** — path utente, ProgramData, bundle di Live:
      assunzioni su esistenza, permessi e maiuscole/minuscole.
- [ ] **Windows ↔ macOS** — ogni ramo per piattaforma è un'interfaccia
      implicita: elencarli e verificare che il ramo macOS non sia solo
      "scritto ma mai eseguito" (è l'origine di tutta la sezione ⑤).
