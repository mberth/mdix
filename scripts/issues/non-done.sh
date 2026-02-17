#!/usr/bin/env bash
set -euo pipefail

issues_root="${1:-plan/issues}"

uv run mdix --root "$issues_root" q \
  | jq -r '
      ("id\ttype\tstatus\tparent\ttitle"),
      (
        .[] | .frontmatter as $f
        | select($f.status != "done")
        | "\($f.id)\t\($f.type)\t\($f.status)\t\($f.parent)\t\($f.title)"
      )
    '
