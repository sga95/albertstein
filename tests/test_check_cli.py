import json
import subprocess
import sys

from lib import progress

CHECK = progress.ROOT / "tools" / "check.py"


def run(*args):
    return subprocess.run([sys.executable, str(CHECK), *args], capture_output=True, text=True)


def test_check_passes_on_the_real_site():
    r = run("--no-secrets")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Tutto ok" in r.stdout


def test_json_output():
    r = run("--no-secrets", "--json")
    data = json.loads(r.stdout)
    assert data["errors"] == []
    assert "lab_notes" in data


def test_lab_markdown_output():
    r = run("--lab-md")
    assert r.returncode == 0
    assert r.stdout.strip()
