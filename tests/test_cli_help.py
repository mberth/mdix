from __future__ import annotations

import subprocess


def test_mdix_help_includes_agent_focused_guidance() -> None:
    proc = subprocess.run(
        ["uv", "run", "mdix", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr

    help_text = proc.stdout
    assert "Quick usage:" in help_text
    assert "Global behavior:" in help_text
    assert "Command guide:" in help_text
    assert "Automation patterns:" in help_text
    assert "Exit codes to rely on in agents/CI:" in help_text
    assert "Help drill-down:" in help_text


def test_mdix_fm_help_includes_agent_focused_guidance() -> None:
    proc = subprocess.run(
        ["uv", "run", "mdix", "fm", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr

    help_text = proc.stdout
    assert "Quick usage:" in help_text
    assert "Recommended workflow:" in help_text
    assert "Normalization operations (repeatable where noted):" in help_text
    assert "Examples:" in help_text
    assert "Output behavior:" in help_text


def test_mdix_schema_help_includes_agent_focused_guidance() -> None:
    proc = subprocess.run(
        ["uv", "run", "mdix", "schema", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr

    help_text = proc.stdout
    assert "Quick usage:" in help_text
    assert "Contract file:" in help_text
    assert "Schema file format (`mdix.schema.yml`):" in help_text
    assert "Minimal example:" in help_text
    assert "Agent/CI workflow:" in help_text
    assert "Exit codes to rely on:" in help_text
    assert "Examples:" in help_text
