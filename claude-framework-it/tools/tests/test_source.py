import json
import tempfile
import unittest
from pathlib import Path

from fwbuild import source

FRAMEWORK = Path(__file__).resolve().parents[1]


def make_root(base: Path, *, drop: str = "") -> Path:
    """Una root di framework finta: le voci obbligatorie, meno quella indicata.

    Root fittizie e non quella vera: la ricerca deve essere provabile senza
    dipendere da dove sta installato il framework che esegue i test.
    """
    for entry in source.REQUIRED:
        if entry == drop:
            continue
        if entry == "VERSION":
            base.mkdir(parents=True, exist_ok=True)
            (base / entry).write_text("9.9.9\n", encoding="utf-8")
        else:
            (base / entry).mkdir(parents=True, exist_ok=True)
    return base


class TestMissing(unittest.TestCase):
    def test_real_framework_is_a_valid_root(self):
        self.assertEqual(source.missing(FRAMEWORK.parent), [])

    def test_reports_what_is_absent(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "monco", drop="profiles")
            self.assertEqual(source.missing(root), ["profiles"])

    def test_unrelated_directory_is_not_a_framework(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(source.missing(Path(d)), list(source.REQUIRED))


class TestResolve(unittest.TestCase):
    def test_finds_root_passed_directly(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "fw")
            self.assertEqual(source.resolve([root]), root)

    def test_finds_framework_subdirectory(self):
        """Sorgente copiato dentro il progetto: si passa la root del progetto."""
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "framework")
            self.assertEqual(source.resolve([Path(d)]), root)

    def test_first_valid_candidate_wins(self):
        with tempfile.TemporaryDirectory() as d:
            master = make_root(Path(d) / "master")
            self.assertEqual(source.resolve([Path(d) / "vuoto", master]), master)

    def test_single_invalid_candidate_raises(self):
        """La regola «percorso indicato ma invalido: errore, nessun fallback»
        non è un caso speciale del risolutore: è il chiamante che passa un
        candidato solo. Un fallback silenzioso maschera un percorso sbagliato."""
        with tempfile.TemporaryDirectory() as d:
            make_root(Path(d) / "altrove")
            with self.assertRaises(LookupError):
                source.resolve([Path(d) / "sbagliato"])

    def test_error_names_what_is_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "monco", drop="agents")
            with self.assertRaises(LookupError) as e:
                source.resolve([root])
            self.assertIn("agents", str(e.exception))


class TestManifest(unittest.TestCase):
    def test_manifest_carries_source_version_and_profile(self):
        """Il profilo è il campo che mancava: senza, un'installazione non sa
        più di cosa è fatta e i permessi non si possono rigenerare."""
        with tempfile.TemporaryDirectory() as d:
            prj = Path(d) / "prj"
            fw = prj / "framework"
            fw.mkdir(parents=True)
            m = source.manifest(prj, fw, "1.2.3", "software")
            self.assertEqual(
                m, {"source": "framework", "version": "1.2.3", "profile": "software"}
            )

    def test_read_manifest_is_none_when_absent_or_broken(self):
        with tempfile.TemporaryDirectory() as d:
            prj = Path(d)
            self.assertIsNone(source.read_manifest(prj))
            (prj / ".claude").mkdir()
            (prj / ".claude" / "framework.json").write_text("{", encoding="utf-8")
            self.assertIsNone(source.read_manifest(prj))

    def test_accepted_keeps_entries_without_a_reason(self):
        """Scartarle qui le farebbe sparire in silenzio: chi le confronta coi
        rilievi deve poterle segnalare."""
        with tempfile.TemporaryDirectory() as d:
            prj = Path(d)
            (prj / ".claude").mkdir()
            (prj / ".claude" / "framework.json").write_text(
                json.dumps({"accepted": {"A": "ragione", "B": "  ", "C": 3}}),
                encoding="utf-8",
            )
            self.assertEqual(
                source.accepted(prj), {"A": "ragione", "B": "", "C": ""}
            )


if __name__ == "__main__":
    unittest.main()
