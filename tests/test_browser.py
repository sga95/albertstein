"""app.js nel browser vero: gira solo se Playwright e Chromium ci sono (in locale, non in CI)."""

import json
import os
import shutil
import threading
from functools import partial
from http.server import ThreadingHTTPServer

import pytest

from lib.progress import SITE

pw_api = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def browser():
    with pw_api.sync_playwright() as pw:
        try:
            b = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH"))
        except Exception as e:  # browser non scaricato
            pytest.skip(f"Chromium non disponibile: {str(e).splitlines()[0]}")
        yield b
        b.close()


def serve(directory):
    import sys

    sys.path.insert(0, str(SITE.parent / "tools"))
    from serve import Handler

    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(directory)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def test_site_json_is_applied(browser, tmp_path):
    site = tmp_path / "site"
    shutil.copytree(SITE, site)
    d = json.loads((site / "data/site.json").read_text(encoding="utf-8"))
    d["tagline"] = "New tagline"
    d["email"] = "a@example.org"
    d["colors"]["navy"] = "#112233"
    d["nav"] = [{"label": "Lab", "path": "lab/", "order": 1}, {"label": "CV", "path": "cv/", "order": 2}]
    d["show"]["notesOnHome"] = False
    d["show"]["photo"] = False
    (site / "data/site.json").write_text(json.dumps(d), encoding="utf-8")
    cv = site / "cv/index.html"
    cv.write_text(cv.read_text(encoding="utf-8").replace('data-order="1"', 'data-order="9"'), encoding="utf-8")

    srv, url = serve(site)
    try:
        page = browser.new_page()
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        page.goto(url + "/", wait_until="load")
        page.wait_for_selector("[data-progress] .cell")
        assert page.text_content("h1") == "New tagline"
        assert page.get_attribute('a[data-site="email"]', "href") == "mailto:a@example.org"
        assert page.evaluate("getComputedStyle(document.querySelector('.band')).backgroundColor") == "rgb(17, 34, 51)"
        assert [a.text_content() for a in page.query_selector_all("header.top nav a")] == ["Lab", "CV"]
        assert page.evaluate("document.querySelector('[data-site-show=notesOnHome]').hidden") is True

        page.goto(url + "/cv/", wait_until="load")
        page.wait_for_selector("[data-earned] li")
        current = [a.text_content() for a in page.query_selector_all('header.top nav a[aria-current="page"]')]
        assert current == ["CV"]
        titles = [h.text_content() for h in page.query_selector_all("main .card h2")]
        assert titles[0] == "01Earned on this path" and titles[-1] == "07About me"
        assert page.evaluate("document.querySelector('.cv-hero img').hidden") is True
        assert page.evaluate("document.querySelector('main .wrap').lastElementChild.className") == "print-link"
    finally:
        srv.shutdown()


def test_without_site_json_the_html_stays(browser, tmp_path):
    site = tmp_path / "site"
    shutil.copytree(SITE, site)
    (site / "data/site.json").unlink()
    srv, url = serve(site)
    try:
        page = browser.new_page()
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        page.goto(url + "/", wait_until="load")
        page.wait_for_selector("[data-progress] .cell")
        assert page.text_content("h1").startswith("I build small networks")
        assert [a.text_content() for a in page.query_selector_all("header.top nav a")] == ["CV", "Lab", "Progress"]
    finally:
        srv.shutdown()
