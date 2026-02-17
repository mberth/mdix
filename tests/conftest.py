from __future__ import annotations

import shutil
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_VAULT = REPO_ROOT / "tests" / "fixtures" / "vault_great_discoveries"


@pytest.fixture
def copied_fixture_vault(tmp_path: Path) -> Path:
    target = tmp_path / "vault"
    shutil.copytree(FIXTURE_VAULT, target)
    return target
