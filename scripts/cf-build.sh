#!/usr/bin/env bash
set -euo pipefail

# Ensure submodules are available in Cloudflare Pages build
if [ -f .gitmodules ]; then
  git submodule sync --recursive
  git submodule update --init --recursive
fi

OUTPUT_DIR="docs/SuperGenius"
mkdir -p "$OUTPUT_DIR"

# Remove old src tree so links are regenerated cleanly
rm -rf "$OUTPUT_DIR/src"

doxybook2 --input sg-docs/doxygen/xml/ --output "$OUTPUT_DIR" -c scripts/doxybook.json

# create the navigation file for mkdocs
python3 scripts/build_navigation.py "$OUTPUT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
mkdocs build
