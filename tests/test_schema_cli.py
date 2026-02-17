from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_mdix(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "mdix", "--root", str(root), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_schema_inventory_reports_field_counts(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(copied_schema_drift_vault, "schema", "inventory")
    assert proc.returncode == 0, proc.stderr

    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    assert summary["files_scanned"] == 4
    assert summary["files_with_frontmatter"] == 4
    assert summary["parse_errors"] == 0
    assert summary["distinct_fields"] >= 9

    counts = {item["field"]: item["count"] for item in payload["fields"]}
    assert counts["title"] == 4
    assert counts["rolle"] == 1
    assert counts["kontakt_email"] == 1
    assert counts["kontakt.email"] == 1
    assert counts["legacy_note"] == 1


def test_schema_validate_strict_fails_with_deterministic_violations(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(copied_schema_drift_vault, "schema", "validate")
    assert proc.returncode == 2

    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    assert summary["files_scanned"] == 4
    assert summary["files_with_frontmatter"] == 4
    assert summary["files_validated"] == 4
    assert summary["violations"] == 2
    assert summary["files_with_violations"] == 2


def test_schema_migrate_dry_run_previews_without_applying(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(copied_schema_drift_vault, "schema", "migrate", "--dry-run")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    assert summary["dry_run"] is True
    assert summary["files_changed"] == 3
    assert summary["operations"] == 5

    updated = next(item for item in payload["changes"] if item["path"] == "people/alice-example.md")
    assert updated["status"] == "preview"
    assert updated["changes"] == [
        {
            "from": "rolle",
            "op": "rename",
            "to": "position",
            "value": "Research Lead",
        },
        {
            "from": "kontakt_email",
            "op": "rename",
            "to": "kontakt.email",
            "value": "alice@example.com",
        },
    ]

    alice_text = (copied_schema_drift_vault / "people" / "alice-example.md").read_text(encoding="utf-8")
    assert "rolle:" in alice_text
    assert "kontakt_email:" in alice_text
    drifted = next(item for item in payload["changes"] if item["path"] == "discoveries/drifted-status.md")
    assert drifted["changes"] == [
        {
            "field": "status",
            "from": "active",
            "op": "value_map",
            "to": "identified",
        },
        {"field": "legacy_note", "op": "unset_if_null"},
    ]
    missing_type = next(item for item in payload["changes"] if item["path"] == "people/missing-type.md")
    assert missing_type["changes"] == [
        {
            "field": "type",
            "op": "set_default",
            "value": "person",
        }
    ]


def test_schema_migrate_apply_writes_changes_without_data_loss(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(copied_schema_drift_vault, "schema", "migrate")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    assert summary["dry_run"] is False
    assert summary["files_changed"] == 3
    assert summary["operations"] == 5

    alice_text = (copied_schema_drift_vault / "people" / "alice-example.md").read_text(encoding="utf-8")
    assert "rolle:" not in alice_text
    assert "kontakt_email:" not in alice_text
    assert "position: Research Lead" in alice_text
    assert "kontakt:" in alice_text
    assert "email: alice@example.com" in alice_text
    drifted_text = (copied_schema_drift_vault / "discoveries" / "drifted-status.md").read_text(encoding="utf-8")
    assert "status: identified" in drifted_text
    assert "legacy_note:" not in drifted_text
    missing_type_text = (copied_schema_drift_vault / "people" / "missing-type.md").read_text(encoding="utf-8")
    assert "type: person" in missing_type_text

    validate_proc = run_mdix(copied_schema_drift_vault, "schema", "validate", "--no-strict")
    assert validate_proc.returncode == 0, validate_proc.stderr
    validate_payload = json.loads(validate_proc.stdout)
    assert validate_payload["summary"]["violations"] == 0


def test_schema_validate_ignores_notes_without_frontmatter(copied_schema_drift_vault: Path) -> None:
    (copied_schema_drift_vault / "README.md").write_text("# fixture\n", encoding="utf-8")
    (copied_schema_drift_vault / "AGENTS.md").write_text("guidance\n", encoding="utf-8")

    proc = run_mdix(copied_schema_drift_vault, "schema", "validate", "--no-strict")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    assert summary["files_scanned"] == 6
    assert summary["files_with_frontmatter"] == 4
    assert summary["files_validated"] == 4
    assert summary["violations"] == 2
    assert all(
        item["path"] not in {"README.md", "AGENTS.md"} or item["code"] != "SCHEMA_REQUIRED_MISSING"
        for item in payload["violations"]
    )


def test_schema_validate_include_exclude_filters_paths_deterministically(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(
        copied_schema_drift_vault,
        "schema",
        "validate",
        "--no-strict",
        "--include",
        "people/**",
        "--exclude",
        "people/alice-example.md",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)

    assert payload["summary"]["files_scanned"] == 2
    assert payload["summary"]["files_validated"] == 2
    assert payload["summary"]["violations"] == 1
    assert payload["violations"] == [
        {
            "actual": None,
            "code": "SCHEMA_REQUIRED_MISSING",
            "expected": {"required": True},
            "field": "type",
            "message": "Missing required field `type`.",
            "path": "people/missing-type.md",
        }
    ]


def test_schema_migrate_include_exclude_filters_paths_deterministically(copied_schema_drift_vault: Path) -> None:
    proc = run_mdix(
        copied_schema_drift_vault,
        "schema",
        "migrate",
        "--dry-run",
        "--include",
        "people/**",
        "--exclude",
        "people/alice-example.md",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["summary"]["files_scanned"] == 2
    assert payload["summary"]["files_changed"] == 1
    assert payload["summary"]["operations"] == 1
    assert payload["changes"] == [
        {
            "changes": [{"field": "type", "op": "set_default", "value": "person"}],
            "path": "people/missing-type.md",
            "status": "preview",
        }
    ]


def test_schema_commands_report_effective_schema_source_path(copied_schema_drift_vault: Path) -> None:
    schema_path = (REPO_ROOT / "tests" / "fixtures" / "vault_schema_drift" / "mdix.schema.yml").resolve()

    validate_proc = run_mdix(
        copied_schema_drift_vault,
        "schema",
        "validate",
        "--no-strict",
        "--schema-path",
        str(schema_path),
    )
    assert validate_proc.returncode == 0, validate_proc.stderr
    validate_payload = json.loads(validate_proc.stdout)
    assert validate_payload["schema"] == schema_path.as_posix()

    migrate_proc = run_mdix(
        copied_schema_drift_vault,
        "schema",
        "migrate",
        "--dry-run",
        "--schema-path",
        str(schema_path),
    )
    assert migrate_proc.returncode == 0, migrate_proc.stderr
    migrate_payload = json.loads(migrate_proc.stdout)
    assert migrate_payload["schema"] == schema_path.as_posix()
