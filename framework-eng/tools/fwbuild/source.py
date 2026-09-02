"""Finding and validating the source root.

A downloadable product cannot hard-code one machine's path: you search in order
and validate before writing. The search is **pure** — the candidates are
assembled by the caller — because it is the only way to test it without
depending on where the framework running the tests lives.
"""

from collections.abc import Sequence
from pathlib import Path

# What the installation cannot even begin without.
REQUIRED = (
    "VERSION",
    "method",
    "coordinator",
    "agents",
    "profiles",
    "templates",
    "skills",
    "tools/fwbuild",
)


def missing(root: Path) -> list[str]:
    """The mandatory entries that are absent. Empty = it is a framework root."""
    return [r for r in REQUIRED if not (Path(root) / r).exists()]


def resolve(bases: Sequence[Path]) -> Path:
    """The first valid root, trying `<base>` and then `<base>/framework`.

    The two shapes — source copied into the project and single master — are
    covered by the same probe, without one more rule.

    "Path given but invalid: an error, no fallback" is not a special case in
    here: it is the caller that, having one, passes a single candidate. A
    silent fallback masks a wrong path.
    """
    tried = []
    for base in bases:
        for cand in (Path(base), Path(base) / "framework"):
            gaps = missing(cand)
            if not gaps:
                return cand
            tried.append(
                f"{cand}: "
                + ("absent" if not cand.is_dir() else f"missing {', '.join(gaps)}")
            )
    raise LookupError("no valid source among:\n  " + "\n  ".join(tried))


def reference(project_root: Path, framework_root: Path) -> str:
    """How `.claude/framework.json` must cite the source.

    The first of the three supported ways is the source **inside** the project:
    there an absolute path is the machine of whoever installed it, and the
    first clone finds a `source` that does not exist. Relative to the project
    root, instead, it travels with the repository. Outside the project a
    relative path does not hold — the depth of the clone is unknown — and the
    absolute one remains the only writable form.

    It is here and not in the skill because the skill already prescribed it, in
    prose, and that is exactly how the rule came to be disregarded.
    """
    project_root = Path(project_root).resolve()
    framework_root = Path(framework_root).resolve()
    if framework_root == project_root or project_root in framework_root.parents:
        return framework_root.relative_to(project_root).as_posix() or "."
    return str(framework_root)


def dereference(project_root: Path, recorded: str) -> Path:
    """The inverse: the `source` read from `framework.json` as a real path.

    A relative path resolves against the project root, not against the working
    directory: `framework-doctor` and `framework-sync` run from `<FW>/tools`,
    not from `<PRJ>`.
    """
    p = Path(recorded)
    return p if p.is_absolute() else (Path(project_root) / p).resolve()
