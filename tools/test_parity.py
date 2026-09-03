"""Guardia strutturale fra `claude-framework-it/` e `claude-framework-eng/`.

Vive **fuori** da entrambi: un test dentro una copia che cita la traduzione
romperebbe l'autosufficienza della cartella, che è la prima proprietà del
sorgente.

**Cosa può e cosa non può.** Non verifica che la traduzione sia fedele — nessun
test lo può fare. Verifica che le due copie abbiano la **stessa forma**: gli
stessi file, gli stessi agenti, gli stessi profili con la stessa meccanica, la
stessa versione, lo stesso numero di test. È il drift strutturale, cioè quello
che si produce aggiungendo qualcosa da una parte sola — ed è esattamente il
difetto che `framework-sync` esiste per evitare fra progetti, qui applicato
fra lingue.

    cd tools && python -m unittest test_parity -v
"""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IT = ROOT / "claude-framework-it"
EN = ROOT / "claude-framework-eng"

SKIP_DIRS = {"__pycache__", ".pytest_cache"}
# I marker di segnaposto: ognuno deve stare **solo** nella sua copia. Un
# `[DA COMPILARE]` rimasto nella traduzione è una porzione non tradotta, e il
# doctor inglese non lo riconoscerebbe nemmeno come segnaposto.
MARKERS = ((IT, "TO FILL IN", "DA COMPILARE"), (EN, "DA COMPILARE", "TO FILL IN"))
TEST_DEF = re.compile(r"^\s*def (test_\w+)", re.MULTILINE)
# I campi di un profilo che hanno una conseguenza meccanica. `name` e
# `description` no, e `critical_surface` è prosa tradotta: sono i tre che
# devono poter differire.
MECHANICAL = ("agents", "cycles", "shared", "settings")


def files(root: Path) -> set[str]:
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(root).parts)
    }


def names(root: Path, rel: str, suffix: str) -> set[str]:
    return {p.stem for p in (root / rel).glob(f"*{suffix}")}


class TestParity(unittest.TestCase):
    def test_both_copies_exist(self):
        self.assertTrue(IT.is_dir(), "claude-framework-it/ assente")
        self.assertTrue(EN.is_dir(), "claude-framework-eng/ assente")

    def test_same_file_tree(self):
        """Un file aggiunto da una parte sola è il primo passo della
        biforcazione, e non lo vede nessuna delle due suite."""
        self.assertEqual(files(IT), files(EN))

    def test_same_version(self):
        a = (IT / "VERSION").read_text(encoding="utf-8").strip()
        b = (EN / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(a, b, "le due copie dichiarano versioni diverse")

    def test_same_agent_roster(self):
        self.assertEqual(names(IT, "agents", ".md"), names(EN, "agents", ".md"))

    def test_same_profiles_and_cycles(self):
        self.assertEqual(names(IT, "profiles", ".toml"), names(EN, "profiles", ".toml"))
        self.assertEqual(names(IT, "cycles", ".md"), names(EN, "cycles", ".md"))

    def test_profiles_differ_only_in_prose(self):
        """Un profilo è una configurazione, non un testo: se la traduzione
        cambia un roster o una guida, i due framework installano progetti
        diversi a parità di risposta al questionario."""
        for p in sorted((IT / "profiles").glob("*.toml")):
            a = tomllib.loads(p.read_text(encoding="utf-8"))
            b = tomllib.loads((EN / "profiles" / p.name).read_text(encoding="utf-8"))
            for field in MECHANICAL:
                with self.subTest(profile=p.stem, field=field):
                    self.assertEqual(a.get(field), b.get(field))

    def test_agent_frontmatter_matches(self):
        """`model`, `effort` e `tools` sono configurazione: tradurli o
        ritoccarli cambierebbe il costo di uno spawn, non la sua lingua."""
        keys = ("name", "model", "effort", "tools", "color")
        for p in sorted((IT / "agents").glob("*.md")):
            a = _frontmatter(p, keys)
            b = _frontmatter(EN / "agents" / p.name, keys)
            with self.subTest(agent=p.stem):
                self.assertEqual(a, b)

    def test_placeholder_markers_do_not_cross_over(self):
        """Il marker della copia sbagliata segnala una porzione non tradotta —
        e il doctor dell'altra lingua non la riconoscerebbe come segnaposto."""
        for root, forbidden, own in MARKERS:
            for p in sorted(root.rglob("*.md")):
                if SKIP_DIRS & set(p.relative_to(root).parts):
                    continue
                text = p.read_text(encoding="utf-8")
                with self.subTest(file=p.relative_to(ROOT).as_posix()):
                    self.assertNotIn(forbidden, text, f"atteso {own}")

    def test_same_tests_per_file(self):
        """Le due suite devono dare lo stesso numero: un test aggiunto da una
        parte sola è una regola che vale solo per metà del prodotto."""
        for p in sorted((IT / "tools" / "tests").glob("test_*.py")):
            a = TEST_DEF.findall(p.read_text(encoding="utf-8"))
            b = TEST_DEF.findall(
                (EN / "tools" / "tests" / p.name).read_text(encoding="utf-8")
            )
            with self.subTest(file=p.name):
                self.assertEqual(sorted(a), sorted(b))


def _frontmatter(path: Path, keys) -> dict:
    """I campi del frontmatter di un agente, senza dipendere da un parser YAML.

    Solo chiavi scalari su una riga: `description` è multilinea e va esclusa —
    è prosa, ed è la parte che la traduzione deve poter cambiare.

    Il nome della chiave ammette le maiuscole perché la piattaforma ne ha
    (`disallowedTools`, `permissionMode`, `maxTurns`): con `[a-z]+` una chiave
    così non veniva letta, e due copie che divergono su di essa passavano.
    """
    out = {}
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.strip() == "---" and out:
            break
        m = re.match(r"^([a-zA-Z]+):\s*(.+)$", line)
        if m and m.group(1) in keys:
            out[m.group(1)] = m.group(2).strip()
    return out


if __name__ == "__main__":
    unittest.main()
