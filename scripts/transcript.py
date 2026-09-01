"""Misura chi paga cosa, leggendo i transcript di Claude Code.

**D0.** Senza un numero, «CLAUDE.md è pagata a ogni spawn» resta un argomento.
Claude Code scrive un `.jsonl` per sessione in `~/.claude/projects/<progetto>/`
e uno per ogni subagent in `<sessione>/subagents/`; i costi stanno in
`message.usage` delle entrate `assistant`.

I due insiemi sono **disgiunti**: il transcript del coordinatore non contiene
entrate `isSidechain`. Sommarli non conta niente due volte.

stdlib pura, come il resto del tooling. Sta fuori da `framework/`: è materiale
di lavoro finché non si è guadagnato un posto nel pacchetto.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


@dataclass
class Leg:
    """Un ramo di sessione: il coordinatore, o un subagent."""

    name: str
    effort: str = ""
    turns: int = 0
    human_turns: int = 0
    tools: int = 0
    # Il prompt del **primo** turno: è ciò che lo spawn carica prima di lavorare
    # — kernel comune, scheda dell'agente, prompt di delega. È il numero che la
    # tesi del framework mette in gioco.
    spawn_context: int = 0
    input: int = 0
    cache_creation: int = 0
    cache_read: int = 0
    output: int = 0

    @property
    def total(self) -> int:
        return self.input + self.cache_creation + self.cache_read + self.output


@dataclass
class Session:
    name: str
    coordinator: Leg
    subagents: list[Leg] = field(default_factory=list)

    @property
    def subagent_total(self) -> int:
        return sum(a.total for a in self.subagents)

    @property
    def total(self) -> int:
        return self.coordinator.total + self.subagent_total


def _is_human(entry: dict) -> bool:
    """Un intervento umano, non un risultato di tool né un'iniezione di sistema.

    D1 conta gli interventi umani: un risultato di tool è un'entrata `user`, e
    contarlo gonfierebbe proprio la metrica del confronto.
    """
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    return isinstance(content, list) and not any(
        isinstance(p, dict) and p.get("type") == "tool_result" for p in content
    )


def read_leg(path: Path, name: str) -> Leg:
    leg = Leg(name)
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # una riga tronca non deve perdere il resto della sessione
        if _is_human(entry):
            leg.human_turns += 1
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        leg.turns += 1
        leg.effort = leg.effort or entry.get("effort") or ""
        if leg.spawn_context == 0:
            leg.spawn_context = sum(usage.get(k, 0) for k in KINDS)
        leg.input += usage.get("input_tokens", 0)
        leg.cache_creation += usage.get("cache_creation_input_tokens", 0)
        leg.cache_read += usage.get("cache_read_input_tokens", 0)
        leg.output += usage.get("output_tokens", 0)
        leg.tools += sum(
            1
            for p in message.get("content", [])
            if isinstance(p, dict) and p.get("type") == "tool_use"
        )
    return leg


def _subagent_name(path: Path) -> str:
    """Come si chiama il ramo: il ruolo se dichiarato, altrimenti l'id.

    `attributionAgent` è il nome dell'agente, `attributionSkill` la skill che
    l'ha lanciato: senza il secondo, due spawn dello stesso ruolo per motivi
    diversi risultano indistinguibili.

    L'`agentId` è già sulla prima riga, l'attribuzione compare dal primo turno
    `assistant`: fermarsi alla prima riga utile darebbe sempre l'id opaco.
    """
    agent_id = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        agent = entry.get("attributionAgent")
        if agent:
            skill = entry.get("attributionSkill")
            return f"{agent}/{skill}" if skill else agent
        agent_id = agent_id or entry.get("agentId") or ""
    return agent_id or path.stem


def read_session(main: Path) -> Session:
    """Il coordinatore più i suoi subagent, se ne ha."""
    main = Path(main)
    session = Session(main.stem, read_leg(main, "coordinatore"))
    subagents = main.with_suffix("") / "subagents"
    if subagents.is_dir():
        for p in sorted(subagents.glob("*.jsonl")):
            session.subagents.append(read_leg(p, _subagent_name(p)))
    return session


def _n(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def report(session: Session) -> str:
    rows = [("coordinatore", session.coordinator)] + [(a.name, a) for a in session.subagents]
    width = max(len(n) for n, _ in rows)
    out = [
        f"sessione {session.name}",
        "",
        f"  {'ramo':<{width}}  {'turni':>6} {'umani':>6} {'tool':>5} "
        f"{'contesto':>10} {'totale':>12}",
    ]
    for name, leg in rows:
        out.append(
            f"  {name:<{width}}  {leg.turns:>6} {leg.human_turns:>6} {leg.tools:>5} "
            f"{_n(leg.spawn_context):>10} {_n(leg.total):>12}"
        )

    total = session.total
    share = 100 * session.subagent_total / total if total else 0.0
    spawn = sum(a.spawn_context for a in session.subagents)
    out += [
        "",
        f"  totale di sessione   {_n(total)} token",
        f"  ripartizione         coordinatore {100 - share:.0f}% · "
        f"subagent {share:.0f}% su {len(session.subagents)} spawn",
    ]
    if session.subagents:
        out.append(
            f"  caricato agli spawn  {_n(spawn)} token — contesto pagato prima "
            "che un subagent lavori"
        )
    return "\n".join(out)


CSV_HEADER = (
    "sessione", "ramo", "turni", "umani", "tool",
    "contesto", "input", "cache_creation", "cache_read", "output", "totale",
)


def csv_rows(sessions: list[Session]) -> list[tuple]:
    """Una riga per ramo: è la forma che serve per confrontare N sessioni.

    Il rapporto testuale si legge una sessione alla volta; D1 ne mette a
    confronto decine, appaiate.
    """
    rows = [CSV_HEADER]
    for s in sessions:
        for leg in [s.coordinator, *s.subagents]:
            rows.append((
                s.name, leg.name, leg.turns, leg.human_turns, leg.tools,
                leg.spawn_context, leg.input, leg.cache_creation,
                leg.cache_read, leg.output, leg.total,
            ))
    return rows


def _ask(text: str) -> str:
    """La richiesta vera dentro un'entrata `user`, spogliata delle iniezioni.

    Molte entrate `user` non le ha scritte l'utente: notifiche di task, output
    di comandi locali, riprese di sessione. Altre — `<ide_opened_file>` — sono
    **anteposte** a una richiesta vera: scartare l'entrata intera perderebbe il
    task invece del rumore. Quindi si toglie ciò che è marcato e si guarda cosa
    resta.
    """
    text = " ".join(text.split())
    while True:
        stripped = re.sub(r"^<([a-zA-Z][\w-]*)>.*?</\1>\s*", "", text, flags=re.DOTALL)
        # solo i tag davvero autochiusi: `/?` mangerebbe anche le aperture,
        # spezzando la coppia e lasciando il testo interno come se fosse una richiesta
        stripped = re.sub(r"^<[a-zA-Z][\w-]*\s*/>\s*", "", stripped)
        if stripped == text:
            return "" if text.startswith(("<", "/", CONTINUATION)) else text
        text = stripped


CONTINUATION = "This session is being continued"


def prompts(path: Path) -> list[str]:
    """Le richieste umane di una sessione, in ordine.

    Il corpus dei task di D1 va estratto dal lavoro già fatto: «rappresentativi
    del lavoro effettivo» non è una qualità che si possa inventare a tavolino.
    """
    out = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not _is_human(entry):
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, list):
            content = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            )
        text = _ask(content or "")
        if text:
            out.append(text)
    return out


def _sessions(target: Path) -> list[Path]:
    target = Path(target).expanduser()
    return [target] if target.is_file() else sorted(target.glob("*.jsonl"))


def main(argv: list[str]) -> int:
    # Come in `fwbuild.cli`: su Windows lo stdout usa la codepage locale, che
    # non copre i caratteri del rapporto.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    modes = {a for a in argv if a.startswith("--")}
    targets = [a for a in argv if not a.startswith("--")]
    if not targets or modes - {"--csv", "--prompts"}:
        print(
            "uso: python scripts/transcript.py [--csv|--prompts] "
            "<sessione.jsonl | cartella progetto>"
        )
        return 1
    paths = _sessions(Path(targets[0]))
    if not paths:
        print(f"nessun transcript in {targets[0]}")
        return 1

    if "--prompts" in modes:
        for path in paths:
            for text in prompts(path):
                print(f"{path.stem[:8]}\t{text[:160]}")
        return 0
    if "--csv" in modes:
        for row in csv_rows([read_session(p) for p in paths]):
            print(";".join(str(c) for c in row))
        return 0
    for path in paths:
        print(report(read_session(path)))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
