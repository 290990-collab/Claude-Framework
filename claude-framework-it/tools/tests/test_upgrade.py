import tempfile
import unittest
from pathlib import Path

from fwbuild import upgrade


def tree(root: Path, files: dict[str, str]) -> Path:
    """Un albero finto: percorso relativo → contenuto. Assente = non c'è."""
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


class TestClassify(unittest.TestCase):
    def _plan(self, base, yours, theirs):
        d = Path(self.enterContext(tempfile.TemporaryDirectory()))
        return upgrade.classify(
            tree(d / "base", base), tree(d / "yours", yours), tree(d / "theirs", theirs)
        )

    def test_only_upstream_changed_is_taken(self):
        plan = self._plan({"a.md": "uno"}, {"a.md": "uno"}, {"a.md": "due"})
        self.assertEqual(plan.theirs, ["a.md"])

    def test_only_you_changed_is_kept(self):
        """È il caso per cui esiste la modalità: la riga che hai promosso con
        `--up` non deve sparire perché è uscita una release."""
        plan = self._plan({"a.md": "uno"}, {"a.md": "mio"}, {"a.md": "uno"})
        self.assertEqual(plan.yours, ["a.md"])

    def test_both_changed_is_a_conflict(self):
        plan = self._plan({"a.md": "uno"}, {"a.md": "mio"}, {"a.md": "due"})
        self.assertEqual(plan.conflict, ["a.md"])

    def test_the_same_addition_on_both_sides_is_nothing_to_do(self):
        """La tua aggiunta è arrivata a monte, identica: non è un conflitto e
        non va aggiunta due volte. Senza questo caso il confronto chiederebbe
        di decidere su ciò che è già deciso."""
        plan = self._plan({"a.md": "uno"}, {"a.md": "mio"}, {"a.md": "mio"})
        self.assertEqual(plan.same, ["a.md"])
        self.assertEqual(plan.conflict, [])

    def test_a_file_you_added_is_kept_and_one_upstream_added_is_taken(self):
        plan = self._plan({}, {"mio.md": "x"}, {"loro.md": "y"})
        self.assertEqual(plan.yours, ["mio.md"])
        self.assertEqual(plan.theirs, ["loro.md"])

    def test_a_deletion_is_classified_like_any_other_change(self):
        """Un file assente è un contenuto: cancellato a monte e non toccato da
        te, si prende la cancellazione; cancellato da te, resta cancellato."""
        plan = self._plan({"a.md": "x", "b.md": "x"}, {"a.md": "x"}, {"b.md": "x"})
        self.assertEqual(plan.theirs, ["a.md"])
        self.assertEqual(plan.yours, ["b.md"])

    def test_caches_are_not_your_additions(self):
        """Esistono solo dove il codice è girato: comparirebbero come aggiunta
        tua a ogni confronto, su file che nessuno ha scritto. `.pytest_cache`
        l'ha trovato la prima prova su un sorgente vero."""
        plan = self._plan(
            {}, {"tools/__pycache__/x.pyc": "b", ".pytest_cache/v/nodeids": "[]"}, {}
        )
        self.assertEqual((plan.yours, plan.conflict), ([], []))


class TestRecord(unittest.TestCase):
    def test_the_base_falls_back_to_version_when_nothing_was_promoted(self):
        """Senza record nessun `--up` è mai stato fatto, quindi `VERSION` è
        ancora un numero pubblicato ed è la base giusta."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "VERSION").write_text("1.3.1\n", encoding="utf-8")
            self.assertIsNone(upgrade.read_record(root))
            self.assertEqual(upgrade.base_version(root), "1.3.1")

    def test_the_record_wins_over_a_version_that_was_incremented(self):
        """`--up` incrementa `VERSION`: da quel momento il numero locale non
        corrisponde a nessuna release, e confrontare contro di esso significa
        confrontare contro un albero che non esiste."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "VERSION").write_text("1.4.0\n", encoding="utf-8")
            upgrade.write_record(root, "1.3.1", "claude-framework-it", "https://x/y.git")
            self.assertEqual(upgrade.base_version(root), "1.3.1")
            self.assertEqual(upgrade.read_record(root)["edition"], "claude-framework-it")

    def test_an_unreadable_record_is_a_missing_one(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "VERSION").write_text("1.3.1\n", encoding="utf-8")
            (root / upgrade.RECORD).write_text("{ rotto", encoding="utf-8")
            self.assertIsNone(upgrade.read_record(root))
            self.assertEqual(upgrade.base_version(root), "1.3.1")


if __name__ == "__main__":
    unittest.main()
