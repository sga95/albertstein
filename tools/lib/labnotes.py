"""Lint delle note di lab in site/lab/: punteggio e suggerimenti, mai un blocco.

Una nota di lab ha quattro sezioni (What I wanted to do, Setup, What happened,
What I learned), almeno un blocco <pre> o un'immagine, e una lezione scritta
davvero. Un post-mortem (nome file con "postmortem") ha le sue cinque sezioni.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from .progress import SITE

LAB = SITE / "lab"
SKIP = {"index.html", "template.html", "postmortem-template.html"}

LAB_SECTIONS = ["What I wanted to do", "Setup", "What happened", "What I learned"]
POSTMORTEM_SECTIONS = ["Timeline", "Root cause", "What helped", "What wasted time", "What I change"]

# frasi lasciate dal template che vanno sostituite
PLACEHOLDERS = [
    "TITLE OF THE NOTE",
    "YYYY-MM-DD",
    "One or two sentences.",
    "One sentence that says what this note is about.",
    "The one thing you would tell someone who is about to do the same lab.",
    "Tools, topology, versions.",
    "Steps, commands, output.",
    "TITLE OF THE POST-MORTEM",
    "Real times, taken from issues, commits, Cloudflare logs.",
    "One sentence. The piece that broke and why it broke what people saw.",
    "Tools, commands, pages that made it clear.",
    "Wrong hypotheses, useless commands, things I believed that were not true.",
    "One or two concrete actions so that next time it takes less.",
    "Downtime: X minutes",
]


@dataclass
class NoteReport:
    path: Path
    kind: str  # "lab" | "postmortem"
    score: int = 0
    checks: list[tuple[bool, str]] = field(default_factory=list)  # (ok, descrizione)
    suggestions: list[str] = field(default_factory=list)

    @property
    def rel(self) -> str:
        try:
            return self.path.relative_to(SITE).as_posix()
        except ValueError:
            return self.path.name


class _NoteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections: dict[str, list[str]] = {}
        self.current: str | None = None
        self._in_h2 = False
        self._h2: list[str] = []
        self.pre = 0
        self.img = 0
        self.title = ""
        self._in_title = False
        self.text: list[str] = []
        self._skip = 0  # dentro <pre>/<code> il testo non conta come prosa

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self._in_h2, self._h2 = True, []
        elif tag == "pre":
            self.pre += 1
            self._skip += 1
        elif tag == "img":
            self.img += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "h2" and self._in_h2:
            self._in_h2 = False
            name = " ".join("".join(self._h2).split())
            name = re.sub(r"^\d+\s*", "", name)  # toglie il numero "01 "
            self.current = name
            self.sections.setdefault(name, [])
        elif tag == "pre":
            self._skip = max(0, self._skip - 1)
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_h2:
            self._h2.append(data)
            return
        if self._in_title:
            self.title += data
            return
        self.text.append(data)
        if self.current is not None and not self._skip:
            self.sections[self.current].append(data)


def _prose(parts: list[str]) -> str:
    return " ".join(" ".join(parts).split())


def lint_note(path: Path) -> NoteReport:
    kind = "postmortem" if "postmortem" in path.name.lower() else "lab"
    wanted = POSTMORTEM_SECTIONS if kind == "postmortem" else LAB_SECTIONS
    parser = _NoteParser()
    parser.feed(path.read_text(encoding="utf-8"))
    report = NoteReport(path, kind)
    checks: list[tuple[bool, str, int, str]] = []  # (ok, label, peso, suggerimento)

    found = {k.lower(): v for k, v in parser.sections.items()}
    for name in wanted:
        ok = name.lower() in found
        checks.append((ok, f"sezione \"{name}\"", 15, f"aggiungi la sezione <h2>{name}</h2>"))

    evidence = parser.pre + parser.img
    checks.append((evidence > 0, "almeno un blocco <pre> o un'immagine", 20,
                   "metti l'output di un comando in un blocco <pre><code> o uno screenshot con <img>"))

    last = wanted[-1]
    lesson = _prose(found.get(last.lower(), []))
    lesson_ok = len(lesson.split()) >= 8 and not any(p in lesson for p in PLACEHOLDERS)
    checks.append((lesson_ok, f"\"{last}\" scritta davvero", 20,
                   f"scrivi almeno una frase vera in \"{last}\": cosa diresti a chi sta per fare lo stesso lab"))

    full = "\n".join(parser.text) + parser.title
    leftovers = [p for p in PLACEHOLDERS if p in full]
    checks.append((not leftovers, "nessun segnaposto del template", 0,
                   "sostituisci: " + "; ".join(f"\"{p}\"" for p in leftovers) if leftovers else ""))

    total = sum(w for _, _, w, _ in checks)
    got = sum(w for ok, _, w, _ in checks if ok)
    report.score = round(100 * got / total) if total else 0
    for ok, label, _, hint in checks:
        report.checks.append((ok, label))
        if not ok and hint:
            report.suggestions.append(hint)
    return report


def lab_notes(lab: Path = LAB) -> list[Path]:
    if not lab.exists():
        return []
    return sorted(p for p in lab.glob("*.html") if p.name not in SKIP)


def lint_all(lab: Path = LAB) -> list[NoteReport]:
    return [lint_note(p) for p in lab_notes(lab)]


def render_markdown(reports: list[NoteReport]) -> str:
    """Commento per la PR. Sempre incoraggiante: suggerimenti, non bocciature."""
    if not reports:
        return "Nessuna nota di lab da controllare in questa PR."
    lines = ["## Note di lab: punteggio e suggerimenti", ""]
    for r in reports:
        lines.append(f"### `{r.rel}`: {r.score}/100")
        for ok, label in r.checks:
            lines.append(f"- [{'x' if ok else ' '}] {label}")
        if r.suggestions:
            lines.append("")
            lines.append("Suggerimenti:")
            for s in r.suggestions:
                lines.append(f"- {s}")
        lines.append("")
    lines.append("_Questo commento non blocca la PR. Il punteggio serve a te, non alla CI._")
    return "\n".join(lines)


def render_text(reports: list[NoteReport]) -> str:
    if not reports:
        return "  nessuna nota di lab in site/lab/ (index e template esclusi)"
    out = []
    for r in reports:
        out.append(f"  {r.rel}: {r.score}/100")
        for ok, label in r.checks:
            out.append(f"    [{'ok' if ok else '  '}] {label}")
        for s in r.suggestions:
            out.append(f"    -> {s}")
    return "\n".join(out)
