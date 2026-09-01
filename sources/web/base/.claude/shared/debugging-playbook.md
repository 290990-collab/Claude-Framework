# Playbook di debug — Portfolio

**Si diagnostica con le evidenze, non con la memoria del modello.** Il debugger
dedicato non esiste in questo framework: questa disciplina la applica
l'`implementer` prima di scrivere un fix.

## Metodo in 6 passi

1. **Fissa il sintomo**: cosa succede vs cosa dovrebbe, da quando (commit? update
   di dipendenze/Next.js?), con che frequenza — "a volte" ≈ quasi sempre timing o
   stato condiviso, oppure differenza server/client.
2. **Fatti prima delle teorie**: console del browser, output del build/dev server,
   `git log` recente, diff dall'ultima versione funzionante. Vietato proporre fix
   in questo passo.
3. **Almeno DUE ipotesi**: per ciascuna cosa la conferma, cosa la falsifica, come
   discriminarle al minor costo. Una sola ipotesi = non hai pensato abbastanza.
4. **Falsifica**: cerca di smontare la favorita; la diagnosi vale solo se spiega
   TUTTI i sintomi (anche "perché solo a volte" e "perché da quella versione").
5. **Fix minimo sulla causa** (non sul sintomo), con i rischi di regressione.
6. **Definisci la verifica**: come si dimostra che il fix funziona e non ha rotto
   altro (a runtime per l'UI, con un test per la logica).

Anti-pattern vietati: fix a tentativi ("proviamo un try/catch"); curare il sintomo
invece della causa; "risolto" perché un bug intermittente non si è ripresentato;
report altrui presi come evidenza.

## Mappa dei sospetti per sintomo

| Sintomo | Primi sospetti |
|---|---|
| "Hydration mismatch" / errore solo in produzione | Contenuto che differisce server/client (date, random, `window`), Server vs Client Component |
| Un progetto non compare o compare sbagliato | Frontmatter/schema non valido, filtro categoria/tag, parsing dei contenuti, cache di build |
| Layout shift (CLS) / salto al caricamento | Immagine senza dimensioni, font senza `next/font`, animazione che sposta il layout |
| Immagine non si carica | `next/image` `remotePatterns` non include l'host, path errato, asset mancante in `public/` |
| Stile incoerente / token non applicato | Valore hardcoded invece del token, chiave token rinominata, ordine/specificità CSS |
| Animazione non parte o "scatta" | `prefers-reduced-motion`, Client Component mancante, durata/easing errati, re-render |
| Link rotto / 404 dopo un cambio | Slug cambiato senza redirect, rotta App Router spostata, riferimento per stringa non aggiornato |
| Errore solo dopo il deploy | Variabile d'ambiente mancante, differenza build vs dev, `NEXT_PUBLIC_*` assente |
| Form di contatto non funziona | Validazione al confine, secret/env mancante, host del servizio non su allowlist, CORS |

## Strumenti

- `git log --oneline -20`, `git diff <ultimo-buono>..HEAD` per delimitare.
- Console e Network del browser (client); output di `pnpm dev`/`pnpm build` (server/build).
- React DevTools per re-render e boundary Server/Client.
- Per race async: cercare lo stato condiviso leggendo il codice, non sperare di
  riprodurre la race al primo colpo.

## Quando fermarsi

Se dopo un'indagine seria l'evidenza non discrimina tra le ipotesi, il deliverable
è: ipotesi rimaste + evidenza mancante + strumentazione (log mirati) da aggiungere
per decidere. Esito legittimo; una certezza inventata no.
