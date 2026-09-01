import tempfile
import unittest
from pathlib import Path

from fwbuild import profile

TOML = """
name = "software"
agents = ["debugger", "security-reviewer"]
shared = ["core/review-checklist.md"]
cycles = []
on_demand = ["compliance-reviewer"]

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
        self.assertIn("compliance-reviewer", prof.on_demand)

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
            on_demand=["compliance-reviewer"],
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


if __name__ == "__main__":
    unittest.main()
