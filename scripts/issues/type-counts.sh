#!/usr/bin/env bash
set -euo pipefail

issues_root="${1:-plan/issues}"

uv run mdix --root "$issues_root" q \
  | jq -r '
      [.[].frontmatter.type]
      | group_by(.)
      | map({type: .[0], count: length})
      | ("type\tcount"), (.[] | "\(.type)\t\(.count)")
    '
