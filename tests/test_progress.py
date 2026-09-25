import json

import pytest

from lib import progress


def load(fixtures, name):
    return json.loads((fixtures / name).read_text(encoding="utf-8"))


def test_syntax_error_has_line_number_and_hint(fixtures):
    with pytest.raises(progress.ProgressSyntaxError) as exc:
        progress.load(fixtures / "progress-broken.json")
    err = exc.value
    assert err.lineno == 6
    msg = str(err)
    assert "riga 6" in msg
    assert "manca una virgola" in msg
    assert '{ "n": 2' in msg  # la riga incriminata viene mostrata


def test_unlock_status_at_start(fixtures):
    st = progress.unlock_status(load(fixtures, "progress-start.json"))
    assert st["missions"]["1"] == "open"
    assert all(v == "locked" for k, v in st["missions"].items() if k != "1")
    assert all(v == "locked" for v in st["bosses"].values())
    for statuses in st["tracks"].values():
        assert statuses[0] == "open" and set(statuses[1:]) == {"locked"}


def test_unlock_status_midway(fixtures):
    st = progress.unlock_status(load(fixtures, "progress-midway.json"))
    assert st["missions"]["7"] == "done"
    assert st["missions"]["8"] == "open"
    assert st["missions"]["9"] == "locked"
    assert st["bosses"] == {"1": "done", "2": "done", "3": "locked", "4": "locked", "5": "locked", "6": "locked"}
    assert st["tracks"]["shield"] == ["done"] * 9
    assert st["tracks"]["voice"][:5] == ["done", "done", "done", "open", "locked"]


def test_boss_opens_when_level_is_complete(fixtures):
    d = load(fixtures, "progress-midway.json")
    for m in d["missions"]:
        if m["n"] == 8:
            m["done"] = True
    assert progress.unlock_status(d)["bosses"]["3"] == "open"


def test_no_warnings_when_order_is_respected(fixtures):
    assert progress.unlock_warnings(load(fixtures, "progress-start.json")) == []
    assert progress.unlock_warnings(load(fixtures, "progress-midway.json")) == []


def test_warnings_when_order_is_violated(fixtures):
    w = progress.unlock_warnings(load(fixtures, "progress-out-of-order.json"))
    assert len(w) == 3
    assert w[0].startswith('missione 3 "The pipeline" è done ma la 2')
    assert w[1].startswith("boss del livello 2")
    assert "4, 5, 6" in w[1]
    assert w[2].startswith("binario Voice: passo 3")


def test_consistency_errors(fixtures):
    d = load(fixtures, "progress-start.json")
    assert progress.consistency_errors(d) == []
    d["missions"].append(dict(d["missions"][0]))  # missione 1 duplicata
    d["tiers"][0]["missions"].append(99)  # missione citata ma inesistente
    d["missions"].append({"n": 21, "title": "x", "done": False, "skill": "y"})  # orfana
    errs = progress.consistency_errors(d)
    assert "la missione numero 1 compare 2 volte" in errs
    assert "il livello 1 cita la missione 99 che non esiste in \"missions\"" in errs
    assert "la missione 21 non appartiene a nessun livello" in errs


def test_track_steps_must_be_numbered_in_order(fixtures):
    d = load(fixtures, "progress-start.json")
    d["tracks"][0]["steps"][1]["n"] = 5
    errs = progress.consistency_errors(d)
    assert errs and errs[0].startswith("binario shield: i passi devono essere numerati 1..9")


def test_every_sheet_referenced_by_progress_exists():
    data = progress.load()
    assert progress.consistency_errors(data) == []


def test_missing_sheet_is_reported(fixtures):
    d = json.loads((fixtures / "progress-start.json").read_text(encoding="utf-8"))
    d["tracks"][0]["file"] = "NOPE.md"
    assert "il binario shield punta a missioni/NOPE.md, che non esiste" in progress.consistency_errors(d)


def test_mind_track_is_second_and_has_eight_steps():
    data = progress.load()
    ids = [t["id"] for t in data["tracks"]]
    assert ids == ["shield", "mind", "pi", "voice", "hire"]
    mind = data["tracks"][1]
    assert mind["file"] == "MIND.md" and len(mind["steps"]) == 8
    sheet = (progress.ROOT / "missioni" / "MIND.md").read_text(encoding="utf-8")
    for s in mind["steps"]:
        assert f"## M{s['n']}." in sheet
        assert f"**Riga CV:** {s['skill']}" in sheet
