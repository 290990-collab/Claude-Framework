"""Portare una release nuova sopra un sorgente che l'utente ha modificato.

`--up` esiste perché il sorgente si modifica: chi lo fa, alla release
successiva, ha davanti una scelta secca — sovrascrivere e perdere il proprio
lavoro, o restare indietro per sempre. Per evitarla serve un dato solo:
**da quale release quella copia veniva**. Il numero in `VERSION` non basta,
perché `--up` lo incrementa e da quel momento non corrisponde più a niente di
pubblicato.

Il confronto è a tre alberi e la classificazione ha quattro esiti, non di più:
sono le sole combinazioni possibili, e trattano una cancellazione come una
modifica qualsiasi (un file assente è un contenuto come gli altri).
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

RECORD = "upstream.json"

# Non sono contenuto del framework: comparirebbero come «aggiunte tue» a ogni
# confronto, e il rumore si impara a ignorare.
SKIP = {"__pycache__", ".git", ".pytest_cache"}


@dataclass(frozen=True)
class Plan:
    """Cosa fare, percorso per percorso, relativo alla root di ogni albero."""

    theirs: list[str] = field(default_factory=list)
    yours: list[str] = field(default_factory=list)
    same: list[str] = field(default_factory=list)
    conflict: list[str] = field(default_factory=list)


def read_record(root: Path) -> dict | None:
    """Il record del sorgente, o `None` se assente o illeggibile.

    Le due cose non si distinguono: per chi aggiorna sono lo stesso guasto,
    cioè nessuna base dichiarata, e la risposta è la stessa.
    """
    try:
        data = json.loads((Path(root) / RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def write_record(root: Path, base: str, edition: str, repo: str) -> dict:
    """Scrive il record. Chi chiama decide *quando*: al primo `--up` porta la
    release da cui si partiva, dopo un aggiornamento quella appena presa."""
    data = {"base": base, "edition": edition, "repo": repo}
    (Path(root) / RECORD).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return data


def base_version(root: Path) -> str:
    """La release da cui confrontare.

    Senza record si ricade su `VERSION`, e la ricaduta è **corretta** proprio nel
    caso in cui il record manca: nessun `--up` è mai stato fatto, quindi `VERSION`
    è ancora un numero pubblicato.
    """
    record = read_record(root)
    if record and isinstance(record.get("base"), str) and record["base"].strip():
        return record["base"].strip()
    return (Path(root) / "VERSION").read_text(encoding="utf-8").strip()


def _digest(path: Path) -> str | None:
    """L'impronta di un file, o `None` se non c'è. L'assenza è un contenuto:
    è ciò che fa classificare una cancellazione senza un ramo in più."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _paths(root: Path) -> set[str]:
    root = Path(root)
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not SKIP & set(p.parts)
    }


def classify(base: Path, yours: Path, theirs: Path) -> Plan:
    """I tre alberi confrontati percorso per percorso.

    `yours` è il sorgente che l'utente usa, `theirs` la release nuova, `base`
    quella da cui `yours` era partito. Non si scrive niente: applicare è una
    decisione, e le decisioni non le prende il tooling.
    """
    base, yours, theirs = Path(base), Path(yours), Path(theirs)
    plan = Plan()
    for rel in sorted(_paths(base) | _paths(yours) | _paths(theirs)):
        b = _digest(base / rel)
        y = _digest(yours / rel)
        t = _digest(theirs / rel)
        if y == t:
            plan.same.append(rel)
        elif y == b:
            plan.theirs.append(rel)
        elif t == b:
            plan.yours.append(rel)
        else:
            plan.conflict.append(rel)
    return plan
