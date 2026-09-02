# Status — cosa è stato chiuso

Registro di ciò che **è stato deciso, misurato o smentito**. Non è un diario del
lavoro: ci si scrive quando qualcosa si chiude, non quando si lavora.

> Si aggiunge in fondo, non si riscrive sopra. Una voce per fatto chiuso.
> Ciò che è ancora in corso sta in [TODO.md](TODO.md); il piano in
> [roadmap.md](roadmap.md).
>
> **Anche le smentite si scrivono.** Un'ipotesi caduta è informazione acquisita:
> non registrarla significa ripagarne il costo fra due mesi.

## Formato di una voce

```
## <numero>. <titolo> — <data>

**Domanda:** cosa si voleva sapere o decidere.
**Esito:** confermato | smentito | deciso | rimandato.
**Evidenza:** dove sta il fatto — file, output, misura. Mai un numero a memoria.
**Conseguenza:** cosa cambia da qui in avanti.
```

---

## 1. D0 — la strumentazione dell'eval esiste — 2026-09-01

**Domanda:** si può misurare il costo in contesto per task, separando il
coordinatore dai subagent?
**Esito:** deciso e chiuso.
**Evidenza:** `scripts/transcript.py`, stdlib pura, con 16 test in
`scripts/test_transcript.py`. Verificato sui transcript reali che coordinatore e
subagent sono insiemi **disgiunti** — il file principale non contiene entrate
`isSidechain` — quindi sommarli non conta niente due volte.
**Conseguenza:** il criterio di D1 è misurabile invece che argomentato. La tesi
centrale del framework smette di essere un'osservazione.

## 2. Il totale grezzo di token misura la cache, non il metodo — 2026-09-01

**Domanda:** si può usare il totale dei token come metrica primaria di D1?
**Esito:** smentito.
**Evidenza:** sui transcript reali `cache_read` è circa il 95% dei totali
grezzi.
**Conseguenza:** la metrica primaria in `docs/eval/protocollo.md` è
`input + cache_creation + cache_read` sommati su tutti i rami, e il CSV tiene i
quattro tipi **separati** — si pagano a tariffe diverse, e un costo in euro si
ricava dopo senza rifare le prove.

## 3. Installing — il difetto era nell'installazione, non nel documento — 2026-09-01

**Domanda:** la procedura di installazione descritta era eseguibile e corretta?
**Esito:** smentito, poi corretto.
**Evidenza:** `trial_install.py` copiava `docs/roadmap.md` senza compilarne i
segnaposto, e `doctor --strict` usciva 1 con `PLACEHOLDER docs/roadmap.md` —
mentre `UPDATE.md` affermava che quello script dimostrava il contrario. Dopo la
correzione il difetto è stato **reintrodotto apposta** per vedere il test
end-to-end diventare rosso su quel test e con quel messaggio.
**Conseguenza:** I0-I5 chiuse. Il sorgente si risolve in tre modi
(`fwbuild source`: copia in-progetto, `$CLAUDE_FRAMEWORK`, `~/.claude/framework/`)
e l'installazione non è più legata al percorso di una macchina.

## 4. `software` e `library` installano la stessa identica cosa — 2026-09-02

**Domanda:** quale profilo descrive meglio questo progetto?
**Esito:** la domanda era mal posta.
**Evidenza:** `framework/profiles/software.toml` e `library.toml` dichiarano lo
stesso `agents`, lo stesso `on_demand`, le stesse sei guide e gli stessi
`settings`. Differiscono solo per `name` e `description`.
**Conseguenza:** scegliere fra i due non ha conseguenze meccaniche. Due profili
indistinguibili all'installazione sono un candidato per la potatura di D2, e la
prova che il catalogo dei profili non è mai stato misurato.

## 5. Un agente attivato come extra non porta con sé le guide che cita — 2026-09-02

**Domanda:** attivare `scientific-reviewer` e `results-analyst` su un profilo
`library` è sufficiente perché funzionino?
**Esito:** smentito.
**Evidenza:** `doctor --strict` ha prodotto due `ERROR SHARED_MISSING`: entrambe
le schede citano `.claude/shared/domain/research-principles.md`, che solo
`profiles/research.toml` elenca fra le `shared`. `profile.roster` risolve gli
agenti; **nessuna funzione risolve le guide che quegli agenti citano**.
**Conseguenza:** qui la guida è stata aggiunta a mano e il doctor passa. Resta un
difetto del framework: la dipendenza agente → guida non è dichiarata da nessuna
parte e si scopre solo col doctor, a installazione già scritta. Registrato in
`UPDATE.md` fra i problemi minori.

## 6. Il framework è installato sul repository che lo produce — 2026-09-02

**Domanda:** la procedura di `framework-install` regge sul progetto che la
genera?
**Esito:** confermato, dopo la correzione della voce 5.
**Evidenza:** `cd framework/tools && python -m fwbuild doctor --strict ../..` →
`OK — nessun rilievo`, uscita 0. Profilo `library`, 12 agenti attivi, 7 guide.
Suite verde dopo l'installazione: 103 test in `framework/tools/tests`, 16 in
`scripts/`.
**Conseguenza:** chiusa l'ultima incoerenza di *Installing* — il framework non
era installato sul repository che lo produce. Le sessioni future partono da
`docs/TODO.md`, non da questa chat.
