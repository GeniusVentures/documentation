---
cover: .gitbook/assets/Screen Shot 2024-02-22 at 1.10.29 PM.png
coverY: 0
---

# GNUS.AI

GNUS.AI is a revolutionary blockchain that harnesses the untapped computing power of devices worldwide to process [Artificial Intelligence (A.I.)](resources/glossary.md#artificial-intelligence-a.i) and [Machine Learning (M.L.) data.](resources/glossary.md#machine-learning-m.l)

{% embed url="https://www.gnus.ai/wp-content/uploads/2024/02/Genius-A.I.mp4?autoplay=1&iframe=true" %}

## MkDocs + Cloudflare Pages

This repository is served by MkDocs (Material) and deployed on Cloudflare Pages.

### Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

### Build

```bash
mkdocs build
```

### Windows (npm scripts)

Use the Windows-native scripts through npm:

```bat
npm run docs:build:win
npm run docs:build:deploy:win
```

### Cloudflare Pages settings

Build command:

```bash
pip install -r requirements.txt && mkdocs build
```

Build output directory:

```
site
```

### Submodules (hdocs)

This repo includes hdoc outputs as git submodules under `hdocs/` (for example `hdocs/sg-hdocs`).
Make sure submodules are initialized when building in CI.

Local:

```bash
git submodule update --init --recursive
```

### Cloudflare Pages with submodules

Option 1 (recommended): Use the build script, which initializes submodules and builds:

Build command:

```bash
./scripts/cf-build.sh
```

Build output directory:

```
site
```

Option 2: If you prefer to keep the build command inline, ensure submodules are enabled in Cloudflare Pages:

- Settings: Build & deployments
- Enable: "Git submodules"

Then use:

```bash
pip install -r requirements.txt && mkdocs build
```

### SuperGenius API reference generation

The SuperGenius Doxygen XML lives in the `sg-docs` submodule under `sg-docs/doxygen/xml` and is committed into the repo after it is built in the main codebase. The Markdown under `docs/supergenius` is generated on demand and therefore must be created before you run MkDocs.

The `scripts/cf-build.sh` script performs the conversion using the `doxybook2` CLI:

```bash
./scripts/cf-build.sh
```

`cf-build.sh` assumes the XML already exists, runs `doxybook2 --input sg-docs/doxygen/xml/ --output docs/supergenius --format markdown`, installs the Python requirements, and then runs `mkdocs build`. After the Markdown is regenerated you can serve or build the site as usual.

Get `doxybook2` for macOS/ARM from https://github.com/GeniusVentures/doxybook2/releases or other platforms from https://github.com/Antonz0/doxybook2/releases/tag/v1.6.1 so the conversion step works on your machine. Once the API reference is refreshed you can continue with the remaining MkDocs workflow (`mkdocs serve` or `mkdocs build`).
