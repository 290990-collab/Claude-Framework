import copy
import re
import unittest
from pathlib import Path

from fwbuild import settings

FRAMEWORK = Path(__file__).resolve().parents[2]

FRAMEWORK_SETTINGS = {
    "outputStyle": "Reporting",
    "permissions": {"deny": ["Read(./**/.env)", "Read(./**/*.key)"]},
    **settings.hooks(settings.HOOKS),
}


class TestMerge(unittest.TestCase):
    def test_merge_records_only_what_it_added(self):
        """Il record è ciò che la disinstallazione toglierà: se porta una voce
        che l'utente aveva già, la disinstallazione gliela porta via."""
        existing = {"permissions": {"deny": ["Read(./**/.env)"], "allow": ["Bash(ls)"]}}
        _, added, conflicts = settings.merge(existing, FRAMEWORK_SETTINGS)
        self.assertEqual(
            added,
            {
                "outputStyle": "Reporting",
                "permissions": {"deny": ["Read(./**/*.key)"]},
                **settings.hooks(settings.HOOKS),
            },
        )
        self.assertEqual(conflicts, [])

    def test_merge_keeps_the_user_value_on_a_conflict(self):
        existing = {"outputStyle": "Mio", "permissions": {"defaultMode": "plan"}}
        framework = {"outputStyle": "Reporting", "permissions": {"defaultMode": "acceptEdits"}}
        merged, added, conflicts = settings.merge(existing, framework)
        self.assertEqual(merged, existing)
        self.assertEqual(added, {})
        self.assertEqual(conflicts, ["outputStyle", "permissions.defaultMode"])


class TestUnmerge(unittest.TestCase):
    def test_unmerge_removes_only_the_record_and_keeps_user_changes(self):
        merged, added, _ = settings.merge({"permissions": {"deny": ["Bash(rm:*)"]}}, FRAMEWORK_SETTINGS)
        merged["outputStyle"] = "Mio"
        merged["permissions"]["deny"].append("Read(./secret)")
        rest, kept = settings.unmerge(merged, added)
        self.assertEqual(
            rest,
            {"outputStyle": "Mio", "permissions": {"deny": ["Bash(rm:*)", "Read(./secret)"]}},
        )
        self.assertEqual(kept, ["outputStyle"])

    def test_merge_then_unmerge_gives_back_the_original(self):
        """L'invariante su cui la disinstallazione si regge: nessuna modifica
        dell'utente in mezzo, il file torna com'era — neanche un contenitore
        vuoto lasciato indietro, neanche un dict condiviso modificato."""
        user_hook = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo x"}]}
        cases = (
            {},
            {"permissions": {"deny": ["Read(./**/.env)"]}, "hooks": {"PreToolUse": [user_hook]}},
            {"outputStyle": "Mio", "env": {"A": "1"}, "permissions": {"allow": ["Bash(ls)"]}},
        )
        for original in cases:
            with self.subTest(original=original):
                before = copy.deepcopy(original)
                merged, added, _ = settings.merge(original, FRAMEWORK_SETTINGS)
                rest, kept = settings.unmerge(merged, added)
                self.assertEqual(rest, before)
                self.assertEqual(original, before)
                self.assertEqual(kept, [])


class TestHooks(unittest.TestCase):
    def test_every_hook_in_the_settings_has_its_script(self):
        """Un hook dichiarato senza script blocca ogni modifica («script
        assente, blocco»); uno script non dichiarato si copia e non gira mai.
        Il comando passa per la codifica della shell: solo ASCII."""
        entries = settings.hooks(settings.HOOKS)["hooks"]["PreToolUse"]
        commands = [h["command"] for e in entries for h in e["hooks"]]
        named = {m for c in commands for m in re.findall(r"\.claude/hooks/(\w+)\.py", c)}
        on_disk = {p.stem for p in (FRAMEWORK / "hooks").glob("*.py")}
        self.assertEqual(named, set(settings.HOOKS))
        self.assertEqual(on_disk, set(settings.HOOKS))
        self.assertLessEqual(set(settings.OPTIONAL_HOOKS), set(settings.HOOKS))
        for c in commands:
            self.assertTrue(c.isascii(), c)
            self.assertIn("$CLAUDE_PROJECT_DIR/", c)


if __name__ == "__main__":
    unittest.main()
