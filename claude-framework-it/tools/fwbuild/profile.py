"""Profili di dominio: quali agenti e quali guide installare."""

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

# Lo stesso pattern del doctor: quello che lì è un rilievo, qui è la domanda
# "cosa serve installare perché quel rilievo non ci sia".
GUIDE_REF = re.compile(r"\.claude/shared/([A-Za-z0-9_./-]+\.md)")


@dataclass(frozen=True)
class Profile:
    """Un campo di lavoro: chi si installa, cosa si legge, cosa si rischia.

    `critical_surface` è la sola risposta che il profilo può dare da solo alla
    domanda del Passo 3.2 — «cosa rende il lavoro sbagliato anche a codice
    perfetto». Non installa nessun agente: la superficie di un campo è nota
    prima di conoscere il progetto, il revisore no.

    Non esiste un campo per gli agenti «da installare più tardi»: `on_demand`
    prometteva questo e `roster` li accodava comunque, cioè li installava. Un
    agente che il campo implica sta in `agents` e si vede; uno che non implica
    lo porta il questionario come extra, o `--activate` a valle.
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
    """Le guide che le schede di questi agenti citano.

    Il profilo elenca le guide del **campo**; un agente attivato come extra
    porta le sue, e nessuno le risolveva: la scheda finiva installata con un
    pointer morto, e il difetto si vedeva solo col doctor a installazione già
    scritta (`SHARED_MISSING`). Un pointer che l'agente non può seguire è peggio
    di assente — sta in un file che lui paga a ogni spawn.
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
