from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter
import yaml


@dataclass(frozen=True)
class FrontmatterRead:
    """
    Parsed frontmatter for a markdown file.

    - frontmatter is None when the file has no frontmatter block.
    - errors is a list of structured error objects (empty when ok).
    """

    frontmatter: dict[str, Any] | None
    errors: list[dict[str, str]]


def _has_frontmatter_block(text: str) -> bool:
    # Very small heuristic: frontmatter must be the first bytes in the file.
    return text.startswith("---\n") or text.startswith("---\r\n")


def read_frontmatter(path: Path) -> FrontmatterRead:
    """
    Read and parse optional YAML frontmatter from a markdown file.

    Malformed YAML does not raise; it is returned in errors.
    """
    text = path.read_text(encoding="utf-8")
    if not _has_frontmatter_block(text):
        return FrontmatterRead(frontmatter=None, errors=[])

    try:
        post = frontmatter.loads(text)
    except yaml.YAMLError as e:
        return FrontmatterRead(
            frontmatter=None,
            errors=[
                {
                    "type": "yaml_error",
                    "message": str(e),
                }
            ],
        )
    except TypeError as e:
        # python-frontmatter can raise TypeError if metadata contains a `content` key,
        # which conflicts with the Post constructor's `content` parameter.
        return FrontmatterRead(
            frontmatter=None,
            errors=[
                {
                    "type": "frontmatter_error",
                    "message": str(e),
                }
            ],
        )

    meta = dict(post.metadata or {})
    return FrontmatterRead(frontmatter=meta, errors=[])


def format_frontmatter_yaml(frontmatter_obj: dict[str, Any] | None) -> str:
    if frontmatter_obj is None:
        return ""
    return yaml.safe_dump(frontmatter_obj, sort_keys=True, allow_unicode=True).rstrip() + "\n"

