import yaml
from engine.tests.helpers import ROOT, load_progress

import readiness
import scan


def test_all_false_means_empty_radar_and_mission_1_next():
    items = scan.scan(ROOT, progress=load_progress("progress-start.json"))
    data = readiness.compute(items, today="2026-01-01")
    assert data["generated_at"] == "2026-01-01"
    assert data["target_roles"] == ["junior-network-engineer", "noc-analyst", "sysadmin-junior"]
    for role in data["roles"]:
        assert role["score_0_100"] == 0
        assert all(a["ratio"] == 0 for a in role["axes"])
        assert role["next_step"]["id"] == "mission:1"
        assert len(role["gaps"]) == len(role["axes"])
    assert all(s["level"] == 0 and s["verified"] is None for s in data["skills"])


def test_midway_scores_make_sense():
    items = scan.scan(ROOT, progress=load_progress("progress-midway.json"))
    data = readiness.compute(items, today="2026-06-01")
    roles = {r["id"]: r for r in data["roles"]}
    skills = {s["id"]: s for s in data["skills"]}
    assert skills["git"]["level"] == 3  # boss 1 attesta git 3
    assert skills["dns"]["level"] == 2
    assert skills["routing"]["level"] == 0
    assert skills["account-security"]["level"] == 2
    # metà percorso: nessun ruolo pronto, nessuno a zero
    for r in roles.values():
        assert 0 < r["score_0_100"] < 100, r["id"]
    # il junior network engineer ha ancora il routing come gap, e la missione 13 lo chiude
    gap = next(g for g in roles["junior-network-engineer"]["gaps"] if g["skill"] == "routing")
    assert gap["next_mission"] == "mission:13"
    # il prossimo passo in ordine di percorso è la missione 8
    assert roles["junior-network-engineer"]["next_step"]["id"] == "mission:8"
    # it-support pesa le skill di Shield, quindi è il più avanti a metà percorso
    assert roles["it-support-l2"]["score_0_100"] >= roles["network-automation-junior"]["score_0_100"]


def test_unverified_propagates_to_the_skill():
    items = scan.scan(ROOT, progress=load_progress("progress-midway.json"))
    data = readiness.compute(items, today="2026-06-01")
    skills = {s["id"]: s for s in data["skills"]}
    assert skills["monitoring"]["verified"] is False  # missione 6 done ma monitor/check.py manca
    assert skills["dns"]["verified"] is True  # solo evidenze manuali: vale la parola


def test_gap_ordering_and_next_item_fallback():
    items = scan.scan(ROOT, progress=load_progress("progress-start.json"))
    role = {"id": "x", "title_it": "x", "title_en": "x",
            "skills": {"routing": {"weight": 5, "min_level": 4}, "git": {"weight": 1, "min_level": 1}}}
    data = readiness.role_readiness(role, readiness.skill_levels(items, yaml.safe_load((ROOT / "data/skills.yaml").read_text())["skills"]), items)
    assert [g["skill"] for g in data["gaps"]] == ["routing", "git"]
    assert data["gaps"][0]["next_mission"] == "boss:5"  # l'unico che porta routing a 4
    assert data["gaps"][1]["next_mission"] == "mission:1"


def test_every_role_only_references_known_skills():
    skills = {s["id"] for s in yaml.safe_load((ROOT / "data/skills.yaml").read_text())["skills"]}
    for role in yaml.safe_load((ROOT / "data/roles.yaml").read_text())["roles"]:
        assert set(role["skills"]) <= skills, role["id"]
        assert all(1 <= v["min_level"] <= 4 and 1 <= v["weight"] <= 5 for v in role["skills"].values())
