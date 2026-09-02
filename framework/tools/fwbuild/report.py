"""Il rapporto di divergenza su molti progetti.

`doctor` risponde «questa installazione regge?». Questo risponde a una domanda
che il singolo non si pone e l'azienda sì: **quante versioni del metodo sono in
giro, e dove**. Su quaranta repository la divergenza non si vede guardando un
repository alla volta — si vede solo aggregando, ed è esattamente il difetto che
il framework esiste per evitare.

Non duplica nessuna verifica: chiama `doctor` su ogni progetto trovato e mette
in fila i risultati.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import doctor, kernel

MARKER = Path(".claude") / "framework.json"
# Le directory che non contengono progetti e costano care da attraversare.
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


@dataclass(frozen=True)
class Project:
    """Un'installazione trovata, con ciò che serve a confrontarla con le altre."""

    path: Path
    declared: str | None
    installed: list[str]
    findings: list[doctor.Finding]
    measure: doctor.Measure | None

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def version(self) -> str:
        """La versione da mostrare: quella dei file, non quella dichiarata.

        `framework.json` dice da dove il progetto è nato; la regione kernel dice
        cosa contiene adesso. Quando divergono conta la seconda — la prima si
        aggiorna dimenticandosene.
        """
        if self.installed:
            return "/".join(sorted(set(self.installed)))
        return self.declared or "?"

    @property
    def errors(self) -> int:
        return sum(1 for f in self.findings if f.severity == "ERROR")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARN")

    @property
    def drifted(self) -> bool:
        return any(f.code == "KERNEL_DRIFT" for f in self.findings)


@dataclass
class Survey:
    projects: list[Project] = field(default_factory=list)
    source_version: str | None = None

    @property
    def versions(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for p in self.projects:
            out[p.version] = out.get(p.version, 0) + 1
        return dict(sorted(out.items()))

    @property
    def behind(self) -> list[Project]:
        """I progetti che non sono sulla versione del sorgente.

        Senza una versione di sorgente non c'è un «indietro»: si riporta la
        distribuzione e basta, invece di eleggere a riferimento la versione più
        diffusa. La maggioranza non è un riferimento.
        """
        if self.source_version is None:
            return []
        return [p for p in self.projects if p.version != self.source_version]

    @property
    def clean(self) -> bool:
        return not self.behind and all(not p.findings for p in self.projects)


def discover(roots, depth: int = 2) -> list[Path]:
    """I progetti installati sotto questi percorsi.

    Si scende di `depth` livelli e non oltre: un rapporto di flotta si punta su
    una cartella di repository, non sul disco. Una ricerca senza fondo su una
    home renderebbe il comando inutilizzabile proprio dove serve.
    """
    found: list[Path] = []

    def walk(d: Path, left: int) -> None:
        if (d / MARKER).is_file():
            found.append(d)
            return
        if left <= 0:
            return
        try:
            children = sorted(c for c in d.iterdir() if c.is_dir())
        except OSError:
            return
        for c in children:
            if c.name not in SKIP:
                walk(c, left - 1)

    for root in roots:
        walk(Path(root), depth)
    return found


def _declared(root: Path) -> str | None:
    try:
        data = json.loads((root / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def _installed(root: Path) -> list[str]:
    out: list[str] = []
    claude = root / "CLAUDE.md"
    files = [claude] if claude.is_file() else []
    agents = root / ".claude" / "agents"
    if agents.is_dir():
        files += sorted(agents.glob("*.md"))
    for f in files:
        region = kernel.parse(f.read_text(encoding="utf-8"))
        if region is not None and region.version not in out:
            out.append(region.version)
    return out


def inspect(root: Path) -> Project:
    root = Path(root)
    claude = root / "CLAUDE.md"
    return Project(
        path=root,
        declared=_declared(root),
        installed=_installed(root),
        findings=doctor.check(root),
        measure=doctor.measure(claude.read_text(encoding="utf-8"))
        if claude.is_file()
        else None,
    )


def survey(roots, depth: int = 2, source_version: str | None = None) -> Survey:
    return Survey(
        projects=[inspect(p) for p in discover(roots, depth)],
        source_version=source_version,
    )


def as_dict(s: Survey) -> dict:
    return {
        "source_version": s.source_version,
        "projects": [
            {
                "path": str(p.path),
                "name": p.name,
                "version": p.version,
                "declared": p.declared,
                "errors": p.errors,
                "warnings": p.warnings,
                "drifted": p.drifted,
                "tokens": None if p.measure is None else p.measure.tokens,
                "findings": [
                    {"code": f.code, "severity": f.severity, "message": f.message}
                    for f in p.findings
                ],
            }
            for p in s.projects
        ],
        "versions": s.versions,
        "behind": [p.name for p in s.behind],
        "clean": s.clean,
    }
