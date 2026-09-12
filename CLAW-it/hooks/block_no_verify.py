"""Hook PreToolUse: gli hook di git non si saltano.

Blocca `--no-verify`, il suo `-n` su `commit` (anche dentro un gruppo come
`-an`) e ogni ritocco di `core.hooksPath`. Un comando che non nomina `git`
passa senza analisi.

Hook chiuso: input illeggibile, virgolette non chiuse in un comando con `git`,
qualunque errore → exit 2.

Exit: 0 lascia passare, 2 blocca col motivo su stderr.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

NAME = "block_no_verify"

# Un comando dentro un argomento (`bash -c "git ..."`) si rianalizza; oltre
# questo livello di annidamento si blocca invece di smettere di guardare.
MAX_DEPTH = 3

# Opzioni globali di git il cui valore sta nel token dopo: quel token non è
# il sottocomando.
GLOBAL_WITH_VALUE = frozenset(
    {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}
)

# Opzioni di `commit` il cui valore sta nel token dopo: il valore è testo, e un
# messaggio `-m "-n"` non è un `-n`.
COMMIT_WITH_VALUE = frozenset(
    {
        "-m",
        "--message",
        "-F",
        "--file",
        "-C",
        "--reuse-message",
        "-c",
        "--reedit-message",
        "--author",
        "--date",
        "-t",
        "--template",
        "--fixup",
        "--squash",
        "--pathspec-from-file",
    }
)

# Opzioni corte di `commit` che prendono un valore: in un gruppo come `-mn` il
# resto del gruppo è il valore, e la `n` è testo.
COMMIT_SHORT_WITH_VALUE = frozenset("mFCct")

# Opzioni corte di `commit` col valore facoltativo, solo attaccato: `-uno` e
# `-S<chiave>` non contengono un `-n`. Non prendono il token dopo, e metterle
# nell'insieme sopra farebbe passare `-u -n`.
COMMIT_SHORT_OPTIONAL_VALUE = frozenset("uS")


def verdict(data: object) -> str | None:
    """Il motivo del blocco, o `None` se il comando passa."""
    if not isinstance(data, dict) or not isinstance(data.get("tool_input"), dict):
        raise ValueError("tool_input assente o non è un oggetto")
    command = data["tool_input"].get("command")
    if not isinstance(command, str):
        raise ValueError("command assente o non è una stringa")
    if "git" not in command.lower():
        return None
    return _scan(command, posix=data.get("tool_name") != "PowerShell", depth=0)


def _scan(command: str, posix: bool, depth: int) -> str | None:
    if depth > MAX_DEPTH:
        return f"comando con git annidato oltre {MAX_DEPTH} livelli"
    tokens = _tokens(command, posix)
    values: set[int] = set()
    for i, (tok, punct) in enumerate(tokens):
        if punct or i in values:
            continue
        # Su ogni token, non solo dopo `git`: la configurazione arriva anche da
        # una variabile d'ambiente (`GIT_CONFIG_KEY_0=core.hooksPath git ...`)
        # o da un alias (`-c alias.ci="commit --no-verify"`).
        low = tok.lower()
        if "core.hookspath" in low:
            return f"{tok}: core.hooksPath non si ritocca"
        if any(_is_no_verify(part) for part in low.split()):
            return f"{tok}: --no-verify"
        if _is_git(tok):
            end = next((j for j in range(i + 1, len(tokens)) if tokens[j][1]), len(tokens))
            reason, taken = _git_args([t for t, _ in tokens[i + 1 : end]])
            if reason:
                return reason
            values.update(i + 1 + k for k in taken)
        elif re.search(r"\s", tok) and "git" in tok.lower():
            reason = _scan(tok, posix, depth + 1)
            if reason:
                return reason
    return None


def _tokens(command: str, posix: bool) -> list[tuple[str, bool]]:
    """`(token, è punteggiatura)`. PowerShell non è POSIX: `\\` è un separatore
    di percorso, non un escape, e le virgolette restano nel token."""
    lex = shlex.shlex(command, posix=posix, punctuation_chars=True)
    lex.whitespace_split = True
    out = []
    for tok in lex:
        punct = tok != "" and all(c in lex.punctuation_chars for c in tok)
        if not posix and len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
            tok = tok[1:-1]
        out.append((tok, punct))
    return out


def _is_git(tok: str) -> bool:
    name = re.split(r"[\\/]", tok)[-1].strip("`").lower()
    return name in ("git", "git.exe")


def _is_no_verify(arg: str) -> bool:
    # git accetta un'opzione lunga abbreviata finché è univoca: `--no-veri` è
    # già `--no-verify`, `--no-ver` è ambiguo con `--no-verbose`.
    return len(arg) >= len("--no-veri") and "--no-verify".startswith(arg)


def _git_args(args: list[str]) -> tuple[str | None, set[int]]:
    """`(motivo, indici dei valori di opzione)` per gli argomenti di un `git`.

    Gli indici restituiti sono testo — il messaggio di un commit — e chi
    chiama non li rianalizza. Ci si ferma al primo `git` che non è il valore
    di un'opzione: lì comincia un altro comando, che chi chiama analizza per
    conto suo. Un `git` valore (`-m git`) non chiude niente.
    """
    values: set[int] = set()
    sub = None
    global_value = False
    k = 0
    while k < len(args):
        arg = args[k]
        low = arg.lower()
        if "core.hookspath" in low:
            return f"git {arg}: core.hooksPath non si ritocca", values
        if sub is None:
            if global_value:
                global_value = False
            elif _is_git(arg):
                break
            elif arg in GLOBAL_WITH_VALUE:
                global_value = True
            elif not arg.startswith("-"):
                sub = low
            k += 1
            continue
        if arg == "--" or _is_git(arg):
            break
        if _is_no_verify(low):
            return f"git {sub} {arg}", values
        if sub == "commit":
            if arg in COMMIT_WITH_VALUE:
                values.add(k + 1)
                k += 2
                continue
            if arg.startswith("-") and not arg.startswith("--"):
                for pos, flag in enumerate(arg[1:]):
                    if flag == "n":
                        return f"git commit {arg}: -n è --no-verify", values
                    if flag in COMMIT_SHORT_WITH_VALUE:
                        if pos == len(arg) - 2:
                            values.add(k + 1)
                            k += 1
                        break
                    if flag in COMMIT_SHORT_OPTIONAL_VALUE:
                        break
        k += 1
    return None, values


def _say(text: str) -> None:
    # Un motivo che non si riesce a stampare non cambia l'esito: l'exit code
    # lo decide il chiamante, e deve arrivare anche con stderr rotto.
    try:
        sys.stderr.write(text + "\n")
        sys.stderr.flush()
    except BaseException:
        pass


def main() -> None:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        found = verdict(data)
        reason = (
            f"{NAME}: {found}. Gli hook di git non si saltano: correggi ciò che "
            "segnalano; se aggirarli è voluto, lo fa l'utente."
            if found
            else None
        )
    except BaseException as exc:
        reason = f"{NAME}: input illeggibile o errore interno ({exc!r}), blocco"
    if reason:
        _say(reason)
    # os._exit e non sys.exit: un flush fallito all'uscita cambierebbe il
    # codice in 120, cioè in «lascia passare».
    os._exit(2 if reason else 0)


if __name__ == "__main__":
    main()
