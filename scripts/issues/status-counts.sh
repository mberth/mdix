#!/usr/bin/env bash
set -euo pipefail

issues_root="${1:-plan/issues}"

uv run mdix --root "$issues_root" q \
  | jq -r '
      [.[].frontmatter.status]
      | group_by(.)
      | map({status: .[0], count: length})
      | ("status\tcount"), (.[] | "\(.status)\t\(.count)")
    '
