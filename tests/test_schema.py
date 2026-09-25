import json

from lib import progress
from lib.schema import validate


def load(fixtures, name):
    return json.loads((fixtures / name).read_text(encoding="utf-8"))


def test_real_progress_is_valid():
    assert validate(progress.load(), progress.load_schema()) == []


def test_fixtures_are_valid(fixtures):
    schema = progress.load_schema()
    for name in ("progress-start.json", "progress-midway.json", "progress-out-of-order.json"):
        assert validate(load(fixtures, name), schema) == [], name


def test_missing_required_key(fixtures):
    d = load(fixtures, "progress-start.json")
    del d["missions"][0]["done"]
    errs = [str(e) for e in validate(d, progress.load_schema())]
    assert errs == ['missions[0]: manca la chiave obbligatoria "done"']


def test_done_must_be_boolean(fixtures):
    d = load(fixtures, "progress-start.json")
    d["missions"][2]["done"] = "true"
    errs = [str(e) for e in validate(d, progress.load_schema())]
    assert errs == ["missions[2].done: deve essere boolean, trovato string"]


def test_unknown_key_is_reported_with_allowed_ones(fixtures):
    d = load(fixtures, "progress-start.json")
    d["missions"][0]["dne"] = True
    errs = [str(e) for e in validate(d, progress.load_schema())]
    assert len(errs) == 1
    assert errs[0].startswith('missions[0].dne: chiave sconosciuta "dne" (ammesse: done, file, n, skill, title)')


def test_incident_date_pattern(fixtures):
    d = load(fixtures, "progress-midway.json")
    d["incidents"][0]["date"] = "2 marzo"
    errs = [str(e) for e in validate(d, progress.load_schema())]
    assert errs and errs[0].startswith("incidents[0].date:")


def test_integer_is_not_boolean_and_vice_versa():
    schema = {"type": "object", "properties": {"n": {"type": "integer"}, "d": {"type": "boolean"}}}
    assert validate({"n": True}, schema)
    assert validate({"d": 1}, schema)
    assert validate({"n": 1, "d": True}, schema) == []


def test_unique_items_and_min_items():
    schema = {"type": "array", "minItems": 2, "uniqueItems": True, "items": {"type": "integer"}}
    assert [str(e) for e in validate([1], schema)] == ["(radice): servono almeno 2 elementi, trovati 1"]
    assert [str(e) for e in validate([1, 1], schema)] == ["[1]: valore duplicato 1"]
