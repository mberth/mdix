from __future__ import annotations

import difflib
import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = REPO_ROOT / "tests" / "specs"
FENCE_RE = re.compile(r"^```([A-Za-z0-9_-]+)\s*$")


@dataclass(frozen=True)
class CommandCase:
    command: str
    expected_stdout: str
    expected_stderr: str
    source: str


def _normalize(text: str) -> str:
    return text.strip("\n")


def _diff(label: str, actual: str, expected: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            expected.splitlines(),
            actual.splitlines(),
            fromfile=f"expected_{label}",
            tofile=f"actual_{label}",
            lineterm="",
        )
    )


def _parse_fenced_blocks(spec_text: str, spec_path: Path) -> list[tuple[str, str, int]]:
    blocks: list[tuple[str, str, int]] = []
    lines = spec_text.splitlines()
    i = 0
    while i < len(lines):
        start = FENCE_RE.match(lines[i])
        if start is None:
            i += 1
            continue

        lang = start.group(1)
        block_start_line = i + 1
        i += 1
        block_lines: list[str] = []
        while i < len(lines) and lines[i] != "```":
            block_lines.append(lines[i])
            i += 1

        if i >= len(lines):
            raise AssertionError(f"Unclosed code fence in {spec_path}")

        blocks.append((lang, "\n".join(block_lines), block_start_line))
        i += 1

    return blocks


def _parse_spec_cases(spec_path: Path) -> list[CommandCase]:
    blocks = _parse_fenced_blocks(spec_path.read_text(encoding="utf-8"), spec_path)
    cases: list[CommandCase] = []
    i = 0
    while i < len(blocks):
        lang, command, start_line = blocks[i]
        if lang != "bash":
            i += 1
            continue

        expected_stdout: str | None = None
        expected_stderr = ""
        j = i + 1
        while j < len(blocks):
            next_lang, block_text, _ = blocks[j]
            if next_lang == "bash":
                break
            if next_lang == "expected":
                expected_stdout = block_text
            elif next_lang == "expected-err":
                expected_stderr = block_text
            j += 1

        if expected_stdout is None:
            raise AssertionError(
                f"Missing ```expected``` block for command in {spec_path}:{start_line}"
            )

        cases.append(
            CommandCase(
                command=command.strip(),
                expected_stdout=expected_stdout,
                expected_stderr=expected_stderr,
                source=f"{spec_path.name}:{start_line}",
            )
        )
        i = j

    if not cases:
        raise AssertionError(f"No bash command blocks found in {spec_path}")
    return cases


def _run_bash(command: str, *, vault_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["VAULT_ROOT"] = str(vault_root)
    return subprocess.run(
        shlex.split("bash -lc " + shlex.quote(command)),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


@pytest.mark.parametrize("spec_path", sorted(SPECS_DIR.glob("*.md")))
def test_markdown_regressions(spec_path: Path, copied_fixture_vault: Path) -> None:
    for case in _parse_spec_cases(spec_path):
        proc = _run_bash(case.command, vault_root=copied_fixture_vault)
        assert proc.returncode == 0, (
            f"{case.source} command failed with exit code {proc.returncode}\n"
            f"command: {case.command}\n"
            f"stderr:\n{proc.stderr}"
        )

        actual_stdout = _normalize(proc.stdout)
        expected_stdout = _normalize(case.expected_stdout)
        assert actual_stdout == expected_stdout, (
            f"{case.source} stdout mismatch for command: {case.command}\n"
            f"{_diff('stdout', actual_stdout, expected_stdout)}"
        )

        actual_stderr = _normalize(proc.stderr)
        expected_stderr = _normalize(case.expected_stderr)
        assert actual_stderr == expected_stderr, (
            f"{case.source} stderr mismatch for command: {case.command}\n"
            f"{_diff('stderr', actual_stderr, expected_stderr)}"
        )
