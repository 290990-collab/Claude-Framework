"""Hook PreToolUse: non si modifica la configurazione di un linter che esiste già.

Un agente che non riesce a far passare un controllo tende a indebolire la
regola invece di correggere il codice. Creare una configurazione nuova resta
lecito: non c'è nulla da indebolire.

Hook chiuso: input illeggibile, campo mancante, qualunque errore → exit 2.
Un controllo che cede in silenzio su un input strano è un controllo spento
senza che nessuno lo sappia.

Exit: 0 lascia passare, 2 blocca col motivo su stderr.
"""

from __future__ import annotations

import json
import os
import sys

NAME = "config_protection"

# Minuscoli: il confronto è sul nome in minuscolo, perché su un filesystem che
# non distingue le maiuscole `.ESLINTRC.JSON` è lo stesso file.
PROTECTED = frozenset(
    {
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.cjs",
        ".eslintrc.json",
        ".eslintrc.yml",
        ".eslintrc.yaml",
        "eslint.config.js",
        "eslint.config.mjs",
        "eslint.config.cjs",
        "eslint.config.ts",
        "eslint.config.mts",
        "eslint.config.cts",
        ".prettierrc",
        ".prettierrc.js",
        ".prettierrc.cjs",
        ".prettierrc.json",
        ".prettierrc.yml",
        ".prettierrc.yaml",
        "prettier.config.js",
        "prettier.config.cjs",
        "prettier.config.mjs",
        "biome.json",
        "biome.jsonc",
        ".ruff.toml",
        "ruff.toml",
        ".shellcheckrc",
        ".stylelintrc",
        ".stylelintrc.json",
        ".stylelintrc.yml",
        ".markdownlint.json",
        ".markdownlint.yaml",
        ".markdownlintrc",
        ".flake8",
        ".pylintrc",
        "pylintrc",
        "mypy.ini",
        ".mypy.ini",
    }
)


def verdict(data: object) -> str | None:
    """Il motivo del blocco, o `None` se l'operazione passa.

    `pyproject.toml` non c'è apposta: porta anche metadati e dipendenze, e
    bloccarlo fermerebbe modifiche legittime.
    """
    if not isinstance(data, dict) or not isinstance(data.get("tool_input"), dict):
        raise ValueError("tool_input assente o non è un oggetto")
    path = data["tool_input"].get("file_path")
    if not isinstance(path, str) or not path:
        raise ValueError("file_path assente o non è una stringa")
    name = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
    if name not in PROTECTED:
        return None
    if not os.path.isabs(path):
        cwd = data.get("cwd")
        if not isinstance(cwd, str) or not cwd:
            raise ValueError("file_path relativo e cwd assente")
        path = os.path.join(cwd, path)
    try:
        # lstat e non exists: un link rotto è comunque una configurazione
        # presente, e ogni errore diverso da «non c'è» la tratta da presente.
        os.lstat(path)
    except FileNotFoundError:
        return None
    return (
        f"{NAME}: {name} esiste già ed è la configurazione di un linter o di "
        "un formatter. Correggi il codice perché rispetti la regola invece di "
        "indebolirla; se la modifica alla configurazione è voluta, chiedila "
        "all'utente."
    )


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
        reason = verdict(data)
    except BaseException as exc:
        reason = f"{NAME}: input illeggibile o errore interno ({exc!r}), blocco"
    if reason:
        _say(reason)
    # os._exit e non sys.exit: un flush fallito all'uscita cambierebbe il
    # codice in 120, cioè in «lascia passare».
    os._exit(2 if reason else 0)


if __name__ == "__main__":
    main()
