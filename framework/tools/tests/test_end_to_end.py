import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import trial_install
from fwbuild import assemble, doctor, kernel, profile

FRAMEWORK = Path(__file__).resolve().parents[2]
LEVEL_THREE = {"compliance-reviewer", "perf-analyst"}


class TestRealFramework(unittest.TestCase):
    def test_version_file_exists(self):
        self.assertTrue((FRAMEWORK / "VERSION").is_file())

    def test_all_nineteen_agents_present(self):
        self.assertEqual(len(list((FRAMEWORK / "agents").glob("*.md"))), 19)

    def test_no_agent_declares_fable(self):
        for p in (FRAMEWORK / "agents").glob("*.md"):
            self.assertNotIn("model: fable", p.read_text(encoding="utf-8"), p.name)

    def test_architect_is_opus_xhigh(self):
        text = (FRAMEWORK / "agents" / "architect.md").read_text(encoding="utf-8")
        self.assertIn("model: opus", text)
        self.assertIn("effort: xhigh", text)

    def test_every_agent_splits_and_assembles(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        for p in sorted((FRAMEWORK / "agents").glob("*.md")):
            fm, method, domain = assemble.split_source(p.read_text(encoding="utf-8"))
            built = assemble.build_agent(fm, method, domain, version)
            self.assertEqual(kernel.verify(built), "OK", p.name)
            self.assertIn("[DA COMPILARE", domain, p.name)

    def test_kernel_assembles_and_verifies(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        out = assemble.build_document(FRAMEWORK / "method", version, "## Il progetto\n\nX\n")
        self.assertEqual(kernel.verify(out), "OK")

    def test_coordinator_guide_assembles_and_verifies(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        out = assemble.build_document(FRAMEWORK / "coordinator", version, "## Roster\n\nX\n")
        self.assertEqual(kernel.verify(out), "OK")

    def test_kernel_has_no_placeholders(self):
        for d in ("method", "coordinator"):
            text = assemble.read_method(FRAMEWORK / d)
            self.assertNotIn("DA COMPILARE", text, d)
            self.assertNotIn("{{", text, d)

    def test_coordinator_content_is_not_in_common_kernel(self):
        """Il kernel comune è pagato da ogni subagent a ogni spawn: ciò che
        serve solo a chi delega non deve finirci. La lista dei titoli è quella
        del doctor, non una copia: due liste divergono in silenzio."""
        common = assemble.read_method(FRAMEWORK / "method")
        for heading in doctor.COORDINATOR_ONLY:
            self.assertNotIn(heading, common, heading)

    def test_watched_headings_still_exist_where_they_belong(self):
        """COORDINATOR_LEAK confronta stringhe: se un titolo viene rinominato
        alla fonte, il check smette di vedere la sezione senza far fallire
        niente. Questo test è ciò che rende visibile il rinomino."""
        sources = assemble.read_method(FRAMEWORK / "coordinator") + (
            FRAMEWORK / "skills" / "framework-install" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for heading in doctor.COORDINATOR_ONLY:
            self.assertIn(heading, sources, heading)

    def test_coordinator_guide_stays_under_budget(self):
        """Anche la guida del coordinatore ha un tetto: è on-demand, non pagata
        a ogni spawn, ma senza soglia è il prossimo posto dove il metodo si
        gonfia. Si misura l'artefatto reale, cicli del profilo inclusi."""
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            text = assemble.read_method(
                FRAMEWORK / "coordinator", assemble.cycle_files(FRAMEWORK, prof.cycles)
            )
            self.assertLess(len(text.split()), 2000, prof.name)

    def test_common_kernel_stays_under_budget(self):
        """Soglia sul costo pagato a ogni spawn. Se la supera, non si aggiunge:
        si sposta in shared/ o si comprime."""
        self.assertLess(len(assemble.read_method(FRAMEWORK / "method").split()), 1600)

    def test_ten_delegation_rules_are_complete_and_in_one_place(self):
        coord = assemble.read_method(FRAMEWORK / "coordinator")
        numbered = re.findall(r"^(\d+)\. \*\*", coord, re.MULTILINE)
        self.assertEqual([int(n) for n in numbered[:10]], list(range(1, 11)))

    def test_variant_b_has_no_markers(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        for d, sentinel in (("method", "Evidence Before Action"), ("coordinator", "delega")):
            out = assemble.build_document(
                FRAMEWORK / d, version, "## Il progetto\n\nX\n", markers=False
            )
            self.assertNotIn("FRAMEWORK:KERNEL", out, d)
            self.assertIn(sentinel, out, d)
            self.assertIn("Il progetto", out, d)

    def test_every_profile_resolves_to_existing_agents(self):
        available = {p.stem for p in (FRAMEWORK / "agents").glob("*.md")}
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            names = profile.roster(prof, [], [])
            self.assertEqual([n for n in names if n not in available], [], prof.name)
            self.assertEqual(profile.check_exclusive(names), [], prof.name)

    def test_every_declared_cycle_exists(self):
        """Un ciclo dichiarato in un profilo e assente da cycles/ farebbe
        promettere al profilo un metodo che il progetto non riceve."""
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            assemble.cycle_files(FRAMEWORK, prof.cycles)  # solleva se manca

    def test_no_orphan_cycle_files(self):
        declared = set()
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            declared |= set(profile.load(path).cycles)
        on_disk = {p.stem for p in (FRAMEWORK / "cycles").glob("*.md")}
        self.assertEqual(on_disk - declared, set(), "cicli su disco che nessun profilo usa")

    def test_every_profile_shared_guide_exists(self):
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            for rel in prof.shared:
                self.assertTrue((FRAMEWORK / "shared" / rel).is_file(), f"{prof.name}: {rel}")

    def test_level_three_agents_are_never_in_profile_agents(self):
        """Gli agenti a invocazione esplicita stanno in on_demand, mai fra quelli
        che il coordinatore può scegliere da solo."""
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            leaked = LEVEL_THREE & set(prof.agents)
            self.assertEqual(leaked, set(), f"{prof.name}: {leaked} deve stare in on_demand")

    def test_level_three_agents_declare_explicit_invocation(self):
        for name in LEVEL_THREE:
            text = (FRAMEWORK / "agents" / f"{name}.md").read_text(encoding="utf-8")
            flat = " ".join(text.split())
            self.assertIn("SOLO SU RICHIESTA ESPLICITA", flat, name)

    def test_three_skills_present_with_matching_name(self):
        for name in ("framework-install", "framework-doctor", "framework-sync"):
            p = FRAMEWORK / "skills" / name / "SKILL.md"
            self.assertTrue(p.is_file(), name)
            self.assertIn(f"name: {name}", p.read_text(encoding="utf-8"))

    def test_state_templates_present(self):
        for name in ("TODO.md", "status.md", "roadmap.md"):
            self.assertTrue((FRAMEWORK / "templates" / name).is_file(), name)

    def test_review_checklist_keeps_generic_block_separable(self):
        text = (FRAMEWORK / "shared" / "core" / "review-checklist.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Blocco generico", text)
        self.assertIn("## Blocco di progetto", text)
        self.assertLess(text.index("## Blocco generico"), text.index("## Blocco di progetto"))

    def test_no_reference_to_source_projects(self):
        forbidden = ("RPLAN", "AbletonLoader", "FindShop", "Avalonia", "Typesense", "CVCS")
        for p in FRAMEWORK.rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            for word in forbidden:
                self.assertNotIn(word, text, f"{p.name} cita {word}")

    def test_sync_down_preserves_domain_cycles(self):
        """La procedura `--down` riassembla la guida del coordinatore dal
        sorgente: se non ripassa i cicli, un progetto `web` perde il ciclo del
        design a ogni aggiornamento, in silenzio e senza rilievi."""
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        prof = profile.load(FRAMEWORK / "profiles" / "web.toml")
        installed = assemble.build_document(
            FRAMEWORK / "coordinator",
            version,
            "## Roster di questo progetto",
            extra=assemble.cycle_files(FRAMEWORK, prof.cycles),
        )
        region = kernel.parse(installed)
        rebuilt = assemble.build_document(
            FRAMEWORK / "coordinator",
            version,
            installed[region.end :],
            extra=assemble.installed_cycles(region.body, FRAMEWORK),
        )
        self.assertIn("Il ciclo del design", rebuilt)

    def test_unfilled_roadmap_is_detectable(self):
        """Un template di stato con scheletro non compilato è indistinguibile
        da uno stato assente per chi lo legge a inizio sessione: deve
        contenere un segnaposto che il doctor riconosce."""
        text = (FRAMEWORK / "templates" / "roadmap.md").read_text(encoding="utf-8")
        self.assertRegex(text, doctor.PLACEHOLDER_RE)

    def test_status_template_is_deliberately_not_a_placeholder(self):
        """`status.md` nasce vuoto per costruzione — ci si scrive quando
        qualcosa si chiude. Segnalarlo renderebbe il Passo 6 impossibile da
        superare a installazione appena fatta."""
        text = (FRAMEWORK / "templates" / "status.md").read_text(encoding="utf-8")
        self.assertNotRegex(text, doctor.PLACEHOLDER_RE)


class TestRealInstall(unittest.TestCase):
    def test_full_install_passes_doctor(self):
        """Il resto della suite verifica i pezzi; questo verifica **l'atto di
        installare**. È l'unico test che cade se l'installazione, tutta intera,
        smette di reggere il Passo 6 — ed è così che è stato trovato il
        `roadmap.md` copiato e mai compilato."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "prova"
            with redirect_stdout(io.StringIO()):
                trial_install.install(root)
            self.assertEqual(doctor.check(root), [])


if __name__ == "__main__":
    unittest.main()
