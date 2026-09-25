import pytest

from engine.tests.helpers import copy_repo


@pytest.fixture
def repo_copy(tmp_path):
    return copy_repo(tmp_path)
