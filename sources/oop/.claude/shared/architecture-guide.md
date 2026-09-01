# Guida all'architettura — AbletonLoader

Topologia: app desktop (Views + Services → Core, C#/Avalonia) ↔ socket
locale ↔ remote script Python dentro Ableton Live.

## Confini e responsabilità

- **`AbletonLoader.Core`** — logica pura e riusabile: `AppConfig`,
  `LiveClient`, `QuickMatch`. Nessuna dipendenza da Avalonia né da API di
  piattaforma; identico su Windows e macOS.
- **`AbletonLoader.App`** — tutto ciò che tocca utente/OS: Views e
  `MenuFlow`, `HookService` (hook globali), `InputSimulator`,
  `LiveWindowDetector`, `CatalogService`, `MacInterop` (interop macOS).
- **`remote-script/LiveLoader`** — vive dentro Live, espone i comandi via
  socket locale; versionato indipendentemente (da incrementare a ogni
  cambio di protocollo).

Regola pratica: una classe in `App` che non usa né UI né API di piattaforma
probabilmente va in `Core`.

## I contratti (cambiarli = decisione architetturale)

1. **Protocollo socket app↔remote script**: cambio coordinato dei due lati,
   incremento versione script, gestione del caso "script vecchio con app
   nuova" (e idealmente il contrario).
2. **Formato `AppConfig`**: persistito sui dischi degli utenti — le nuove
   versioni leggono le config vecchie (default per campi mancanti, mai
   rename senza compatibilità di lettura).
3. **Formato del catalogo**: rigenerabile, ma una rigenerazione forzata a
   ogni update è un costo per l'utente — segnalare quando un cambio la
   impone.
4. **Struttura di installazione** (path del remote script dentro Live,
   posizioni note dei file): impatta `build/` e `installer/`.

## Decisioni vincolanti già prese

- Cross-platform via Avalonia, porting macOS attivo: niente nuove
  dipendenze Windows-only nel Core; nel layer App il platform-specific va
  dietro un'astrazione (pattern `MacInterop`).
- Superficie antivirus minima: hook e input simulation al minimo
  indispensabile; vincono le alternative meno invasive anche se meno
  eleganti.
- Remote script senza dipendenze esterne.
- Socket come confine di fiducia: è loopback-only (`127.0.0.1`), ma accetta
  comandi da qualunque processo locale — un comando non può fare più di ciò
  che l'UI stessa consente, e i payload si validano (lunghezze, campi,
  range). Non aggiungere comandi che ampliano ciò che un mittente può
  provocare oltre le azioni dell'utente.

## Valutare una proposta di design (per l'architect)

1. Quali contratti tocca? (nessuno = rischio molto più basso)
2. Cosa succede agli utenti esistenti al primo avvio dopo l'update?
3. Degrada con grazia con Live chiuso / aperto senza remote script?
4. Aggiunge superficie antivirus o permessi nuovi?
5. Complica il porting macOS?
6. Qual è l'alternativa più semplice che risolve il 90% del problema? (KISS)
