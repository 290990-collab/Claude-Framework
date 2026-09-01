# LiveLoader — Pubblicazione, donazioni, copyright, marketing

> **Documento di lavoro interno.** Contiene note fiscali e personali: **non
> pubblicarlo nel repo pubblico** (aggiungilo a `.gitignore` o tienilo fuori dal
> repo). Serve come base per le decisioni e per il Q&A con Claude.
>
> Non è consulenza legale né fiscale. Sul punto fiscale (l'unico davvero
> delicato) è indicato dove conviene un commercialista.
> Contesto: autore in **Italia**. Fonti verificate a luglio 2026.

---

## 0. La decisione che tocca tutto: il nome

`AbletonLoader` usa il marchio **Ableton**. Le linee guida marchi di Ableton
consentono di usare "Ableton"/"Live" **solo per dichiarare compatibilità**, con
il marchio **meno prominente** del nome del prodotto e una nota di attribuzione.
Un prodotto chiamato *letteralmente* "AbletonLoader" non rispetta questo
principio.

- Rischio concreto per un tool gratuito di nicchia: **basso** (al massimo una
  diffida, non una causa). Ma con sito + marketing + SEO conviene sistemare
  **prima** di costruire brand e backlink.
- **Azione consigliata:** rinominare ora. Nome proprio + tagline "for Ableton
  Live". Candidati da verificare come non-marchio: *LiveLoader, QuickLoad,
  PatchDeck, InstaLoad, LoadDeck*.
- Aggiungere comunque in README/sito: *"Ableton and Live are trademarks of
  Ableton AG. This project is not affiliated with Ableton."*

---

## 1. È legale pubblicare + ricevere donazioni?

**Sì**, in Italia/UE distribuire software gratis e ricevere donazioni volontarie
è pienamente legale. Non serve costituire nulla per pubblicare. Gli unici nodi
sono: il **nome/marchio** (§0), la **responsabilità** (coperta dalla licenza,
§2) e il **fisco** sulle donazioni (§3).

---

## 2. Copyright (anche se è gratis) — come funziona

- Il copyright nasce **automaticamente** alla creazione (Convenzione di Berna):
  nessuna registrazione, nessun costo, nemmeno il simbolo © obbligatorio. Il
  software è tutelato come opera dell'ingegno (Italia: **L. 633/1941**, art.
  64-bis ss.).
- **"Gratis" ≠ "pubblico dominio".** Resti proprietario; "rendere free" =
  **concedere una licenza**.
  - **Open source (MIT)** ← scelta consigliata: codice pubblico, chiunque può
    usarlo/modificarlo/ridistribuirlo *mantenendo la tua nota di copyright*. La
    clausola **"AS IS, no warranty"** ti scherma da responsabilità se il tool
    causa problemi. Massima adozione, minimo sforzo.
  - Alternativa: **freeware** (solo binario, sorgente chiuso, EULA). Più
    controllo, meno community.
- **Diritto morale d'autore**: in Italia **inalienabile e perpetuo** — resti per
  sempre riconosciuto come autore, anche con MIT.
- **Prova di paternità**: non serve registrare. **Cronologia git + timestamp
  GitHub** sono già prova solida. (Formale/opzionale: registro software SIAE —
  sovrabbondante per un tool MIT.)
- **Rovescio della medaglia — diritti su ciò che spedisci:**
  - ⚠️ **Icone Icons8** (usate nella app): la free tier richiede in genere
    **attribuzione con backlink**. Da sistemare prima del rilascio: o attribuisci
    o sostituisci con icone realmente libere (Lucide/Tabler, licenza MIT/ISC).
  - Font **Inter** (OFL) e **Avalonia**/**SharpHook** (MIT): OK.

---

## 3. Donazioni & PayPal

**PayPal da solo non è la scelta migliore.** Meglio incassare *tramite* una
pagina dedicata (che sotto usa comunque PayPal/Stripe) con UX migliore e
commissioni più basse:

| Piattaforma | Commissione piattaforma | Note |
|---|---|---|
| **Ko-fi** | **0%** sulle donazioni singole | payout via PayPal/Stripe. Consigliata |
| **GitHub Sponsors** | **0%** | ideale per pubblico dev/open source, integrato nel repo |
| **Buy Me a Coffee** | 5% | comodo ma trattiene di più |
| **PayPal "nudo"** | ~3,4% + €0,35 (IT) | il "friends & family" è contro le regole per uso da creator |

**Consiglio:** Ko-fi **+** GitHub Sponsors. Framing "offrimi un caffè / tip"
rende più di un freddo link PayPal.me.

### Soglia per lo sblocco Pro via donazione

Ipotesi di modello: donazione a **importo libero**, ma la chiave Pro parte solo
sopra una soglia che lasci **netti ≥ €2** in tasca. Formula:

```
soglia_lorda = (netto_voluto + commissione_fissa) / (1 - commissione_%)
```

Con `netto_voluto = 2` e le commissioni della tabella qui sopra:

| Incasso | Commissioni (da riverificare) | Lordo minimo | Soglia pratica |
|---|---|---|---|
| Ko-fi (payout Stripe) | 0% piattaforma + processing Stripe | ~€2,3 | **€3** |
| Ko-fi (payout PayPal) | 0% piattaforma + ~3,4% + €0,35 | ~€2,4 | **€3** |
| PayPal "nudo" | ~3,4% + €0,35 | ~€2,4 | **€3** |
| Buy Me a Coffee | 5% + processing | ~€2,6 | **€3** |
| Gumroad | ~10% + processing | ~€2,6 | **€3** |

⚠️ Le percentuali vengono dalla tabella sopra e **non sono state riverificate sui
tariffari attuali**: prima di fissare la soglia, controllare le condizioni reali
della piattaforma scelta (in particolare il processing sul payout di Ko-fi, che
la tabella "0%" non copre) e l'eventuale commissione su valuta/paese.

Conseguenza pratica: **€3 copre tutti gli scenari**, è una cifra credibile per un
"caffè" e resta sopra i €2 netti anche nel caso peggiore.

**I due importi decisi (2026-08-01):**

| | Netto voluto | Lordo da chiedere | Campo sulla pagina |
|---|---|---|---|
| **Consigliato** (preselezionato) | 10 | ~**11** (10,4 con Stripe, 10,7 con PayPal) | importo di default |
| **Minimo** (sotto non si dona) | 2 | **3** | importo minimo imposto |

Stessa cifra in £/$/€ a seconda del mercato: sono valute diverse, non un cambio —
un donatore UK vede 11 £, uno USA 11 $.

**Il minimo dev'essere imposto dalla piattaforma, non solo suggerito.** È il
criterio con cui scegliere dove incassare: una pagina che accetta €1 e poi non
consegna la chiave produce solo richieste di rimborso. Se nessuna piattaforma
impone davvero il minimo, il ripiego è vendere un **prodotto a prezzo fisso 3**
con "paga di più se vuoi" (Gumroad/itch.io lo fanno nativamente) invece della
donazione libera — cambia il framing, non i conti.

La soglia va scritta nella pagina di donazione *prima* del pagamento, non dopo.
Stato operativo e sotto-punti da decidere: `TODO.md` ② → "Sblocco Pro via
donazione".

### Il vero punto di attenzione: il fisco (Italia)

- Donazioni **spontanee, occasionali, modeste**, ricevute nella **sfera privata**
  (non come corrispettivo del software) → in genere **non** rilevano ai fini
  delle imposte sui redditi.
- Se diventano **abituali/organizzate** o sembrano un "prezzo" → **reddito**:
  *redditi diversi* se occasionale; *lavoro autonomo* se abituale → **Partita
  IVA**. Regola pratica: sotto ~**€5.000/anno** senza attività continuativa la
  P.IVA non è richiesta; oltre, sì.
- Le piattaforme **segnalano gli incassi al Fisco** (normativa **DAC7**):
  "incasso e ignoro" non è sicuro se le cifre crescono.
- ➡️ **Azione:** tieni una traccia ordinata degli incassi. Se superano lo
  spicciolo, **una consulenza singola da un commercialista** vale l'investimento.

---

## 4. "Sicurezza personale" — checklist

- **Responsabilità civile:** la clausola *AS IS / senza garanzie* della MIT ti
  copre. Aggiungi un rigo di disclaimer anche sulla pagina download.
- **Privacy dati personali:** la MIT richiede un nome come titolare del
  copyright, che sarà pubblico. Puoi usare il **nome del progetto/brand** invece
  del nome legale completo per più riservatezza (resti comunque l'autore per
  legge). Trade-off: privacy vs. credibilità.
- **Sito/WHOIS:** attiva la **privacy WHOIS** (in UE spesso di default). Usa una
  **email dedicata** al progetto, non quella personale.
- **Finanziaria:** PayPal può congelare fondi — non farci passare nulla di
  critico; conto/email dedicati aiutano.
- **Antivirus/SmartScreen** (rischio reputazionale, non legale): l'exe non
  firmato fa comparire "Windows ha protetto il PC". Mitigazioni in §6.
- **Doxxing/molestie:** rischio basso per un dev-tool di nicchia; rename + brand
  email + WHOIS privacy coprono il grosso.

---

## 5. Piattaforme a costo zero utili per i musicisti (oltre GitHub)

- **itch.io** — ottima per tool gratuiti/pay-what-you-want per creativi;
  categoria "Music Production", donazioni integrate, buona discoverability.
  **Consiglio forte.**
- **KVR Audio** — il ritrovo di chi fa musica con software: forum + submission al
  database prodotti/news → pubblico mirato. Gratis.
- **Gumroad** — download pay-what-you-want, utile per **mailing list**.
- **Reddit** — r/ableton, r/edmproduction, r/WeAreTheMusicMakers,
  r/musicproduction: una **GIF demo** porta molto traffico (rispetta le regole
  self-promo).
- **YouTube** — video **60–90s** di screen recording: l'asset di marketing a più
  alta leva. Incollalo ovunque.
- **Product Hunt** — lancio in un giorno, spike + backlink.
- **Discord/forum** dei producer e forum Ableton.

---

## 6. Sito web + il problema dell'exe non firmato

Il sito è la **casa canonica**; tutto il resto punta lì (SEO). Serve: HTTPS,
WHOIS privacy, email dedicata, pagina download (installer + video + donazioni +
link GitHub), **checksum SHA-256** e link **VirusTotal** dei file.

**Exe non firmato — opzioni (dal più economico):**

1. **Gratis:** accetti l'avviso al primo avvio + SHA-256/VirusTotal + istruzioni
   ("More info → Run anyway"). La reputazione SmartScreen cresce coi download.
2. **~$10/mese — Microsoft Trusted Signing:** ora **aperto ai singoli
   sviluppatori** (verificare eleggibilità dall'Italia), firma in cloud senza
   token hardware. Opzione moderna più economica; elimina gran parte degli
   avvisi. **Consigliata** quando il progetto è pubblico (risolve il vincolo
   antivirus).
3. **~$220/anno — certificato OV** (Sectigo/Comodo): richiede token hardware/HSM,
   più costoso/macchinoso. NB: gli **EV non "saltano" più SmartScreen** dal 2024
   → non pagare l'EV solo per quello.

---

## 7. Strategia sforzo/resa — i passi

**Prep (una volta):**
1. **Rinomina** via dal marchio (§0).
2. `LICENSE` **MIT** + `README` (inglese) con **GIF/video**, install per OS,
   setup una-tantum della Control Surface, troubleshooting (incluso l'avviso
   Windows + checksum).
3. Sistema la **licenza delle icone** (Icons8 → attribuzione o sostituzione).
4. **Video demo** 60–90s.
5. **Ko-fi** + **GitHub Sponsors** (donazioni opzionali, "il tool è e resta
   gratis").
6. Sito: pagina download canonica.
7. *(Opzionale ~$120/anno)* **Trusted Signing** per abbattere gli avvisi AV.

**Lancio (un giorno coordinato):** GitHub release + itch.io live → post
r/ableton + r/edmproduction (con GIF), forum + news **KVR**, **Product Hunt**,
social, blog del sito. Chiedi a qualche amico star/upvote iniziali (valanga di
reputazione + aiuta la telemetria SmartScreen).

**Mantenimento (passivo):** video in pin, README aggiornato, rispondi alle issue,
tagga le release. Lascia lavorare itch.io/KVR/SEO sulla coda lunga.

**Classifica sforzo/resa:** *Video + Reddit + itch.io + KVR* = **80% della
portata col 20% dello sforzo.** Donazioni: *Ko-fi/GitHub Sponsors > PayPal nudo*.
Igiene legale: *rename + MIT + WHOIS privacy + licenza icone* = assicurazione a
costo quasi zero.

---

## 8. Stima economica realistica — 1 anno

Modello **free + donazioni volontarie**, tool di nicchia (produttori Ableton),
marketing organico (niente ads). Tasso di donazione tipico per software gratuito:
**~0,5–2%** degli utenti attivi; donazione media **~€3–5**.

| Scenario | Download anno 1 | Donazioni | Ricavo lordo/anno |
|---|---|---|---|
| **Pessimistico** (poca trazione) | 500–1.500 | ~1% × ~€4 | **€10–50** |
| **Moderato** (buon video + qualche hit Reddit/KVR) | 3.000–8.000 | ~1% × ~€5 | **€50–200** |
| **Ottimistico** (front page subreddit / YouTuber lo mostra) | 15.000–40.000 | 1–2% × ~€5 | **€500–3.000** |

**Verità onesta:** con il modello donazioni l'aspettativa realistica anno 1 è
**decine–basse centinaia di €** ("coffee money"). Se compri dominio (~€10/anno) +
firma (~€120/anno), **l'anno 1 probabilmente costa più di quanto rende**:
va trattato come **investimento in reputazione**, non come fonte di reddito.

**Il vero ROI non sono le donazioni, ma:**
- **Portfolio/reputazione** (aiuta a trovare lavoro/clienti freelance — vale
  potenzialmente molto più delle donazioni).
- **Audience/mailing list** riutilizzabile in futuro.
- **Opzionalità:** se prende piede, puoi aggiungere dopo un tier a pagamento.

**Se l'obiettivo è reddito (non donazioni):** la leva è un modello **freemium**
— core gratis + **"Pro" a pagamento** (€5–15 una tantum) su Gumroad/itch.io.
Anche a 1–3% di conversione a €7 su qualche migliaio di download = alcune
centinaia di €, e scala meglio delle donazioni. Cambia però il posizionamento
"free/MIT" (si tiene il core MIT e si vende un Pro chiuso, oppure tutto freeware).

---

## 9. Decisioni aperte (per il Q&A / implementazione)

- [ ] **Nome definitivo** (sblocca repo, brand, sito, LICENSE).
- [ ] **Modello:** solo donazioni, oppure free + Pro a pagamento?
- [ ] **Titolare copyright:** nome legale o brand? (privacy vs. credibilità)
- [ ] **Piattaforme donazioni:** Ko-fi? GitHub Sponsors? entrambe? → mi servono i link
- [ ] **Firma exe:** gratis (checksum) ora, Trusted Signing dopo?
- [ ] **Dominio/sito:** dove hosti (il tuo sito esistente vs. pagina dedicata)?
- [x] **Rename del tool "AbletonLoader" → "LiveLoader"** (assembly/exe, product,
  tray/titoli/notice, data folder con migrazione, remote script + Control Surface,
  installer/portable/macOS bundle). Namespace C# interni lasciati `AbletonLoader.*`
  (non visibili all'utente). Fatto 2026-07-16.
