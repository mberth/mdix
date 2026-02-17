#!/usr/bin/env bash
set -euo pipefail

issues_root="${1:-plan/issues}"

uv run mdix --root "$issues_root" q \
  | jq -r '
      map(.frontmatter) as $fm
      | ("id\tstatus\tchildren\tchild_status_counts\ttitle"),
        (
          $fm[]
          | select(.type == "epic") as $epic
          | ($fm | map(select(.parent == $epic.id))) as $children
          | ($children | map(.status) | group_by(.) | map({key: .[0], value: length}) | from_entries) as $by_status
          | "\($epic.id)\t\($epic.status)\t\($children | length)\t\($by_status | tojson)\t\($epic.title)"
        )
    '
