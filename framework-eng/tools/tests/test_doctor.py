import re
import tempfile
import unittest
from pathlib import Path

from fwbuild import assemble, doctor, kernel

AGENT_FM = "---\nname: {n}\nmodel: opus\neffort: high\n---\n"
# The source's version, not a literal: `VERSION_MISMATCH` compares the project
# with the source, and a fixed value would make the suite fail at the first
# VERSION bump.
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
        g.write_text("# guide", encoding="utf-8")
    (root / "docs").mkdir(parents=True)
    rows = "\n".join(f"| where | `{n}` | haiku |" for n in routing)
    if orchestration:
        # The routing table lives in the coordinator's guide, not in CLAUDE.md:
        # it is content the subagents must not pay for.
        (root / ".claude" / "shared" / "orchestration.md").write_text(
            assemble.build_document_from_text(
                "## Delegation\n",
                VERSION,
                "| Situation | Agent | Model |\n|---|---|---|\n" + rows + "\n",
                markers=markers,
            ),
            encoding="utf-8",
        )
    project = "## The project\n\nA trial project.\n"
    if placeholder:
        project += "\n[TO FILL IN] — module map\n"
    if leak:
        project += "\n## The code cycle\n\nExplorer, then architect.\n"
    (root / "CLAUDE.md").write_text(
        assemble.build_document_from_text("## Method\n", VERSION, project, markers=markers),
        encoding="utf-8",
    )
    for n in agents:
        model = "fable" if fable else "opus"
        fm = AGENT_FM.format(n=n).replace("model: opus", f"model: {model}")
        (root / ".claude" / "agents" / f"{n}.md").write_text(
            assemble.build_agent(
                fm, "## Method\n", "## Domain\n", VERSION, markers=markers
            ),
            encoding="utf-8",
        )
    if state:
        for f in ("TODO.md", "status.md", "roadmap.md"):
            (root / "docs" / f).write_text("# empty\n", encoding="utf-8")
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
                f.read_text(encoding="utf-8").replace("## Method", "## Other"),
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
        """framework-doctor explains the PLACEHOLDER finding and necessarily
        contains that string: scanning it would produce a false positive on
        every run."""
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d)
            (root / ".claude" / "skills" / "framework-doctor" / "SKILL.md").write_text(
                "The `PLACEHOLDER` finding flags a leftover `[TO FILL IN]`.\n",
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
        """Removing the markers is no less serious than rewriting the method
        inside the region: without markers, drift stops being visible."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            f = p / ".claude" / "agents" / "explorer.md"
            f.write_text(strip_markers(f.read_text(encoding="utf-8")), encoding="utf-8")
            self.assertIn("KERNEL_MISSING", codes(doctor.check(p)))

    def test_installation_without_markers_is_not_flagged(self):
        """The variant without tracking is a legitimate choice: no marker in
        any tracked file, no finding."""
        with tempfile.TemporaryDirectory() as d:
            self.assertNotIn("KERNEL_MISSING", codes(doctor.check(make_project(d, markers=False))))

    def test_detects_dangling_shared_pointer_in_an_agent(self):
        """Almost every pointer to a guide lives in the agents: checking them
        only in CLAUDE.md leaves the majority uncovered."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            f = p / ".claude" / "agents" / "explorer.md"
            f.write_text(
                f.read_text(encoding="utf-8") + "See `.claude/shared/core/absent.md`.",
                encoding="utf-8",
            )
            self.assertIn("SHARED_MISSING", codes(doctor.check(p)))

    def test_detects_unfilled_state_template(self):
        """A state template copied and not filled in is indistinguishable from
        absent state for whoever reads it at session start."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            (p / "docs" / "TODO.md").write_text("- [ ] {{active task}}", encoding="utf-8")
            self.assertIn("PLACEHOLDER", codes(doctor.check(p)))

    def _rewrap(self, f, version):
        """Rewrites a file's kernel region at another version, leaving the hash
        consistent: it is the case no other check sees."""
        text = f.read_text(encoding="utf-8")
        r = kernel.parse(text)
        f.write_text(
            text[: r.start] + kernel.wrap(r.body, version) + text[r.end + 1 :],
            encoding="utf-8",
        )

    def test_detects_missing_settings_file(self):
        """`settings.json` carries the profile's permissions, among them the
        prohibition on reading secrets: absent, that prohibition does not
        exist."""
        with tempfile.TemporaryDirectory() as d:
            found = doctor.check(make_project(d, settings=False))
            self.assertIn("SETTINGS_MISSING", codes(found))

    def test_detects_shared_guide_nobody_cites(self):
        """The inverse of SHARED_MISSING: a guide installed and never cited is
        context paid for and never opened."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, guides=("core/never-cited.md",))
            self.assertIn("SHARED_ORPHAN", codes(doctor.check(p)))

    def test_cited_shared_guide_is_not_an_orphan(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, guides=("core/cited.md",))
            f = p / "CLAUDE.md"
            f.write_text(
                f.read_text(encoding="utf-8") + "`.claude/shared/core/cited.md`",
                encoding="utf-8",
            )
            self.assertNotIn("SHARED_ORPHAN", codes(doctor.check(p)))

    def test_detects_version_skew_between_documents(self):
        """Two documents of the same project at different versions: the hash
        matches on both, because each matches its own method."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            self._rewrap(p / ".claude" / "agents" / "explorer.md", "0.3.0")
            self.assertIn("VERSION_MISMATCH", codes(doctor.check(p)))

    def test_detects_installation_behind_the_source(self):
        """An old but internally consistent method: it is the fork between
        projects, and before this check no finding saw it."""
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d)
            tracked = [p / "CLAUDE.md", p / ".claude" / "shared" / "orchestration.md"]
            tracked += list((p / ".claude" / "agents").glob("*.md"))
            for f in tracked:
                self._rewrap(f, "0.3.0")
            self.assertEqual(codes(doctor.check(p)), {"VERSION_MISMATCH"})


if __name__ == "__main__":
    unittest.main()
