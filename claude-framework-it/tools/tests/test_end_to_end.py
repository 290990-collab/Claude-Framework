import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import trial_install
from fwbuild import assemble, cli, doctor, kernel, profile, source

FRAMEWORK = Path(__file__).resolve().parents[2]
SURFACE_ONLY = {"compliance-reviewer", "perf-analyst"}
CONF_PERCENT_RE = re.compile(r"CONF:.*%")


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

    def test_agent_colors_are_platform_values(self):
        """`color` ha otto valori documentati. Sei schede ne dichiaravano uno
        inventato — brown, teal, magenta, violet — e nessun test lo vedeva:
        una configurazione che la piattaforma non riconosce non fallisce, viene
        ignorata, che è il modo in cui resta sbagliata per sempre."""
        valid = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
        for path in sorted((FRAMEWORK / "agents").glob("*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("color:"):
                    self.assertIn(line.split(":", 1)[1].strip(), valid, path.name)
                    break

    def test_read_only_reviewers_have_no_shell(self):
        """«Non modifica il codice» sopra una shell è una promessa, non una
        garanzia. Per chi non deve eseguire niente, toglierla la rende la
        configurazione della scheda."""
        for name in (
            "security-reviewer",
            "compliance-reviewer",
            "data-quality-reviewer",
            "scientific-reviewer",
        ):
            text = (FRAMEWORK / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("tools: Read, Grep, Glob\n", text, name)

    def test_every_profile_denies_the_same_secrets(self):
        """Un permesso che dipende dal campo è un permesso che qualcuno ha
        dimenticato di copiare: `.env.local` era negato solo su web."""
        needed = {
            "Read(./**/.env)",
            "Read(./**/.env.*)",
            "Read(./**/*.env)",
            "Read(./**/*.key)",
            "Read(./**/*.pem)",
        }
        for path in sorted((FRAMEWORK / "profiles").glob("*.toml")):
            prof = profile.load(path)
            deny = set(prof.settings["permissions"]["deny"])
            self.assertEqual(needed - deny, set(), prof.name)

    def test_state_templates_use_one_placeholder_syntax(self):
        """Ce n'erano due, `{{...}}` e `<...>`, e il doctor ne vedeva una: una
        riga da riempire poteva sopravvivere all'installazione senza rilievo."""
        for name in ("TODO.md", "status.md", "roadmap.md"):
            text = (FRAMEWORK / "templates" / name).read_text(encoding="utf-8")
            self.assertNotIn("{{", text, name)
            for line in text.splitlines():
                self.assertFalse(line.strip().startswith("<"), f"{name}: {line}")

    def test_profiles_declare_no_deferred_roster(self):
        """`on_demand` prometteva «più tardi» e `roster` li accodava comunque:
        il campo diceva il contrario di quello che faceva."""
        for path in sorted((FRAMEWORK / "profiles").glob("*.toml")):
            self.assertNotIn("on_demand", path.read_text(encoding="utf-8"), path.name)

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
            self.assertLess(
                len(text.split()), assemble.COORDINATOR_WORD_BUDGET, prof.name
            )

    def test_common_kernel_stays_under_budget(self):
        """Soglia sul costo pagato a ogni spawn. Se la supera, non si aggiunge:
        si sposta in shared/ o si comprime."""
        self.assertLess(
            len(assemble.read_method(FRAMEWORK / "method").split()),
            assemble.METHOD_WORD_BUDGET,
        )

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

    def test_surface_only_agents_are_in_no_profile(self):
        """Conformità e prestazioni non sono campi: un progetto software può
        trattare dati personali e un altro no. Chi le presidia lo sceglie la
        domanda sulla superficie critica, non il profilo {} metterli in un profilo
        li installerebbe ovunque, che è il costo fisso tolto con D4."""
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            leaked = SURFACE_ONLY & set(prof.agents)
            self.assertEqual(leaked, set(), f"{prof.name}: {leaked} lo sceglie la domanda 2")

    def test_surface_only_agents_are_reachable_from_the_question(self):
        """Fuori da ogni profilo, la domanda 2 è la loro **unica** via d'ingresso.
        Se una riga della tabella sparisce, l'agente resta in catalogo e non lo
        raggiunge più nessuno: installato mai, e nessun rilievo che lo dica."""
        skill = (FRAMEWORK / "skills" / "framework-install" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        blocco = skill[skill.index("**2. Superficie critica**") : skill.index("**3. Stile")]
        for name in sorted(SURFACE_ONLY):
            self.assertIn(f"`{name}`", blocco, name)

    def test_exclusive_pairs_declare_their_boundary(self):
        """`EXCLUSIVE` è una guardia, non una spiegazione: dice che i due non
        convivono, non dove passa la linea. Se la linea vive solo nel check, un
        agente attivato a mano arriva senza sapere cosa non è suo — e la
        riga di confine è proprio il genere di prosa che sparisce a una
        riscrittura, senza che niente lo veda."""
        for a, b in profile.EXCLUSIVE:
            for one, other in ((a, b), (b, a)):
                text = (FRAMEWORK / "agents" / f"{one}.md").read_text(encoding="utf-8")
                self.assertIn(f"`{other}`", text, f"{one} non nomina {other}")
                flat = " ".join(text.split())
                self.assertIn("mai entrambi", flat, one)

    def test_critical_surface_table_routes_to_agents_that_exist(self):
        """La domanda 2 del questionario è una tabella di routing, e ha lo stesso
        modo di rompersi di quella del coordinatore: rinominare un agente lascia
        in piedi la riga che lo cita, e chi installa sceglie una risposta che non
        porta a nessun file. Il doctor qui non può aiutare: il difetto sta nella
        skill, prima che un'installazione esista."""
        skill = (FRAMEWORK / "skills" / "framework-install" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        blocco = skill[skill.index("**2. Superficie critica**") : skill.index("**3. Stile")]
        # Più permissivo di `doctor.ROUTING_AGENT_RE`, e di proposito: quello accetta
        # solo minuscole, quindi un rinomino con una maiuscola sfuggirebbe alla
        # riga invece di farla fallire.
        revisori = re.findall(r"^\|[^|]*\|\s*`([^`]+)`\s*\|$", blocco, re.MULTILINE)
        self.assertGreaterEqual(len(revisori), 3, "tabella dei revisori non letta")
        for name in revisori:
            self.assertTrue((FRAMEWORK / "agents" / f"{name}.md").is_file(), name)

    def test_final_reviewer_asks_for_the_uncovered_critical_surface(self):
        """Le superfici senza revisore dedicato (contratto pubblico,
        accessibilità) non hanno un agente e non devono averne uno: finiscono
        nel mandato di chi verifica per ultimo. Se il segnaposto smette di
        chiederle, chi installa non le scrive e la superficie sparisce."""
        text = (FRAMEWORK / "agents" / "final-reviewer.md").read_text(encoding="utf-8")
        _, _, domain = assemble.split_source(text)
        self.assertIn("superficie critica", domain)

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

    def test_report_confidence_is_categorical_not_a_percentage(self):
        """La confidenza auto-riportata da un LLM è mal calibrata: una
        percentuale mette precisione finta nella posizione che il coordinatore
        legge per prima. Il formato vive in un punto solo di tutto il
        framework, e un punto solo si riscrive per distrazione: questo test è
        ciò che impedisce al formato vecchio di tornare senza che nessuno lo
        veda."""
        for p in FRAMEWORK.rglob("*.md"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), CONF_PERCENT_RE, str(p))

    def test_report_schema_carries_a_falsifier(self):
        """`SMENTIRE` è ciò che rende utile un giudizio categorico: senza, il
        coordinatore legge un'etichetta e non sa cosa la smentirebbe."""
        text = assemble.read_method(FRAMEWORK / "method")
        self.assertIn("CONF: ALTA | MEDIA | BASSA", text)
        self.assertIn("SMENTIRE:", text)

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


class TestInstalledBudget(unittest.TestCase):
    """`TOKEN_BUDGET`: la soglia sulla parte che il sorgente non vede."""

    def _installed(self, d, extra_words):
        root = Path(d) / "prova"
        with redirect_stdout(io.StringIO()):
            trial_install.install(root)
        if extra_words:
            claude = root / "CLAUDE.md"
            claude.write_text(
                claude.read_text(encoding="utf-8")
                + "\n## Extra\n\n"
                + ("parola " * extra_words)
                + "\n",
                encoding="utf-8",
            )
        return root

    def test_measure_separates_kernel_from_project_sections(self):
        """Le due parti hanno discipline opposte — una col tetto sul sorgente,
        l'altra senza nessun tetto — e la misura è ciò che le distingue. Se
        tornassero indistinte, il rilievo guarderebbe il totale e non direbbe
        di chi è la crescita."""
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        text = assemble.build_document(
            FRAMEWORK / "method", version, "## Il progetto\n\nuno due tre\n"
        )
        m = doctor.measure(text)
        self.assertTrue(m.has_region)
        self.assertEqual(
            m.kernel_words, len(assemble.read_method(FRAMEWORK / "method").split())
        )
        self.assertEqual(m.project_words, 6)
        self.assertEqual(m.total_words, m.kernel_words + 6)

    def test_measure_does_not_invent_a_split_without_markers(self):
        """La variante senza marker è legittima. Attribuire tutto al progetto
        farebbe scattare il rilievo su un'installazione sana."""
        m = doctor.measure("## Il progetto\n\nuno due tre\n")
        self.assertFalse(m.has_region)
        self.assertEqual(m.project_words, 0)

    def test_a_small_file_is_below_the_floor_and_stays_quiet(self):
        """Il rapporto su un file minuscolo è vero e irrilevante: un avviso sul
        costo di undici token è rumore, e un avviso che scatta sempre non lo
        legge più nessuno."""
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        text = assemble.build_document_from_text(
            "## Metodo\n\nuno\n", version, "## Il progetto\n\n" + ("x " * 50) + "\n"
        )
        m = doctor.measure(text)
        self.assertGreater(m.project_words, m.kernel_words)
        self.assertLess(m.total_words, assemble.METHOD_WORD_BUDGET)

    def test_a_normal_install_is_under_budget(self):
        """Se il rilievo scattasse sull'installazione di riferimento sarebbe
        rumore, e un avviso che scatta sempre non lo legge più nessuno."""
        with tempfile.TemporaryDirectory() as d:
            root = self._installed(d, 0)
            self.assertNotIn("TOKEN_BUDGET", [f.code for f in doctor.check(root)])

    def test_project_sections_larger_than_the_kernel_are_reported(self):
        """La soglia è il kernel, unica grandezza nota: il progetto non scrive
        più del metodo."""
        with tempfile.TemporaryDirectory() as d:
            root = self._installed(d, 1400)
            found = [f for f in doctor.check(root) if f.code == "TOKEN_BUDGET"]
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].severity, "WARN")

    def test_old_report_format_is_reported_in_an_installed_project(self):
        """Un progetto installato prima del formato categorico se lo tiene:
        l'hash della regione kernel torna, perché torna su quel testo lì, e la
        versione dichiarata è quella con cui il progetto è nato. Senza questo
        rilievo nessun check lo vede."""
        with tempfile.TemporaryDirectory() as d:
            root = self._installed(d, 0)
            claude = root / "CLAUDE.md"
            claude.write_text(
                claude.read_text(encoding="utf-8").replace(
                    "CONF: ALTA | MEDIA | BASSA", "CONF: <0-100" + "%>"
                ),
                encoding="utf-8",
            )
            self.assertIn("REPORT_FORMAT", [f.code for f in doctor.check(root)])

    def test_every_code_the_doctor_can_emit_is_documented(self):
        """Un rilievo senza una voce nella skill è un codice che chi lo riceve
        non sa cosa farne."""
        skill = (FRAMEWORK / "skills" / "framework-doctor" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        src = (FRAMEWORK / "tools" / "fwbuild" / "doctor.py").read_text(encoding="utf-8")
        emitted = set(re.findall(r'Finding\(\s*"([A-Z_]+)"', src))
        self.assertTrue(emitted)
        for code in sorted(emitted):
            self.assertIn("### `" + code + "`", skill, code)


class TestSourceReference(unittest.TestCase):
    """Come `.claude/framework.json` cita il sorgente."""

    def test_source_inside_the_project_is_recorded_relative(self):
        """Il primo dei tre modi previsti è il sorgente dentro il progetto: lì
        un assoluto è la macchina di chi ha installato, e muore al clone."""
        self.assertEqual(
            source.reference(Path("/prj"), Path("/prj/framework")), "framework"
        )

    def test_source_outside_the_project_stays_absolute(self):
        """Fuori dal progetto il relativo non regge: la profondità del clone
        non è nota."""
        out = Path("/altrove/framework").resolve()
        self.assertEqual(source.reference(Path("/prj"), out), str(out))

    def test_recorded_reference_resolves_back(self):
        recorded = source.reference(Path("/prj"), Path("/prj/framework"))
        self.assertEqual(
            source.dereference(Path("/prj"), recorded),
            Path("/prj/framework").resolve(),
        )

    def test_install_records_a_portable_source(self):
        """Il difetto stava nella skill, cioè in prosa: qui si verifica
        sull'artefatto scritto."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "prova"
            with redirect_stdout(io.StringIO()):
                trial_install.install(root)
            recorded = json.loads(
                (root / ".claude" / "framework.json").read_text(encoding="utf-8")
            )["source"]
            self.assertEqual(
                source.dereference(root, recorded).resolve(), FRAMEWORK.resolve()
            )


class TestProfilesAreDistinguishable(unittest.TestCase):
    def test_every_profile_declares_its_critical_surface(self):
        """La superficie critica del campo è nota prima di conoscere il
        progetto: è la sola risposta che un profilo può dare da solo alla
        domanda del Passo 3.2."""
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            self.assertTrue(prof.critical_surface.strip(), prof.name)

    def test_no_two_profiles_are_interchangeable(self):
        """`software` e `library` differivano solo per `name` e `description`:
        sceglierli non aveva nessuna conseguenza meccanica. Questo test
        impedisce di reintrodurre la scelta senza esito."""
        seen = {}
        for path in sorted((FRAMEWORK / "profiles").glob("*.toml")):
            prof = profile.load(path)
            key = (
                tuple(prof.agents),
                tuple(prof.cycles),
                tuple(prof.shared),
                repr(prof.settings),
                prof.critical_surface,
            )
            self.assertNotIn(key, seen, prof.name + " == " + str(seen.get(key)))
            seen[key] = prof.name

    def test_the_install_skill_starts_from_the_declared_surface(self):
        """Un campo che nessun passo legge è configurazione morta."""
        text = (FRAMEWORK / "skills" / "framework-install" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("critical_surface", text)


class TestCli(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(argv)
        return code, buf.getvalue()

    def _install(self, d):
        root = Path(d) / "prova"
        with redirect_stdout(io.StringIO()):
            trial_install.install(root)
        return root

    def test_doctor_json_carries_findings_and_measure(self):
        """Il formato per la CI: un consumatore che non deve leggere prosa."""
        with tempfile.TemporaryDirectory() as d:
            code, out = self._run(["doctor", "--json", str(self._install(d))])
            self.assertEqual(code, 0)
            payload = json.loads(out)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["findings"], [])
            self.assertTrue(payload["measure"]["split"])
            self.assertGreater(payload["measure"]["tokens"], 0)

    def test_doctor_json_keeps_the_strict_exit_code(self):
        """`--json` è un formato, non una postura: l'uscita dev'essere la stessa
        col flag e senza. Su un'installazione pulita è 0 — prima era 1, perché
        il ramo JSON restituiva il codice prima di guardare se ci fossero
        rilievi, e una CI che aggiungeva il flag falliva sempre."""
        with tempfile.TemporaryDirectory() as d:
            root = self._install(d)
            for argv in (
                ["doctor", str(root)],
                ["doctor", "--strict", str(root)],
                ["doctor", "--json", str(root)],
                ["doctor", "--strict", "--json", str(root)],
            ):
                with self.subTest(argv=" ".join(argv[:-1])):
                    self.assertEqual(self._run(argv)[0], 0)

            # E quando un rilievo c'è, entrambe le forme lo fanno cadere.
            (root / ".claude" / "settings.json").unlink()
            self.assertEqual(self._run(["doctor", "--strict", str(root)])[0], 1)
            self.assertEqual(
                self._run(["doctor", "--strict", "--json", str(root)])[0], 1
            )

    def test_install_writes_a_complete_manifest(self):
        """`framework.json` è l'unico posto che dice da dove il progetto è nato
        e di cosa è fatto: la prova guarda il file scritto, non la prosa che lo
        prescrive."""
        with tempfile.TemporaryDirectory() as d:
            root = self._install(d)
            data = json.loads(
                (root / ".claude" / "framework.json").read_text(encoding="utf-8")
            )
            self.assertEqual(data["profile"], "software")
            self.assertEqual(
                data["version"],
                (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip(),
            )
            self.assertTrue(data["source"])

    def test_cost_prints_its_assumptions_with_the_number(self):
        """Una cifra senza le sue ipotesi è un numero che nessuno può
        contestare: prezzo, spawn e persone stanno accanto al totale."""
        with tempfile.TemporaryDirectory() as d:
            code, out = self._run(
                ["cost", str(self._install(d)), "--spawns", "200", "--devs", "12"]
            )
            self.assertEqual(code, 0)
            self.assertIn("200 spawn al giorno", out)
            self.assertIn("12 persone", out)
            self.assertIn("$/Mtok", out)
            self.assertIn("--price", out)

    def test_cost_without_an_installation_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = self._run(["cost", d])
            self.assertEqual(code, 1)
            self.assertIn("CLAUDE.md assente", out)


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
