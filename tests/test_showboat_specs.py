from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SHOWBOAT_SPECS_DIR = REPO_ROOT / "tests" / "specs" / "showboat"


def _discover_showboat_specs() -> list[Path]:
    specs: list[Path] = []
    for path in sorted(SHOWBOAT_SPECS_DIR.glob("*.md")):
        if "<!-- showboat-id:" in path.read_text(encoding="utf-8"):
            specs.append(path)
    return specs


SHOWBOAT_SPECS = _discover_showboat_specs()


def test_showboat_specs_exist() -> None:
    assert SHOWBOAT_SPECS, f"No showboat specs found in {SHOWBOAT_SPECS_DIR}"


@pytest.mark.parametrize("spec_path", SHOWBOAT_SPECS)
def test_showboat_spec_verifies(spec_path: Path) -> None:
    proc = subprocess.run(
        ["showboat", "verify", str(spec_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"showboat verify failed for {spec_path.relative_to(REPO_ROOT)}\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )
