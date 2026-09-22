from __future__ import annotations

from collections.abc import Iterable
import os
from pathlib import Path, PurePosixPath


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


def path_in_scope(rel_path: str, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    """
    Apply the `--include`/`--exclude` glob filters to one vault-relative path.

    Include first, then exclude: a path has to match one include pattern (when any
    are given) and no exclude pattern.
    """
    path = PurePosixPath(rel_path)
    if include and not any(path.match(pattern) for pattern in include):
        return False
    if exclude and any(path.match(pattern) for pattern in exclude):
        return False
    return True
