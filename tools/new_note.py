#!/usr/bin/env python3
"""make note TITLE="..." e make postmortem TITLE="...".

Crea site/lab/YYYY-MM-DD-slug.html partendo da site/lab/template.html
(per il post-mortem: site/lab/postmortem-template.html) e aggiunge la riga
in cima alla lista in site/lab/index.html. Non tocca progress.json: per un
post-mortem stampa il pezzo da incollare a mano nella lista "incidents".
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.progress import SITE  # noqa: E402

LAB = SITE / "lab"
TEMPLATE = LAB / "template.html"
POSTMORTEM_TEMPLATE = LAB / "postmortem-template.html"
INDEX = LAB / "index.html"
EMPTY_ROW = '<li class="empty-state">No notes yet.</li>'


def slugify(title: str) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "note"


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_note(template: str, title: str, day: date, kind: str) -> str:
    t = html_escape(title)
    out = template.replace("TITLE OF THE POST-MORTEM", t).replace("TITLE OF THE NOTE", t)
    out = out.replace("YYYY-MM-DD", day.isoformat())
    if kind == "lab":
        out = out.replace(" · Packet Tracer or Wireshark or Incident", " · Lab")
    return out


def insert_in_index(index_html: str, row: str) -> str:
    """Mette la riga in cima a <ul class="notes"> e toglie il segnaposto "No notes yet"."""
    index_html = index_html.replace("          " + EMPTY_ROW + "\n", "").replace(EMPTY_ROW, "")
    marker = '<ul class="notes">'
    if marker not in index_html:
        raise SystemExit("site/lab/index.html: non trovo <ul class=\"notes\">, aggiungi la riga a mano")
    return index_html.replace(marker, marker + "\n          " + row, 1)


def create(title: str, kind: str, day: date | None = None, lab: Path = LAB) -> Path:
    day = day or date.today()
    template = lab / ("postmortem-template.html" if kind == "postmortem" else "template.html")
    if not template.exists():
        raise SystemExit(f"manca {template}")
    prefix = f"{day.isoformat()}-postmortem-" if kind == "postmortem" else f"{day.isoformat()}-"
    target = lab / f"{prefix}{slugify(title)}.html"
    if target.exists():
        raise SystemExit(f"{target.name} esiste già in {lab}: scegli un altro titolo")
    target.write_text(build_note(template.read_text(encoding="utf-8"), title, day, kind), encoding="utf-8")

    index = lab / "index.html"
    label = f"Post-mortem: {title}" if kind == "postmortem" else title
    row = f'<li><span class="date mono">{day.isoformat()}</span><a href="{target.name}">{html_escape(label)}</a></li>'
    index.write_text(insert_in_index(index.read_text(encoding="utf-8"), row), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="titolo della nota")
    ap.add_argument("--postmortem", action="store_true", help="crea un post-mortem invece di una nota di lab")
    ap.add_argument("--date", help="data YYYY-MM-DD (default: oggi)")
    args = ap.parse_args(argv)
    if not args.title.strip():
        ap.error("il titolo è vuoto: make note TITLE=\"Il mio primo lab\"")
    day = date.fromisoformat(args.date) if args.date else date.today()
    kind = "postmortem" if args.postmortem else "lab"
    target = create(args.title.strip(), kind, day)
    rel = target.relative_to(SITE.parent).as_posix()
    print(f"creato {rel}")
    print(f"aggiunta la riga in cima a site/lab/index.html")
    print(f"apri il file, sostituisci i testi segnaposto, poi: make check")
    if kind == "postmortem":
        print()
        print("quando è finito, aggiungi in site/data/progress.json, nella lista \"incidents\":")
        print(f'  {{ "date": "{day.isoformat()}", "title": "Post-mortem: {args.title.strip()}", "url": "../lab/{target.name}" }}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
