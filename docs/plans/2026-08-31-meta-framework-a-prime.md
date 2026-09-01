# Meta-framework A′ — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Costruire il framework generale per Claude Code descritto nella spec —
kernel versionato e hashato, 19 agenti, guide on-demand, profili di dominio,
tre skill di ciclo di vita — con il tooling che ne verifica l'integrità.

**Architecture:** I sorgenti stanno in `framework/` in moduli separati. Un
tool Python (`tools/fwbuild/`) assembla `CLAUDE.md` e gli agenti inserendo il
metodo dentro una regione delimitata da marker con hash sha256, e verifica le
installazioni esistenti rilevando il drift. La variante **B** è lo stesso build
con i marker disattivati.

**Tech Stack:** Python 3.12 **stdlib puro** (`hashlib`, `tomllib`, `pathlib`,
`argparse`, `re`, `unittest`). Nessuna dipendenza da installare — vincolo dalle
direttive globali dell'utente: nessuna installazione senza conferma esplicita.
Markdown per il contenuto del framework. TOML per profili e varianti.

**Spec:** [docs/design/2026-08-31-meta-framework.md](../design/2026-08-31-meta-framework.md)

> ## ⚠️ Piano eseguito — documento storico
>
> Tutti i task sono stati completati (Task 0 saltato: niente git). Il codice
> reale è divergente da quanto scritto qui, per queste decisioni prese durante
> l'esecuzione. **La fonte di verità è il codice, non questo piano.**
>
> | deviazione | motivo |
> |---|---|
> | `tools/` è dentro `framework/` | la cartella copiata dev'essere autosufficiente |
> | `build_claude_md` → `build_document` | costruisce due tipi di documento, non solo `CLAUDE.md` |
> | kernel diviso: `method/` + `coordinator/` | `CLAUDE.md` è letto da ogni subagent: il 39% era contenuto da coordinatore, pagato a ogni spawn e inutilizzabile da chi esegue |
> | aggiunti `cycles/`, `SKILLS_MISSING`, `COORDINATOR_LEAK` | gap trovati nell'audit finale |
> | rimosso `build/variants.toml` | configurazione che nessuno leggeva |
> | Task 5: solo `doctor`, niente `build` | la generazione richiede giudizio e vive nella skill |
> | 74 test, non 48 | verifiche aggiunte con la separazione per destinatario |

## Global Constraints

- **Economia dei token è il vincolo di prima classe.** Ogni file che finisce in
  `CLAUDE.md` è pagato a ogni spawn di agente: densità massima, zero prosa di
  cortesia, zero ripetizioni fra sezioni.
- **Comunicazione fra agenti telegrafica in entrambe le direzioni** (spec §6.2),
  con posizionamento per primacy/recency: **i bordi sono per le istruzioni, il
  centro per il materiale di consultazione**. Coordinatore→agente nell'ordine
  `TASK · DONE QUANDO · VINCOLI · MATERIALE (file:riga) · DONE QUANDO ripetuto`;
  agente→coordinatore con lo schema `CONF/CHANGED/ASSUMED/RISK/UNVERIFIED`,
  ≤150 parole, che non va riordinato (`CONF` apre il giudizio, `UNVERIFIED`
  chiude su ciò da non dimenticare).
- **Mai generare `model: fable`.** `architect` = `model: opus`, `effort: xhigh`.
- **Ogni agente si regge da solo**: nessun agente si definisce per riferimento a
  un altro. Il metodo comune arriva dalla regione kernel del suo file.
- **Si installa quello che serve, non si cancella nulla** (spec §5.1): il master
  di ogni agente resta in `framework/agents/`.
- **Pochi test sensati, mai molti test deboli** (spec §6.3): un test che
  passerebbe anche col difetto presente non si scrive.
- **Lingua:** contenuto del framework in italiano (le varianti EN sono
  artefatti 3 e 4, fuori da questo piano). Codice, identificatori e nomi di file
  in inglese.
- **Deviazione dalla spec, deliberata:** i profili sono `.toml`, non `.yml`.
  Motivo: `tomllib` è stdlib in Python 3.12, PyYAML no — e installarlo
  richiederebbe conferma. Aggiornare la spec §4 di conseguenza (Task 11).
- **Commit:** la cartella non è un repo git. Se il Task 0 viene rifiutato, tutti
  gli step "Commit" del piano si saltano; nient'altro cambia.

---

### Task 0: Repository git (richiede approvazione dell'utente)

**Files:**
- Create: `.gitignore`

**Interfaces:**
- Produces: repo git inizializzato, su cui poggiano tutti gli step "Commit".

Task opzionale. `framework-sync --su` (promozione di una modifica locale verso il
sorgente) è molto più semplice sopra una storia git che sopra confronti di file,
ma nulla nel resto del piano lo richiede.

- [ ] **Step 1: Chiedere conferma all'utente**

Se rifiutata: marcare il task come saltato e ignorare ogni step "Commit" nei
task successivi. Non reinizializzare git in autonomia.

- [ ] **Step 2: Inizializzare il repo**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
git init
git branch -M main
```

- [ ] **Step 3: Creare `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
_build/
```

- [ ] **Step 4: Primo commit**

```bash
git add .gitignore docs/
git commit -m "chore: init framework workshop with design spec and plan"
```

---

### Task 1: `fwbuild.kernel` — normalizzazione, hash, marker

**Files:**
- Create: `tools/fwbuild/__init__.py` (vuoto)
- Create: `tools/tests/__init__.py` (vuoto — **necessario**: senza, i test non si
  importano fra loro e `discover -t .` non mette `tools/` su `sys.path`)
- Create: `tools/fwbuild/kernel.py`
- Test: `tools/tests/test_kernel.py`

**Interfaces:**
- Produces:
  - `normalize(text: str) -> str`
  - `digest(text: str) -> str` (sha256 esadecimale, primi 8 caratteri)
  - `wrap(body: str, version: str) -> str`
  - `parse(text: str) -> KernelRegion | None` con
    `KernelRegion(version: str, declared: str, body: str, start: int, end: int)`
  - `verify(text: str) -> str` che ritorna `"OK"` | `"DRIFT"` | `"MISSING"`

Il cuore di A′. `normalize` decide cosa conta come modifica: fine riga e spazi in
coda non sono drift, il testo sì.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tools/tests/test_kernel.py
import unittest
from fwbuild import kernel


class TestNormalize(unittest.TestCase):
    def test_crlf_becomes_lf(self):
        self.assertEqual(kernel.normalize("a\r\nb"), "a\nb\n")

    def test_trailing_whitespace_stripped(self):
        self.assertEqual(kernel.normalize("a   \nb\t\n"), "a\nb\n")

    def test_ends_with_single_newline(self):
        self.assertEqual(kernel.normalize("a\n\n\n"), "a\n")


class TestDigest(unittest.TestCase):
    def test_stable_across_line_endings(self):
        self.assertEqual(kernel.digest("x\ny\n"), kernel.digest("x\r\ny\r\n"))

    def test_stable_across_trailing_whitespace(self):
        self.assertEqual(kernel.digest("x\ny\n"), kernel.digest("x  \ny \n"))

    def test_changes_when_text_changes(self):
        self.assertNotEqual(kernel.digest("x\n"), kernel.digest("y\n"))

    def test_is_eight_hex_chars(self):
        d = kernel.digest("x\n")
        self.assertEqual(len(d), 8)
        self.assertTrue(all(c in "0123456789abcdef" for c in d))


class TestWrapParse(unittest.TestCase):
    def test_round_trip_preserves_body(self):
        body = "## Metodo\n\nRegola uno.\n"
        region = kernel.parse(kernel.wrap(body, "1.0.0"))
        self.assertEqual(region.body, kernel.normalize(body))
        self.assertEqual(region.version, "1.0.0")

    def test_parse_returns_none_without_marker(self):
        self.assertIsNone(kernel.parse("nessun marker qui\n"))

    def test_wrapped_text_contains_declared_digest(self):
        body = "corpo\n"
        self.assertIn(kernel.digest(body), kernel.wrap(body, "1.0.0"))


class TestVerify(unittest.TestCase):
    def test_ok_when_untouched(self):
        self.assertEqual(kernel.verify(kernel.wrap("corpo\n", "1.0.0")), "OK")

    def test_drift_when_body_edited(self):
        text = kernel.wrap("corpo\n", "1.0.0").replace("corpo", "corpo modificato")
        self.assertEqual(kernel.verify(text), "DRIFT")

    def test_missing_when_no_region(self):
        self.assertEqual(kernel.verify("solo testo\n"), "MISSING")

    def test_no_drift_from_line_ending_change(self):
        text = kernel.wrap("a\nb\n", "1.0.0").replace("\n", "\r\n")
        self.assertEqual(kernel.verify(text), "OK")
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: FAIL con `ModuleNotFoundError: No module named 'fwbuild'`.

- [ ] **Step 3: Implementare `fwbuild/kernel.py`**

```python
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
    body_start = text.index("\n", m.end()) + 1
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
```

E i due file di package vuoti: `tools/fwbuild/__init__.py`, `tools/tests/__init__.py`.

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
touch fwbuild/__init__.py tests/__init__.py
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: `test_kernel` 14 test PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/fwbuild/__init__.py tools/fwbuild/kernel.py tools/tests/test_kernel.py
git commit -m "feat(fwbuild): kernel region hashing and markers"
```

---

### Task 2: `fwbuild.assemble` — comporre CLAUDE.md e gli agenti

**Files:**
- Create: `tools/fwbuild/assemble.py`
- Test: `tools/tests/test_assemble.py`

**Interfaces:**
- Consumes: `kernel.wrap`, `kernel.normalize` (Task 1)
- Produces:
  - `read_method(method_dir: Path) -> str` — concatena `method/*.md` in ordine
    lessicale di nome file (`00-`, `10-`, …)
  - `build_claude_md(method_dir: Path, version: str, project_sections: str, *, markers: bool = True) -> str`
  - `build_agent(frontmatter: str, method_body: str, domain_block: str, version: str, *, markers: bool = True) -> str`
  - `split_source(text: str) -> tuple[str, str, str]` — spezza un sorgente di
    agente in `(frontmatter, method_body, domain_block)`. Serve al build **e**
    alle verifiche: il parsing dei sorgenti sta in un posto solo, mai
    riscritto a mano in uno script di controllo.

Regola non negoziabile: **il frontmatter YAML resta fuori dalla regione hashata**
(spec §3.2). Cambiare `model:` è configurazione, non drift.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tools/tests/test_assemble.py
import tempfile
import unittest
from pathlib import Path

from fwbuild import assemble, kernel

FRONTMATTER = "---\nname: implementer\nmodel: opus\neffort: high\n---\n"


class TestReadMethod(unittest.TestCase):
    def test_concatenates_in_filename_order(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "10-b.md").write_text("BETA\n", encoding="utf-8")
            (p / "00-a.md").write_text("ALFA\n", encoding="utf-8")
            out = assemble.read_method(p)
            self.assertLess(out.index("ALFA"), out.index("BETA"))

    def test_ignores_non_markdown(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "00-a.md").write_text("ALFA\n", encoding="utf-8")
            (p / "notes.txt").write_text("RUMORE\n", encoding="utf-8")
            self.assertNotIn("RUMORE", assemble.read_method(p))


class TestBuildClaudeMd(unittest.TestCase):
    def _method_dir(self, tmp):
        p = Path(tmp)
        (p / "10-orchestration.md").write_text("## Orchestrazione\n", encoding="utf-8")
        return p

    def test_kernel_region_verifies(self):
        with tempfile.TemporaryDirectory() as d:
            out = assemble.build_claude_md(self._method_dir(d), "1.0.0", "## Il progetto\n")
            self.assertEqual(kernel.verify(out), "OK")

    def test_project_sections_outside_region(self):
        with tempfile.TemporaryDirectory() as d:
            out = assemble.build_claude_md(self._method_dir(d), "1.0.0", "## Il progetto\n")
            region = kernel.parse(out)
            self.assertNotIn("Il progetto", region.body)
            self.assertIn("Il progetto", out)

    def test_markers_off_emits_no_marker(self):
        with tempfile.TemporaryDirectory() as d:
            out = assemble.build_claude_md(
                self._method_dir(d), "1.0.0", "## Il progetto\n", markers=False
            )
            self.assertNotIn("FRAMEWORK:KERNEL", out)
            self.assertIn("Orchestrazione", out)
            self.assertIn("Il progetto", out)


class TestBuildAgent(unittest.TestCase):
    def test_frontmatter_is_outside_kernel_region(self):
        out = assemble.build_agent(FRONTMATTER, "## Metodo\n", "## Dominio\n", "1.0.0")
        region = kernel.parse(out)
        self.assertNotIn("model: opus", region.body)
        self.assertTrue(out.startswith("---\n"))

    def test_changing_model_does_not_cause_drift(self):
        a = assemble.build_agent(FRONTMATTER, "## Metodo\n", "## Dominio\n", "1.0.0")
        b = a.replace("model: opus", "model: sonnet")
        self.assertEqual(kernel.verify(b), "OK")

    def test_editing_method_causes_drift(self):
        a = assemble.build_agent(FRONTMATTER, "## Metodo\n", "## Dominio\n", "1.0.0")
        b = a.replace("## Metodo", "## Metodo cambiato")
        self.assertEqual(kernel.verify(b), "DRIFT")

    def test_domain_block_outside_region(self):
        out = assemble.build_agent(FRONTMATTER, "## Metodo\n", "## Dominio\n", "1.0.0")
        self.assertNotIn("Dominio", kernel.parse(out).body)
        self.assertIn("## Dominio", out)


SOURCE = (
    "---\nname: implementer\nmodel: opus\n---\n\n"
    "## Metodo\n\nFai la cosa.\n\n"
    "## Contesto di progetto\n\n[DA COMPILARE]\n"
)


class TestSplitSource(unittest.TestCase):
    def test_returns_three_parts(self):
        fm, method, domain = assemble.split_source(SOURCE)
        self.assertIn("name: implementer", fm)
        self.assertIn("Fai la cosa", method)
        self.assertIn("DA COMPILARE", domain)

    def test_method_excludes_domain_block(self):
        _, method, _ = assemble.split_source(SOURCE)
        self.assertNotIn("DA COMPILARE", method)

    def test_horizontal_rule_in_body_does_not_break_parsing(self):
        text = SOURCE.replace("Fai la cosa.", "Fai la cosa.\n\n---\n\nPoi verifica.")
        fm, method, _ = assemble.split_source(text)
        self.assertIn("name: implementer", fm)
        self.assertIn("Poi verifica", method)

    def test_round_trips_through_build_agent(self):
        fm, method, domain = assemble.split_source(SOURCE)
        built = assemble.build_agent(fm, method, domain, "1.0.0")
        self.assertEqual(kernel.verify(built), "OK")
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest tests.test_assemble -v
```

Atteso: FAIL con `ImportError: cannot import name 'assemble'`.

- [ ] **Step 3: Implementare `fwbuild/assemble.py`**

```python
"""Assemblaggio degli artefatti installabili.

Il metodo generato vive dentro la regione kernel; frontmatter e blocchi di
progetto restano fuori, perché sono la superficie che l'utente adatta.
"""
from pathlib import Path

from . import kernel


def read_method(method_dir: Path) -> str:
    parts = [
        p.read_text(encoding="utf-8")
        for p in sorted(method_dir.glob("*.md"), key=lambda p: p.name)
    ]
    return kernel.normalize("\n".join(parts))


def build_claude_md(
    method_dir: Path,
    version: str,
    project_sections: str,
    *,
    markers: bool = True,
) -> str:
    method = read_method(method_dir)
    head = kernel.wrap(method, version) if markers else kernel.normalize(method)
    return f"{head}\n{kernel.normalize(project_sections)}"


def build_agent(
    frontmatter: str,
    method_body: str,
    domain_block: str,
    version: str,
    *,
    markers: bool = True,
) -> str:
    body = kernel.wrap(method_body, version) if markers else kernel.normalize(method_body)
    return f"{kernel.normalize(frontmatter)}\n{body}\n{kernel.normalize(domain_block)}"


METHOD_HEADING = "## Metodo"
DOMAIN_HEADING = "## Contesto di progetto"


def split_source(text: str) -> tuple[str, str, str]:
    """Spezza un sorgente di agente in (frontmatter, metodo, blocco dominio).

    Il frontmatter si delimita sui primi due '---' a inizio riga, non su una
    split globale: un '---' usato come riga orizzontale nel corpo non deve
    rompere il parsing.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0].strip() != "---":
        raise ValueError("sorgente senza frontmatter")
    close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    frontmatter = "\n".join(lines[: close + 1]) + "\n"
    rest = "\n".join(lines[close + 1 :])

    m_at = rest.index(METHOD_HEADING)
    d_at = rest.index(DOMAIN_HEADING)
    if d_at < m_at:
        raise ValueError(f"{DOMAIN_HEADING} precede {METHOD_HEADING}")
    return frontmatter, rest[m_at:d_at], rest[d_at:]
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: `test_assemble` 13 test PASS; suite completa ancora verde.

- [ ] **Step 5: Commit**

```bash
git add tools/fwbuild/assemble.py tools/tests/test_assemble.py
git commit -m "feat(fwbuild): assemble CLAUDE.md and agent files"
```

---

### Task 3: `fwbuild.profile` — profili di dominio e selezione del roster

**Files:**
- Create: `tools/fwbuild/profile.py`
- Test: `tools/tests/test_profile.py`

**Interfaces:**
- Produces:
  - `Profile(name, agents, shared, cycles, on_demand, settings)` — `settings` è il
    `dict` da cui l'installer genera `.claude/settings.json` (spec §5)
  - `load(path: Path) -> Profile`
  - `roster(profile: Profile, extras: list[str], drop: list[str]) -> list[str]`
  - `check_exclusive(agents: list[str]) -> list[str]` — ritorna i conflitti trovati

Vincolo dalla spec §8.4/7: `deploy` e `infra` non possono coesistere. La lista
degli agenti sempre attivi (livello 1) è costante e non dipende dal profilo.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tools/tests/test_profile.py
import tempfile
import unittest
from pathlib import Path

from fwbuild import profile

TOML = """
name = "software"
agents = ["debugger", "security-reviewer"]
shared = ["core/review-checklist.md"]
cycles = []
on_demand = ["compliance-reviewer"]

[settings.permissions]
deny = ["Read(./**/*.key)"]
"""


class TestLoad(unittest.TestCase):
    def _write(self, text):
        d = tempfile.mkdtemp()
        p = Path(d) / "software.toml"
        p.write_text(text, encoding="utf-8")
        return p

    def test_reads_fields(self):
        prof = profile.load(self._write(TOML))
        self.assertEqual(prof.name, "software")
        self.assertIn("debugger", prof.agents)
        self.assertIn("compliance-reviewer", prof.on_demand)

    def test_reads_settings_for_settings_json(self):
        prof = profile.load(self._write(TOML))
        self.assertEqual(prof.settings["permissions"]["deny"], ["Read(./**/*.key)"])

    def test_settings_defaults_to_empty(self):
        minimal = 'name = "bare"\nagents = []\n'
        self.assertEqual(profile.load(self._write(minimal)).settings, {})


class TestRoster(unittest.TestCase):
    def _profile(self):
        return profile.Profile(
            name="software",
            agents=["debugger", "security-reviewer"],
            shared=[],
            cycles=[],
            on_demand=["compliance-reviewer"],
            settings={},
        )

    def test_always_includes_level_one(self):
        got = profile.roster(self._profile(), extras=[], drop=[])
        for name in profile.ALWAYS:
            self.assertIn(name, got)

    def test_extras_are_added(self):
        got = profile.roster(self._profile(), extras=["frontend"], drop=[])
        self.assertIn("frontend", got)

    def test_drop_removes_profile_agent(self):
        got = profile.roster(self._profile(), extras=[], drop=["debugger"])
        self.assertNotIn("debugger", got)

    def test_drop_cannot_remove_level_one(self):
        got = profile.roster(self._profile(), extras=[], drop=["architect"])
        self.assertIn("architect", got)

    def test_result_has_no_duplicates(self):
        got = profile.roster(self._profile(), extras=["debugger"], drop=[])
        self.assertEqual(len(got), len(set(got)))


class TestExclusive(unittest.TestCase):
    def test_deploy_and_infra_conflict(self):
        self.assertTrue(profile.check_exclusive(["deploy", "infra"]))

    def test_deploy_alone_is_fine(self):
        self.assertEqual(profile.check_exclusive(["deploy"]), [])
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest tests.test_profile -v
```

Atteso: FAIL con `ImportError: cannot import name 'profile'`.

- [ ] **Step 3: Implementare `fwbuild/profile.py`**

```python
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
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: `test_profile` 10 test PASS; suite completa ancora verde.

- [ ] **Step 5: Commit**

```bash
git add tools/fwbuild/profile.py tools/tests/test_profile.py
git commit -m "feat(fwbuild): domain profiles and roster selection"
```

---

### Task 4: `fwbuild.doctor` — le sette verifiche

**Files:**
- Create: `tools/fwbuild/doctor.py`
- Test: `tools/tests/test_doctor.py`

**Interfaces:**
- Consumes: `kernel.verify`, `profile.check_exclusive`
- Produces:
  - `Finding(code: str, severity: str, message: str)` — severity `"ERROR"` o `"WARN"`
  - `check(project_root: Path) -> list[Finding]`

Le sette verifiche della spec §8.4, codici stabili perché le skill vi si
riferiscono: `PLACEHOLDER`, `ROSTER_MISSING`, `ROSTER_ORPHAN`, `SHARED_MISSING`,
`KERNEL_DRIFT`, `STATE_MISSING`, `FABLE`, `EXCLUSIVE`.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tools/tests/test_doctor.py
import tempfile
import unittest
from pathlib import Path

from fwbuild import assemble, doctor

AGENT_FM = "---\nname: {n}\nmodel: opus\neffort: high\n---\n"


def make_project(tmp, *, agents=("explorer",), routing=("explorer",),
                 placeholder=False, fable=False, state=True):
    root = Path(tmp)
    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "shared").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    rows = "\n".join(f"| dove | `{n}` | haiku |" for n in routing)
    project = f"## Orchestrazione\n\n| Situazione | Subagent | Modello |\n|---|---|---|\n{rows}\n"
    if placeholder:
        project += "\n[DA COMPILARE] — mappa moduli\n"
    (root / "CLAUDE.md").write_text(
        assemble.build_claude_md_from_text("## Metodo\n", "1.0.0", project),
        encoding="utf-8",
    )
    for n in agents:
        model = "fable" if fable else "opus"
        fm = AGENT_FM.format(n=n).replace("model: opus", f"model: {model}")
        (root / ".claude" / "agents" / f"{n}.md").write_text(
            assemble.build_agent(fm, "## Metodo\n", "## Dominio\n", "1.0.0"),
            encoding="utf-8",
        )
    if state:
        for f in ("TODO.md", "status.md", "roadmap.md"):
            (root / "docs" / f).write_text("# vuoto\n", encoding="utf-8")
    return root


def codes(findings):
    return {f.code for f in findings}


class TestDoctor(unittest.TestCase):
    def test_clean_project_has_no_findings(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(doctor.check(make_project(d)), [])

    def test_detects_placeholder(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("PLACEHOLDER", codes(doctor.check(make_project(d, placeholder=True))))

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
            f.write_text(f.read_text(encoding="utf-8").replace("## Metodo", "## Altro"),
                         encoding="utf-8")
            self.assertIn("KERNEL_DRIFT", codes(doctor.check(p)))

    def test_detects_missing_state_files(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("STATE_MISSING", codes(doctor.check(make_project(d, state=False))))

    def test_detects_fable(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("FABLE", codes(doctor.check(make_project(d, fable=True))))

    def test_detects_deploy_infra_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_project(d, agents=("explorer", "deploy", "infra"),
                             routing=("explorer", "deploy", "infra"))
            self.assertIn("EXCLUSIVE", codes(doctor.check(p)))
```

- [ ] **Step 2: Aggiungere l'helper mancante a `assemble.py`**

`build_claude_md_from_text` serve ai test per non passare da una directory.
Aggiungere in `tools/fwbuild/assemble.py`:

```python
def build_claude_md_from_text(
    method: str, version: str, project_sections: str, *, markers: bool = True
) -> str:
    head = kernel.wrap(method, version) if markers else kernel.normalize(method)
    return f"{head}\n{kernel.normalize(project_sections)}"
```

E riscrivere `build_claude_md` per riusarlo:

```python
def build_claude_md(method_dir, version, project_sections, *, markers=True):
    return build_claude_md_from_text(
        read_method(method_dir), version, project_sections, markers=markers
    )
```

- [ ] **Step 3: Eseguire i test e verificare che falliscano**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest tests.test_doctor -v
```

Atteso: FAIL con `ImportError: cannot import name 'doctor'`.

- [ ] **Step 4: Implementare `fwbuild/doctor.py`**

```python
"""Le sette verifiche di integrità di un'installazione (spec §8.4)."""
import re
from dataclasses import dataclass
from pathlib import Path

from . import kernel, profile

PLACEHOLDER_RE = re.compile(r"\{\{|DA COMPILARE")
ROUTING_AGENT_RE = re.compile(r"^\|[^|]*\|\s*`([a-z-]+)`\s*\|", re.MULTILINE)
STATE_FILES = ("TODO.md", "status.md", "roadmap.md")


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str


def _markdown_files(root: Path) -> list[Path]:
    files = [root / "CLAUDE.md"]
    files += sorted((root / ".claude").rglob("*.md"))
    return [f for f in files if f.is_file()]


def check(root: Path) -> list[Finding]:
    out: list[Finding] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        return [Finding("STATE_MISSING", "ERROR", "CLAUDE.md assente")]

    for f in _markdown_files(root):
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root).as_posix()
        if PLACEHOLDER_RE.search(text):
            out.append(Finding("PLACEHOLDER", "ERROR", f"{rel}: segnaposto non compilato"))
        if kernel.verify(text) == "DRIFT":
            out.append(Finding("KERNEL_DRIFT", "WARN", f"{rel}: regione kernel modificata"))
        if re.search(r"^model:\s*fable\s*$", text, re.MULTILINE):
            out.append(Finding("FABLE", "ERROR", f"{rel}: model fable non disponibile"))

    routed = set(ROUTING_AGENT_RE.findall(claude_md.read_text(encoding="utf-8")))
    agents_dir = root / ".claude" / "agents"
    present = {p.stem for p in agents_dir.glob("*.md")} if agents_dir.is_dir() else set()
    for name in sorted(routed - present):
        out.append(Finding("ROSTER_MISSING", "ERROR",
                           f"{name}: citato nella tabella di routing, file assente"))
    for name in sorted(present - routed):
        out.append(Finding("ROSTER_ORPHAN", "WARN",
                           f"{name}: file presente, assente dalla tabella di routing"))

    for conflict in profile.check_exclusive(sorted(present)):
        out.append(Finding("EXCLUSIVE", "ERROR", f"agenti mutuamente esclusivi: {conflict}"))

    for ref in sorted(set(re.findall(r"\.claude/shared/([A-Za-z0-9_./-]+\.md)",
                                     claude_md.read_text(encoding="utf-8")))):
        if not (root / ".claude" / "shared" / ref).is_file():
            out.append(Finding("SHARED_MISSING", "ERROR", f".claude/shared/{ref} referenziato ma assente"))

    for name in STATE_FILES:
        if not (root / "docs" / name).is_file():
            out.append(Finding("STATE_MISSING", "ERROR", f"docs/{name} assente"))

    return out
```

- [ ] **Step 5: Eseguire i test e verificare che passino**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: `test_doctor` 8 test PASS; suite completa ancora verde.

- [ ] **Step 6: Commit**

```bash
git add tools/fwbuild/doctor.py tools/fwbuild/assemble.py tools/tests/test_doctor.py
git commit -m "feat(fwbuild): seven installation integrity checks"
```

---

### Task 5: CLI `fwbuild`

**Files:**
- Create: `tools/fwbuild/__main__.py`
- Create: `tools/fwbuild/cli.py`
- Test: `tools/tests/test_cli.py`

**Interfaces:**
- Consumes: `assemble`, `doctor`, `profile`
- Produces: `main(argv: list[str]) -> int` con il comando `doctor PATH`.
  Exit code 0 se nessun `ERROR`, 1 altrimenti.

Solo `doctor`. La generazione degli artefatti richiede giudizio (risposte al
questionario, blocchi di dominio) e resta nella skill `framework-install`, che
chiama le funzioni di `assemble`. Un comando `build` non serve finché non si
lavora alla variante B: aggiungerlo ora sarebbe codice speculativo.

- [ ] **Step 1: Scrivere i test che falliscono**

```python
# tools/tests/test_cli.py
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from fwbuild import cli
from tests.test_doctor import make_project


class TestDoctorCommand(unittest.TestCase):
    def test_exit_zero_on_clean_project(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["doctor", str(root)]), 0)

    def test_exit_one_when_error_finding(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d, placeholder=True)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["doctor", str(root)]), 1)

    def test_prints_finding_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_project(d, placeholder=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.main(["doctor", str(root)])
            self.assertIn("PLACEHOLDER", buf.getvalue())
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest tests.test_cli -v
```

Atteso: FAIL con `ImportError: cannot import name 'cli'`.

- [ ] **Step 3: Implementare `cli.py` e `__main__.py`**

```python
# tools/fwbuild/cli.py
"""Entrypoint: python -m fwbuild <comando>."""
import argparse
from pathlib import Path

from . import doctor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fwbuild")
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("doctor", help="verifica un'installazione")
    d.add_argument("path", type=Path)

    args = parser.parse_args(argv)

    if args.command == "doctor":
        findings = doctor.check(args.path)
        if not findings:
            print("OK — nessun rilievo")
            return 0
        for f in findings:
            print(f"{f.severity:5} {f.code:16} {f.message}")
        return 1 if any(f.severity == "ERROR" for f in findings) else 0
    return 0
```

```python
# tools/fwbuild/__main__.py
import sys

from .cli import main

sys.exit(main())
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: `test_cli` 3 test PASS; suite completa ancora verde (48 test).

- [ ] **Step 5: Commit**

```bash
git add tools/fwbuild/cli.py tools/fwbuild/__main__.py tools/tests/test_cli.py
git commit -m "feat(fwbuild): command line interface"
```

---

### Task 6: Il kernel — `framework/method/`

**Files:**
- Create: `framework/VERSION`
- Create: `framework/method/00-preamble.md`
- Create: `framework/method/10-orchestration.md`
- Create: `framework/method/20-evidence.md`
- Create: `framework/method/30-code-principles.md`
- Create: `framework/method/40-state.md`

**Interfaces:**
- Produces: il testo del metodo che ogni agente e ogni `CLAUDE.md` incorporeranno.
  Consumato da `assemble.read_method` (Task 2).

**Fonte:** spec §6, che contiene già il testo canonico. Copiarlo, non riscriverlo.
`framework/VERSION` contiene la riga `1.0.0`.

Ripartizione:

| file | contenuto (spec) |
|---|---|
| `00-preamble.md` | ruolo del team, lingua, come si legge il file |
| `10-orchestration.md` | §6.1: coordinatore, 10 regole token, ciclo del codice |
| `20-evidence.md` | §6.2: Evidence Before Action (8 regole), report standard, «come si parlano gli agenti» — inclusi il template di delega a 5 blocchi e la regola bordi/centro per primacy-recency |
| `30-code-principles.md` | §6.3: principi di modifica, no-installazioni, principio sui test |
| `40-state.md` | §6.4: i 4 livelli di stato |

- [ ] **Step 1: Scrivere `framework/VERSION` e i cinque file di metodo**

Densità massima: è il testo pagato a ogni spawn. Nessuna sezione può ripetere
ciò che un'altra dice già.

- [ ] **Step 2: Verificare che l'assemblaggio funzioni**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -c "
from pathlib import Path
from fwbuild import assemble, kernel
root = Path('..')
out = assemble.build_claude_md(root/'framework'/'method', (root/'framework'/'VERSION').read_text().strip(), '## Il progetto\n\nSegnaposto.\n')
print('verify:', kernel.verify(out))
print('parole kernel:', len(kernel.parse(out).body.split()))
"
```

Atteso: `verify: OK`. Il conteggio parole è il costo per spawn — annotarlo nel
report; se supera ~2500 parole, comprimere prima di proseguire.

- [ ] **Step 3: Verificare l'assenza di segnaposto e di `fable`**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
grep -rn "DA COMPILARE\|{{\|fable" framework/method/ framework/VERSION || echo "PULITO"
```

Atteso: `PULITO`.

- [ ] **Step 4: Commit**

```bash
git add framework/VERSION framework/method/
git commit -m "feat(framework): kernel method modules"
```

---

### Task 7: Agenti di livello 1 (6 file)

**Files:**
- Create: `framework/agents/{explorer,architect,implementer,tester,refactorer,final-reviewer}.md`

**Interfaces:**
- Consumes: il metodo di Task 6 (incorporato in fase di build, non copiato qui)
- Produces: i sei agenti sempre installati (spec §7)

**Struttura obbligatoria di ogni file** — è il contratto che `assemble.build_agent`
si aspetta:

```markdown
---
name: <nome>
description: >
  <quando usarlo — è ciò che il coordinatore legge per fare routing:
  telegrafico, dice il caso d'uso e i confini, mai la biografia dell'agente>
model: <haiku|sonnet|opus>
effort: <low|medium|high|xhigh>
tools: <lista>
color: <colore>
---

## Metodo
<corpo che finirà nella regione kernel>

## Contesto di progetto
[DA COMPILARE — istruzioni su cosa mettere qui, compilato dall'installer]
```

Frontmatter esatti (spec §7):

| file | model | effort | tools |
|---|---|---|---|
| `explorer.md` | haiku | low | Read, Grep, Glob |
| `architect.md` | opus | xhigh | Read, Grep, Glob, Bash |
| `implementer.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `tester.md` | sonnet | medium | Read, Grep, Glob, Edit, Write, Bash |
| `refactorer.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `final-reviewer.md` | opus | high | Read, Grep, Glob, Bash |

**Fonte da distillare:** `sources/base/.claude/agents/*.md` per la struttura,
`sources/research-ai/.claude/agents/*.md` per la densità (sono i più maturi).
Correzioni obbligatorie rispetto ai sorgenti:

- `architect`: `model: opus` + `effort: xhigh`, **mai** `fable`.
- `tester`: incorporare il principio «pochi test sensati» (spec §6.3) —
  è la differenza sostanziale rispetto al `tester` dei sorgenti.
- `final-reviewer`: mantenere «non fidarti mai degli altri agenti» e il verdetto
  `APPROVATO | APPROVATO CON RISERVE | RESPINTO`.
- Nessun agente nomina un altro agente per definirsi.

- [ ] **Step 1: Scrivere i sei file**

- [ ] **Step 2: Verificare che ogni file si assembli e produca una regione valida**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -c "
import pathlib
from fwbuild import assemble, kernel
version = pathlib.Path('../framework/VERSION').read_text(encoding='utf-8').strip()
for p in sorted(pathlib.Path('../framework/agents').glob('*.md')):
    fm, method, domain = assemble.split_source(p.read_text(encoding='utf-8'))
    built = assemble.build_agent(fm, method, domain, version)
    assert kernel.verify(built) == 'OK', p.name
    assert 'model: fable' not in built, p.name
    print(f'{p.name:22} OK  parole metodo: {len(method.split())}')
"
```

Atteso: 6 righe `OK`. Usa `split_source` (Task 2): il parsing dei sorgenti sta
in un posto solo e resta coperto da test.

- [ ] **Step 3: Verificare che nessun agente ne nomini un altro per definirsi**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
grep -n "sostituto\|equivalente di\|come il .*-reviewer" framework/agents/*.md || echo "PULITO"
```

Atteso: `PULITO`.

- [ ] **Step 4: Commit**

```bash
git add framework/agents/
git commit -m "feat(framework): level-1 agents"
```

---

### Task 8: Revisori di superficie critica (4 file)

**Files:**
- Create: `framework/agents/security-reviewer.md`
- Create: `framework/agents/scientific-reviewer.md`
- Create: `framework/agents/data-quality-reviewer.md`
- Create: `framework/agents/compliance-reviewer.md`

**Interfaces:**
- Produces: i quattro revisori. Tutti `model: opus`, `effort: high`,
  `tools: Read, Grep, Glob, Bash`. Nessuno modifica codice.

**Il punto centrale di questo task:** ognuno è scritto **in proprio**. Nessuno
nomina gli altri, nessuno si presenta come variante o sostituto di un altro.
Quello che condividono — posizione nel workflow, formato dei finding con
`file:riga` + scenario concreto + correzione minima — arriva dalla regione kernel.

| agente | modello di minaccia da sviluppare |
|---|---|
| `security-reviewer` | attaccante: input non fidato, segreti, path traversal, SSRF, escalation, dati personali esposti |
| `scientific-reviewer` | conclusione invalida: leakage, circolarità, confronto non appaiato, metrica satura, baseline mancante, significatività, claim non supportati, ablation non attribuibile |
| `data-quality-reviewer` | dato corrotto a monte: schema, encoding, duplicati, valori fuori range, idempotenza, chiavi instabili, unità/valute implicite |
| `compliance-reviewer` | violazione normativa: base giuridica, minimizzazione, pseudonimizzazione insufficiente, licenze incompatibili, ToS delle fonti |

`compliance-reviewer` è **livello 3**: la sua `description` deve dichiarare
esplicitamente che si invoca **solo su richiesta dell'utente**, mai in autonomia
(spec §7).

**Fonte da distillare:** `sources/*/.claude/agents/security-reviewer.md` (le tre
varianti divergono di ~50 righe su 64: prendere il metodo comune, non una
variante), `sources/research-ai/.claude/agents/scientific-reviewer.md` (già
maturo — togliere solo il rimando al security reviewer),
`sources/web/website2/.claude/agents/data-ingestion.md` §regole 2-4 per la
qualità del dato, `sources/web/website2/docs/TODO.md` §GDPR per la compliance.

- [ ] **Step 1: Scrivere i quattro file**

- [ ] **Step 2: Verificare assemblaggio e indipendenza reciproca**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
for a in security scientific data-quality compliance; do
  printf "%-16s " "$a"
  grep -c "security-reviewer\|scientific-reviewer\|data-quality-reviewer\|compliance-reviewer" \
    "framework/agents/${a}-reviewer.md" | tr -d '\n'
  echo " riferimenti ad altri revisori (atteso: 0 oltre il proprio name:)"
done
grep -n "solo su richiesta" framework/agents/compliance-reviewer.md
```

Atteso: ogni file cita solo il proprio nome nel frontmatter;
`compliance-reviewer` contiene la clausola di invocazione su richiesta.

- [ ] **Step 3: Commit**

```bash
git add framework/agents/
git commit -m "feat(framework): critical-surface reviewers"
```

---

### Task 9: Specialisti di dominio (9 file)

**Files:**
- Create: `framework/agents/{debugger,frontend,api-scout,deploy,infra,data-ingestion,results-analyst,literature,perf-analyst}.md`

**Interfaces:**
- Produces: gli agenti attivati dal questionario (livello 2) più `perf-analyst`
  (livello 3).

| file | model | effort | tools |
|---|---|---|---|
| `debugger.md` | opus | high | Read, Grep, Glob, Edit, Bash |
| `frontend.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `api-scout.md` | sonnet | medium | Read, Grep, Glob, WebSearch, WebFetch |
| `deploy.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `infra.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `data-ingestion.md` | opus | high | Read, Grep, Glob, Edit, Write, Bash |
| `results-analyst.md` | opus | high | Read, Grep, Glob, Bash |
| `literature.md` | sonnet | medium | Read, Grep, Glob, WebSearch, WebFetch |
| `perf-analyst.md` | opus | high | Read, Grep, Glob, Bash |

**`api-scout` è nuovo** — non esiste nei sorgenti. Contenuto da scrivere da zero
(spec §7): verifica firme e comportamenti di librerie esterne, legge **prima** i
package installati (`node_modules`, `site-packages`, lockfile) e solo poi la
documentazione online, perché la verità è la versione installata; consegna
`simbolo — firma — fonte — versione`; non modifica nulla; se una firma non è
verificabile lo dichiara invece di dedurla.

`perf-analyst`: `description` con la clausola «solo su richiesta dell'utente».

**Fonte da distillare:** `sources/web/base/.claude/agents/{deploy,frontend}.md`,
`sources/web/website2/.claude/agents/{infra,data-ingestion}.md`,
`sources/research-ai/.claude/agents/{results-analyst,literature,debugger}.md`.

- [ ] **Step 1: Scrivere i nove file**

- [ ] **Step 2: Verificare il roster completo — 19 agenti**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
n=$(ls framework/agents/*.md | wc -l); echo "agenti: $n (atteso 19)"
grep -L "^model:" framework/agents/*.md || echo "tutti hanno model:"
grep -l "model: fable" framework/agents/*.md && echo "ERRORE: fable presente" || echo "nessun fable"
grep -n "solo su richiesta" framework/agents/perf-analyst.md
```

Atteso: `agenti: 19`, nessun `fable`, clausola presente in `perf-analyst`.

- [ ] **Step 3: Commit**

```bash
git add framework/agents/
git commit -m "feat(framework): domain specialist agents including api-scout"
```

---

### Task 10: Guide condivise — `framework/shared/`

**Files:**
- Create: `framework/shared/core/{conventions,coding-standards,architecture-guide,testing-guide,debugging-playbook,review-checklist}.md`
- Create: `framework/shared/domain/{design-guide,research-principles,data-guide}.md`

**Interfaces:**
- Produces: le guide caricate on-demand dietro pointer (regola 6 dell'economia
  dei token). Non entrano mai in `CLAUDE.md`.

**Vincolo dalla spec §2.3 punto 5:** in `review-checklist.md` il blocco generico
di correttezza (null handling, off-by-one, encoding, rilascio risorse, contratti,
regressioni) deve restare **separato e estraibile** dal blocco di dominio. In
`sources/web/base` i due sono stati fusi e la parte generica non è più
recuperabile — è l'errore da non ripetere.

`testing-guide.md` sviluppa il principio «pochi test sensati» del kernel con
esempi concreti: cosa significa testare al livello giusto, invarianti contro
esempi, quando un rischio va in `UNVERIFIED` invece che in un test finto.

- [ ] **Step 1: Scrivere le sei guide core**

- [ ] **Step 2: Scrivere le tre guide di dominio**

`design-guide.md` da `sources/web/base/.claude/shared/design-guide.md`
(token, motion, accessibilità, performance — generalizzato oltre Next.js).
`research-principles.md` da `sources/research-ai/.claude/shared/research-principles.md`
(togliere i riferimenti a RPLAN e agli esperimenti specifici).
`data-guide.md` nuovo: normalizzazione deterministica, idempotenza, chiavi
stabili, DB come source of truth e indice derivato.

- [ ] **Step 3: Verificare separabilità e assenza di riferimenti a progetti specifici**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
grep -n "^## " framework/shared/core/review-checklist.md
grep -rn "RPLAN\|AbletonLoader\|FindShop\|Avalonia\|floorplan" framework/shared/ || echo "PULITO"
```

Atteso: `review-checklist.md` ha sezioni distinte per il blocco generico e per
quello di dominio; nessun riferimento ai progetti sorgente.

- [ ] **Step 4: Commit**

```bash
git add framework/shared/
git commit -m "feat(framework): shared on-demand guides"
```

---

### Task 11: Profili e template

**Files:**
- Create: `framework/profiles/{software,research,web,data,library}.toml`
- Create: `framework/templates/{TODO.md,status.md,roadmap.md}`
- Create: `framework/build/variants.toml`
- Modify: `docs/design/2026-08-31-meta-framework.md` §4 (`.yml` → `.toml`)

**Interfaces:**
- Consumes: `profile.load` (Task 3)
- Produces: i cinque profili che mappano dominio → roster, guide, cicli.

Ogni profilo dichiara solo gli agenti **oltre** il livello 1 (`profile.ALWAYS`
li aggiunge sempre). Esempio completo, `software.toml`:

```toml
name = "software"
agents = ["debugger", "security-reviewer", "api-scout"]
shared = [
  "core/conventions.md",
  "core/coding-standards.md",
  "core/architecture-guide.md",
  "core/testing-guide.md",
  "core/debugging-playbook.md",
  "core/review-checklist.md",
]
cycles = []
on_demand = ["compliance-reviewer", "perf-analyst"]

[settings.permissions]
deny = ["Read(./**/*.env)", "Read(./**/*.key)", "Read(./**/*.pem)"]
```

La tabella `[settings]` diventa `.claude/settings.json` in fase di installazione
(spec §5). Ogni profilo nega almeno la lettura dei file di segreti pertinenti al
suo dominio: `research` aggiunge gli artefatti pesanti (`*.ckpt`, `*.npz`),
`data` le esportazioni con dati personali.

| profilo | `agents` oltre il livello 1 | `cycles` |
|---|---|---|
| `software` | debugger, security-reviewer, api-scout | — |
| `research` | debugger, api-scout, results-analyst, literature, scientific-reviewer | `research` |
| `web` | frontend, deploy, security-reviewer, api-scout | `design` |
| `data` | debugger, data-ingestion, data-quality-reviewer, infra, api-scout | — |
| `library` | debugger, api-scout, security-reviewer | — |

`variants.toml`:

```toml
[a-prime]
markers = true
version_tracking = true

[b]
markers = false
version_tracking = false
```

I template sono **vuoti ma strutturati**: `TODO.md` con le sezioni *In corso /
Prossimi / Decisioni aperte / Ultimo aggiornamento* e il tetto di ~60 righe
dichiarato in testa; `status.md` e `roadmap.md` analoghi.

- [ ] **Step 1: Scrivere i cinque profili**

- [ ] **Step 2: Scrivere i tre template e `variants.toml`**

- [ ] **Step 3: Verificare che ogni profilo si carichi e non abbia conflitti**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -c "
import pathlib
from fwbuild import profile
agents = {p.stem for p in pathlib.Path('../framework/agents').glob('*.md')}
for p in sorted(pathlib.Path('../framework/profiles').glob('*.toml')):
    prof = profile.load(p)
    r = profile.roster(prof, [], [])
    missing = [a for a in r if a not in agents]
    conflicts = profile.check_exclusive(r)
    print(f'{prof.name:10} agenti:{len(r):3} mancanti:{missing} conflitti:{conflicts}')
    assert not missing and not conflicts, prof.name
"
```

Atteso: cinque righe, `mancanti:[]` e `conflitti:[]` ovunque.

- [ ] **Step 4: Aggiornare la spec §4 da `.yml` a `.toml`**

- [ ] **Step 5: Commit**

```bash
git add framework/profiles/ framework/templates/ framework/build/ docs/design/
git commit -m "feat(framework): domain profiles, state templates, variants"
```

---

### Task 12: Skill `framework-install`

**Files:**
- Create: `framework/skills/framework-install/SKILL.md`

**Interfaces:**
- Consumes: profili (Task 11), agenti (Task 7-9), guide (Task 10), CLI (Task 5)
- Produces: la procedura di installazione e adattamento (spec §8.1-8.3)

La skill è **istruzioni per il coordinatore**, non uno script: le decisioni di
adattamento richiedono giudizio. Delega al tooling solo ciò che è meccanico
(assemblaggio, hash, verifiche).

Passi che la skill deve prescrivere, nell'ordine (spec §8.1):

1. Rilevare progetto vuoto o codebase esistente.
2. Se esiste codice: **delegare la ricognizione a `explorer`** (haiku), non
   leggere il repo a prezzo pieno. L'installer applica a sé stesso la regola 3.
3. Questionario (spec §8.2): 4 domande sempre — campo del progetto, superficie
   critica, stile delle risposte su **due assi** (forma + base di conoscenza
   assunta), autonomia concessa — più le condizionali pertinenti al profilo.
4. Selezione del roster e installazione selettiva (spec §5.1): si copia solo
   l'attivo, il master resta in `framework/`.
5. Generazione: `CLAUDE.md` assemblato, agenti con blocco dominio compilato,
   guide pertinenti, `.claude/settings.json` serializzato da `Profile.settings`
   (Task 3), file di stato vuoti dai template.
6. Verifica finale: `python -m fwbuild doctor <progetto>` deve uscire con 0.

La skill deve dichiarare esplicitamente:

- che **non installa nulla** (pacchetti, dipendenze) senza conferma dell'utente;
- che gli `@import` in `CLAUDE.md` vanno **verificati**, non assunti: se non
  funzionano, concatenazione fisica (spec §10.1);
- che il questionario si fa **una domanda alla volta**, non come blocco unico.

- [ ] **Step 1: Scrivere `SKILL.md` con frontmatter `name` e `description`**

- [ ] **Step 2: Verificare che la skill copra tutti i passi della spec §8**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
for k in "explorer" "questionario" "superficie critica" "base di conoscenza" \
         "autonomia" "doctor" "conferma" "@import"; do
  printf "%-22s " "$k"
  grep -qi "$k" framework/skills/framework-install/SKILL.md && echo "presente" || echo "ASSENTE"
done
```

Atteso: tutte `presente`.

- [ ] **Step 3: Commit**

```bash
git add framework/skills/framework-install/
git commit -m "feat(framework): install skill"
```

---

### Task 13: Skill `framework-doctor` e `framework-sync`

**Files:**
- Create: `framework/skills/framework-doctor/SKILL.md`
- Create: `framework/skills/framework-sync/SKILL.md`

**Interfaces:**
- Consumes: CLI `fwbuild doctor` (Task 5)
- Produces: le due skill di ciclo di vita.

`framework-doctor`: lancia `python -m fwbuild doctor .`, interpreta i codici di
finding (`PLACEHOLDER`, `ROSTER_MISSING`, `ROSTER_ORPHAN`, `SHARED_MISSING`,
`KERNEL_DRIFT`, `STATE_MISSING`, `FABLE`, `EXCLUSIVE`) e per ognuno propone la
correzione. `KERNEL_DRIFT` **non è un errore**: è un'informazione, e la domanda
da porre all'utente è se quella modifica va promossa nel sorgente.

`framework-sync`: le due direzioni della spec §8.5.

- **giù** — porta una versione nuova del kernel nel progetto preservando
  l'adattatore. I conflitti sulle regioni modificate localmente si **presentano
  all'utente**, non si risolvono da soli.
- **su** — promuove una modifica locale in `framework/method/` o
  `framework/agents/`, incrementa `framework/VERSION`, e lo dichiara.
- `--activate <agente>` / `--deactivate <agente>` (spec §5.1): copia dal master
  la versione **corrente**, o rimuove dall'installazione lasciando il master
  intatto.

- [ ] **Step 1: Scrivere le due `SKILL.md`**

- [ ] **Step 2: Verificare la copertura dei codici di finding**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
for c in PLACEHOLDER ROSTER_MISSING ROSTER_ORPHAN SHARED_MISSING KERNEL_DRIFT STATE_MISSING FABLE EXCLUSIVE; do
  printf "%-16s " "$c"
  grep -q "$c" framework/skills/framework-doctor/SKILL.md && echo "gestito" || echo "NON GESTITO"
done
grep -c "activate\|deactivate" framework/skills/framework-sync/SKILL.md
```

Atteso: tutti `gestito`; `framework-sync` menziona activate/deactivate.

- [ ] **Step 3: Commit**

```bash
git add framework/skills/
git commit -m "feat(framework): doctor and sync lifecycle skills"
```

---

### Task 14: Installazione di prova end-to-end e variante B

**Files:**
- Create: `tools/tests/test_end_to_end.py`

**Interfaces:**
- Consumes: tutto quanto sopra
- Produces: la prova che il framework si installa e si verifica davvero.

- [ ] **Step 1: Scrivere il test end-to-end**

```python
# tools/tests/test_end_to_end.py
import tempfile
import unittest
from pathlib import Path

from fwbuild import assemble, doctor, kernel, profile

FRAMEWORK = Path(__file__).resolve().parents[2] / "framework"


class TestRealFramework(unittest.TestCase):
    def test_version_file_exists(self):
        self.assertTrue((FRAMEWORK / "VERSION").is_file())

    def test_all_nineteen_agents_present(self):
        self.assertEqual(len(list((FRAMEWORK / "agents").glob("*.md"))), 19)

    def test_no_agent_declares_fable(self):
        for p in (FRAMEWORK / "agents").glob("*.md"):
            self.assertNotIn("model: fable", p.read_text(encoding="utf-8"), p.name)

    def test_kernel_assembles_and_verifies(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        out = assemble.build_claude_md(FRAMEWORK / "method", version, "## Il progetto\n\nX\n")
        self.assertEqual(kernel.verify(out), "OK")

    def test_variant_b_has_no_markers(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        out = assemble.build_claude_md(
            FRAMEWORK / "method", version, "## Il progetto\n\nX\n", markers=False
        )
        self.assertNotIn("FRAMEWORK:KERNEL", out)

    def test_every_profile_resolves_to_existing_agents(self):
        available = {p.stem for p in (FRAMEWORK / "agents").glob("*.md")}
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            names = profile.roster(prof, [], [])
            self.assertEqual([n for n in names if n not in available], [], prof.name)
            self.assertEqual(profile.check_exclusive(names), [], prof.name)

    def test_every_profile_shared_guide_exists(self):
        for path in (FRAMEWORK / "profiles").glob("*.toml"):
            prof = profile.load(path)
            for rel in prof.shared:
                self.assertTrue((FRAMEWORK / "shared" / rel).is_file(), f"{prof.name}: {rel}")
```

- [ ] **Step 2: Eseguire la suite completa**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework/tools"
python -m unittest discover -s tests -t . -v
```

Atteso: tutti PASS. Se `test_all_nineteen_agents_present` fallisce, il roster è
incompleto: contare e completare prima di proseguire.

- [ ] **Step 3: Installazione di prova su un progetto finto**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
rm -rf _build/prova && mkdir -p _build/prova
# Eseguire la skill framework-install sul profilo "software", progetto vuoto,
# rispondendo al questionario con valori di prova.
python -m fwbuild doctor _build/prova
```

Atteso: `OK — nessun rilievo`, exit code 0.

- [ ] **Step 4: Verificare che il drift venga rilevato davvero**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
sed -i 's/## Orchestrazione/## Orchestrazione modificata/' _build/prova/CLAUDE.md
python -m fwbuild doctor _build/prova   # atteso: KERNEL_DRIFT
```

Atteso: una riga `WARN  KERNEL_DRIFT`. È la prova che A′ funziona: senza questa,
il framework è solo un template.

- [ ] **Step 5: Misurare il costo per spawn**

```bash
cd "c:/Users/Enrico Di Maria/Desktop/Claude Framework"
wc -w _build/prova/CLAUDE.md
```

Annotare il valore nel report: è il contesto pagato a ogni spawn di agente. I
`CLAUDE.md` sorgente vanno da 1.400 a 2.600 parole; restare in quella fascia.

- [ ] **Step 6: Commit**

```bash
git add tools/tests/test_end_to_end.py
git commit -m "test: end-to-end framework integrity and drift detection"
```

---

## Ordine di esecuzione e vincolo sul contesto

I task 7-10 distillano `sources/` in `framework/`. Vanno eseguiti **in ordine e
senza saltare avanti e indietro**: ogni file scritto è materiale sorgente che non
serve più rileggere. Se la sessione viene compattata a metà, il lavoro già scritto
su disco è la difesa — quello non ancora scritto va rileggo da `sources/`.

Task 1-5 (tooling) sono indipendenti da `sources/` e possono essere eseguiti in
qualunque momento prima del Task 14.
