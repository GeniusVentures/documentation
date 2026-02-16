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
