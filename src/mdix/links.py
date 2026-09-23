"""
Wikilink scanning and resolution.

`mdix` reads `[[wikilinks]]` the way Obsidian does: a link is a note *name*, not a
path, and the vault decides what it points at. The lookup order is documented in
`docs/links.md`; this module is the implementation of that document.
"""

from __future__ import annotations

import os
import re
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .frontmatter_io import read_frontmatter
from .vault import DEFAULT_IGNORED_DIRS, iter_files, iter_markdown_files, path_in_scope

MARKDOWN_SUFFIX = ".md"

# Targets cannot span lines and cannot contain further brackets.
_WIKILINK_RE = re.compile(r"(!?)\[\[([^\[\]\n]*)\]\]")
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)$")


def normalize_key(text: str) -> str:
    """
    Fold a link target or filename into a comparison key.

    Obsidian matches note names case-insensitively and normalizes unicode, so
    `[[Ampere]]`, `[[ampere]]` and a file named `Ampère.md` do not all mean the
    same thing, but `[[Ampère]]` and `Ampère.md` do.
    """
    return unicodedata.normalize("NFC", " ".join(text.split())).casefold()


@dataclass(frozen=True)
class WikiLink:
    """One `[[wikilink]]` occurrence in one note."""

    line: int
    raw: str
    target: str
    subpath: str | None
    display: str | None
    embed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "line": self.line,
            "raw": self.raw,
            "target": self.target,
            "subpath": self.subpath,
            "display": self.display,
            "embed": self.embed,
        }


@dataclass(frozen=True)
class Resolution:
    """Where a link target points, and which rule got it there."""

    resolved: str | None
    via: str | None
    candidates: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"resolved": self.resolved, "via": self.via, "candidates": list(self.candidates)}


UNRESOLVED = Resolution(resolved=None, via=None, candidates=())


def split_target(link_text: str) -> tuple[str, str | None, str | None]:
    """
    Split the inside of `[[...]]` into (target, subpath, display).

    `Note#Heading|Label` -> ("Note", "#Heading", "Label").
    The display text is everything after the first `|`; the subpath is everything
    from the first `#` of the path part, kept with its `#` so `#^block-id` stays
    distinguishable from `#Heading`.
    """
    display: str | None = None
    if "|" in link_text:
        link_text, _, display_raw = link_text.partition("|")
        display = display_raw.strip()

    subpath: str | None = None
    if "#" in link_text:
        link_text, _, subpath_raw = link_text.partition("#")
        subpath = "#" + subpath_raw.strip()

    return link_text.strip(), subpath, display


def _mask_inline_code(line: str) -> str:
    """Blank out inline code spans so `` `[[not a link]]` `` is not scanned."""
    chars = list(line)
    index = 0
    length = len(line)
    while index < length:
        if line[index] != "`":
            index += 1
            continue

        open_end = index
        while open_end < length and line[open_end] == "`":
            open_end += 1
        run = open_end - index

        close_start = _find_closing_backticks(line, open_end, run)
        if close_start is None:
            index = open_end
            continue

        for position in range(open_end, close_start):
            chars[position] = " "
        index = close_start + run
    return "".join(chars)


def _find_closing_backticks(line: str, start: int, run: int) -> int | None:
    """Index of the next backtick run of exactly `run` characters, or None."""
    index = start
    length = len(line)
    while index < length:
        if line[index] != "`":
            index += 1
            continue
        end = index
        while end < length and line[end] == "`":
            end += 1
        if end - index == run:
            return index
        index = end
    return None


def iter_scannable_lines(text: str) -> Iterator[tuple[int, str]]:
    """
    Yield (line number, scannable text) for every line that can hold a link.

    Fenced code blocks and inline code are blanked out, because Obsidian does not
    turn them into links. Frontmatter is kept: Obsidian renders `[[...]]` in a
    property value as a link, and the graph counts it.
    """
    lines = text.splitlines()
    fence_char: str | None = None
    fence_len = 0
    in_frontmatter = bool(lines) and lines[0].strip() == "---"

    for number, line in enumerate(lines, start=1):
        if in_frontmatter:
            if number > 1 and line.strip() in {"---", "..."}:
                in_frontmatter = False
            else:
                yield number, _mask_inline_code(line)
            continue

        fence_match = _FENCE_RE.match(line.lstrip())
        if fence_char is None:
            if fence_match:
                fence_char = fence_match.group(1)[0]
                fence_len = len(fence_match.group(1))
                continue
            yield number, _mask_inline_code(line)
            continue

        # Inside a fence: only a matching closing fence matters.
        if fence_match and fence_match.group(1)[0] == fence_char and len(fence_match.group(1)) >= fence_len:
            if not fence_match.group(2).strip():
                fence_char = None
                fence_len = 0


def scan_links(text: str) -> list[WikiLink]:
    """Every wikilink in one note's text, in document order."""
    links: list[WikiLink] = []
    for number, line in iter_scannable_lines(text):
        for match in _WIKILINK_RE.finditer(line):
            embed = match.group(1) == "!"
            target, subpath, display = split_target(match.group(2))
            if not target and not subpath:
                continue
            links.append(
                WikiLink(
                    line=number,
                    raw=match.group(0),
                    target=target,
                    subpath=subpath,
                    display=display,
                    embed=embed,
                )
            )
    return links


_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_BLOCK_ID_RE = re.compile(r"(?:^|\s)\^([A-Za-z0-9-]+)\s*$")


@dataclass(frozen=True)
class NoteAnchors:
    """The headings and block ids of one note: what `#Heading` and `#^id` can point at."""

    headings: frozenset[str]
    block_ids: frozenset[str]

    def has(self, subpath: str) -> bool:
        """
        Whether `#Heading`, `#Parent#Child` or `#^block-id` exists in the note.

        Headings compare like note names (case-insensitive, whitespace collapsed).
        A nested subpath needs every heading in it to exist.
        """
        parts = [part for part in subpath.split("#") if part.strip()]
        if not parts:
            return True
        if len(parts) == 1 and parts[0].startswith("^"):
            return parts[0][1:].strip().casefold() in self.block_ids
        return all(normalize_key(part) in self.headings for part in parts)


def note_anchors(text: str) -> NoteAnchors:
    """ATX headings and `^block-id` markers of a note, outside frontmatter and code fences."""
    headings: set[str] = set()
    block_ids: set[str] = set()
    for _, line in _iter_body_lines(text):
        heading = _HEADING_RE.match(line)
        if heading:
            headings.add(normalize_key(heading.group(1)))
            continue
        block = _BLOCK_ID_RE.search(line)
        if block:
            block_ids.add(block.group(1).casefold())
    return NoteAnchors(headings=frozenset(headings), block_ids=frozenset(block_ids))


def _iter_body_lines(text: str) -> Iterator[tuple[int, str]]:
    """Lines of the note body: frontmatter and fenced code blocks left out."""
    lines = text.splitlines()
    in_frontmatter = bool(lines) and lines[0].strip() == "---"
    fence_char: str | None = None
    fence_len = 0
    for number, line in enumerate(lines, start=1):
        if in_frontmatter:
            if number > 1 and line.strip() in {"---", "..."}:
                in_frontmatter = False
            continue
        fence_match = _FENCE_RE.match(line.lstrip())
        if fence_char is None:
            if fence_match:
                fence_char = fence_match.group(1)[0]
                fence_len = len(fence_match.group(1))
                continue
            yield number, line
            continue
        if fence_match and fence_match.group(1)[0] == fence_char and len(fence_match.group(1)) >= fence_len:
            if not fence_match.group(2).strip():
                fence_char = None
                fence_len = 0


def _relpath_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _depth(rel_path: str) -> int:
    return rel_path.count("/")


def _folder(rel_path: str) -> str:
    head, _, _ = rel_path.rpartition("/")
    return head


def _common_prefix_len(left: str, right: str) -> int:
    left_parts = left.split("/") if left else []
    right_parts = right.split("/") if right else []
    count = 0
    for a, b in zip(left_parts, right_parts):
        if normalize_key(a) != normalize_key(b):
            break
        count += 1
    return count


class LinkIndex:
    """
    A resolved view of one vault: which names exist, and where.

    Build it once per command; every lookup is then in-memory.
    """

    def __init__(self, root: Path, *, ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS) -> None:
        self.root = root.resolve()
        self._paths: list[str] = []
        self._by_path: dict[str, str] = {}
        self._by_name: dict[str, list[str]] = {}
        self._by_alias: dict[str, list[str]] = {}
        self._anchors: dict[str, NoteAnchors] = {}

        for path in iter_files(self.root, ignored_dirs=ignored_dirs):
            rel = _relpath_posix(path, self.root)
            self._paths.append(rel)
            self._by_path.setdefault(normalize_key(rel), rel)
            name = rel.rpartition("/")[2]
            self._by_name.setdefault(normalize_key(name), []).append(rel)
            if name.endswith(MARKDOWN_SUFFIX):
                stem = name[: -len(MARKDOWN_SUFFIX)]
                self._by_name.setdefault(normalize_key(stem), []).append(rel)

        for path in iter_markdown_files(self.root, ignored_dirs=ignored_dirs):
            rel = _relpath_posix(path, self.root)
            for alias in _read_aliases(path):
                self._by_alias.setdefault(normalize_key(alias), []).append(rel)

    def subpath_found(self, rel: str | None, subpath: str | None) -> bool | None:
        """
        Whether a link's `#Heading` or `#^block-id` exists in the note it resolved to.

        None when there is nothing to check: no subpath, no note, or a destination
        that is not Markdown (an attachment has no headings).
        """
        if not subpath or rel is None or not rel.endswith(MARKDOWN_SUFFIX):
            return None
        anchors = self._anchors.get(rel)
        if anchors is None:
            try:
                text = (self.root / rel).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return None
            anchors = note_anchors(text)
            self._anchors[rel] = anchors
        return anchors.has(subpath)

    @property
    def paths(self) -> list[str]:
        return list(self._paths)

    def _lookup_path(self, candidate: str) -> str | None:
        candidate = candidate.strip("/")
        if not candidate:
            return None
        found = self._by_path.get(normalize_key(candidate))
        if found is not None:
            return found
        if not candidate.endswith(MARKDOWN_SUFFIX):
            return self._by_path.get(normalize_key(candidate + MARKDOWN_SUFFIX))
        return None

    def _by_suffix(self, target: str) -> list[str]:
        """Files whose path ends in the given partial path (Obsidian resolves those too)."""
        wanted = [normalize_key(part) for part in target.strip("/").split("/")]
        with_md = list(wanted)
        with_md[-1] = normalize_key(wanted[-1] + MARKDOWN_SUFFIX)

        matches: list[str] = []
        for rel in self._paths:
            parts = [normalize_key(part) for part in rel.split("/")]
            if len(parts) < len(wanted):
                continue
            tail = parts[-len(wanted) :]
            if tail == wanted or tail == with_md:
                matches.append(rel)
        return matches

    def resolve(self, target: str, *, source: str | None = None, use_aliases: bool = True) -> Resolution:
        """
        Resolve one link target. See `docs/links.md` for the rule order.

        `source` is the vault-relative path of the note the link is written in;
        it decides relative paths and, for ambiguous names, which note is closest.
        """
        target = unicodedata.normalize("NFC", target.strip())
        if not target:
            if source is None:
                return UNRESOLVED
            return Resolution(resolved=source, via="self", candidates=(source,))

        if source is not None and (target.startswith("./") or target.startswith("../")):
            joined = os.path.normpath(os.path.join(_folder(source), target)).replace(os.sep, "/")
            if joined.startswith(".."):
                return UNRESOLVED
            found = self._lookup_path(joined)
            return Resolution(found, "relative_path", (found,)) if found else UNRESOLVED

        found = self._lookup_path(target)
        if found is not None:
            return Resolution(found, "exact_path", (found,))

        if source is not None and "/" in target:
            joined = os.path.normpath(os.path.join(_folder(source), target)).replace(os.sep, "/")
            if not joined.startswith(".."):
                found = self._lookup_path(joined)
                if found is not None:
                    return Resolution(found, "relative_path", (found,))

        if "/" in target:
            candidates = self._by_suffix(target)
            if candidates:
                return self._pick(candidates, source=source, via="path_suffix")
        else:
            candidates = self._by_name.get(normalize_key(target), [])
            if candidates:
                return self._pick(candidates, source=source, via="basename")

        if use_aliases:
            candidates = self._by_alias.get(normalize_key(target), [])
            if candidates:
                return self._pick(candidates, source=source, via="alias")

        return UNRESOLVED

    def _pick(self, candidates: Iterable[str], *, source: str | None, via: str) -> Resolution:
        ordered = sorted(set(candidates), key=lambda rel: _closeness_key(rel, source))
        return Resolution(ordered[0], via, tuple(ordered))


def _closeness_key(rel_path: str, source: str | None) -> tuple[int, int, int, str]:
    """
    Sort key for ambiguous names: closest to the source note first.

    Obsidian links to "the file closest to the current one"; mdix reads that as
    same folder first, then the longest shared folder prefix, then the shallowest
    path, then lexicographic order so the answer never depends on the filesystem.
    """
    if source is None:
        return (1, 0, _depth(rel_path), rel_path)
    source_folder = _folder(source)
    same_folder = 0 if _folder(rel_path) == source_folder else 1
    return (same_folder, -_common_prefix_len(_folder(rel_path), source_folder), _depth(rel_path), rel_path)


def _read_aliases(path: Path) -> list[str]:
    """Frontmatter aliases of one note (`aliases`, or the legacy singular `alias`)."""
    try:
        fm_read = read_frontmatter(path)
    except (OSError, UnicodeDecodeError):
        return []
    meta = fm_read.frontmatter
    if not meta:
        return []

    aliases: list[str] = []
    for key in ("aliases", "alias"):
        value = meta.get(key)
        if isinstance(value, str):
            aliases.append(value)
        elif isinstance(value, list):
            aliases.extend(item for item in value if isinstance(item, str))
    return [alias.strip() for alias in aliases if alias.strip()]


def collect_links(
    root: Path,
    *,
    source: str | None = None,
    index: LinkIndex | None = None,
    use_aliases: bool = True,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    check_subpaths: bool = False,
) -> list[dict[str, Any]]:
    """
    Every wikilink in the vault (or in one note), resolved, in deterministic order.

    With `check_subpaths`, each record also carries `subpath_found`: whether the
    `#Heading` or `#^block-id` exists in the destination note (None when the link
    has no subpath or no Markdown destination).

    `include`/`exclude` scope which notes are *scanned*; every note in the vault
    stays a possible destination, so excluding the templates folder does not turn
    links into a template page unresolved.

    Order is path order first, then line order, then order within the line.
    """
    root = root.resolve()
    link_index = index if index is not None else LinkIndex(root)

    if source is not None:
        paths = [root / source]
    else:
        paths = list(iter_markdown_files(root))

    records: list[dict[str, Any]] = []
    for path in paths:
        rel = _relpath_posix(path, root)
        if not path_in_scope(rel, include, exclude):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for link in scan_links(text):
            resolution = link_index.resolve(link.target, source=rel, use_aliases=use_aliases)
            record = {"path": rel, **link.as_dict()}
            record["resolved"] = resolution.resolved
            record["via"] = resolution.via
            if check_subpaths:
                record["subpath_found"] = link_index.subpath_found(resolution.resolved, link.subpath)
            records.append(record)
    return records


def unresolved_targets(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    The frontier: one row per unresolved target, most-wanted first.

    Targets are grouped by their comparison key, so `[[Ion channel]]` and
    `[[ion channel]]` are one row; `target` is the spelling used by most notes
    (ties go to the alphabetically first), and `variants` lists every spelling.
    `count` counts notes, not occurrences.
    """
    groups: dict[str, dict[str, Any]] = {}
    for record in records:
        if record.get("resolved") is not None:
            continue
        target = str(record["target"])
        key = normalize_key(target)
        group = groups.setdefault(key, {"spellings": {}, "sources": set(), "occurrences": 0})
        group["spellings"][target] = group["spellings"].get(target, 0) + 1
        group["sources"].add(str(record["path"]))
        group["occurrences"] += 1

    rows: list[dict[str, Any]] = []
    for group in groups.values():
        spellings: dict[str, int] = group["spellings"]
        target = sorted(spellings.items(), key=lambda item: (-item[1], item[0]))[0][0]
        rows.append(
            {
                "target": target,
                "count": len(group["sources"]),
                "occurrences": group["occurrences"],
                "sources": sorted(group["sources"]),
                "variants": sorted(spellings),
            }
        )

    rows.sort(key=lambda row: (-row["count"], -row["occurrences"], normalize_key(row["target"])))
    return rows


def missing_subpaths(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sections owed by notes that exist: one row per `note#subpath` that is linked but missing.

    Needs records from `collect_links(..., check_subpaths=True)`. Rows are grouped by
    destination note and subpath, have the same fields as `unresolved_targets` plus
    `note` (the destination) and `subpath`, and sort the same way.
    """
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        if record.get("subpath_found") is not False:
            continue
        note = str(record["resolved"])
        subpath = str(record["subpath"])
        spelling = f"{record['target']}{subpath}"
        group = groups.setdefault(
            (note, normalize_key(subpath)),
            {"note": note, "subpath": subpath, "spellings": {}, "sources": set(), "occurrences": 0},
        )
        group["spellings"][spelling] = group["spellings"].get(spelling, 0) + 1
        group["sources"].add(str(record["path"]))
        group["occurrences"] += 1

    rows: list[dict[str, Any]] = []
    for group in groups.values():
        spellings: dict[str, int] = group["spellings"]
        target = sorted(spellings.items(), key=lambda item: (-item[1], item[0]))[0][0]
        rows.append(
            {
                "target": target,
                "note": group["note"],
                "subpath": group["subpath"],
                "count": len(group["sources"]),
                "occurrences": group["occurrences"],
                "sources": sorted(group["sources"]),
                "variants": sorted(spellings),
            }
        )

    rows.sort(key=lambda row: (-row["count"], -row["occurrences"], normalize_key(row["target"])))
    return rows
