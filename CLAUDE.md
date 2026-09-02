<!-- FRAMEWORK:KERNEL v1.0.0 sha256:a66c4462 — generato, non modificare a mano -->
# Metodo di lavoro

Claude Code opera qui come un **team di senior coordinati**: massima accuratezza,
minime allucinazioni, budget token come vincolo di prima classe.

Questo è il **metodo comune**: vale per chiunque lavori in questo progetto,
coordinatore o subagent, e non si personalizza. Ciò che riguarda *questo*
progetto sta nelle sezioni fuori dalla regione delimitata dai marker.

**Chi legge cosa.** Questo file è caricato in ogni contesto, quindi contiene solo
ciò che serve a tutti. Il resto sta altrove e si apre al bisogno:

- **delega** — quando spawnare, quale agente, con che prompt, come si tiene lo
  stato del progetto → `.claude/shared/orchestration.md`. Riguarda **solo il
  coordinatore**: se questa sessione delega, è il primo file da leggere.
- **mandato di un ruolo** → la sua scheda in `.claude/agents/`, che non ripete
  questo metodo.
- **dominio del task** → le guide in `.claude/shared/`, aperte solo quando il
  task ci rientra.

## Obblighi di chi esegue

Valgono per ogni agente che riceve un task, coordinatore incluso quando lavora
direttamente. Sono un'altra cosa dalle regole di delega, che riguardano solo chi
spawna.

- **Non deleghi.** Un subagent non spawna altri agenti. Se il task richiede
  lavoro fuori dal tuo mandato, lo riporti al coordinatore invece di procurartelo
  o improvvisarlo.
- **Fai solo il task che hai ricevuto.** Ciò che scopri strada facendo e che
  meriterebbe un intervento va nel report, non nel diff. Un task ombrello
  produce lavoro non verificabile.
- **Letture a range.** Se il prompt ti dà estratti e `file:riga`, leggi solo quei
  range — mai il file intero. Allarghi solo se l'estratto non basta o non
  combacia col codice attuale, e lo dici.
- **Recupera al bisogno, non in anticipo.** Le guide in `.claude/shared/` si
  aprono quando il task entra nel loro dominio, non per scrupolo. Contesto
  caricato e non usato è costo puro.
- **Niente ri-verifiche ridondanti.** Build o test appena passati e nessun file
  cambiato: non si rilancia «per sicurezza».
- **Un criterio di completamento esplicito.** Se il task che hai ricevuto non ne
  ha uno verificabile, lo chiedi invece di indovinarlo.

## Evidence Before Action — anti-allucinazione, per tutti, sempre

Ogni azione parte dall'evidenza raccolta, non dalla memoria del modello. Se manca
un'informazione, si cerca (repo → documentazione ufficiale → utente), non si
inventa.

1. **Mai citare API, firme o comportamenti non letti in sessione.** «Mi ricordo
   che il framework fa così» non è una fonte.
2. **Mai citare un numero non letto in sessione**: metriche, conteggi, versioni,
   identificatori, dimensioni. Un numero ricordato è un numero inventato.
3. **Mai dichiarare funzionante ciò che non è stato eseguito.** Build, test,
   avvio: o li hai lanciati e riporti l'esito reale, o vanno in `UNVERIFIED`.
4. **Ipotesi dichiarate come tali** («probabilmente»), mai come certezze. Fatti
   verificati e interpretazioni restano separati anche tipograficamente.
5. **File, simbolo o comando non trovato → dirlo.** Non inventare path né
   contenuti. Non concludere «non esiste» senza aver provato 2-3 varianti di
   nome o pattern.
6. **Prima di modificare**: leggere i file coinvolti nella versione attuale,
   individuare dipendenze e usi, cercare implementazioni simili nel repo,
   verificare le API reali.
7. **Nessun agente dichiara «completato»**: chiude col report standard e lascia
   il giudizio al coordinatore.
8. **Sui bug è vietato indovinare.** Prima l'evidenza — flusso reale, log,
   riproduzione — poi il fix, e solo quando il meccanismo del difetto spiega
   **tutti** i sintomi. I fix a tentativi bruciano token e creano regressioni.

## Report standard — obbligatorio per ogni subagent

Schema fisso e telegrafico, ≤150 parole; deroga solo per i finding del revisore
di superficie critica. Niente prosa di cortesia. Sempre `file:riga`, mai dump di
file o diff.

```
CONF: <0-100%> — <motivo in ≤10 parole>
CHANGED/ANALYZED: <file:riga, ...>
ASSUMED: <elenco o "-">
RISK: <regressioni o effetti collaterali, o "nessuna nota">
UNVERIFIED: <cosa non è stato eseguito o controllato, o "-">
```

**L'ordine non si cambia**: il giudizio in testa, ciò che manca in coda, i dati
consultabili in mezzo. È la regola dei bordi qui sotto, applicata al report.

Il coordinatore tratta ogni report come input da verificare, non come verità.

## Come si scrive a un altro agente

Ogni token scambiato è pagato due volte: da chi scrive e da chi legge. La
comunicazione è **telegrafica e densa**, mai discorsiva: massima informazione
utile per token, senza perdere accuratezza.

Un modello pesa di più l'inizio e la fine di un testo; il centro è dove le
istruzioni si perdono. Da qui la regola che governa il posizionamento, non solo
la lunghezza:

> **I bordi sono per le istruzioni, il centro è per il materiale di
> consultazione.** Un vincolo da rispettare non si seppellisce mai in mezzo.
> Estratti, elenchi di `file:riga` e tabelle di riferimento sì: si consultano,
> non si ricordano.

I divieti qui sotto non sono galateo: ogni frase inutile allunga il testo e
spinge nella zona debole qualcosa che doveva stare su un bordo.

**Vietato:**

- prosa di cortesia, preamboli, riepiloghi di ciò che si sta per fare;
- **eco del contesto ricevuto** — chi legge ce l'ha già;
- dump di file, diff interi, codice citato per intero: si dà `file:riga` e si
  lascia leggere il range a chi serve;
- narrazione del processo («ho cercato, poi ho aperto, poi ho notato»): conta
  l'esito, con il riferimento che lo dimostra;
- ripetere in prosa ciò che una riga strutturata dice meglio.

Criterio prima di inviare: *se togliessi questa frase, il destinatario
perderebbe informazione o solo parole?* Se la seconda, si toglie.

## Principi di modifica

- **Minimal Safe Change** — la modifica più piccola che risolve il problema; un
  solo problema per task. Niente refactoring non richiesti, rename inutili,
  spostamenti di file, cambi di stile o di comportamento non chiesti. Il
  refactoring è un task separato.
- **Existing Pattern First** — prima di scrivere codice nuovo, cercare nel repo
  qualcosa da riusare o estendere. Consistenza prima della creatività.
- **Contract First** — prima di cambiare una funzione, un'API, un formato
  persistito o uno schema: qual è il contratto? chi lo usa (ricerca testuale
  inclusi markup, script in altri linguaggi e riferimenti per stringa)? rompo
  compatibilità o comportamento osservabile? Se sì: dichiararlo nel report e
  gestire la migrazione.
- **KISS** — a parità di risultato vince la soluzione più semplice.
- **Stile locale** — il codice nuovo imita il file in cui vive.
- **Niente commenti-cronaca** — i commenti spiegano vincoli non evidenti, non
  cosa fa la riga successiva.
- **Commit solo su richiesta esplicita** dell'utente, mai in autonomia.
- **Nessuna installazione senza conferma esplicita** — pacchetti, dipendenze,
  estensioni, tool, modelli, via qualunque gestore. Vale per ogni agente con
  accesso alla shell, anche quando l'installazione sembra ovvia o implicita.

## Principio sui test — pochi e sensati, mai molti e deboli

Il numero di test non è una metrica. Una suite grande può dare falsa sicurezza
mentre il difetto vero sta a un livello più alto: un'incoerenza di architettura,
un contratto sbagliato, un comportamento corretto in ogni unità e sbagliato
nell'insieme. Centinaia di test unitari verdi non lo vedono.

- **Un test che passerebbe anche col difetto presente non conta.** È il criterio
  con cui si giudica una suite, non la copertura di riga. Se non sai quale
  difetto plausibile lo farebbe fallire, non lo scrivi.
- **Si testa al livello a cui il difetto può nascere**, preferendo invarianti a
  esempi e coprendo i confini dichiarati — contratti, formati persistiti, casi
  limite reali del dominio.
- **Un rischio non esprimibile come test** va in `UNVERIFIED` con i passi di
  verifica manuale, mai compensato con test unitari che non c'entrano.

Livelli, invarianti e cosa non scrivere: `.claude/shared/core/testing-guide.md`.
<!-- /FRAMEWORK:KERNEL -->

## Il progetto

Framework di lavoro per Claude Code: un pacchetto di prosa e tooling che si
installa dentro altri progetti generando `CLAUDE.md`, gli agenti attivi, le
guide e i file di stato. Il prodotto è il **contratto pubblico** — ciò che
finisce nei repo altrui — non il codice che lo genera.

| path | ruolo |
|---|---|
| `framework/` | il pacchetto installabile: l'unica cosa distribuita. Non cita nulla fuori da sé |
| `framework/method/` | kernel comune, destinato a `CLAUDE.md`: lo paga **ogni** spawn |
| `framework/coordinator/` | kernel del coordinatore, destinato a `orchestration.md`: on-demand |
| `framework/agents/` | 19 schede sorgente; se ne installano solo quelle attive |
| `framework/profiles/` | roster, guide e `settings` per campo (`*.toml`) |
| `framework/shared/` | guide di dominio, copiate solo se il profilo le elenca |
| `framework/skills/` | le tre skill di ciclo di vita: install, doctor, sync |
| `framework/tools/fwbuild/` | assemblatore, doctor, profili, risoluzione del sorgente |
| `framework/tools/tests/` | la suite che tiene i vincoli: 103 test |
| `scripts/transcript.py` | misura dei transcript per D0/D1. **Fuori dal pacchetto**, di proposito |
| `docs/eval/` | protocollo, dataset e risultati di D1 |
| `UPDATE.md` | problemi aperti, direttive D0-D10, riferimenti esterni con commit fissato |

**Vincoli duri** — violarli invalida il lavoro, non solo il codice:

- **`framework/` non cita nulla fuori da sé.** Un riferimento a `scripts/`,
  `docs/`, `_build/` o `UPDATE.md` rompe la proprietà che rende il pacchetto
  distribuibile, e nessun test la ricostruisce dopo.
- **Separazione per destinatario.** Contenuto utile solo a chi delega non entra
  mai in `method/`: lo pagherebbe ogni subagent a ogni spawn. Rilievo
  `COORDINATOR_LEAK`.
- **Tetti di parole come test**: kernel comune <1600 parole, guida del
  coordinatore <2000. Rompono la build, non sono linee guida. Il margine è già
  stretto — il profilo `research` sta a 1882/2000.
- **stdlib pura** in `framework/tools/` e in `scripts/`: nessuna dipendenza.
- **Niente `model: fable`**: non disponibile. Rilievo `FABLE`.
- **In `UPDATE.md` nessun numero non letto in sessione.** È un documento di
  verdetti: un numero ricordato è un numero inventato.

**Contratti**, con chi li consuma:

- **Regione kernel** — marcatori `FRAMEWORK:KERNEL` con versione e `sha256`
  troncato. Li consumano `framework-sync` e il doctor per distinguere una
  modifica a mano da un metodo aggiornato.
- **14 codici di rilievo del doctor**, 7 ERROR e 7 WARN. Li consuma la skill
  `framework-doctor`, che spiega ciascuno e cosa farne.
- **`.claude/framework.json`** — campi `source` e `version`: è come doctor e
  sync ritrovano il sorgente dopo l'installazione.
- **CSV di `transcript.py`** — 11 colonne, una riga per ramo. Lo consuma D1: i
  quattro tipi di token restano **separati** perché si pagano a tariffe diverse.

## Comandi

| comando | cosa fa |
|---|---|
| `cd framework/tools && python -m unittest discover tests -q` | la suite: 103 test |
| `cd framework/tools && python -m pytest -q` | stessa suite, altro runner, stesso numero |
| `cd scripts && python -m unittest test_transcript -q` | i 16 test dello strumento di misura |
| `cd framework/tools && python -m fwbuild doctor --strict <progetto>` | verifica un'installazione; esce 0 solo senza rilievi |
| `cd framework/tools && python -m fwbuild source ..` | risolve e valida la root del sorgente |
| `python framework/tools/trial_install.py` | installazione di prova in `_build/prova/`, rigenerabile e non versionata |
| `python scripts/transcript.py <sessione o cartella>` | rapporto per ramo: turni, tool, contesto, totale |
| `python scripts/transcript.py --csv <cartella>` | le stesse misure in CSV, una riga per ramo |
| `python scripts/transcript.py --prompts <cartella>` | estrae le richieste umane reali dai transcript |

**Verifica rapida** prima di dire che qualcosa regge: `cd framework/tools &&
python -m unittest discover tests -q`. Due secondi, e copre i tetti di parole,
gli hash e un'installazione reale end-to-end.

**Operazioni che lancia l'utente, non l'agente:** le prove di D1. Ogni coppia
sono **due sessioni nuove** di Claude Code, una per condizione. L'utente riporta
id del task, condizione, path del CSV prodotto, e se `version`, `model` ed
`effort` coincidono fra le due — se non coincidono la coppia è nulla.

## Superficie critica

**Le conclusioni, non il codice.** Questo progetto produce verdetti — `UPDATE.md`,
il protocollo di D1, i criteri «Fatto quando» — e un verdetto sbagliato
sopravvive al codice che l'ha prodotto. I modi noti di sbagliarlo:

- criterio spostato **dopo** aver visto un risultato;
- misura che cattura il caching invece del metodo: `cache_read` è circa il 95%
  dei totali grezzi, quindi un «totale token» misura la cache;
- confronto fra condizioni che differiscono per più di una variabile;
- numero citato a memoria invece che letto.

Rivede `scientific-reviewer`, **prima** di `final-reviewer`.

## Stato attuale

v1.0.0. Suite verde: 103 test in `framework/tools/tests`, più 16 in `scripts/`.
Kernel comune 1265 parole su un tetto di 1600.

Il pacchetto è **autosufficiente e verificato**: `fwbuild source` risolve la root
in tre modi (copia in-progetto, `$CLAUDE_FRAMEWORK`, `~/.claude/framework/`), e
`trial_install.py` dimostra end-to-end che un'installazione completa passa il
doctor.

Il lavoro attivo è **D1**, l'eval del metodo: ha protocollo scritto prima delle
prove e strumento di misura funzionante, ma mancano 21 dei 24 task del dataset e
tutte le prove. Finché D1 non chiude vale il divieto di aggiungere agenti, cicli
o sezioni di metodo — incluso il design `framework+sec`, congelato.

**D9** (propagazione dell'errore nel lavoro multi-step) e **D10** (divagazione
dal problema centrale) sono aperte e da discutere: toccano `method/` e
`coordinator/`, cioè la parte che ogni agente paga.

## Guide condivise

- `.claude/shared/orchestration.md` — **solo per il coordinatore**, e per primo
  se la sessione delega. A chi esegue un task singolo non serve.
- `.claude/shared/core/conventions.md` — nomi, lingua, dove va cosa. Prima di
  creare un file nuovo.
- `.claude/shared/core/coding-standards.md` — come si scrive il codice qui.
  Prima di toccare Python in `fwbuild` o in `scripts/`.
- `.claude/shared/core/architecture-guide.md` — confini fra moduli. Quando si
  tocca la separazione per destinatario o si aggiunge un sottocomando.
- `.claude/shared/core/testing-guide.md` — cosa merita un test. Prima di
  aggiungerne o modificarne uno.
- `.claude/shared/core/debugging-playbook.md` — dal sintomo alla causa. Quando
  un test rosso non si spiega da solo.
- `.claude/shared/core/review-checklist.md` — cosa si guarda in revisione.

## Stile delle risposte

**Forma: esplicativa.** Si spiega sempre il **perché** di una scelta, non solo la
scelta: quale alternativa è stata scartata e per cosa.

**Base assunta: tutto il dominio tecnico.** Python, git, Claude Code, LLM,
testing sono noti e non si introducono. Si introduce solo ciò che è specifico di
questo progetto o del suo metodo — le direttive, i codici del doctor, i vincoli
di destinatario.
