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


def test_q_returns_structured_error_when_frontmatter_has_content_key(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    bad = vault / "bad.md"
    bad.write_text(
        "---\ncontent: oops\n---\n\nBody\n",
        encoding="utf-8",
    )

    proc = run_mdix(vault, "q")
    assert proc.returncode == 0, proc.stderr

    items = json.loads(proc.stdout)
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["path"] == "bad.md"
    assert items[0]["frontmatter"] is None
    assert items[0]["errors"]
    assert items[0]["errors"][0]["type"] == "frontmatter_error"


def test_fm_show_returns_structured_error_when_frontmatter_has_content_key(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    bad = vault / "bad.md"
    bad.write_text(
        "---\ncontent: oops\n---\n\nBody\n",
        encoding="utf-8",
    )

    proc = run_mdix(vault, "fm", "show", "bad.md")
    assert proc.returncode == 0, proc.stderr

    obj = json.loads(proc.stdout)
    assert obj["path"] == "bad.md"
    assert obj["frontmatter"] is None
    assert obj["errors"]
    assert obj["errors"][0]["type"] == "frontmatter_error"

