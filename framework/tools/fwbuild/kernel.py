"""Regione kernel: normalizzazione, hash e marker.

Il marker delimita il metodo generato dentro un file adattato a mano.
L'hash copre il solo corpo normalizzato: fine riga e spazi in coda non
contano come modifica, il testo sì.
"""

import hashlib
import re
from dataclasses import dataclass

OPEN_RE = re.compile(
    r"<!-- FRAMEWORK:KERNEL v(?P<version>\S+) sha256:(?P<declared>[0-9a-f]{8}) "
    r"— generato, non modificare a mano -->"
)
CLOSE = "<!-- /FRAMEWORK:KERNEL -->"


@dataclass(frozen=True)
class KernelRegion:
    version: str
    declared: str
    body: str
    start: int
    end: int


def normalize(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    joined = "\n".join(line.rstrip() for line in lines).strip("\n")
    return joined + "\n" if joined else "\n"


def digest(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:8]


def wrap(body: str, version: str) -> str:
    body_n = normalize(body)
    marker = (
        f"<!-- FRAMEWORK:KERNEL v{version} sha256:{digest(body_n)} "
        f"— generato, non modificare a mano -->"
    )
    return f"{marker}\n{body_n}{CLOSE}\n"


def parse(text: str) -> KernelRegion | None:
    m = OPEN_RE.search(text)
    if not m:
        return None
    newline = text.find("\n", m.end())
    if newline == -1:
        return None
    body_start = newline + 1
    close_at = text.find(CLOSE, body_start)
    if close_at == -1:
        return None
    return KernelRegion(
        version=m.group("version"),
        declared=m.group("declared"),
        body=normalize(text[body_start:close_at]),
        start=m.start(),
        end=close_at + len(CLOSE),
    )


def verify(text: str) -> str:
    region = parse(text)
    if region is None:
        return "MISSING"
    return "OK" if digest(region.body) == region.declared else "DRIFT"
