import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from fwbuild import cli, kernel, report

# Import assoluto e non relativo: `unittest discover -s tests` carica i moduli
# come top-level, e un `.test_doctor` lì dentro non ha un pacchetto padre. I due
# runner devono dare lo stesso numero.
from tests.test_doctor import VERSION, make_project


def installed(tmp, name, version=VERSION, declared=None):
    """Un progetto trovabile da `discover`: il marker più i file del fixture.

    `make_project` costruisce un'installazione valida ma non scrive
    `framework.json` — è il file che dice «qui c'è un'installazione», e senza
    quello il rapporto non ha niente da cui partire.
    """
    root = Path(tmp) / name
    root.mkdir(parents=True)
    make_project(root)
    if version != VERSION:
        for f in [root / "CLAUDE.md"] + sorted(
            (root / ".claude" / "agents").glob("*.md")
        ):
            t = f.read_text(encoding="utf-8")
            r = kernel.parse(t)
            if r is not None:
                f.write_text(
                    t[: r.start] + kernel.wrap(r.body, version) + t[r.end + 1 :],
                    encoding="utf-8",
                )
    (root / ".claude" / "framework.json").write_text(
        json.dumps({"source": "framework", "version": declared or version}),
        encoding="utf-8",
    )
    return root


class TestDiscovery(unittest.TestCase):
    def test_finds_projects_below_the_given_path(self):
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha")
            installed(d, "beta")
            found = report.discover([d])
            self.assertEqual(sorted(p.name for p in found), ["alpha", "beta"])

    def test_a_project_path_is_itself_a_result(self):
        """Puntare il comando su un repository solo deve funzionare: è come si
        prova prima di puntarlo su quaranta."""
        with tempfile.TemporaryDirectory() as d:
            root = installed(d, "alpha")
            self.assertEqual(report.discover([root]), [root])

    def test_the_search_stops_at_the_declared_depth(self):
        """Un rapporto di flotta si punta su una cartella di repository. Senza
        fondo, su una home, il comando diventa inutilizzabile proprio dove
        serve."""
        with tempfile.TemporaryDirectory() as d:
            deep = Path(d) / "a" / "b" / "c"
            deep.mkdir(parents=True)
            installed(deep, "alpha")
            self.assertEqual(report.discover([d], depth=2), [])
            self.assertEqual(len(report.discover([d], depth=4)), 1)

    def test_a_project_is_not_searched_through(self):
        """Trovato il marker si smette di scendere: un progetto che ne contiene
        un altro conterebbe due volte, e le sottocartelle di un repo sono la
        parte cara da attraversare."""
        with tempfile.TemporaryDirectory() as d:
            outer = installed(d, "alpha")
            installed(outer, "vendored")
            self.assertEqual(report.discover([d]), [outer])


class TestSurvey(unittest.TestCase):
    def test_the_version_shown_is_the_one_in_the_files(self):
        """`framework.json` dice da dove il progetto è nato, la regione kernel
        dice cosa contiene adesso. Quando divergono conta la seconda: la prima
        si aggiorna dimenticandosene."""
        with tempfile.TemporaryDirectory() as d:
            root = installed(d, "alpha", version="0.9.0", declared="1.0.0")
            p = report.inspect(root)
            self.assertEqual(p.declared, "1.0.0")
            self.assertEqual(p.version, "0.9.0")

    def test_projects_off_the_source_version_are_listed_as_behind(self):
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha")
            installed(d, "beta", version="0.9.0")
            s = report.survey([d], source_version=VERSION)
            self.assertEqual([p.name for p in s.behind], ["beta"])
            self.assertEqual(s.versions, {"0.9.0": 1, VERSION: 1})
            self.assertFalse(s.clean)

    def test_without_a_source_version_there_is_no_direction(self):
        """La maggioranza non è un riferimento: senza una versione di sorgente
        si riporta la distribuzione, non un «indietro» inventato."""
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha")
            installed(d, "beta", version="0.9.0")
            s = report.survey([d])
            self.assertEqual(s.behind, [])
            self.assertEqual(len(s.versions), 2)

    def test_a_fleet_on_one_version_and_without_findings_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha")
            installed(d, "beta")
            s = report.survey([d], source_version=VERSION)
            self.assertEqual(s.behind, [])
            self.assertTrue(s.clean, [f for p in s.projects for f in p.findings])

    def test_manual_edits_to_the_method_are_counted(self):
        """Il drift è la voce che rende il rapporto utile: un metodo modificato
        a mano in un repo è la biforcazione al primo passo."""
        with tempfile.TemporaryDirectory() as d:
            root = installed(d, "alpha")
            c = root / "CLAUDE.md"
            c.write_text(
                c.read_text(encoding="utf-8").replace("Metodo", "Metodo cambiato"),
                encoding="utf-8",
            )
            self.assertTrue(report.inspect(root).drifted)


class TestReportCli(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(argv)
        return code, buf.getvalue()

    def test_json_carries_every_project_and_the_aggregate(self):
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha")
            installed(d, "beta", version="0.9.0")
            code, out = self._run(["report", "--json", d])
            self.assertEqual(code, 0)
            payload = json.loads(out)
            self.assertEqual(len(payload["projects"]), 2)
            self.assertEqual(payload["behind"], ["beta"])
            self.assertFalse(payload["clean"])

    def test_strict_fails_when_a_project_diverges(self):
        """Senza `--strict` il rapporto è un rapporto. Con, è un cancello di
        CI: è la differenza fra vedere la divergenza e non lasciarla passare."""
        with tempfile.TemporaryDirectory() as d:
            installed(d, "alpha", version="0.9.0")
            self.assertEqual(self._run(["report", "--strict", d])[0], 1)
            self.assertEqual(self._run(["report", d])[0], 0)

    def test_nothing_found_says_what_it_was_looking_for(self):
        """Un rapporto vuoto senza spiegazione si legge come «tutto a posto»."""
        with tempfile.TemporaryDirectory() as d:
            code, out = self._run(["report", d])
            self.assertEqual(code, 0)
            self.assertIn("framework.json", out)


if __name__ == "__main__":
    unittest.main()
