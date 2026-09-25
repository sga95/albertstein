"""Estrae le evidenze dal repo.

Per ogni missione, boss e passo dei binari (gli "item") produce:
  id, kind, n, title, done (da progress.json), verified (True/False/None),
  missing (controlli falliti), attests (skill -> livello), last_evidence (data ISO o None).

verified è None quando nessun controllo è automatico (solo "manual"): vale la parola di Alberto.
Non scrive mai nulla. Non usa LLM.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import LAB, PROGRESS, ROOT, RULES, SITE, SITE_JSON  # noqa: E402

LAB_SKIP = {"index.html", "template.html", "postmortem-template.html"}


@dataclass
class Item:
    id: str
    kind: str  # mission | boss | track
    n: int
    title: str
    done: bool
    verified: bool | None
    missing: list[str] = field(default_factory=list)
    attests: dict[str, int] = field(default_factory=dict)
    last_evidence: str | None = None
    file: str = ""
    track: str = ""


def _git_dates(path: str, root: Path = ROOT) -> list[str]:
    """Date (ISO) dei commit che toccano path, dal più recente. Lista vuota se git non c'è."""
    try:
        run = subprocess.run(
            ["git", "-C", str(root), "log", "--format=%cs", "--", path],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if run.returncode != 0:
        return []
    return [line.strip() for line in run.stdout.splitlines() if line.strip()]


def lab_notes(lab: Path = LAB) -> list[Path]:
    if not lab.exists():
        return []
    return sorted(p for p in lab.glob("*.html") if p.name not in LAB_SKIP)


class Checker:
    """Esegue i controlli di evidence-rules.yaml contro il repo."""

    def __init__(self, root: Path = ROOT, progress: dict | None = None, site_json: dict | None = None):
        self.root = root
        self.site = root / "site"
        self.progress = progress if progress is not None else json.loads((root / "site/data/progress.json").read_text(encoding="utf-8"))
        sj = root / "site/data/site.json"
        self.site_json = site_json if site_json is not None else (json.loads(sj.read_text(encoding="utf-8")) if sj.exists() else {})

    def check(self, rule: dict) -> tuple[bool | None, str, str | None]:
        """Ritorna (esito, descrizione, data dell'ultima evidenza). Esito None = manuale."""
        if "manual" in rule:
            return None, f"manuale: {rule['manual']}", None
        if "file" in rule:
            p = self.root / rule["file"]
            dates = _git_dates(rule["file"], self.root)
            return p.exists(), f"file {rule['file']}", dates[0] if dates else None
        if "glob" in rule:
            n = rule.get("min", 1)
            matches = sorted(self.root.glob(rule["glob"]))
            date_ = None
            for m in matches[:5]:
                d = _git_dates(str(m.relative_to(self.root)), self.root)
                if d and (date_ is None or d[0] > date_):
                    date_ = d[0]
            return len(matches) >= n, f"almeno {n} file {rule['glob']} (trovati {len(matches)})", date_
        if "commits" in rule:
            n = rule.get("min", 1)
            dates = _git_dates(rule["commits"], self.root)
            return len(dates) >= n, f"almeno {n} commit su {rule['commits']} (trovati {len(dates)})", dates[0] if dates else None
        if "html_contains" in rule:
            p = self.root / rule["html_contains"]
            ok = p.exists() and rule["text"] in p.read_text(encoding="utf-8")
            dates = _git_dates(rule["html_contains"], self.root)
            return ok, f"{rule['html_contains']} contiene \"{rule['text']}\"", dates[0] if dates else None
        if "nav" in rule:
            labels = [x.get("label") for x in self.site_json.get("nav", [])]
            return rule["nav"] in labels, f"voce di menu \"{rule['nav']}\"", None
        if "lab_notes" in rule:
            notes = lab_notes(self.site / "lab")
            n = rule["lab_notes"]
            date_ = None
            for p in notes:
                d = _git_dates(f"site/lab/{p.name}", self.root)
                if d and (date_ is None or d[0] > date_):
                    date_ = d[0]
            return len(notes) >= n, f"almeno {n} note di lab (trovate {len(notes)})", date_
        if "incidents" in rule:
            inc = self.progress.get("incidents", [])
            n = rule["incidents"]
            date_ = max((i.get("date") for i in inc), default=None)
            return len(inc) >= n, f"almeno {n} incidenti con post-mortem (trovati {len(inc)})", date_
        raise ValueError(f"regola sconosciuta: {rule}")


def scan(root: Path = ROOT, progress: dict | None = None, rules: dict | None = None, site_json: dict | None = None) -> list[Item]:
    rules = rules if rules is not None else yaml.safe_load((root / "data/evidence-rules.yaml").read_text(encoding="utf-8"))
    checker = Checker(root, progress, site_json)
    progress = checker.progress
    progress_dates = _git_dates("site/data/progress.json", root)
    fallback_date = progress_dates[0] if progress_dates else None
    items: list[Item] = []

    def build(id_: str, kind: str, n: int, title: str, done: bool, spec: dict, **extra) -> Item:
        item = Item(id_, kind, n, title, bool(done), None, attests=dict(spec.get("attests", {})), **extra)
        results = [checker.check(r) for r in spec.get("evidence", [])]
        automatic = [(ok, desc, d) for ok, desc, d in results if ok is not None]
        if automatic:
            item.verified = all(ok for ok, _, _ in automatic)
            item.missing = [desc for ok, desc, _ in automatic if not ok]
        if done:
            dates = [d for ok, _, d in results if ok and d]
            item.last_evidence = max(dates) if dates else fallback_date
        return item

    for m in progress.get("missions", []):
        spec = rules.get("missions", {}).get(m["n"], {})
        items.append(build(f"mission:{m['n']}", "mission", m["n"], m["title"], m.get("done", False), spec,
                           file=m.get("file") or f"{m['n']:02d}.md"))
    for t in progress.get("tiers", []):
        spec = rules.get("bosses", {}).get(t["id"], {})
        items.append(build(f"boss:{t['id']}", "boss", t["id"], t["boss"]["title"], t["boss"].get("done", False), spec,
                           file=f"BOSS-{t['id']}.md"))
    for t in progress.get("tracks", []):
        for s in t["steps"]:
            spec = rules.get("tracks", {}).get(t["id"], {}).get(s["n"], {})
            items.append(build(f"track:{t['id']}:{s['n']}", "track", s["n"], s["title"], s.get("done", False), spec,
                               file=t["file"], track=t["id"]))
    return items


def main() -> int:
    items = scan()
    print(json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
