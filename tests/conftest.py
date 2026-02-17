from __future__ import annotations

import shutil
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_VAULT = REPO_ROOT / "tests" / "fixtures" / "vault_great_discoveries"
SCHEMA_DRIFT_FIXTURE_VAULT = REPO_ROOT / "tests" / "fixtures" / "vault_schema_drift"


@pytest.fixture
def copied_fixture_vault(tmp_path: Path) -> Path:
    target = tmp_path / "vault"
    shutil.copytree(FIXTURE_VAULT, target)
    return target


@pytest.fixture
def copied_schema_drift_vault(tmp_path: Path) -> Path:
    target = tmp_path / "vault-schema-drift"
    shutil.copytree(SCHEMA_DRIFT_FIXTURE_VAULT, target)
    return target
