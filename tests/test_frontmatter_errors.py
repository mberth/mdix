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


def test_q_strict_keeps_json_on_stdout_and_fails_with_stderr_summary(copied_fixture_vault: Path) -> None:
    proc = run_mdix(copied_fixture_vault, "q", "--fail-on-errors")
    assert proc.returncode != 0

    items = json.loads(proc.stdout)
    assert isinstance(items, list)
    errored_paths = [i["path"] for i in items if i["errors"]]
    assert errored_paths == [
        "discoveries/problematic-content-key.md",
        "media/broken-frontmatter.md",
    ]

    assert "q strict mode: found parse errors in 2 note(s)" in proc.stderr
    assert "- discoveries/problematic-content-key.md: frontmatter_error" in proc.stderr
    assert "- media/broken-frontmatter.md: yaml_error" in proc.stderr


def test_q_strict_on_clean_vault_exits_zero_and_writes_no_stderr(copied_fixture_vault: Path) -> None:
    (copied_fixture_vault / "discoveries" / "problematic-content-key.md").write_text(
        """---
title: "Content Key Fixed"
type: discovery
tags: ["physics"]
---
This frontmatter is valid.
""",
        encoding="utf-8",
    )
    (copied_fixture_vault / "media" / "broken-frontmatter.md").write_text(
        """---
title: "Broken Frontmatter Fixed"
type: media
tags: ["paper"]
---
Now this file parses correctly.
""",
        encoding="utf-8",
    )

    proc = run_mdix(copied_fixture_vault, "q", "--strict")
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr.strip() == ""

    items = json.loads(proc.stdout)
    assert all(not item["errors"] for item in items)


def test_fm_show_returns_structured_error_when_frontmatter_has_content_key(copied_fixture_vault: Path) -> None:
    proc = run_mdix(copied_fixture_vault, "fm", "show", "discoveries/problematic-content-key.md")
    assert proc.returncode == 0, proc.stderr

    obj = json.loads(proc.stdout)
    assert obj["path"] == "discoveries/problematic-content-key.md"
    assert obj["frontmatter"] is None
    assert obj["errors"]
    assert obj["errors"][0]["type"] == "frontmatter_error"

