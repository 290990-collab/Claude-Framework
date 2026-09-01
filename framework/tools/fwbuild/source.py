"""Trovare e validare la root del sorgente.

Un prodotto scaricabile non può cablare il percorso di una macchina: si cerca in
ordine e si valida prima di scrivere. La ricerca è **pura** — i candidati li
assembla il chiamante — perché è l'unico modo di provarla senza dipendere da
dove sta il framework che esegue i test.
"""

from collections.abc import Sequence
from pathlib import Path

# Ciò senza cui l'installazione non può nemmeno cominciare.
REQUIRED = (
    "VERSION",
    "method",
    "coordinator",
    "agents",
    "profiles",
    "templates",
    "skills",
    "tools/fwbuild",
)


def missing(root: Path) -> list[str]:
    """Le voci obbligatorie assenti. Vuoto = è una root di framework."""
    return [r for r in REQUIRED if not (Path(root) / r).exists()]


def resolve(bases: Sequence[Path]) -> Path:
    """La prima root valida, provando `<base>` e poi `<base>/framework`.

    Le due forme — sorgente copiato nel progetto e master unico — sono coperte
    dalla stessa prova, senza una regola in più.

    «Percorso indicato ma invalido: errore, nessun fallback» non è un caso
    speciale qui dentro: è il chiamante che, avendone uno, passa un candidato
    solo. Un fallback silenzioso maschera un percorso sbagliato.
    """
    tried = []
    for base in bases:
        for cand in (Path(base), Path(base) / "framework"):
            gaps = missing(cand)
            if not gaps:
                return cand
            tried.append(
                f"{cand}: "
                + ("assente" if not cand.is_dir() else f"manca {', '.join(gaps)}")
            )
    raise LookupError("nessun sorgente valido fra:\n  " + "\n  ".join(tried))
