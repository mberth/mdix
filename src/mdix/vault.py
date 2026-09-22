from __future__ import annotations

from collections.abc import Iterable
import os
from pathlib import Path


DEFAULT_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
    }
)


def iter_files(root: Path, *, ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS) -> Iterable[Path]:
    """
    Deterministically yield all files under root, whatever their extension.

    Link resolution needs this: a wikilink can point at an attachment
    (`[[diagram.png]]`), not only at a note.

    Ordering is stable across runs on the same filesystem:
    - directory traversal is lexicographically sorted
    - filenames are lexicographically sorted
    """
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Deterministic traversal + allow pruning
        dirnames[:] = sorted(d for d in dirnames if d not in ignored_dirs)
        for name in sorted(filenames):
            yield Path(dirpath) / name


def iter_markdown_files(root: Path, *, ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS) -> Iterable[Path]:
    """
    Deterministically yield all *.md files under root.

    Ordering is stable across runs on the same filesystem:
    - directory traversal is lexicographically sorted
    - filenames are lexicographically sorted
    """
    for path in iter_files(root, ignored_dirs=ignored_dirs):
        if path.name.endswith(".md"):
            yield path
