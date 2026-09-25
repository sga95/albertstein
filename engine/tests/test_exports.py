import json
import shutil

from engine.tests.helpers import ROOT

import render


def copy(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copytree(ROOT / "site", repo / "site")
    shutil.copytree(ROOT / "data", repo / "data")
    return repo


def test_quests_and_loot_exports(tmp_path):
    repo = copy(tmp_path)
    q = render.export_quests(repo)
    assert {x["category"] for x in q["quests"]} == {"network", "gaming", "puzzles", "electronics", "science", "books"}
    ids = [x["id"] for x in q["quests"]]
    assert len(ids) == len(set(ids))
    loot = render.export_loot(repo)
    assert set(loot["loot"]) == {"1", "2", "3", "4", "5", "6"}
    assert "note" not in json.dumps(loot)  # le note per Stefano non finiscono sul sito


def test_puzzle_solution_is_released_after_seven_days(tmp_path):
    repo = copy(tmp_path)
    (repo / "data/puzzles.yaml").write_text(
        "puzzles:\n"
        "  - date: 2026-10-05\n    title: A\n    question: q\n    hint: h\n    solution: s\n"
        "  - date: 2026-10-12\n    title: B\n    question: q2\n    solution: s2\n", encoding="utf-8")
    out = render.export_puzzles(repo, today="2026-10-12")
    a, b = out["puzzles"]
    assert a["solution"] == "s" and a["solution_on"] == "2026-10-12"
    assert b["solution"] is None and b["solution_on"] == "2026-10-19"
    out = render.export_puzzles(repo, today="2026-10-19")
    assert out["puzzles"][1]["solution"] == "s2"


def test_pages_counts(tmp_path):
    repo = copy(tmp_path)
    pages = render.export_pages(repo, puzzles=0)
    assert pages == {"puzzle": 0, "codex": 0, "reading": 6}
    codex = repo / "site/codex/index.html"
    codex.write_text(codex.read_text(encoding="utf-8").replace('<dl class="codex">\n', '<dl class="codex">\n<dt>ARP</dt><dd>Who has this IP.</dd>\n'), encoding="utf-8")
    assert render.export_pages(repo, puzzles=2)["codex"] == 1
