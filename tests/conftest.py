import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pytest  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def site_copy(tmp_path: Path) -> Path:
    """Copia di site/ in una cartella temporanea, per test che scrivono o rompono file."""
    import shutil

    dst = tmp_path / "site"
    shutil.copytree(ROOT / "site", dst)
    return dst
