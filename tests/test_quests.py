import json
import subprocess
import sys

import yaml

from lib import progress
from lib.schema import validate


def test_progress_accepts_quests(fixtures):
    d = json.loads((fixtures / "progress-start.json").read_text(encoding="utf-8"))
    d["quests"] = [{"id": "lag-lab", "title": "Lag lab", "done": False}]
    assert validate(d, progress.load_schema()) == []
    d["quests"][0]["note"] = "x"
    assert validate(d, progress.load_schema())


def test_quests_in_progress_exist_in_catalogue():
    catalogue = {q["id"] for q in yaml.safe_load((progress.ROOT / "data/quests.yaml").read_text(encoding="utf-8"))["quests"]}
    for q in progress.load().get("quests", []):
        assert q["id"] in catalogue, q


def test_quests_md_mentions_every_quest_id():
    text = (progress.ROOT / "missioni/QUESTS.md").read_text(encoding="utf-8")
    for q in yaml.safe_load((progress.ROOT / "data/quests.yaml").read_text(encoding="utf-8"))["quests"]:
        assert f"(`{q['id']}`)" in text, q["id"]


def test_codex_lint(tmp_path, monkeypatch):
    sys.path.insert(0, str(progress.ROOT / "tools"))
    import check

    site = tmp_path / "site"
    (site / "codex").mkdir(parents=True)
    page = site / "codex" / "index.html"
    monkeypatch.setattr(progress, "SITE", site)
    page.write_text("<dl><dt>ARP</dt><dd>" + "word " * 41 + "</dd><dt>DNS</dt><dd>Names to addresses.</dd><dt></dt><dd>x</dd></dl>", encoding="utf-8")
    errors, _ = check.check_codex()
    assert any('"ARP" ha 41 parole' in e for e in errors)
    assert any("senza termine" in e for e in errors)
    assert len(errors) == 2


def test_subnet_quiz_generates_valid_answers():
    sys.path.insert(0, str(progress.ROOT / "tools"))
    import ipaddress
    import random

    import subnet_quiz

    rng = random.Random(1)
    seen = set()
    for _ in range(200):
        q, a = subnet_quiz.make_question(rng)
        seen.add(q.split()[0])
        if q.startswith(("Network", "Broadcast", "First", "Last")):
            ipaddress.ip_address(a)
        elif q.startswith("Usable"):
            assert int(a) >= 2
        elif q.startswith("Dotted"):
            ipaddress.ip_network("0.0.0.0/" + a)
        else:
            assert a.startswith("/")
    assert {"Network", "Broadcast", "Usable", "Dotted", "Prefix", "First", "Last"} <= seen


def test_subnet_quiz_scores():
    sys.path.insert(0, str(progress.ROOT / "tools"))
    import random

    import subnet_quiz

    rng = random.Random(3)
    answers = [subnet_quiz.make_question(random.Random(3))[1]]
    # stesse domande, risposte giuste alla prima e sbagliate dopo
    qs = [subnet_quiz.make_question(rng) for _ in range(3)]
    it = iter([qs[0][1], "wrong", qs[2][1]])
    out = []
    score, _ = subnet_quiz.run(3, 3, 600, ask=lambda _: next(it), out=out.append)
    assert score == 2
    assert out[-1].startswith("Score 2/3")
