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


def test_fm_normalize_dry_run_previews_batch_cleanup_operations(copied_fixture_vault: Path) -> None:
    target = copied_fixture_vault / "people" / "legacy-null.md"
    target.write_text(
        """---
nickname: "Legacy Alias"
status: active
title: null
obsolete: null
---
Legacy note that needs normalized frontmatter.
""",
        encoding="utf-8",
    )

    proc = run_mdix(
        copied_fixture_vault,
        "fm",
        "normalize",
        "--dry-run",
        "--include",
        "people/legacy-null.md",
        "--map-value",
        "status",
        "active",
        "identified",
        "--set-default",
        "type",
        "person",
        "--derive",
        "title",
        "nickname",
        "--derive-from-filename",
        "display_title",
        "--remove-null-keys",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["summary"]["files_scanned"] == 1
    assert payload["summary"]["files_changed"] == 1
    assert payload["summary"]["operations"] == 5
    assert payload["changes"] == [
        {
            "changes": [
                {"field": "status", "from": "active", "op": "value_map", "to": "identified"},
                {"field": "type", "op": "set_default", "value": "person"},
                {"field": "title", "from": "nickname", "op": "derive", "source": "field", "value": "Legacy Alias"},
                {"field": "display_title", "op": "derive_from_filename", "value": "Legacy Null"},
                {"fields": ["obsolete"], "op": "remove_null_keys"},
            ],
            "path": "people/legacy-null.md",
            "status": "preview",
        }
    ]

    unchanged = target.read_text(encoding="utf-8")
    assert "status: active" in unchanged
    assert "title: null" in unchanged
