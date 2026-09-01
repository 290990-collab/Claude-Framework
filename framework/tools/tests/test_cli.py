import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fwbuild import cli
from tests.test_doctor import make_project

FRAMEWORK = Path(__file__).resolve().parents[2]
VERSION = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()


class TestDoctorCommand(unittest.TestCase):
    def test_exit_zero_on_clean_project(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["doctor", str(root)]), 0)

    def test_exit_one_when_error_finding(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d, placeholder=True)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["doctor", str(root)]), 1)

    def test_prints_finding_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d, placeholder=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.main(["doctor", str(root)])
            self.assertIn("PLACEHOLDER", buf.getvalue())

    def test_strict_exits_one_on_warning_only(self):
        """Il Passo 6 dell'installazione dice che qualunque rilievo la lascia
        incompleta: senza --strict quella regola resterebbe solo prosa."""
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d, skills=False)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["doctor", str(root)]), 0)
                self.assertEqual(cli.main(["doctor", "--strict", str(root)]), 1)


class TestSourceCommand(unittest.TestCase):
    def test_prints_root_and_version(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(cli.main(["source", str(FRAMEWORK)]), 0)
        self.assertIn(f"v{VERSION}", buf.getvalue())

    def test_exit_one_and_says_what_is_missing(self):
        """Il gate serve a fermarsi **prima** di aver creato una cartella: deve
        dire cosa manca, non solo che qualcosa non va."""
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cli.main(["source", d]), 1)
            self.assertIn("method", buf.getvalue())

    def test_explicit_path_is_the_only_candidate(self):
        """Dove la regola «nessun fallback» è davvero decisa."""
        self.assertEqual(cli._bases(Path("/x")), [Path("/x")])

    def test_env_var_comes_before_home(self):
        """Il modo «master unico»: senza, resta solo il sorgente nel progetto."""
        with patch.dict(os.environ, {"CLAUDE_FRAMEWORK": "/master"}):
            self.assertEqual(cli._bases(None)[1], Path("/master"))


if __name__ == "__main__":
    unittest.main()
