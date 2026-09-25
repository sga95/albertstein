import json

from engine.tests.helpers import ROOT, load_progress

import scan


def test_scan_covers_every_item_of_the_real_progress():
    items = scan.scan(ROOT)
    progress = json.loads((ROOT / "site/data/progress.json").read_text(encoding="utf-8"))
    import yaml
    n_steps = sum(len(t["steps"]) for t in progress["tracks"])
    n_certs = len(yaml.safe_load((ROOT / "data/certs.yaml").read_text(encoding="utf-8"))["certs"])
    assert len(items) == len(progress["missions"]) + len(progress["tiers"]) + n_steps + len(progress.get("quests", [])) + n_certs
    assert all(it.attests for it in items if it.kind != "cert"), "ogni item deve attestare almeno una skill"


def test_nothing_done_means_nothing_verified_or_dated():
    items = scan.scan(ROOT, progress=load_progress("progress-start.json"))
    assert not any(it.done for it in items)
    assert all(it.last_evidence is None for it in items)


def test_manual_only_items_are_neither_verified_nor_unverified():
    items = {it.id: it for it in scan.scan(ROOT, progress=load_progress("progress-midway.json"))}
    assert items["mission:2"].done and items["mission:2"].verified is None
    assert items["track:shield:1"].verified is None


def test_done_without_evidence_is_unverified_with_reasons():
    items = {it.id: it for it in scan.scan(ROOT, progress=load_progress("progress-midway.json"))}
    m6 = items["mission:6"]
    assert m6.done and m6.verified is False
    assert "file monitor/check.py" in m6.missing
    assert "file .github/workflows/uptime.yml" in m6.missing
    m7 = items["mission:7"]
    assert m7.verified is False and m7.missing == ["almeno 1 note di lab (trovate 0)"]


def test_evidence_present_makes_it_verified(repo_copy):
    progress = load_progress("progress-midway.json")
    (repo_copy / "monitor").mkdir()
    (repo_copy / "monitor/check.py").write_text("print('ok')\n")
    (repo_copy / ".github/workflows").mkdir(parents=True)
    (repo_copy / ".github/workflows/uptime.yml").write_text("on: schedule\n")
    (repo_copy / "site/lab/2026-03-01-vlan.html").write_text("<html></html>")
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    assert items["mission:6"].verified is True and items["mission:6"].missing == []
    assert items["mission:7"].verified is True
    # senza git la data dell'evidenza resta ignota
    assert items["mission:6"].last_evidence is None


def test_incidents_and_nav_rules(repo_copy):
    progress = load_progress("progress-midway.json")
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    assert items["boss:2"].verified is True  # la fixture ha un incidente
    assert items["boss:2"].last_evidence == "2026-03-02"
    assert items["boss:1"].verified is False
    assert 'voce di menu "Now"' in items["boss:1"].missing


def test_unknown_rule_is_an_error(repo_copy):
    import pytest

    rules = {"missions": {1: {"evidence": [{"teleport": "x"}], "attests": {"git": 1}}}, "bosses": {}, "tracks": {}}
    with pytest.raises(ValueError):
        scan.scan(repo_copy, progress=load_progress("progress-start.json"), rules=rules)


def test_quest_items_come_from_progress_and_need_a_note(repo_copy):
    progress = load_progress("progress-start.json")
    progress["quests"] = [{"id": "lag-lab", "title": "Lag lab", "done": True}, {"id": "radio", "title": "Radio", "done": False}]
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    assert items["quest:lag-lab"].done and items["quest:lag-lab"].verified is False
    assert items["quest:lag-lab"].missing == ['una nota di lab con "lag-lab" nel nome']
    (repo_copy / "site/lab/2026-04-01-lag-lab.html").write_text("<html></html>")
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    assert items["quest:lag-lab"].verified is True
    assert items["quest:radio"].done is False


def test_passed_cert_attests_level_3_on_its_roles(repo_copy):
    progress = load_progress("progress-start.json")
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    assert items["cert:ccna"].done is False and items["cert:ccna"].verified is None
    (repo_copy / "site/certs/proof").mkdir(parents=True)
    (repo_copy / "site/certs/proof/ccna.png").write_bytes(b"x")
    items = {it.id: it for it in scan.scan(repo_copy, progress=progress)}
    ccna = items["cert:ccna"]
    assert ccna.done and ccna.verified is True
    assert ccna.attests["routing"] == 3 and ccna.attests["ip-addressing"] == 3
    import readiness, yaml
    skills = yaml.safe_load((ROOT / "data/skills.yaml").read_text())["skills"]
    levels = readiness.skill_levels(list(items.values()), skills)
    assert levels["routing"]["level"] == 3 and levels["routing"]["verified"] is True
