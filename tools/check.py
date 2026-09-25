#!/usr/bin/env python3
"""make check: tutti i controlli del sito in un comando.

Uso:
  python3 tools/check.py            tutti i controlli, esce con 1 se c'è un errore
  python3 tools/check.py --lab-md   solo il lint delle note, in Markdown (per il commento in PR)
  python3 tools/check.py --json     stampa il riepilogo in JSON (per la CI)

Errori (bloccano): JSON rotto, schema non rispettato, incoerenze, link rotti,
immagini mancanti o senza alt, pagine o immagini troppo pesanti.
Avvisi (non bloccano): regola di sblocco violata, file in check-ignore.txt ancora mancanti.
Il lint delle note di lab dà un punteggio, mai un errore.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import labnotes, pages, progress  # noqa: E402
from lib.schema import validate  # noqa: E402


def _rel(path: Path) -> str:
    try:
        return path.relative_to(progress.ROOT).as_posix()
    except ValueError:
        return str(path)


def check_progress() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = progress.load()
    except progress.ProgressSyntaxError as e:
        return [str(e)], []
    rel = progress.PROGRESS.relative_to(progress.ROOT).as_posix()
    for err in validate(data, progress.load_schema()):
        errors.append(f"{rel}: {err}")
    if errors:
        return errors, warnings
    errors.extend(f"{rel}: {e}" for e in progress.consistency_errors(data))
    warnings.extend(f"{rel}: regola di sblocco: {w}" for w in progress.unlock_warnings(data))
    return errors, warnings


def check_site_json() -> tuple[list[str], list[str]]:
    """site.json: JSON valido e chiavi conosciute. Ogni chiave è opzionale."""
    if not progress.SITE_JSON.exists():
        return [], ["site/data/site.json manca: il sito usa i testi scritti nell'HTML"]
    try:
        data = progress.load(progress.SITE_JSON)
    except progress.ProgressSyntaxError as e:
        return [str(e)], []
    rel = _rel(progress.SITE_JSON)
    errors = [f"{rel}: {err}" for err in validate(data, progress.load_schema(progress.SITE_SCHEMA))]
    warnings = []
    for item in data.get("nav", []) if not errors else []:
        target = progress.SITE / item["path"]
        if item["path"].endswith("/") or item["path"] == "":
            target = target / "index.html"
        if not target.exists():
            errors.append(f"{rel}: la voce di menu \"{item['label']}\" punta a {item['path']}, che non esiste in site/")
    return errors, warnings


def check_codex() -> tuple[list[str], list[str]]:
    """site/codex/index.html: ogni voce <dd> al massimo 40 parole, ogni <dt> non vuoto."""
    import re
    from html import unescape
    page = progress.SITE / "codex" / "index.html"
    if not page.exists():
        return [], []
    html = page.read_text(encoding="utf-8")
    errors = []
    terms = re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", html, flags=re.S)
    for term, definition in terms:
        words = len(re.sub(r"<[^>]+>", " ", unescape(definition)).split())
        clean = re.sub(r"<[^>]+>", "", term).strip()
        if not clean:
            errors.append("codex/index.html: una voce senza termine (<dt> vuoto)")
        elif words > 40:
            errors.append(f"codex/index.html: \"{clean}\" ha {words} parole, il massimo è 40: taglia, è un glossario")
        elif words == 0:
            errors.append(f"codex/index.html: \"{clean}\" non ha definizione")
    return errors, []


def check_secrets() -> tuple[list[str], list[str]]:
    """gitleaks se installato, altrimenti un avviso. In CI gira sempre come job separato."""
    exe = shutil.which("gitleaks")
    if not exe:
        return [], ["gitleaks non installato: il controllo dei secret gira solo in CI (o installalo: https://github.com/gitleaks/gitleaks)"]
    run = subprocess.run(
        [exe, "detect", "--source", str(progress.ROOT), "--no-banner", "--redact", "--exit-code", "1"],
        capture_output=True, text=True,
    )
    if run.returncode == 0:
        return [], []
    tail = (run.stdout + run.stderr).strip().splitlines()[-15:]
    return ["gitleaks ha trovato possibili secret:\n  " + "\n  ".join(tail)], []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lab-md", action="store_true", help="solo lint note di lab, output Markdown")
    ap.add_argument("--json", action="store_true", help="riepilogo in JSON")
    ap.add_argument("--no-secrets", action="store_true", help="salta gitleaks")
    args = ap.parse_args(argv)

    reports = labnotes.lint_all()
    if args.lab_md:
        print(labnotes.render_markdown(reports))
        return 0

    sections: list[tuple[str, list[str], list[str]]] = []
    sections.append(("progress.json", *check_progress()))
    sections.append(("site.json", *check_site_json()))
    sections.append(("pagine HTML: link, immagini, alt, peso", *pages.check_pages()))
    sections.append(("codex: massimo 40 parole per voce", *check_codex()))
    if not args.no_secrets:
        sections.append(("secret", *check_secrets()))

    all_errors = [e for _, errs, _ in sections for e in errs]
    all_warnings = [w for _, _, warns in sections for w in warns]

    if args.json:
        print(json.dumps({
            "errors": all_errors,
            "warnings": all_warnings,
            "lab_notes": [{"file": r.rel, "score": r.score, "suggestions": r.suggestions} for r in reports],
        }, ensure_ascii=False, indent=2))
        return 1 if all_errors else 0

    for name, errs, warns in sections:
        state = "ERRORE" if errs else "ok"
        print(f"[{state:>6}] {name}")
        for e in errs:
            print("  errore: " + e.replace("\n", "\n  "))
        for w in warns:
            print("  avviso: " + w)
    print("[  info] note di lab")
    print(labnotes.render_text(reports))
    print()
    if all_errors:
        print(f"{len(all_errors)} errore/i, {len(all_warnings)} avviso/i. Leggi CONTRIBUTING.md per capire il messaggio.")
        return 1
    print(f"Tutto ok. {len(all_warnings)} avviso/i.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
