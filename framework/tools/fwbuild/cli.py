"""Entrypoint: python -m fwbuild <comando>."""

import argparse
import os
import sys
from pathlib import Path

from . import doctor, source


def _force_utf8_stdout() -> None:
    """Su Windows lo stdout di Python usa la codepage locale (cp1252), che non
    copre tutti i caratteri dei messaggi. Senza questo, un rilievo con un
    carattere fuori tabella fa fallire il comando invece di stamparlo."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def _bases(path: Path | None) -> list[Path]:
    """L'ordine di ricerca del sorgente. È la parte impura, e sta qui apposta.

    Un percorso indicato è l'**unico** candidato: se non regge è un errore, non
    un fallback sul successivo.
    """
    if path is not None:
        return [path]
    env = os.environ.get("CLAUDE_FRAMEWORK")
    return [
        Path.cwd(),
        *([Path(env)] if env else []),
        Path.home() / ".claude" / "framework",
    ]


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(prog="fwbuild")
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("doctor", help="verifica un'installazione")
    d.add_argument("path", type=Path)
    # Un'installazione completa non ha rilievi di nessuna gravità:
    # --strict è quella regola resa meccanica, per la CI e per il Passo 6.
    d.add_argument("--strict", action="store_true", help="uscita 1 anche con soli avvisi")

    s = sub.add_parser("source", help="risolve e valida la root del sorgente")
    s.add_argument("path", type=Path, nargs="?")

    args = parser.parse_args(argv)

    if args.command == "source":
        try:
            root = source.resolve(_bases(args.path))
        except LookupError as err:
            print(err)
            return 1
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        print(f"{root} v{version}")
        return 0

    if args.command == "doctor":
        findings = doctor.check(args.path)
        if not findings:
            print("OK — nessun rilievo")
            return 0
        for f in findings:
            print(f"{f.severity:5} {f.code:16} {f.message}")
        return 1 if args.strict or any(f.severity == "ERROR" for f in findings) else 0
    return 0
