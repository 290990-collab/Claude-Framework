"""Le verifiche di integrità di un'installazione.

Quattordici codici di rilievo: sette di gravità ERROR (PLACEHOLDER,
ROSTER_MISSING, SHARED_MISSING, STATE_MISSING, KERNEL_MISSING, FABLE, EXCLUSIVE)
e sette di gravità WARN (ROSTER_ORPHAN, KERNEL_DRIFT, COORDINATOR_LEAK,
SKILLS_MISSING, VERSION_MISMATCH, SETTINGS_MISSING, SHARED_ORPHAN).
Ogni codice è spiegato, con cosa farne, nella skill `framework-doctor`.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from . import kernel, profile

PLACEHOLDER_RE = re.compile(r"\{\{|DA COMPILARE")
ROUTING_AGENT_RE = re.compile(r"^\|[^|]*\|\s*`([a-z-]+)`\s*\|", re.MULTILINE)
FABLE_RE = re.compile(r"^model:\s*fable\s*$", re.MULTILINE)
SHARED_REF_RE = re.compile(r"\.claude/shared/([A-Za-z0-9_./-]+\.md)")
STATE_FILES = ("TODO.md", "status.md", "roadmap.md")
ORCHESTRATION = "shared/orchestration.md"

# Titoli che appartengono alla guida del coordinatore. Se ricompaiono in
# CLAUDE.md, ogni subagent li paga a ogni spawn senza poterli usare: è la
# separazione per destinatario che si sta riperdendo.
COORDINATOR_ONLY = (
    "Economia dei token — le dieci regole della delega",
    "Il ciclo del codice",
    "Come si scrive un prompt di delega",
    "Lo stato che si aggiorna da solo",
    "Scegliere fra agenti che sembrano vicini",
    "Roster di questo progetto",
)


def _source_version() -> str | None:
    """La versione del sorgente, dedotta dalla posizione del pacchetto.

    `fwbuild` vive in `framework/tools/`: la root del sorgente è due livelli
    sopra. Se non è raggiungibile il check si salta — il doctor deve restare
    utilizzabile senza il sorgente.
    """
    p = Path(__file__).resolve().parents[2] / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else None


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str


def _markdown_files(root: Path) -> list[Path]:
    """I file adattati al progetto, che vanno verificati.

    `.claude/skills/` è escluso: le skill sono file di framework copiati alla
    lettera, senza regione kernel né blocchi da compilare — e `framework-doctor`
    contiene per forza la stringa `DA COMPILARE`, perché ne spiega il rilievo.
    I file di stato in `docs/` sono inclusi: nascono da un template con
    segnaposto, e un template non compilato è indistinguibile da uno stato
    assente per chi lo legge a inizio sessione.
    """
    files = [root / "CLAUDE.md"]
    claude_dir = root / ".claude"
    if claude_dir.is_dir():
        skills = claude_dir / "skills"
        files += sorted(
            p for p in claude_dir.rglob("*.md") if skills not in p.parents
        )
    files += [root / "docs" / name for name in STATE_FILES]
    return [f for f in files if f.is_file()]


def check(root: Path) -> list[Finding]:
    root = Path(root)
    out: list[Finding] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        return [Finding("STATE_MISSING", "ERROR", "CLAUDE.md assente")]

    agents_dir = root / ".claude" / "agents"
    present = {p.stem for p in agents_dir.glob("*.md")} if agents_dir.is_dir() else set()

    # I file che nascono **con** una regione kernel. Le guide di `shared/` no:
    # si copiano e si compilano, non contengono metodo generato.
    tracked = {"CLAUDE.md", f".claude/{ORCHESTRATION}"} | {
        f".claude/agents/{name}.md" for name in present
    }

    texts = {
        f.relative_to(root).as_posix(): f.read_text(encoding="utf-8")
        for f in _markdown_files(root)
    }
    claude_text = texts["CLAUDE.md"]
    versions: dict[str, str] = {}
    referenced: set[str] = set()

    # La variante senza marker è legittima: nessun tracking, per scelta. Ma se
    # anche un solo file tracciato ce l'ha, l'installazione è tracciata, e un
    # file che li ha persi non è distinguibile da uno riscritto a mano.
    markers = any(kernel.parse(t) for rel, t in texts.items() if rel in tracked)

    for rel, text in texts.items():
        if PLACEHOLDER_RE.search(text):
            out.append(
                Finding("PLACEHOLDER", "ERROR", f"{rel}: segnaposto non compilato")
            )
        if FABLE_RE.search(text):
            out.append(Finding("FABLE", "ERROR", f"{rel}: model fable non disponibile"))
        status = kernel.verify(text)
        if status == "DRIFT":
            out.append(
                Finding("KERNEL_DRIFT", "WARN", f"{rel}: regione kernel modificata")
            )
        elif status == "MISSING" and markers and rel in tracked:
            out.append(
                Finding(
                    "KERNEL_MISSING",
                    "ERROR",
                    f"{rel}: marker rimossi — il metodo non è più verificabile",
                )
            )
        if rel in tracked:
            region = kernel.parse(text)
            if region is not None:
                versions[rel] = region.version
        # Il pointer si verifica ovunque, non solo in CLAUDE.md: le guide sono
        # citate dagli agenti, ed è lì che quasi tutti i pointer vivono.
        for ref in sorted(set(SHARED_REF_RE.findall(text))):
            referenced.add(ref)
            if not (root / ".claude" / "shared" / ref).is_file():
                out.append(
                    Finding(
                        "SHARED_MISSING",
                        "ERROR",
                        f"{rel} → .claude/shared/{ref}: referenziata ma assente",
                    )
                )

    # La tabella di routing è contenuto da coordinatore: vive nella sua guida.
    # Si ricade su CLAUDE.md solo dove quella guida non c'è (installazione
    # parziale, o progetto senza delega), così il roster resta verificabile.
    routed = set(ROUTING_AGENT_RE.findall(texts.get(f".claude/{ORCHESTRATION}", claude_text)))

    for name in sorted(routed - present):
        out.append(
            Finding(
                "ROSTER_MISSING",
                "ERROR",
                f"{name}: citato nella tabella di routing, file assente",
            )
        )
    for name in sorted(present - routed):
        out.append(
            Finding(
                "ROSTER_ORPHAN",
                "WARN",
                f"{name}: file presente, assente dalla tabella di routing",
            )
        )

    # Le versioni: prima fra loro, poi contro il sorgente. Nessun altro check
    # le vede — su un metodo vecchio l'hash torna, perché torna su quello.
    # È la biforcazione fra progetti, cioè il difetto che il framework esiste
    # per evitare.
    declared = sorted(set(versions.values()))
    if len(declared) > 1:
        common = max(declared, key=list(versions.values()).count)
        odd = sorted(rel for rel, v in versions.items() if v != common)
        out.append(
            Finding(
                "VERSION_MISMATCH",
                "WARN",
                f"progetto a v{common}, ma: "
                + ", ".join(f"{rel} v{versions[rel]}" for rel in odd),
            )
        )
    source = _source_version()
    if source is not None and declared and declared != [source]:
        out.append(
            Finding(
                "VERSION_MISMATCH",
                "WARN",
                f"installazione a v{'/'.join(declared)}, sorgente a v{source}: "
                "riallinea con framework-sync --down",
            )
        )

    # L'inverso di SHARED_MISSING. Una guida che nessuno cita è contesto
    # installato e mai aperto: il costo c'è, l'uso no.
    shared_dir = root / ".claude" / "shared"
    if shared_dir.is_dir():
        for p in sorted(shared_dir.rglob("*.md")):
            rel = p.relative_to(shared_dir).as_posix()
            if rel != "orchestration.md" and rel not in referenced:
                out.append(
                    Finding(
                        "SHARED_ORPHAN",
                        "WARN",
                        f".claude/shared/{rel}: installata e citata da nessuno",
                    )
                )

    for conflict in profile.check_exclusive(sorted(present)):
        out.append(
            Finding("EXCLUSIVE", "ERROR", f"agenti mutuamente esclusivi: {conflict}")
        )

    for name in STATE_FILES:
        if not (root / "docs" / name).is_file():
            out.append(Finding("STATE_MISSING", "ERROR", f"docs/{name} assente"))

    for skill in ("framework-doctor", "framework-sync"):
        if not (root / ".claude" / "skills" / skill / "SKILL.md").is_file():
            out.append(
                Finding(
                    "SKILLS_MISSING",
                    "WARN",
                    f".claude/skills/{skill}/ assente: la skill non è invocabile "
                    "in questo progetto",
                )
            )

    if present and not (root / ".claude" / "settings.json").is_file():
        out.append(
            Finding(
                "SETTINGS_MISSING",
                "WARN",
                ".claude/settings.json assente: i permessi del profilo — fra cui "
                "il divieto di leggere segreti — non sono in vigore",
            )
        )

    if present and f".claude/{ORCHESTRATION}" not in texts:
        out.append(
            Finding(
                "SHARED_MISSING",
                "ERROR",
                f".claude/{ORCHESTRATION} assente: senza, il coordinatore non ha "
                "le regole di delega",
            )
        )

    for heading in COORDINATOR_ONLY:
        if heading in claude_text:
            out.append(
                Finding(
                    "COORDINATOR_LEAK",
                    "WARN",
                    f'CLAUDE.md contiene "{heading}": è contenuto da coordinatore, '
                    f"pagato da ogni subagent a ogni spawn",
                )
            )

    return out
