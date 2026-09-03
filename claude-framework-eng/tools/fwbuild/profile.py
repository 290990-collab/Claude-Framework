"""Domain profiles: which agents and which guides to install."""

import re
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ALWAYS = [
    "explorer",
    "architect",
    "implementer",
    "tester",
    "refactorer",
    "final-reviewer",
]

EXCLUSIVE = [("deploy", "infra")]

# The same pattern as the doctor's: what is a finding there is, here, the
# question "what has to be installed so that finding does not exist".
GUIDE_REF = re.compile(r"\.claude/shared/([A-Za-z0-9_./-]+\.md)")


@dataclass(frozen=True)
class Profile:
    """A field of work: who is installed, what is read, what is at risk.

    `critical_surface` is the only answer a profile can give on its own to the
    question of Step 3.2 — "what makes the work wrong even with perfect code".
    It installs no agent: a field's surface is known before knowing the
    project, its reviewer is not.

    There is no field for agents "to be installed later": `on_demand` promised
    that and `roster` appended them anyway, which means it installed them. An
    agent the field implies belongs in `agents`, where it is visible; one the
    field does not imply is brought in by the questionnaire as an extra, or by
    `--activate` afterwards.
    """

    name: str
    agents: list[str]
    shared: list[str]
    cycles: list[str]
    settings: dict
    critical_surface: str = ""


def load(path: Path) -> Profile:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Profile(
        name=data["name"],
        agents=list(data.get("agents", [])),
        shared=list(data.get("shared", [])),
        cycles=list(data.get("cycles", [])),
        settings=dict(data.get("settings", {})),
        critical_surface=data.get("critical_surface", ""),
    )


def roster(profile: Profile, extras: list[str], drop: list[str]) -> list[str]:
    droppable = set(drop) - set(ALWAYS)
    out: list[str] = []
    for name in ALWAYS + profile.agents + list(extras):
        if name not in out and name not in droppable:
            out.append(name)
    return out


def check_exclusive(agents: list[str]) -> list[str]:
    present = set(agents)
    return [f"{a} + {b}" for a, b in EXCLUSIVE if a in present and b in present]


def required_guides(framework_root: Path, agents: Sequence[str]) -> list[str]:
    """The guides these agents' cards cite.

    The profile lists the guides of the **field**; an agent activated as an
    extra brings its own, and nothing resolved them: the card ended up
    installed with a dead pointer, and the defect was visible only with the
    doctor, on an already written installation (`SHARED_MISSING`). A pointer
    the agent cannot follow is worse than an absent one — it sits in a file it
    pays for at every spawn.
    """
    out: list[str] = []
    for name in agents:
        src = framework_root / "agents" / f"{name}.md"
        if not src.is_file():
            continue
        for ref in GUIDE_REF.findall(src.read_text(encoding="utf-8")):
            if ref not in out:
                out.append(ref)
    return sorted(out)
