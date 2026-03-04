#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ── Submodules ────────────────────────────────────────────────────────────────
if [ -f .gitmodules ]; then
  git submodule sync --recursive
  git submodule update --init --recursive
fi

# ── SuperGenius API docs ──────────────────────────────────────────────────────
OUTPUT_DIR="docs/SuperGenius"
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR/src"

doxybook2 --input sg-docs/doxygen/xml/ --output "$OUTPUT_DIR" -c scripts/doxybook.json
python3 scripts/build_navigation.py "$OUTPUT_DIR"

# ── Python venv + MkDocs build ────────────────────────────────────────────────
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
mkdocs build

# ── Deploy to Cloudflare Pages ────────────────────────────────────────────────
# Install wrangler if not already available.
if ! command -v wrangler &>/dev/null; then
  npm install
fi

npx wrangler pages deploy site \
  --project-name=gnus-ai-docs \
  --commit-dirty=true

