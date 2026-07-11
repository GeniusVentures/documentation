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
OUTPUT_DIR="$REPO_ROOT/docs/SuperGenius"
SG_DOCS_DIR="$REPO_ROOT/sg-docs"
SUPERGENIUS_ROOT="$(cd "$REPO_ROOT/../SuperGenius" && pwd)"
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR/src"

mkdir -p "$SG_DOCS_DIR/doxygen"

pushd "$SUPERGENIUS_ROOT" >/dev/null
DOXY_OVERRIDE_FILE="$SG_DOCS_DIR/.cf-doxygen.Doxyfile"
cat > "$DOXY_OVERRIDE_FILE" <<EOF
@INCLUDE = $SG_DOCS_DIR/Doxyfile
FULL_PATH_NAMES = NO
OUTPUT_DIRECTORY = $SG_DOCS_DIR/doxygen
EOF
doxygen "$DOXY_OVERRIDE_FILE"
rm -f "$DOXY_OVERRIDE_FILE"
popd >/dev/null

doxybook2 --input sg-docs/doxygen/xml/ --output "$OUTPUT_DIR" -c scripts/doxybook.json
python3 scripts/build_navigation.py "$OUTPUT_DIR"

# ── Python venv + MkDocs build ────────────────────────────────────────────────
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
mkdocs build

# Always compress MkDocs search index and serve it as gzipped JSON.
# INDEX_FILE="site/search/search_index.json"
# if [ -f "$INDEX_FILE" ]; then
#  gzip -9 -c "$INDEX_FILE" > "$INDEX_FILE.gz"
#  mv "$INDEX_FILE.gz" "$INDEX_FILE"
#
#  HEADERS_FILE="site/_headers"
#  if [ ! -f "$HEADERS_FILE" ] || ! grep -q '^/search/search_index.json$' "$HEADERS_FILE"; then
#    {
#      echo ""
#      echo "/search/search_index.json"
#      echo "  Content-Type: application/json; charset=utf-8"
#      echo "  Content-Encoding: gzip"
#    } >> "$HEADERS_FILE"
#  fi
#fi
