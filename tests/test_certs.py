import json
import shutil
import subprocess
import sys

import pytest
import yaml

from lib import progress

NODE = shutil.which("node")
CERTS = yaml.safe_load((progress.ROOT / "data/certs.yaml").read_text(encoding="utf-8"))["certs"]


def refs(data):
    out = {f"mission:{m['n']}" for m in data["missions"]}
    out |= {f"boss:{t['id']}" for t in data["tiers"]}
    out |= {f"track:{t['id']}:{s['n']}" for t in data["tracks"] for s in t["steps"]}
    return out


def test_every_prereq_exists_in_progress():
    known = refs(progress.load())
    for c in CERTS:
        assert set(c["prereq_steps"]) <= known, c["id"]
        assert c["study_free"] and c["exam_url"].startswith("https://")


def test_certs_json_matches_catalogue():
    out = json.loads((progress.SITE / "data/certs.json").read_text(encoding="utf-8"))
    assert [c["id"] for c in out["certs"]] == [c["id"] for c in CERTS]
    assert set(out["status"].values()) <= {"requested", "granted", "passed"}


def js_cert_status(cert, status, data):
    script = ("const app = require(process.argv[1]); let raw=''; process.stdin.on('data', c => raw += c);"
              "process.stdin.on('end', () => { const i = JSON.parse(raw); process.stdout.write(JSON.stringify(app.certStatus(i.cert, i.status, i.data))); });")
    run = subprocess.run([NODE, "-e", script, str(progress.SITE / "app.js")],
                         input=json.dumps({"cert": cert, "status": status, "data": data}), capture_output=True, text=True, check=True)
    return json.loads(run.stdout)


@pytest.mark.skipif(NODE is None, reason="node non installato")
def test_cert_status_in_app_js(fixtures):
    start = json.loads((fixtures / "progress-start.json").read_text(encoding="utf-8"))
    mid = json.loads((fixtures / "progress-midway.json").read_text(encoding="utf-8"))
    aws = next(c for c in CERTS if c["id"] == "aws-ccp")   # prereq: mission 12
    udemy = next(c for c in CERTS if c["id"] == "udemy-course")  # prereq: mission 3
    assert js_cert_status(aws, {}, start) == {"state": "locked", "missing": ["Mission 12: Backup and restore drill"]}
    assert js_cert_status(udemy, {}, mid)["state"] == "ready"
    assert js_cert_status(udemy, {"udemy-course": "granted"}, mid)["state"] == "granted"
    assert js_cert_status(udemy, {"udemy-course": "passed"}, start)["state"] == "passed"
    thm = next(c for c in CERTS if c["id"] == "thm-premium")  # prereq: shield 9
    assert js_cert_status(thm, {}, mid)["state"] == "ready"
    assert js_cert_status(thm, {}, start)["missing"] == ["Shield 9: Your public footprint"]


def test_cert_status_tool_parses_the_form(tmp_path, monkeypatch):
    sys.path.insert(0, str(progress.ROOT / "tools"))
    import cert_status

    status = tmp_path / "certs-status.json"
    monkeypatch.setattr(cert_status, "STATUS", status)
    body = "### Tipo di richiesta\n\ncertificazione\n\n### Cosa chiedi\n\nccna\n\n### Perché adesso\n\nho chiuso la 13\n"
    (tmp_path / "issue.md").write_text(body, encoding="utf-8")
    assert cert_status.main(["--body", str(tmp_path / "issue.md"), "--state", "requested"]) == 0
    assert json.loads(status.read_text())["status"] == {"ccna": "requested"}
    cert_status.main(["--id", "ccna", "--state", "granted"])
    assert json.loads(status.read_text())["status"] == {"ccna": "granted"}
    # una richiesta di loot non tocca le certificazioni
    (tmp_path / "loot.md").write_text("### Tipo di richiesta\n\nloot\n\n### Cosa chiedi\n\nboss 1\n", encoding="utf-8")
    assert cert_status.main(["--body", str(tmp_path / "loot.md"), "--state", "requested"]) == 0
    assert json.loads(status.read_text())["status"] == {"ccna": "granted"}
    with pytest.raises(SystemExit):
        cert_status.main(["--id", "nope", "--state", "granted"])
