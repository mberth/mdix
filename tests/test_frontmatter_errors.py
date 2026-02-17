from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run_mdix(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "mdix", "--root", str(root), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_q_returns_structured_error_when_frontmatter_has_content_key(copied_fixture_vault: Path) -> None:
    proc = run_mdix(copied_fixture_vault, "q")
    assert proc.returncode == 0, proc.stderr

    items = json.loads(proc.stdout)
    assert isinstance(items, list)
    edge_case = next(i for i in items if i["path"] == "discoveries/problematic-content-key.md")
    assert edge_case["frontmatter"] is None
    assert edge_case["errors"]
    assert edge_case["errors"][0]["type"] == "frontmatter_error"


def test_fm_show_returns_structured_error_when_frontmatter_has_content_key(copied_fixture_vault: Path) -> None:
    proc = run_mdix(copied_fixture_vault, "fm", "show", "discoveries/problematic-content-key.md")
    assert proc.returncode == 0, proc.stderr

    obj = json.loads(proc.stdout)
    assert obj["path"] == "discoveries/problematic-content-key.md"
    assert obj["frontmatter"] is None
    assert obj["errors"]
    assert obj["errors"][0]["type"] == "frontmatter_error"

