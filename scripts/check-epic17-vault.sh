#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vault_path="$repo_root/tmp/ai-barcamp-greifswald"

if [[ ! -e "$vault_path" ]]; then
  echo "epic17 setup error: '$vault_path' does not exist." >&2
  echo "Create/update pointer with: ln -sfn ../../ai-barcamp-greifswald tmp/ai-barcamp-greifswald" >&2
  exit 1
fi

if [[ ! -d "$vault_path" ]]; then
  echo "epic17 setup error: '$vault_path' exists but is not a directory." >&2
  exit 1
fi

echo "epic17 vault pointer OK: $vault_path"
