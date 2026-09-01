import re
import tempfile
import unittest
from pathlib import Path

from fwbuild import assemble, doctor, kernel

AGENT_FM = "---\nname: {n}\nmodel: opus\neffort: high\n---\n"
# La versione del sorgente, non un letterale: `VERSION_MISMATCH` confronta il
# progetto col sorgente, e un valore fisso farebbe fallire la suite al primo
# bump di VERSION.
VERSION = (Path(__file__).resolve().parents[2] / "VERSION").read_text(
    encoding="utf-8"
).strip()


def make_project(
    tmp,
    *,
    agents=("explorer",),
    routing=("explorer",),
    placeholder=False,
    fable=False,
    state=True,
    orchestration=True,
    leak=False,
    skills=True,
    markers=True,
    settings=True,
    guides=(),
):
    root = Path(tmp)
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "shared").mkdir(parents=True)
    if skills:
        for name in ("framework-doctor", "framework-sync"):
            d = root / ".claude" / "skills" / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(f"name: {name}\n", encoding="utf-8")
    if settings:
        (root / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    for rel in guides:
        g = root / ".claude" / "shared" / rel
        g.parent.mkdir(parents=True, exist_ok=True)
        g.write_text("# guida", encoding="utf-8")
    (root / "docs").mkdir(parents=True)
    rows = "\n".join(f"| dove | `{n}` | haiku |" for n in routing)
    if orchestration:
        # La tabella di routing vive nella guida del coordinatore, non in
        # CLAUDE.md: è contenuto che i subagent non devono pagare.
        (root / ".claude" / "shared" / "orchestration.md").write_text(
            assemble.build_document_from_text(
                "## Delega\n",
                VERSION,
                "| Situazione | Agente | Modello |\n|---|---|---|\n" + rows + "\n",
                markers=markers,
            ),
            encoding="utf-8",
        )
    project = "## Il progetto\n\nProgetto di prova.\n"
    if placeholder:
        project += "\n[DA COMPILARE] — mappa moduli\n"
    if leak:
        project += "\n## Il ciclo del codice\n\nExplorer, poi architect.\n"
    (root / "CLAUDE.md").write_text(
        assemble.build_document_from_text("## Metodo\n", VERSION, project, markers=markers),
        encoding="utf-8",
    )
    for n in agents:
        model = "fable" if fable else "opus"
        fm = AGENT_FM.format(n=n).replace("model: opus", f"model: {model}")
        (root / ".claude" / "agents" / f"{n}.md").write_text(
            assemble.build_agent(
                fm, "## Metodo\n", "## Dominio\n", VERSION, markers=markers
            ),
            encoding="utf-8",
        )
    if state:
        for f in ("TODO.md", "status.md", "roadmap.md"):
            (root / "docs" / f).write_text("# vuoto\n", encoding="utf-8")
    return root


def strip_markers(text):
    return re.sub(r"<!-- /?FRAMEWORK:KERNEL[^>]*-->", "", text)


def codes(findings):
    return {f.code for f in findings}


class TestDoctor(unittest.TestCase):
    def test_clean_project_has_no_findings(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(doctor.check(make_project(d)), [])

    def test_detects_placeholder(self):
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, placeholder=True))
            self.assertIn("PLACEHOLDER", codes(found))

    def test_detects_agent_in_routing_without_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, agents=("explorer",), routing=("explorer", "frontend"))
            self.assertIn("ROSTER_MISSING", codes(doctor.check(p)))

    def test_detects_agent_file_not_in_routing(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, agents=("explorer", "frontend"), routing=("explorer",))
            self.assertIn("ROSTER_ORPHAN", codes(doctor.check(p)))

    def test_detects_kernel_drift(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            f = p / "CLAUDE.md"
            f.write_text(
                f.read_text(encoding="utf-8").replace("## Metodo", "## Altro"),
                encoding="utf-8",
            )
            self.assertIn("KERNEL_DRIFT", codes(doctor.check(p)))

    def test_detects_missing_state_files(self):
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, state=False))
            self.assertIn("STATE_MISSING", codes(found))

    def test_detects_fable(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("FABLE", codes(doctor.check(make_project(d, fable=True))))

    def test_skills_are_not_scanned_for_placeholders(self):
        """framework-doctor spiega il rilievo PLACEHOLDER e contiene per forza
        quella stringa: scansionarlo produrrebbe un falso positivo a ogni run."""
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d)
            (root / ".claude" / "skills" / "framework-doctor" / "SKILL.md").write_text(
                "Il rilievo `PLACEHOLDER` segnala un `[DA COMPILARE]` residuo.\n",
                encoding="utf-8",
            )
            self.assertNotIn("PLACEHOLDER", codes(doctor.check(root)))

    def test_detects_missing_lifecycle_skills(self):
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, skills=False))
            self.assertIn("SKILLS_MISSING", codes(found))

    def test_detects_missing_orchestration_guide(self):
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, orchestration=False))
            self.assertIn("SHARED_MISSING", codes(found))

    def test_detects_coordinator_content_leaking_into_claude_md(self):
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, leak=True))
            self.assertIn("COORDINATOR_LEAK", codes(found))

    def test_detects_deploy_infra_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(
                d,
                agents=("explorer", "deploy", "infra"),
                routing=("explorer", "deploy", "infra"),
            )
            self.assertIn("EXCLUSIVE", codes(doctor.check(p)))

    def test_detects_stripped_kernel_markers(self):
        """Togliere i marker non è meno grave che riscrivere il metodo dentro
        la regione: senza marker, il drift smette di essere visibile."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            f = p / ".claude" / "agents" / "explorer.md"
            f.write_text(strip_markers(f.read_text(encoding="utf-8")), encoding="utf-8")
            self.assertIn("KERNEL_MISSING", codes(doctor.check(p)))

    def test_installation_without_markers_is_not_flagged(self):
        """La variante senza tracking è una scelta legittima: nessun marker in
        nessun file tracciato, nessun rilievo."""
        with tempfile.TemporaryDirectory() as d:
            self.assertNotIn("KERNEL_MISSING", codes(doctor.check(make_project(d, markers=False))))

    def test_detects_dangling_shared_pointer_in_an_agent(self):
        """Quasi tutti i pointer alle guide vivono negli agenti: verificarli
        solo in CLAUDE.md lascia scoperta la maggioranza."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            f = p / ".claude" / "agents" / "explorer.md"
            f.write_text(
                f.read_text(encoding="utf-8") + "Vedi `.claude/shared/core/assente.md`.",
                encoding="utf-8",
            )
            self.assertIn("SHARED_MISSING", codes(doctor.check(p)))

    def test_detects_unfilled_state_template(self):
        """Un template di stato copiato e non compilato è indistinguibile da
        uno stato assente per chi lo legge a inizio sessione."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            (p / "docs" / "TODO.md").write_text("- [ ] {{task attivo}}", encoding="utf-8")
            self.assertIn("PLACEHOLDER", codes(doctor.check(p)))

    def _rewrap(self, f, version):
        """Riscrive la regione kernel di un file a un'altra versione,
        lasciando l'hash coerente: è il caso che nessun altro check vede."""
        text = f.read_text(encoding="utf-8")
        r = kernel.parse(text)
        f.write_text(
            text[: r.start] + kernel.wrap(r.body, version) + text[r.end + 1 :],
            encoding="utf-8",
        )

    def test_detects_missing_settings_file(self):
        """`settings.json` porta i permessi del profilo, fra cui il divieto
        di leggere segreti: assente, quel divieto non esiste."""
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, settings=False))
            self.assertIn("SETTINGS_MISSING", codes(found))

    def test_detects_shared_guide_nobody_cites(self):
        """L'inverso di SHARED_MISSING: una guida installata e mai citata è
        contesto pagato e mai aperto."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, guides=("core/mai-citata.md",))
            self.assertIn("SHARED_ORPHAN", codes(doctor.check(p)))

    def test_cited_shared_guide_is_not_an_orphan(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, guides=("core/citata.md",))
            f = p / "CLAUDE.md"
            f.write_text(
                f.read_text(encoding="utf-8") + "`.claude/shared/core/citata.md`",
                encoding="utf-8",
            )
            self.assertNotIn("SHARED_ORPHAN", codes(doctor.check(p)))

    def test_detects_version_skew_between_documents(self):
        """Due documenti dello stesso progetto a versioni diverse: l'hash
        torna su entrambi, perché torna ognuno sul proprio metodo."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            self._rewrap(p / ".claude" / "agents" / "explorer.md", "0.3.0")
            self.assertIn("VERSION_MISMATCH", codes(doctor.check(p)))

    def test_detects_installation_behind_the_source(self):
        """Metodo vecchio ma internamente coerente: è la biforcazione fra
        progetti, e prima di questo check nessun rilievo la vedeva."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            tracked = [p / "CLAUDE.md", p / ".claude" / "shared" / "orchestration.md"]
            tracked += list((p / ".claude" / "agents").glob("*.md"))
            for f in tracked:
                self._rewrap(f, "0.3.0")
            self.assertEqual(codes(doctor.check(p)), {"VERSION_MISMATCH"})


if __name__ == "__main__":
    unittest.main()
