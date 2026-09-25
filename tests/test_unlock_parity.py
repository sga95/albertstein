"""La regola di sblocco in Python deve dare lo stesso risultato di site/app.js."""

import json
import shutil
import subprocess

import pytest

from lib import progress

NODE = shutil.which("node")
FIXTURE_NAMES = ["progress-start.json", "progress-midway.json", "progress-out-of-order.json"]


def js_status(data: dict) -> dict:
    script = (
        "const app = require(process.argv[1]);"
        "let raw = '';"
        "process.stdin.on('data', c => raw += c);"
        "process.stdin.on('end', () => process.stdout.write(JSON.stringify(app.unlockStatus(JSON.parse(raw)))));"
    )
    run = subprocess.run(
        [NODE, "-e", script, str(progress.SITE / "app.js")],
        input=json.dumps(data), capture_output=True, text=True, check=True,
    )
    return json.loads(run.stdout)


@pytest.mark.skipif(NODE is None, reason="node non installato: il confronto con app.js gira in CI")
@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_python_matches_app_js(fixtures, name):
    data = json.loads((fixtures / name).read_text(encoding="utf-8"))
    assert progress.unlock_status(data) == js_status(data)


@pytest.mark.skipif(NODE is None, reason="node non installato")
def test_python_matches_app_js_on_every_single_step(fixtures):
    """Accende un passo alla volta, anche fuori ordine, e pretende lo stesso stato."""
    base = json.loads((fixtures / "progress-start.json").read_text(encoding="utf-8"))
    variants = []
    for i in range(len(base["missions"])):
        d = json.loads(json.dumps(base))
        d["missions"][i]["done"] = True
        variants.append(d)
    for i in range(len(base["tiers"])):
        d = json.loads(json.dumps(base))
        d["tiers"][i]["boss"]["done"] = True
        variants.append(d)
    for data in variants:
        assert progress.unlock_status(data) == js_status(data)
