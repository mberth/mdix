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


def iter_markdown_files(root: Path, *, ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS) -> Iterable[Path]:
    """
    Deterministically yield all *.md files under root.

    Ordering is stable across runs on the same filesystem:
    - directory traversal is lexicographically sorted
    - filenames are lexicographically sorted
    """
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Deterministic traversal + allow pruning
        dirnames[:] = sorted(d for d in dirnames if d not in ignored_dirs)
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield Path(dirpath) / name
