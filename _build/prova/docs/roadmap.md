# Roadmap

Il **cosa** e il **come**: obiettivi, in che ordine e perché in quell'ordine. Lo
stato di avanzamento non sta qui — sta in [TODO.md](TODO.md).

> Ordinata per **dipendenza**, non per priorità percepita: ciò che sblocca altro
> viene prima. Un obiettivo senza criterio di completamento non è un obiettivo.

## Obiettivi

### 1. Follow affidabile su file ruotato

**Perché:** è la regressione che rende `logtail -f` inservibile in produzione, e
blocca ogni lavoro sui filtri incrementali.
**Fatto quando:** `tests/test_follow.py` copre rotazione, troncamento e
ricreazione del file, e passa su `fixtures/big.log` a memoria costante.
**Dipende da:** —
**Rischi:** il comportamento della rotazione dipende dal filesystem — va provato
anche su volume di rete.

## Fuori ambito, di proposito

<Cose che potrebbero sembrare parte del progetto e non lo sono, con la ragione.
Serve a non ridiscuterle ogni volta.>
