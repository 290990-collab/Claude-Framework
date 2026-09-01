"""Profili di dominio: quali agenti e quali guide installare."""

import tomllib
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


@dataclass(frozen=True)
class Profile:
    name: str
    agents: list[str]
    shared: list[str]
    cycles: list[str]
    on_demand: list[str]
    settings: dict


def load(path: Path) -> Profile:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Profile(
        name=data["name"],
        agents=list(data.get("agents", [])),
        shared=list(data.get("shared", [])),
        cycles=list(data.get("cycles", [])),
        on_demand=list(data.get("on_demand", [])),
        settings=dict(data.get("settings", {})),
    )


def roster(profile: Profile, extras: list[str], drop: list[str]) -> list[str]:
    droppable = set(drop) - set(ALWAYS)
    out: list[str] = []
    for name in ALWAYS + profile.agents + list(extras) + profile.on_demand:
        if name not in out and name not in droppable:
            out.append(name)
    return out


def check_exclusive(agents: list[str]) -> list[str]:
    present = set(agents)
    return [f"{a} + {b}" for a, b in EXCLUSIVE if a in present and b in present]
