import json
import shutil

from engine.tests.helpers import ROOT, load_progress

import render


def test_radar_is_empty_at_zero_and_filled_otherwise():
    axes = [{"name": f"s{i}", "short": f"s{i}", "ratio": 0.0, "weight": 1} for i in range(5)]
    svg = render.radar_svg(axes)
    assert "<polygon" in svg and 'fill="var(--accent)"' not in svg
    axes[0]["ratio"] = 1.0
    assert 'fill="var(--accent)"' in render.radar_svg(axes)
    assert render.radar_svg(axes[:2]) == ""


def test_render_writes_json_and_page(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copytree(ROOT / "site", repo / "site")
    shutil.copytree(ROOT / "data", repo / "data")
    (repo / "site/data/progress.json").write_text(json.dumps(load_progress("progress-midway.json")), encoding="utf-8")
    data = render.render(today="2026-06-01", root=repo)
    out = json.loads((repo / "site/data/readiness.json").read_text(encoding="utf-8"))
    assert out["generated_at"] == "2026-06-01"
    assert [r["id"] for r in out["roles"][:3]] == out["target_roles"]
    html = (repo / "site/readiness/index.html").read_text(encoding="utf-8")
    assert '<svg class="radar"' in html
    assert "unverified" in html  # missione 6 senza monitor/check.py
    assert 'href="https://github.com/sga95/albertstein/blob/main/missioni/' in html
    assert len(html.encode()) < 200 * 1024


def test_committed_output_is_up_to_date():
    """Il json e la pagina nel repo devono coincidere con quello che il motore genera oggi (a parte la data)."""
    committed = json.loads((ROOT / "site/data/readiness.json").read_text(encoding="utf-8"))
    import readiness, scan
    fresh = readiness.compute(scan.scan(ROOT), today=committed["generated_at"])
    assert fresh["roles"] == committed["roles"]
    assert fresh["skills"] == committed["skills"]
