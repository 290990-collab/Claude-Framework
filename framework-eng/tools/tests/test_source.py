import tempfile
import unittest
from pathlib import Path

from fwbuild import source

FRAMEWORK = Path(__file__).resolve().parents[1]


def make_root(base: Path, *, drop: str = "") -> Path:
    """A fake framework root: the mandatory entries, minus the named one.

    Fictitious roots and not the real one: the search must be testable without
    depending on where the framework running the tests is installed.
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
            root = make_root(Path(d) / "maimed", drop="profiles")
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
        """Source copied inside the project: the project root is passed."""
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "framework")
            self.assertEqual(source.resolve([Path(d)]), root)

    def test_first_valid_candidate_wins(self):
        with tempfile.TemporaryDirectory() as d:
            master = make_root(Path(d) / "master")
            self.assertEqual(source.resolve([Path(d) / "empty", master]), master)

    def test_single_invalid_candidate_raises(self):
        """The rule "path given but invalid: an error, no fallback" is not a
        special case of the resolver: it is the caller that passes a single
        candidate. A silent fallback masks a wrong path."""
        with tempfile.TemporaryDirectory() as d:
            make_root(Path(d) / "elsewhere")
            with self.assertRaises(LookupError):
                source.resolve([Path(d) / "wrong"])

    def test_error_names_what_is_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_root(Path(d) / "maimed", drop="agents")
            with self.assertRaises(LookupError) as e:
                source.resolve([root])
            self.assertIn("agents", str(e.exception))


if __name__ == "__main__":
    unittest.main()
