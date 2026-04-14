#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

"$SCRIPT_DIR/cf-build.sh"

# Install wrangler if not already available.
if ! command -v wrangler &>/dev/null; then
  npm install
fi

npx wrangler pages deploy site \
  --project-name=gnus-ai-docs \
  --commit-dirty=true

