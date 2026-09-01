# Standard di codice — AbletonLoader

Regola sovraordinata: **il codice nuovo imita il file in cui vive**. Questi
standard valgono dove il file non dà indicazioni.

## C# (App e Core)

Threading — la fonte principale di bug qui:

- La UI si tocca solo via `Dispatcher.UIThread`: callback di hook e letture
  dal socket arrivano su thread NON-UI.
- Stato condiviso tra thread (hook ↔ UI ↔ socket) protetto o confinato,
  seguendo i pattern dei servizi esistenti prima di inventarne.
- Niente `async void` fuori dagli event handler; `await`, mai
  `.Result`/`.Wait()` (deadlock).

Robustezza:

- Risorse native (hook, handle, socket, processi): `IDisposable`
  implementato e chiamato, unhook garantito anche sui percorsi d'errore.
- Input esterno (nomi preset/plugin, messaggi socket, config da disco) non
  fidato: validare lunghezze, caratteri nei path, formati.
- Path: `Path.Combine`, mai concatenazione; gestire spazi e non-ASCII
  (l'utente tipo ha path come `C:\Users\Enrico Di Maria\...`).
- Log con contesto; mai dati sensibili né contenuto dei tasti premuti.

Avalonia 12:

- Firme API verificate nell'uso reale del repo (alcune cambiate rispetto
  alla 11), mai dalla memoria.
- Binding e nomi in `.axaml` sono stringhe: ogni rename lato C# si
  ricontrolla a mano lato XAML.
- Finestre secondarie (`ToastWindow`, `QuickLauncherWindow`, ...): pattern
  di ownership e chiusura delle viste esistenti.

P/Invoke e piattaforma: nuovo P/Invoke solo se previsto dal piano
(superficie antivirus e portabilità); mai Windows-only nel Core; nel layer
App isolare per piattaforma come fa `MacInterop`.

## Python (remote script)

- Interprete incorporato in Live: nessuna dipendenza esterna, prudenza con
  le feature recenti del linguaggio.
- `Live.*` dal thread giusto; le callback del socket non toccano il
  documento di Live se il pattern esistente prevede lo scheduling.
- Handler difensivi: try/except con log, mai crash (un'eccezione non
  gestita degrada l'esperienza dentro Live).
- Protocollo = contratto versionato (Contract First): messaggi nuovi
  retrocompatibili, versione dello script aggiornata a ogni cambio.

## Performance (app residente)

Gira accanto a una DAW per ore: il costo a riposo deve essere quasi nullo.

- Idle ≈ 0% CPU: niente busy-polling; timer/eventi al posto di loop
  d'attesa, intervalli larghi quanto la reattività percepita consente.
- Percorsi caldi (callback hook, drain del socket, matching): niente
  allocazioni evitabili né lavoro O(n) ripetuto per tasto/messaggio.
- Il matching resta reattivo su cataloghi da migliaia di preset; se una
  struttura dati non regge, dichiararlo nel report invece di subirlo.
- UI istantanea: il lavoro pesante fuori dal thread UI, risultati
  marshallati con `Dispatcher.UIThread`.

## Regole comuni

- Nomi che dicono cosa, commenti (pochi) che dicono perché.
- Funzioni corte, un livello di astrazione; 3 livelli di `if` annidati ≈
  manca un early-return.
- Costanti nominate al posto di numeri/stringhe magiche ripetute.
- Simmetria: se esistono `Start`/`Stop`, `Hook`/`Unhook`, ogni nuova
  risorsa segue lo stesso schema.
- Degradazione con grazia: mai crashare la sessione di Live dell'utente;
  ogni fallimento (Live chiuso, socket caduto, script assente o vecchio,
  config corrotta) ha un esito visibile e recuperabile, mai un crash
  silenzioso.
