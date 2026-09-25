import json
import re

import yaml

from lib import progress
from lib.schema import validate


def test_pi_track_is_sealed_until_boss_1(fixtures):
    data = progress.load()
    st = progress.unlock_status(data)
    assert st["sealed"]["pi"] is True and st["sealed"]["shield"] is False
    assert set(st["tracks"]["pi"]) == {"locked"}
    data["tiers"][0]["boss"]["done"] = True
    st = progress.unlock_status(data)
    assert st["sealed"]["pi"] is False and st["tracks"]["pi"][0] == "open"


def test_requires_mission_and_schema(fixtures):
    d = json.loads((fixtures / "progress-start.json").read_text(encoding="utf-8"))
    d["tracks"][0]["requires"] = {"mission": 2}
    assert validate(d, progress.load_schema()) == []
    assert progress.unlock_status(d)["sealed"]["shield"] is True
    d["missions"][0]["done"] = d["missions"][1]["done"] = True
    assert progress.unlock_status(d)["sealed"]["shield"] is False
    d["tracks"][0]["requires"] = {"quest": "x"}
    assert validate(d, progress.load_schema())


def test_pi_md_has_every_step_and_cv_line():
    sheet = (progress.ROOT / "missioni/PI.md").read_text(encoding="utf-8")
    pi = next(t for t in progress.load()["tracks"] if t["id"] == "pi")
    assert pi["requires"] == {"boss": 1} and len(pi["steps"]) == 16
    for s in pi["steps"][:15]:
        assert f"## P{s['n']}." in sheet, s["n"]
        assert f"**Riga CV:** {s['skill']}" in sheet, s["n"]
    assert "## Boss Pi" in sheet and pi["steps"][15]["skill"] in sheet


def test_hardware_references_exist():
    hw = yaml.safe_load((progress.ROOT / "data/hardware.yaml").read_text(encoding="utf-8"))
    quests = {q["id"] for q in yaml.safe_load((progress.ROOT / "data/quests.yaml").read_text(encoding="utf-8"))["quests"]}
    data = progress.load()
    pi_steps = {s["n"] for t in data["tracks"] if t["id"] == "pi" for s in t["steps"]}
    missions = {m["n"] for m in data["missions"]}
    levels = {t["id"] for t in data["tiers"]}
    for item in hw["hardware"]:
        assert item["status"] in ("owned", "requested", "granted", "arrived", "none"), item["id"]
        if "kit" in item:
            assert item["kit"] in hw["kits"], item["id"]
        for ref in item["for"]:
            if m := re.fullmatch(r"P(\d+)", ref):
                assert int(m.group(1)) in pi_steps, ref
            elif m := re.fullmatch(r"M(\d+)", ref):
                assert int(m.group(1)) in missions, ref
            elif m := re.fullmatch(r"L(\d+)", ref):
                assert int(m.group(1)) in levels, ref
            elif ref.startswith("Q:"):
                assert ref[2:] in quests, ref
            else:
                raise AssertionError(ref)
    non_loot = sum(i["cost_eur"] for i in hw["hardware"] if not i.get("loot") and i["id"] != "mini-pc")
    kits_total = sum(k["cost_eur"] for k in hw["kits"].values())
    assert kits_total < 60
    out = json.loads((progress.SITE / "data/gear.json").read_text(encoding="utf-8"))
    assert [i["id"] for i in out["hardware"]] == [i["id"] for i in hw["hardware"]]
