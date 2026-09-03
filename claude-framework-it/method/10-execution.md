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
