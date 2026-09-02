"""Entry point: python -m fwbuild <command>."""

import argparse
import json
import os
import sys
from pathlib import Path

from . import doctor, report, source

# Claude Opus 5 list price, uncached input tokens, in dollars per million. It
# is a declared default, not a truth: prices change and caching lowers the real
# figure. `--price` exists so that whoever reads chooses the number.
PRICE_PER_MTOK = 5.00
WORKING_DAYS = 22


def _force_utf8_stdout() -> None:
    """On Windows, Python's stdout uses the local code page (cp1252), which
    does not cover all the characters in the messages. Without this, a finding
    with an out-of-table character makes the command fail instead of printing
    it."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def _bases(path: Path | None) -> list[Path]:
    """The source search order. It is the impure part, and it is here on purpose.

    A path that was given is the **only** candidate: if it does not hold it is
    an error, not a fallback onto the next one.
    """
    if path is not None:
        return [path]
    env = os.environ.get("CLAUDE_FRAMEWORK")
    return [
        Path.cwd(),
        *([Path(env)] if env else []),
        Path.home() / ".claude" / "framework",
    ]


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    parser = argparse.ArgumentParser(prog="fwbuild")
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("doctor", help="check an installation")
    d.add_argument("path", type=Path)
    # A complete installation has no findings of any severity: --strict is that
    # rule made mechanical, for CI and for Step 6.
    d.add_argument("--strict", action="store_true", help="exit 1 even with warnings only")
    d.add_argument("--json", action="store_true", help="findings and measures as JSON, for CI")

    r = sub.add_parser("report", help="method divergence across several projects")
    r.add_argument("paths", type=Path, nargs="+")
    r.add_argument(
        "--depth", type=int, default=2, help="how many levels down to look for projects"
    )
    r.add_argument("--json", action="store_true", help="report as JSON, for CI")
    r.add_argument(
        "--strict", action="store_true", help="exit 1 if a project diverges or has findings"
    )

    c = sub.add_parser("cost", help="what the installed CLAUDE.md costs")
    c.add_argument("path", type=Path)
    c.add_argument("--spawns", type=int, default=100, help="spawns per day per person")
    c.add_argument("--devs", type=int, default=1, help="how many people work on the repo")
    c.add_argument(
        "--price", type=float, default=PRICE_PER_MTOK, help="$ per million input tokens"
    )

    s = sub.add_parser("source", help="resolve and validate the source root")
    s.add_argument("path", type=Path, nargs="?")

    args = parser.parse_args(argv)

    if args.command == "source":
        try:
            root = source.resolve(_bases(args.path))
        except LookupError as err:
            print(err)
            return 1
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        print(f"{root} v{version}")
        return 0

    if args.command == "doctor":
        findings = doctor.check(args.path)
        code = 1 if args.strict or any(f.severity == "ERROR" for f in findings) else 0
        if args.json:
            print(json.dumps(_report(args.path, findings), ensure_ascii=False, indent=2))
            return code
        if not findings:
            print("OK — no findings")
            return 0
        for f in findings:
            print(f"{f.severity:5} {f.code:16} {f.message}")
        return code

    if args.command == "cost":
        return _cost(args.path, args.spawns, args.devs, args.price)

    if args.command == "report":
        s = report.survey(args.paths, args.depth, _source_version())
        if args.json:
            print(json.dumps(report.as_dict(s), ensure_ascii=False, indent=2))
        else:
            _print_survey(s)
        return 1 if args.strict and not s.clean else 0
    return 0


def _measure(path: Path) -> doctor.Measure | None:
    """The measurement of an installation's CLAUDE.md, or None if absent.

    The missing file is not an error of this layer: the doctor already reports
    it as STATE_MISSING, and duplicating the message would give two entries for
    one fact.
    """
    claude_md = Path(path) / "CLAUDE.md"
    if not claude_md.is_file():
        return None
    return doctor.measure(claude_md.read_text(encoding="utf-8"))


def _report(path: Path, findings: list[doctor.Finding]) -> dict:
    m = _measure(path)
    return {
        "path": str(path),
        "ok": not findings,
        "errors": sum(1 for f in findings if f.severity == "ERROR"),
        "warnings": sum(1 for f in findings if f.severity == "WARN"),
        "measure": None
        if m is None
        else {
            "kernel_words": m.kernel_words,
            "project_words": m.project_words,
            "total_words": m.total_words,
            "tokens": m.tokens,
            "split": m.has_region,
        },
        "findings": [
            {"code": f.code, "severity": f.severity, "message": f.message}
            for f in findings
        ],
    }


def _n(value: float, decimals: int = 0) -> str:
    """A number with thousands separators, in the English convention."""
    return f"{value:,.{decimals}f}"


def _cost(path: Path, spawns: int, devs: int, price: float) -> int:
    """The size of CLAUDE.md translated into a budget line.

    The full cost, that is, the upper bound: prompt caching lowers the real
    figure and is not measurable from here. Every assumption is printed
    alongside the number — a total without its assumptions is a number nobody
    can contest.
    """
    m = _measure(path)
    if m is None:
        print(f"{path}: CLAUDE.md absent — nothing to measure")
        return 1

    per_day = m.tokens * spawns * devs
    daily = per_day / 1_000_000 * price
    people = "person" if devs == 1 else "people"

    print(f"CLAUDE.md: {_n(m.total_words)} words ≈ {_n(m.tokens)} tokens, paid at every spawn.")
    if m.has_region:
        print(
            f"  of which kernel {_n(m.kernel_words)} (with a ceiling) and project "
            f"{_n(m.project_words)} (without)."
        )
    print(
        f"{_n(spawns)} spawns a day × {devs} {people} = "
        f"{_n(per_day / 1_000_000, 1)} million tokens a day of common context alone."
    )
    print(
        f"At ${_n(price, 2)}/Mtok: ${_n(daily, 2)} a day, "
        f"${_n(daily * WORKING_DAYS, 2)} a month ({WORKING_DAYS} working days)."
    )
    print(
        "Full cost: prompt caching lowers it. Claude Opus 5 list price (input) — "
        "change it with --price."
    )
    return 0


def _source_version() -> str | None:
    """The version of the source this command runs from.

    It is the report's reference: without it, divergence has no direction and
    stays a distribution. The most widespread version is not elected as a
    reference — the majority is not a reference.
    """
    p = Path(__file__).resolve().parents[2] / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else None


def _print_survey(s) -> None:
    """The report in readable form: the projects first, then what follows.

    The per-project row is for finding which one to fix; the last two lines are
    the answer to the question a single person does not ask — how many versions
    of the method are out there.
    """
    if not s.projects:
        print("no installation found (looking for .claude/framework.json)")
        return

    width = max([len("project")] + [len(p.name) for p in s.projects])
    print(f"{len(s.projects)} installations\n")
    print(f"{'project':<{width}}  {'version':<10} {'findings':<10} CLAUDE.md")
    for p in sorted(s.projects, key=lambda p: p.name):
        mark = " " if s.source_version in (None, p.version) else "!"
        counts = " ".join(
            part
            for part in (
                f"{p.errors}E" if p.errors else "",
                f"{p.warnings}W" if p.warnings else "",
            )
            if part
        ) or "-"
        size = "-" if p.measure is None else f"{_n(p.measure.tokens)} tok"
        print(f"{p.name:<{width}}  {p.version:<9}{mark} {counts:<10} {size}")

    spread = ", ".join(f"{v} ({n})" for v, n in s.versions.items())
    print(f"\nVersions out there: {spread}", end="")
    print(f" — source at {s.source_version}" if s.source_version else "")
    drift = sum(1 for p in s.projects if p.drifted)
    err = sum(1 for p in s.projects if p.errors)
    print(
        f"Diverging from the source: {len(s.behind)} · with kernel drift: {drift} · "
        f"with errors: {err}"
    )
    if s.behind:
        print(
            "To realign with framework-sync --down: "
            + ", ".join(sorted(p.name for p in s.behind))
        )
