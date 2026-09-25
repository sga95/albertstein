import json
import subprocess
import sys

from lib import progress
from lib.schema import validate

CHECK = progress.ROOT / "tools" / "check.py"


def load_site():
    return json.loads(progress.SITE_JSON.read_text(encoding="utf-8"))


def test_real_site_json_is_valid():
    assert validate(load_site(), progress.load_schema(progress.SITE_SCHEMA)) == []


def test_every_nav_entry_points_to_an_existing_page():
    for item in load_site()["nav"]:
        assert (progress.SITE / item["path"] / "index.html").exists(), item


def test_unknown_key_and_bad_color():
    schema = progress.load_schema(progress.SITE_SCHEMA)
    d = load_site()
    d["colours"] = {}
    d["colors"]["accent"] = "orange-ish"
    errs = [str(e) for e in validate(d, schema)]
    assert any(e.startswith('colours: chiave sconosciuta "colours"') for e in errs)
    assert any(e.startswith("colors.accent:") for e in errs)


def test_every_key_is_optional():
    assert validate({}, progress.load_schema(progress.SITE_SCHEMA)) == []


def test_data_site_keys_in_html_exist_in_site_json():
    """Ogni data-site="chiave" nelle pagine deve avere la chiave in site.json (o app.js non la tocca)."""
    import re

    site = load_site()

    def has(key):
        node = site
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return isinstance(node, str)

    for page in progress.SITE.rglob("*.html"):
        html = page.read_text(encoding="utf-8")
        for key in re.findall(r'data-site="([^"]+)"', html):
            assert has(key), f"{page.name}: data-site=\"{key}\" non è in site.json"
        for key in re.findall(r'data-site-show="([^"]+)"', html):
            assert key in site["show"], f"{page.name}: data-site-show=\"{key}\" non è in site.json show"


def test_check_reports_missing_nav_target(tmp_path, monkeypatch):
    """check_site_json segnala una voce di menu che punta a una pagina inesistente."""
    sys.path.insert(0, str(progress.ROOT / "tools"))
    import check

    d = load_site()
    d["nav"].append({"label": "Now", "path": "now/", "order": 9})
    fake = tmp_path / "site.json"
    fake.write_text(json.dumps(d), encoding="utf-8")
    monkeypatch.setattr(progress, "SITE_JSON", fake)
    errors, _ = check.check_site_json()
    assert len(errors) == 1
    assert 'la voce di menu "Now" punta a now/, che non esiste' in errors[0]


def test_cv_sections_have_unique_data_order():
    import re

    html = (progress.SITE / "cv" / "index.html").read_text(encoding="utf-8")
    orders = [int(x) for x in re.findall(r'data-order="(\d+)"', html)]
    assert orders == sorted(orders) and len(orders) == len(set(orders)) == 7
