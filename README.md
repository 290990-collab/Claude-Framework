# Claude Framework

Un metodo di lavoro installabile per **Claude Code**: agenti specializzati, regole
di delega, guide di dominio e file di stato, generati in un progetto e poi
**verificabili** — con uno strumento che dice quando l'installazione si è rotta e
un canale per far risalire nel sorgente le modifiche che valgono per tutti.

> **English** — the same framework, fully translated, lives in
> [`claude-framework-eng/`](claude-framework-eng/README.md). Install one or the
> other, not both.

---

## Cosa risolve

Chi usa Claude Code su più progetti finisce con un `CLAUDE.md` scritto a mano per
ognuno. Dopo qualche mese le versioni divergono, nessuno sa quale sia quella
buona, e il file cresce finché ogni subagent paga un contesto che non usa.

Il framework attacca le tre cause:

| Problema | Cosa fa il framework |
|---|---|
| Il metodo si biforca fra progetti | Un sorgente unico, versionato; `framework-sync` porta le versioni giù e le migliorie su |
| Le modifiche a mano spariscono | Il metodo generato vive in una **regione kernel** con un hash: modificarla è lecito, ma diventa visibile |
| `CLAUDE.md` gonfia e costa | Separazione per **destinatario**: chi delega legge un file a parte, che gli altri non pagano |

---

## Requisiti

- **Claude Code**
- **Python 3.11+** — solo per il tooling, e solo `tomllib` dalla stdlib

Nessuna dipendenza da installare.

---

## Installazione

Si fa **una volta per macchina**. Da lì in poi ogni progetto nuovo è una riga.

```bash
git clone https://github.com/290990-collab/Claude-Framework.git ~/.claude/claude-framework
cp -r ~/.claude/claude-framework/claude-framework-it ~/.claude/framework
cp -r ~/.claude/framework/skills/framework-install ~/.claude/skills/
```

```powershell
git clone https://github.com/290990-collab/Claude-Framework.git $HOME\.claude\claude-framework
Copy-Item -Recurse $HOME\.claude\claude-framework\claude-framework-it $HOME\.claude\framework
Copy-Item -Recurse $HOME\.claude\framework\skills\framework-install $HOME\.claude\skills\
```

Per l'inglese, `claude-framework-eng` al posto di `claude-framework-it`.

La destinazione si chiama `framework/` perché è uno dei posti in cui l'installer
guarda. Cerca in quest'ordine: `./framework/` nel progetto, `$CLAUDE_FRAMEWORK`,
`~/.claude/framework/`. Per tenere il sorgente altrove, basta la variabile.

Controllo che il sorgente sia valido:

```bash
cd ~/.claude/framework/tools && python -m fwbuild source ..
```

---

## Uso

### Le tre skill

| Skill | Quando | Cosa fa |
|---|---|---|
| `/framework-install` | **una volta per progetto** | Legge il progetto, fa il questionario, sceglie il roster, genera tutto, verifica il risultato |
| `/framework-doctor` | quando qualcosa non torna | 18 controlli sull'installazione, con la remedy per ognuno |
| `/framework-sync` | manutenzione | Porta versioni **giù** nel progetto, migliorie **su** nel sorgente, attiva o disattiva un agente |

Le modalità di `framework-sync` — `--down`, `--up`, `--activate <agente>`,
`--deactivate <agente>` — si chiedono alla skill in linguaggio naturale: **non
sono flag da shell.**

### Cosa scrive in un progetto

`/framework-install` con il profilo `software` produce:

```
CLAUDE.md                      metodo comune + contesto del progetto
.claude/framework.json         sorgente, versione, profilo
.claude/settings.json          permessi del profilo (incluso il divieto sui segreti)
.claude/agents/                9 schede: solo il roster scelto
.claude/shared/orchestration.md  regole di delega + tabella di routing — solo chi delega
.claude/shared/core/           6 guide, aperte on-demand
.claude/skills/                framework-doctor, framework-sync
docs/TODO.md                   dove siamo adesso
docs/status.md                 decisioni chiuse e risultati
docs/roadmap.md                dove si va
```

I blocchi `[DA COMPILARE — …]` sono i punti che l'installer riempie con te
durante il questionario: sono il contesto del progetto, l'unica parte che si
personalizza.

### I cinque profili

| Profilo | Agenti | Cicli aggiunti | Per |
|---|---:|---|---|
| `software` | 9 | — | Applicazioni e servizi |
| `library` | 9 | — | Librerie e pacchetti |
| `web` | 11 | design | Siti e interfacce |
| `data` | 12 | — | Pipeline e dati |
| `research` | 11 | ricerca | Esperimenti e misure |

Sei agenti sono sempre presenti — `explorer`, `architect`, `implementer`,
`tester`, `refactorer`, `final-reviewer`: sono il ciclo del codice. Il master ne
contiene **19**; gli altri si aggiungono con `--activate`.

---

## Comandi

Tutti da `<sorgente>/tools`.

| Comando | Risponde a |
|---|---|
| `python -m fwbuild doctor <progetto>` | «Questa installazione regge?» |
| `python -m fwbuild source <sorgente>` | «Questo sorgente è valido?» |
| `python -m fwbuild cost <progetto>` | «Quanto costa il contesto comune?» |
| `python -m fwbuild report <cartella>` | «Quante versioni sono in giro, e dove?» |

Opzioni che contano:

| Flag | Su | Effetto |
|---|---|---|
| `--strict` | `doctor`, `report` | Esce 1 anche sui soli avvisi. **Da usare sempre**, in CI e a mano |
| `--json` | `doctor`, `report` | Stesso contenuto in una struttura sola. Non cambia l'exit code |
| `--spawns N --devs N --price N` | `cost` | Traduce le parole in token e in spesa reale |
| `--depth N` | `report` | Quanti livelli scendere cercando le installazioni |

```
$ python -m fwbuild doctor --strict ../../mio-progetto
OK — nessun rilievo

$ python -m fwbuild cost ../../mio-progetto --spawns 200 --devs 12
CLAUDE.md: 1.584 parole ≈ 2.107 token, pagati a ogni spawn.
  di cui kernel 1.275 (con tetto) e progetto 309 (senza).
200 spawn al giorno × 12 persone = 5,1 milioni di token al giorno di solo contesto comune.
```

Il doctor produce 18 rilievi su tre livelli: **ERROR** (installazione rotta),
**WARN** (giudizio), **NOTE** (avviso che il progetto dichiara di accettare, in
`framework.json`, con una ragione scritta — gli errori non si accettano).

---

## Il ciclo di manutenzione

Il metodo generato vive dentro una regione delimitata:

```html
<!-- FRAMEWORK:KERNEL v1.1.0 sha256:a3f9c1e4 — generato, non modificare a mano -->
…
<!-- /FRAMEWORK:KERNEL -->
```

Non è bloccata. Se la modifichi, l'hash smette di tornare e il doctor segnala
`KERNEL_DRIFT` — che **non è un errore**, è informazione. A quel punto la
domanda è una sola:

> È un miglioramento che vale per tutti i progetti, o una deroga di questo?

- **Miglioramento** → `/framework-sync` in modalità `--up`: la modifica risale
  nel sorgente, la versione si incrementa, il prossimo progetto nasce con dentro.
- **Deroga locale** → si annota, e il prossimo che legge il rilievo sa che è voluta.

È la direzione che di solito manca, ed è il motivo per cui altrove il metodo si
biforca.

---

## Le due copie

`claude-framework-it/` e `claude-framework-eng/` sono lo stesso framework, non
uno l'appendice dell'altro. Restano allineati per costruzione:
[`tools/test_parity.py`](tools/test_parity.py) fallisce se una copia ha un file,
un agente, un profilo, una versione o un test che l'altra non ha.

```bash
cd claude-framework-it/tools && python -m unittest discover -s tests -t . -q   # 160 test
cd claude-framework-eng/tools && python -m unittest discover -s tests -t . -q  # 160 test
cd tools && python -m unittest test_parity -q                                  # 9 test
```

---

## Stato

**Versione 1.1.0.** 329 test verdi, installazione di prova pulita sotto
`doctor --strict` in entrambe le lingue.

Cosa **non** è stato verificato, e va detto: il framework non è ancora stato
usato dall'inizio alla fine su un progetto reale in produzione. I test provano
che l'installazione è coerente e che il tooling fa ciò che dichiara — non che il
metodo produca lavoro migliore. Quella misura non esiste, e finché non esiste
nessun numero di risparmio va creduto.

## Licenza

Nessuna licenza dichiarata: tutti i diritti riservati dall'autore.
