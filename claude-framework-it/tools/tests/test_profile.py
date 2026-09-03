import tempfile
import unittest
from pathlib import Path

from fwbuild import profile

TOML = """
name = "software"
agents = ["debugger", "security-reviewer"]
shared = ["core/review-checklist.md"]
cycles = []

[settings.permissions]
deny = ["Read(./**/*.key)"]
"""


class TestLoad(unittest.TestCase):
    def _write(self, text):
        d = tempfile.mkdtemp()
        p = Path(d) / "software.toml"
        p.write_text(text, encoding="utf-8")
        return p

    def test_reads_fields(self):
        prof = profile.load(self._write(TOML))
        self.assertEqual(prof.name, "software")
        self.assertIn("debugger", prof.agents)
        self.assertNotIn("compliance-reviewer", prof.agents)

    def test_reads_settings_for_settings_json(self):
        prof = profile.load(self._write(TOML))
        self.assertEqual(prof.settings["permissions"]["deny"], ["Read(./**/*.key)"])

    def test_settings_defaults_to_empty(self):
        minimal = 'name = "bare"\nagents = []\n'
        self.assertEqual(profile.load(self._write(minimal)).settings, {})


class TestRoster(unittest.TestCase):
    def _profile(self):
        return profile.Profile(
            name="software",
            agents=["debugger", "security-reviewer"],
            shared=[],
            cycles=[],
            settings={},
        )

    def test_always_includes_level_one(self):
        got = profile.roster(self._profile(), extras=[], drop=[])
        for name in profile.ALWAYS:
            self.assertIn(name, got)

    def test_extras_are_added(self):
        got = profile.roster(self._profile(), extras=["frontend"], drop=[])
        self.assertIn("frontend", got)

    def test_drop_removes_profile_agent(self):
        got = profile.roster(self._profile(), extras=[], drop=["debugger"])
        self.assertNotIn("debugger", got)

    def test_drop_cannot_remove_level_one(self):
        got = profile.roster(self._profile(), extras=[], drop=["architect"])
        self.assertIn("architect", got)

    def test_result_has_no_duplicates(self):
        got = profile.roster(self._profile(), extras=["debugger"], drop=[])
        self.assertEqual(len(got), len(set(got)))


class TestExclusive(unittest.TestCase):
    def test_deploy_and_infra_conflict(self):
        self.assertTrue(profile.check_exclusive(["deploy", "infra"]))

    def test_deploy_alone_is_fine(self):
        self.assertEqual(profile.check_exclusive(["deploy"]), [])


class TestRequiredGuides(unittest.TestCase):
    """Le guide che un agente cita e che il profilo può non elencare.

    Il difetto è emerso installando il framework su se stesso: attivare
    `scientific-reviewer` su un profilo `library` produce un pointer morto,
    perché quella scheda cita una guida che solo `research` installa.
    """

    FRAMEWORK = Path(__file__).resolve().parents[2]

    def test_finds_the_guide_an_extra_agent_brings(self):
        got = profile.required_guides(self.FRAMEWORK, ["scientific-reviewer"])
        self.assertIn("domain/research-principles.md", got)

    def test_a_profile_alone_has_no_gap(self):
        """Nessun profilo è incoerente da solo: il buco si apre con gli extra.

        È il motivo per cui la prova end-to-end non lo vedeva — usa `research`,
        che quella guida la installa già.
        """
        for name in ("software", "library", "research", "web", "data"):
            prof = profile.load(self.FRAMEWORK / "profiles" / f"{name}.toml")
            needed = profile.required_guides(
                self.FRAMEWORK, profile.roster(prof, extras=[], drop=[])
            )
            with self.subTest(profile=name):
                self.assertEqual(sorted(set(needed) - set(prof.shared)), [])

    def test_library_plus_scientific_reviewer_needs_a_guide_it_lacks(self):
        prof = profile.load(self.FRAMEWORK / "profiles" / "library.toml")
        roster = profile.roster(prof, extras=["scientific-reviewer"], drop=[])
        needed = profile.required_guides(self.FRAMEWORK, roster)
        self.assertEqual(
            sorted(set(needed) - set(prof.shared)), ["domain/research-principles.md"]
        )

    def test_unknown_agent_is_skipped_not_fatal(self):
        self.assertEqual(profile.required_guides(self.FRAMEWORK, ["inesistente"]), [])


if __name__ == "__main__":
    unittest.main()
