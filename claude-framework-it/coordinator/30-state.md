## Lo stato che si aggiorna da solo

Senza uno stato scritto, ogni sessione riparte a indovinare. Quattro livelli,
ognuno con il suo ritmo e il suo tetto.

**Lo scrive il coordinatore.** I subagent riportano e basta: chi scrive lo stato
deve aver visto il quadro intero, e un agente che ha visto un task solo non ce
l'ha. È anche il motivo per cui questa sezione sta qui e non in `CLAUDE.md`.

| Liv. | File | Contiene | Si aggiorna | Tetto |
|---|---|---|---|---|
| 1 | `docs/TODO.md` | dove siamo **adesso**: in corso, in attesa, prossimo passo, bloccati | a **ogni** step | ~60 righe |
| 2 | `docs/status.md` | decisioni chiuse, risultati misurati, ipotesi confermate o smentite | quando qualcosa si chiude | 1 voce |
| 3 | `CLAUDE.md § Stato attuale` | il quadro: cosa sa il progetto oggi | solo se **cambia il quadro** | ~25 righe |
| 4 | memoria persistente | fatti che valgono **fra** sessioni: chi è l'utente, direttive, decisioni | a ogni scoperta o cambio strutturale | 1 file |

`docs/roadmap.md` **non è un livello**: i livelli dicono dove siamo, la roadmap
dove andiamo — obiettivi, ordine di dipendenza, criteri di completamento. Si
tocca quando un obiettivo si chiude o se ne aggiunge uno, non a ogni step.

**Regole:**

- **Si aggiunge o si spunta, non si riscrive.**
- **Si comprime prima di aggiungere** quando il tetto è raggiunto. La traccia
  lunga scende di livello, non gonfia quello corrente.
- **Inizio sessione:** livello 1 per primo, sempre. **Fine task:** livello 1
  sempre; livello 2 se qualcosa si è chiuso; livello 3 se una conclusione è
  cambiata.
- **Niente duplicazione fra livelli.** TODO = stato, `status.md` = risultati,
  `CLAUDE.md` = quadro, memoria = ciò che sopravvive alla sessione.
- **Operazioni lunghe o asincrone**: appena parte qualcosa che l'utente deve
  lanciare o attendere, la riga va in *In attesa* con cosa deve rispondere.
- ⚠️ Il livello 3 sta dentro la parte di progetto di `CLAUDE.md`, **fuori dalla
  regione kernel**: aggiornarlo non deve mai produrre un rilievo di drift.

**Il livello 4 va rivisitato, non solo riempito.** A ogni cambiamento
significativo — path, contratti, moduli spostati — e a ogni scoperta che chiude o
smentisce un'ipotesi, chiedersi *«questo supera una memoria?»* e, se sì,
correggerla o annotarla come superata **subito**. Anche la memoria è compatta: un
fatto per file, nessun numero duplicato dal repo, nessun path che non esiste più.
⚠️ **In conflitto vince il repo**: una memoria vecchia non annotata è un bias
attivo, fa ripartire la sessione successiva con la visione di un mese prima.
