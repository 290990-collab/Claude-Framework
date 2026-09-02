# TODO

Solo lo **stato**: dove siamo adesso. Il *cosa* e il *come* stanno in
[roadmap.md](roadmap.md); i risultati chiusi in [status.md](status.md).

> Primo file a inizio sessione, ultimo a fine task. Tetto ~60 righe: **si
> comprime prima di aggiungere**, la traccia lunga scende in `status.md`.
> Si aggiunge o si spunta, non si riscrive.

## In corso

- [ ] D1 — completare il dataset: 21 dei 24 task ancora da scegliere dal corpus
      di 230 richieste reali, secondo le regole in `docs/eval/task.md`

## Prossimi

- [ ] Pilota di D1 sui 3 task già scritti (T01-T03): valida la procedura prima
      di spendere 40 sessioni. Se il pilota costringe a cambiare il criterio,
      quei 3 escono dal dataset e si rifanno
- [ ] Discutere D9 e D10 — toccano `method/` e `coordinator/`, cioè la parte
      che ogni agente paga
- [ ] R3 — checklist di pacchettizzazione da `claude-os`: disinstallazione,
      template di issue, CI che esegue la suite

## In attesa

- **Le prove di D1 le lancia l'utente**: due sessioni nuove per coppia, ordine
  alternato. Deve riportare id del task, condizione, path del CSV prodotto, e se
  `version`, `model` ed `effort` coincidono fra le due condizioni.

## Bloccati

- **D2, D5, D6, D7** dipendono da D1: senza un numero sono opinioni.
- **`framework+sec`** congelato: aggiunge agenti, un ciclo, una guida e un check
  — precisamente ciò che è vietato finché D1 non chiude. C'è anche un vincolo
  meccanico che decide da solo: il profilo `research` è a 1882/2000 parole.

## Decisioni aperte

- [ ] **Licenza del progetto**: non dichiarata. Blocca la pubblicazione, non lo
      sviluppo. Opzioni da valutare quando la pubblicazione si avvicina.
- [ ] **D9** — dove va il presidio contro la propagazione dell'errore, e quanto
      costa verificare fra uno step e l'altro invece che solo in fondo. Sbloccata
      da una misura del tasso d'errore reale, quindi da D0/D1.
- [ ] **D10** — se la divagazione sia problema di metodo (caro: si paga in
      `CLAUDE.md` a ogni spawn) o di instradamento (quasi gratis: una riga in
      `coordinator/`).

---

Ultimo aggiornamento: 2026-09-02
