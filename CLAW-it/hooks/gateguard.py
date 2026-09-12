"""Hook PreToolUse: il primo tocco di un file chiede i fatti prima della modifica.

La prima Edit, Write o MultiEdit su un file del progetto viene negata con
l'elenco dei fatti da raccogliere — chi importa il file, cosa cambia di
pubblico — e il secondo tentativo sullo stesso file passa. Chiedere
«sei sicuro?» ottiene sempre sì; chiedere chi importa il file costringe a
cercarlo.

Hook aperto: è un'abitudine, non una difesa. Un errore interno lascia passare
con un avviso su stderr invece di bloccare il lavoro, e l'unico blocco è il
primo tocco, registrato prima di negarlo: senza registrazione il secondo
tentativo verrebbe negato di nuovo, all'infinito.

Si spegne con `FRAMEWORK_GATEGUARD=off` (o `0`, `false`).

Exit: 0 lascia passare, 2 nega il primo tocco coi fatti su stderr.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile

NAME = "gateguard"

OFF = frozenset({"off", "0", "false"})

# I file di stato del framework si aggiornano a ogni passo del lavoro: chiedere
# chi li importa non ha senso.
STATE_FILES = ("TODO.md", "status.md", "roadmap.md")

STATE_DIR = "claw-gateguard"


def verdict(data: object) -> str | None:
    """I fatti da presentare al primo tocco, o `None` se l'operazione passa."""
    if os.environ.get("FRAMEWORK_GATEGUARD", "").strip().lower() in OFF:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("tool_input"), dict):
        raise ValueError("tool_input assente o non è un oggetto")
    file_path = data["tool_input"].get("file_path")
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("file_path assente o non è una stringa")
    session = data.get("session_id")
    if not isinstance(session, str) or not session:
        raise ValueError("session_id assente o non è una stringa")
    cwd = data.get("cwd")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    if not isinstance(root, str) or not root:
        raise ValueError("né CLAUDE_PROJECT_DIR né cwd")
    root = os.path.normcase(os.path.abspath(root))
    base = cwd if isinstance(cwd, str) and cwd else root
    path = os.path.normcase(os.path.abspath(os.path.join(base, file_path)))
    if not _inside(path, root):
        return None
    if path in {os.path.normcase(os.path.join(root, "docs", n)) for n in STATE_FILES}:
        return None

    state = os.path.join(
        tempfile.gettempdir(),
        STATE_DIR,
        hashlib.sha256(session.encode("utf-8")).hexdigest()[:16] + ".json",
    )
    seen = _load(state)
    if path in seen:
        return None
    creating = data.get("tool_name") == "Write" and not os.path.exists(path)
    _store(state, seen + [path])
    return _creation_facts(file_path) if creating else _edit_facts(file_path)


def _inside(path: str, root: str) -> bool:
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        # Unità diverse su Windows: il file è fuori dal progetto.
        return False


def _load(state: str) -> list[str]:
    if not os.path.exists(state):
        return []
    with open(state, encoding="utf-8") as f:
        seen = json.load(f)
    if not isinstance(seen, list) or not all(isinstance(p, str) for p in seen):
        raise ValueError(f"stato illeggibile: {state}")
    return seen


def _store(state: str, seen: list[str]) -> None:
    # os.replace: un altro hook della stessa sessione che legge in quel momento
    # trova il file vecchio o quello nuovo, mai uno scritto a metà.
    folder = os.path.dirname(state)
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(seen, f)
        os.replace(tmp, state)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _edit_facts(file_path: str) -> str:
    return (
        f"{NAME}: prima di modificare {file_path} presenta questi fatti, poi riprova.\n"
        "1. Quali file importano o richiamano questo file: cercali, non dedurli.\n"
        "2. Quali funzioni, classi o interfacce pubbliche cambiano con la modifica.\n"
        "3. Se il file legge o scrive dati, il loro formato: campi, struttura, "
        "date, con valori sintetici.\n"
        "4. L'istruzione dell'utente che motiva la modifica, citata alla lettera.\n"
        "Il secondo tentativo sullo stesso file passa."
    )


def _creation_facts(file_path: str) -> str:
    return (
        f"{NAME}: prima di creare {file_path} presenta questi fatti, poi riprova.\n"
        "1. Quale file, e a quale riga, chiamerà il file nuovo.\n"
        "2. Che nessun file esistente fa già la stessa cosa: cercalo, non dedurlo.\n"
        "Il secondo tentativo sullo stesso file passa."
    )


def _say(text: str) -> None:
    # Un avviso che non si riesce a stampare non cambia l'esito.
    try:
        sys.stderr.write(text + "\n")
        sys.stderr.flush()
    except BaseException:
        pass


def main() -> None:
    code = 0
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        facts = verdict(data)
    except BaseException as exc:
        _say(f"{NAME}: errore interno ({exc!r}), lascio passare senza controllo")
    else:
        if facts:
            _say(facts)
            code = 2
    os._exit(code)


if __name__ == "__main__":
    main()
