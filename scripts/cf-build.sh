#!/usr/bin/env bash
set -euo pipefail

# Ensure submodules are available in Cloudflare Pages build
if [ -f .gitmodules ]; then
  git submodule sync --recursive
  git submodule update --init --recursive
fi

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs build
