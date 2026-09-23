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


def resolve(root: Path, target: str, *args: str) -> subprocess.CompletedProcess[str]:
    return run_mdix(root, "links", "resolve", target, *args)


def test_resolve_reports_destination_and_matching_rule(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[ada-lovelace]]")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload == {
        "candidates": ["people/ada-lovelace.md"],
        "display": None,
        "from": None,
        "resolved": "people/ada-lovelace.md",
        "subpath": None,
        "target": "ada-lovelace",
        "via": "basename",
    }


def test_resolve_accepts_bare_target_subpath_and_display_text(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "analytical-engine#Notes|the engine")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["target"] == "analytical-engine"
    assert payload["subpath"] == "#Notes"
    assert payload["display"] == "the engine"
    assert payload["resolved"] == "projects/analytical-engine.md"


def test_resolve_prefers_the_note_in_the_source_folder(copied_links_vault: Path) -> None:
    from_people = resolve(copied_links_vault, "[[overview]]", "--from", "people/ada-lovelace.md")
    from_projects = resolve(copied_links_vault, "[[overview]]", "--from", "projects/analytical-engine.md")

    assert json.loads(from_people.stdout)["resolved"] == "people/overview.md"
    assert json.loads(from_projects.stdout)["resolved"] == "projects/overview.md"
    # Ambiguity stays visible: both candidates are reported, best match first.
    assert json.loads(from_people.stdout)["candidates"] == ["people/overview.md", "projects/overview.md"]


def test_resolve_follows_relative_paths_from_the_source_note(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[../projects/analytical-engine]]", "--from", "people/ada-lovelace.md")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["resolved"] == "projects/analytical-engine.md"
    assert payload["via"] == "relative_path"


def test_resolve_matches_a_partial_path_anywhere_in_the_vault(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[hardware/mill]]", "--from", "index.md")
    assert json.loads(proc.stdout)["via"] == "path_suffix"
    assert json.loads(proc.stdout)["resolved"] == "projects/hardware/mill.md"


def test_resolve_falls_back_to_frontmatter_aliases(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[Countess of Lovelace]]")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["resolved"] == "people/ada-lovelace.md"
    assert payload["via"] == "alias"

    without_aliases = resolve(copied_links_vault, "[[Countess of Lovelace]]", "--no-aliases")
    assert without_aliases.returncode == 1
    assert json.loads(without_aliases.stdout)["resolved"] is None


def test_resolve_matches_names_case_insensitively(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[ADA-LOVELACE]]")
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["resolved"] == "people/ada-lovelace.md"


def test_resolve_points_a_bare_subpath_at_the_source_note(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[#Notes]]", "--from", "projects/analytical-engine.md")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["resolved"] == "projects/analytical-engine.md"
    assert payload["via"] == "self"


def test_resolve_exits_one_when_no_note_matches(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[difference-engine]]")
    assert proc.returncode == 1
    assert json.loads(proc.stdout) == {
        "candidates": [],
        "display": None,
        "from": None,
        "resolved": None,
        "subpath": None,
        "target": "difference-engine",
        "via": None,
    }


def test_resolve_rejects_a_source_note_that_does_not_exist(copied_links_vault: Path) -> None:
    proc = resolve(copied_links_vault, "[[ada-lovelace]]", "--from", "people/nobody.md")
    assert proc.returncode != 0
    assert "File not found" in proc.stderr


def test_ls_reports_every_occurrence_with_stable_fields(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--from", "people/ada-lovelace.md")
    assert proc.returncode == 0, proc.stderr
    records = json.loads(proc.stdout)

    assert [record["target"] for record in records] == [
        "analytical-engine",
        "overview",
        "../projects/analytical-engine",
        "Punch Card",
        "diagram.png",
    ]
    engine = records[0]
    assert engine == {
        "display": "engine",
        "embed": False,
        "line": 9,
        "path": "people/ada-lovelace.md",
        "raw": "[[analytical-engine#Notes|engine]]",
        "resolved": "projects/analytical-engine.md",
        "subpath": "#Notes",
        "target": "analytical-engine",
        "via": "basename",
    }
    assert records[-1]["embed"] is True
    assert records[-1]["resolved"] == "attachments/diagram.png"


def test_ls_skips_fenced_code_blocks_and_inline_code(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--from", "people/ada-lovelace.md")
    targets = [record["target"] for record in json.loads(proc.stdout)]
    assert "difference-engine" not in targets


def test_ls_reads_links_in_frontmatter_values(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--from", "index.md")
    records = json.loads(proc.stdout)
    assert records[0] == {
        "display": None,
        "embed": False,
        "line": 4,
        "path": "index.md",
        "raw": "[[people/ada-lovelace]]",
        "resolved": "people/ada-lovelace.md",
        "subpath": None,
        "target": "people/ada-lovelace",
        "via": "exact_path",
    }


def test_ls_unresolved_only_filters_to_missing_notes(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--unresolved-only")
    records = json.loads(proc.stdout)
    assert all(record["resolved"] is None for record in records)
    assert sorted({record["target"] for record in records}) == ["Punch Card", "difference-engine", "punch card"]


def test_unresolved_ranks_targets_by_how_many_notes_want_them(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "unresolved")
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == [
        {
            "count": 2,
            "occurrences": 3,
            "sources": ["people/ada-lovelace.md", "projects/analytical-engine.md"],
            "target": "punch card",
            "variants": ["Punch Card", "punch card"],
        },
        {
            "count": 1,
            "occurrences": 1,
            "sources": ["index.md"],
            "target": "difference-engine",
            "variants": ["difference-engine"],
        },
    ]


def test_unresolved_shrinks_when_the_missing_note_is_written(copied_links_vault: Path) -> None:
    (copied_links_vault / "projects" / "punch-card.md").write_text(
        '---\ntitle: "Punch card"\naliases:\n  - punch card\n---\n\nA card with holes in it.\n',
        encoding="utf-8",
    )
    proc = run_mdix(copied_links_vault, "links", "unresolved")
    rows = json.loads(proc.stdout)
    assert [row["target"] for row in rows] == ["difference-engine"]


def test_unresolved_human_output_lists_the_notes_asking_for_the_page(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "unresolved", "--human")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == (
        "2  punch card\n"
        "   - people/ada-lovelace.md\n"
        "   - projects/analytical-engine.md\n"
        "1  difference-engine\n"
        "   - index.md\n"
    )


def test_ls_include_scopes_the_scan_to_matching_notes(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--include", "people/**")
    assert proc.returncode == 0, proc.stderr
    assert sorted({record["path"] for record in json.loads(proc.stdout)}) == [
        "people/ada-lovelace.md",
        "people/overview.md",
    ]


def test_ls_exclude_drops_matching_notes_from_the_scan(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--exclude", "people/**")
    paths = {record["path"] for record in json.loads(proc.stdout)}
    assert "people/ada-lovelace.md" not in paths
    assert "index.md" in paths


def test_an_excluded_note_is_still_a_link_destination(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "ls", "--exclude", "people/**")
    records = json.loads(proc.stdout)
    alias_link = [record for record in records if record["target"] == "Ada"]
    assert [record["resolved"] for record in alias_link] == ["people/ada-lovelace.md"]


def test_unresolved_respects_the_scan_scope(copied_links_vault: Path) -> None:
    proc = run_mdix(copied_links_vault, "links", "unresolved", "--exclude", "people/**")
    assert json.loads(proc.stdout) == [
        {
            "count": 1,
            "occurrences": 2,
            "sources": ["projects/analytical-engine.md"],
            "target": "punch card",
            "variants": ["punch card"],
        },
        {
            "count": 1,
            "occurrences": 1,
            "sources": ["index.md"],
            "target": "difference-engine",
            "variants": ["difference-engine"],
        },
    ]


def _subpath_vault(tmp_path: Path) -> Path:
    root = tmp_path / "vault"
    (root / "complexes").mkdir(parents=True)
    (root / "genes").mkdir()
    (root / "complexes" / "Complex I.md").write_text(
        "---\n# not a heading: frontmatter comment\ntitle: Complex I\n---\n\n"
        "# Complex I\n\n## Structure\n\n### Q module ###\n\nA pumped proton. ^pump\n\n"
        "```text\n## N module\n```\n",
        encoding="utf-8",
    )
    (root / "genes" / "NDUFS4.md").write_text(
        "At the [[Complex I#N module|N module]] and the [[Complex I#Q module|Q module]].\n"
        "See [[Complex I#Structure#Q module]], [[Complex I#^pump]] and [[Complex I#^gone]].\n"
        "Also [[Complex I#N module]] again, and [[Leigh syndrome]].\n",
        encoding="utf-8",
    )
    (root / "genes" / "NDUFV1.md").write_text("In the [[complex i#n module]].\n", encoding="utf-8")
    return root


def test_subpaths_are_not_checked_by_default(tmp_path: Path) -> None:
    root = _subpath_vault(tmp_path)
    proc = resolve(root, "[[Complex I#N module]]")
    assert proc.returncode == 0, proc.stderr
    assert "subpath_found" not in json.loads(proc.stdout)

    rows = json.loads(run_mdix(root, "links", "unresolved").stdout)
    assert [row["target"] for row in rows] == ["Leigh syndrome"]


def test_resolve_with_subpaths_reports_missing_heading_and_exits_1(tmp_path: Path) -> None:
    root = _subpath_vault(tmp_path)

    found = resolve(root, "[[Complex I#q module|Q]]", "--subpaths")
    assert found.returncode == 0, found.stderr
    assert json.loads(found.stdout)["subpath_found"] is True

    missing = resolve(root, "[[Complex I#N module]]", "--subpaths")
    assert missing.returncode == 1
    payload = json.loads(missing.stdout)
    assert payload["resolved"] == "complexes/Complex I.md"
    assert payload["subpath_found"] is False

    human = resolve(root, "[[Complex I#N module]]", "--subpaths", "--human")
    assert human.stdout.strip() == "complexes/Complex I.md\tbasename\tmissing #N module"

    plain = resolve(root, "[[Complex I]]", "--subpaths")
    assert plain.returncode == 0
    assert json.loads(plain.stdout)["subpath_found"] is None


def test_ls_with_subpaths_marks_each_link(tmp_path: Path) -> None:
    root = _subpath_vault(tmp_path)
    proc = run_mdix(root, "links", "ls", "--from", "genes/NDUFS4.md", "--subpaths")
    assert proc.returncode == 0, proc.stderr
    found = {record["raw"]: record["subpath_found"] for record in json.loads(proc.stdout)}
    assert found == {
        "[[Complex I#N module|N module]]": False,  # only inside a code fence
        "[[Complex I#Q module|Q module]]": True,  # closing #s are not part of the heading
        "[[Complex I#Structure#Q module]]": True,
        "[[Complex I#^pump]]": True,
        "[[Complex I#^gone]]": False,
        "[[Complex I#N module]]": False,
        "[[Leigh syndrome]]": None,
    }

    only = run_mdix(root, "links", "ls", "--subpaths", "--unresolved-only", "--human")
    lines = only.stdout.strip().splitlines()
    assert "genes/NDUFS4.md:1: Complex I -> complexes/Complex I.md (basename) missing #N module" in lines
    assert "genes/NDUFS4.md:3: Leigh syndrome -> - (unresolved)" in lines
    assert len(lines) == 5


def test_unresolved_with_subpaths_lists_owed_sections(tmp_path: Path) -> None:
    root = _subpath_vault(tmp_path)
    proc = run_mdix(root, "links", "unresolved", "--subpaths")
    assert proc.returncode == 0, proc.stderr
    rows = json.loads(proc.stdout)
    assert rows[0] == {
        "target": "Complex I#N module",
        "note": "complexes/Complex I.md",
        "subpath": "#N module",
        "count": 2,
        "occurrences": 3,
        "sources": ["genes/NDUFS4.md", "genes/NDUFV1.md"],
        "variants": ["Complex I#N module", "complex i#n module"],
    }
    assert [row["target"] for row in rows[1:]] == ["Complex I#^gone", "Leigh syndrome"]

    human = run_mdix(root, "links", "unresolved", "--subpaths", "--human")
    assert "2  Complex I#N module  (missing in complexes/Complex I.md)" in human.stdout.splitlines()
