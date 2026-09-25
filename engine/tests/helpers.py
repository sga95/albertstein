import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine" / "core"))

FIXTURES = ROOT / "tests" / "fixtures"


def load_progress(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def copy_repo(tmp_path: Path) -> Path:
    """Copia di site/ e data/ senza git: i controlli sui commit danno 0."""
    dst = tmp_path / "repo"
    dst.mkdir()
    shutil.copytree(ROOT / "site", dst / "site")
    shutil.copytree(ROOT / "data", dst / "data")
    return dst
