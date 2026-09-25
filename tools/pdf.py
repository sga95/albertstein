#!/usr/bin/env python3
"""make pdf: esporta la pagina CV in site/cv/Alberto-Galliani-CV.pdf con lo stile di stampa.

Serve Playwright (solo per questo comando, non in CI):
  pip install playwright && python3 -m playwright install chromium

Avvia un server locale sulla cartella site/, apre la pagina CV in Chromium headless,
aspetta che app.js abbia applicato site.json e progress.json, e stampa in A4.
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.progress import SITE  # noqa: E402
from serve import Handler  # noqa: E402

DEFAULT_OUT = SITE / "cv" / "Alberto-Galliani-CV.pdf"


def export(out: Path = DEFAULT_OUT, page_path: str = "cv/") -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "Playwright non installato. Solo per questo comando:\n"
            "  pip install playwright && python3 -m playwright install chromium"
        )

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(SITE)))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            # CHROMIUM_PATH: usa un Chromium già installato invece di quello scaricato da Playwright
            exe = os.environ.get("CHROMIUM_PATH")
            browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{port}/{page_path}", wait_until="load")
            # app.js ha finito quando la lista "earned" ha almeno una riga (anche quella vuota)
            page.wait_for_selector("[data-earned] li", timeout=10_000)
            page.emulate_media(media="print")
            out.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(
                path=str(out),
                format="A4",
                print_background=True,
                margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"},
            )
            browser.close()
    finally:
        server.shutdown()
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"file di uscita (default {DEFAULT_OUT.relative_to(SITE.parent)})")
    args = ap.parse_args(argv)
    out = export(args.out)
    print(f"scritto {out.relative_to(SITE.parent) if out.is_relative_to(SITE.parent) else out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
