# Guida all'architettura — {{PROGETTO}}

Topologia: [DA COMPILARE — componenti e come comunicano, in 1-2 righe].

## Confini e responsabilità

[DA COMPILARE] — un bullet per modulo: responsabilità + cosa NON può
dipendere da cosa (es. core = logica pura, nessuna dipendenza UI/piattaforma;
app = tutto ciò che tocca utente/OS; componenti in altri processi/host =
versionati indipendentemente, versione da incrementare a ogni cambio di
contratto).

Regola pratica (se il progetto separa core/app): una classe nel modulo
applicativo che non usa né UI né API di piattaforma probabilmente va nel
core.

## I contratti (cambiarli = decisione architetturale)

[DA COMPILARE] — i contratti REALI del progetto nelle 4 classi:

1. **Protocolli tra componenti** (IPC, rete, API): cambio coordinato di
   tutti i lati, versione incrementata, gestito il caso "lato vecchio con
   lato nuovo".
2. **Formati persistiti** (config, dati utente): le nuove versioni leggono
   i dati vecchi (default per campi mancanti, mai rename senza
   compatibilità di lettura).
3. **Formati rigenerabili** (cache, indici): una rigenerazione forzata a
   ogni update è un costo per l'utente — segnalare quando un cambio la
   impone.
4. **Struttura di installazione/deploy** (path noti, layout): impatta
   build e installer.

Input da altri processi (socket, pipe, file condivisi) = confine di
fiducia: un comando ricevuto non può fare più di ciò che l'UI stessa
consente; payload validati (lunghezze, campi, range).

## Decisioni vincolanti già prese

[DA COMPILARE] — decisioni che nessun task ribalta senza mandato esplicito
(es. cross-platform: niente API di piattaforma nel core; superficie
sensibile minima: vince l'alternativa meno invasiva anche se meno elegante;
runtime embedded senza dipendenze esterne).

## Valutare una proposta di design (per l'architect)

1. Quali contratti tocca? (nessuno = rischio molto più basso)
2. Cosa succede agli utenti esistenti al primo avvio dopo l'update?
3. Degrada con grazia se le dipendenze esterne mancano o cambiano versione?
4. Aggiunge superficie sensibile o permessi nuovi?
5. Complica la portabilità?
6. Qual è l'alternativa più semplice che risolve il 90% del problema? (KISS)
