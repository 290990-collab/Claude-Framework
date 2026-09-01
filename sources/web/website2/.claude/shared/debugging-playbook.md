# Playbook di debug — FindShop

**Si diagnostica con le evidenze, non con la memoria del modello.**

## Metodo in 6 passi

1. **Fissa il sintomo**: cosa succede vs cosa dovrebbe, da quando (commit?
   update di dipendenze/OS?), con che frequenza — "a volte" ≈ quasi sempre
   timing o stato condiviso.
2. **Fatti prima delle teorie**: log dell'app, `git log` recente, diff
   dall'ultima versione funzionante nota. Vietato proporre fix in questo
   passo.
3. **Almeno DUE ipotesi**: per ciascuna cosa la conferma, cosa la
   falsifica, come discriminarle al minor costo. Una sola ipotesi = non hai
   ancora pensato abbastanza.
4. **Falsifica**: cerca di smontare la favorita; la diagnosi vale solo se
   spiega TUTTI i sintomi (anche il "perché solo a volte" e il "perché da
   quella versione").
5. **Fix minimo sulla causa** (non sul sintomo), con i rischi di
   regressione. Lo applica l'implementer.
6. **Definisci la verifica**: come si dimostra che il fix funziona e non ha
   rotto altro.

Anti-pattern vietati: fix a tentativi ("proviamo un try/catch"); curare il
sintomo (sopprimere l'eccezione) invece della causa; "risolto" perché un
bug intermittente non si è ripresentato dopo un run; report altrui presi
come evidenza.

## Mappa dei sospetti per sintomo

Tabella `sintomo → primi sospetti`, da far crescere a ogni bug risolto:

| Sintomo | Primi sospetti |
|---|---|
| Ricerca non trova un capo che esiste | Indicizzazione mancante/parziale, normalizzazione nome, filtro geo troppo stretto, facet errata |
| Risultati geo sbagliati o vuoti | Coordinate/SRID errati in PostGIS o nell'indice, raggio, lat/lon invertite |
| Prezzi o valute errati | Normalizzazione prezzi (centesimi vs float), valuta assente, dati adapter sporchi |
| Dati negozio non aggiornati | Pipeline di ingestion ferma o adapter in errore, sync verso Typesense non eseguita |
| Errori intermittenti sotto carico | Promise non attese, race su stato condiviso, pool di connessioni DB esaurito |
| Comportamento diverso dopo deploy | Migrazione non applicata, schema indice cambiato senza reindex, env/config |
| Errore solo su un client (web o mobile) | API versione disallineata, app mobile non aggiornata, differenze di piattaforma |

## Strumenti

- `git log --oneline -20`, `git diff <ultimo-buono>..HEAD` per delimitare.
- Log dell'app (meccanismo esistente; se manca nel punto critico, il fix
  proposto include log mirati).
- Log strutturati di API e worker di ingestion (aggregatore/observability);
  log del client web (console/telemetria) e mobile (device/crash reporting);
  stato dei job di ingestion e degli errori per adapter.
- Race di concorrenza (async/eventi): cercare lo stato condiviso leggendo il
  codice, non sperare di riprodurre la race al primo colpo.

## Diagnosabilità by design (proattiva)

I bug peggiori (timing, ambiente, "va in debug non in release") girano
sulla macchina dell'utente e qui non si riproducono: il codice nuovo a
rischio nasce già osservabile, non lo si strumenta dopo.

- Ogni percorso rischioso nuovo (I/O esterno, IPC, migrazioni di dati)
  emette il log/contatore che ne permetterebbe la diagnosi a posteriori
  dai log disponibili — senza dati sensibili.
- Deve esistere (o si aggiunge) un modo per l'utente di produrre un bundle
  diagnostico: nessun bug remoto si chiude senza evidenza raccoglibile.

## Quando fermarsi

Se dopo un'indagine seria l'evidenza non discrimina tra le ipotesi, il
deliverable è: ipotesi rimaste + evidenza mancante + strumentazione
(log/contatori) da aggiungere per decidere. Esito legittimo; una certezza
inventata no.
