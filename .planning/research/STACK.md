# Technology Stack

**Project:** GNUS.AI Documentation Site Refactoring
**Researched:** 2026-07-08
**Domain:** Documentation site migration from embedded gendoc-template code to gendoc-template submodule

## Executive Summary

The documentation project was the **origin** of the `gendoc-template` submodule -- its embedded `javascripts/`, `stylesheets/`, `scripts/`, and `mkdocs.yml` were extracted into the reusable template now used by GeniusCogntiveSystem. The refactoring completes the circle: this project becomes a consumer of its own extracted template.

However, the documentation project has **three unique characteristics** that prevent it from following the "pure" gendoc-template host pattern (where the host has only a `gendoc.yml` file):

1. **`docs/` is a gitbook submodule** -- not a regular directory of hand-written docs. It contains GitBook-format content that requires the `rewrite_gitbook_paths.py` MkDocs hook to convert to standard Markdown at build time.
2. **Custom SuperGenius API pipeline** -- a Doxygen + doxybook2 pipeline specific to the SuperGenius SDK, using `scripts/doxybook.json` and `sg-docs/` submodule configs that gendoc-template's generic `source_references` feature does not replicate.
3. **Project-specific build orchestration** -- `cf-build.sh`/`cf-build.bat` runs the Doxygen pipeline and LLM catalog generation with project-specific paths.

These three differences mean the documentation project uses a **hybrid pattern**: gendoc-template submodule for shared assets and core MkDocs hooks, with a **project-local `mkdocs.yml`** that adds the GitBook-rewriting hook and project-specific asset references.

## Recommended Stack

### File Ownership: Submodule vs Host Project

This is the central question of the refactoring. Every file must be classified as either submodule-provided (can be removed from host) or host-unique (must be kept).

#### Files Provided by gendoc-template Submodule (HOST CAN REMOVE)

These files exist in the gendoc-template submodule. The host project's copies are duplicates and should be removed.

| File | Confidence | Reason |
|------|------------|--------|
| `javascripts/breadcrumbs.js` | HIGH | Byte-identical to gendoc-template version (3597 bytes) |
| `javascripts/external-links.js` | HIGH | Byte-identical to gendoc-template version (1005 bytes) |
| `javascripts/mathjax.js` | HIGH | Byte-identical to gendoc-template version (670 bytes) |
| `javascripts/mermaid.js` | HIGH | Byte-identical to gendoc-template version (1195 bytes) |
| `javascripts/nav-state.js` | HIGH | gendoc-template has newer version (14233 bytes vs host's 11390 bytes). Same file, template has improvements. |
| `javascripts/ask/` (Ask AI widget) | HIGH | Only exists in gendoc-template. This is the widget this refactoring aims to enable. |
| `stylesheets/theme.css` | HIGH | gendoc-template version (275 lines) is a superset of host's `extra.css` (227 lines). Same brand palette, plus Ask AI drawer styles. |
| `requirements.txt` | HIGH | gendoc-template provides identical package set plus `pyyaml>=6.0` (needed by load-gendoc-config.py) |

#### Files the Host Project MUST KEEP (Not Provided by Submodule)

| File | Confidence | Reason |
|------|------------|--------|
| `docs/` (gitbook submodule) | HIGH | The actual documentation content. Referenced in `.gitmodules` as `path = docs`, `url = ../gitbook`. |
| `sg-docs/` (sg-docs submodule) | HIGH | SuperGenius Doxygen configuration files (Doxyfile, etc.). Custom to this project. |
| `scripts/rewrite_gitbook_paths.py` | HIGH | MkDocs hook that converts GitBook syntax (cover images, embed tags, math delimiters, asset paths, Doxygen tags) to standard Markdown. **Not present in gendoc-template.** Critical path dependency. |
| `scripts/build_navigation.py` | HIGH | Custom navigation builder that generates the SuperGenius API reference nav section. Different purpose from gendoc-template's `build-navigation.py`. |
| `scripts/doxybook.json` | HIGH | Doxybook2 configuration for SuperGenius. Different from gendoc-template's version. |
| `scripts/cf-build.sh` | HIGH | Cloudflare Pages build script orchestrating: submodule init, SuperGenius Doxygen+doxybook2 pipeline, venv setup, mkdocs build, LLM catalog generation. Must be updated to use submodule paths. |
| `scripts/cf-build.bat` | HIGH | Windows equivalent of cf-build.sh. Must be updated similarly. |
| `stylesheets/extra.css` | MEDIUM | Project-specific GitBook compatibility overrides. Some rules may duplicate theme.css. Should be audited: keep only rules NOT in gendoc-template's theme.css. |
| `gendoc.yml` | HIGH | NEW file to create. The host project configuration. Does not exist yet. |
| `mkdocs.yml` | HIGH | Project-local mkdocs configuration. Cannot be deleted because it needs the `rewrite_gitbook_paths.py` hook that gendoc-template's mkdocs.yml doesn't include. |

#### Files to EVALUATE (May be Replaceable)

| File | Confidence | Assessment |
|------|------------|------------|
| `scripts/build_llms.py` | MEDIUM | gendoc-template has a newer version (`build-llms.py`, 445 lines vs host's 306 lines). The template version is a superset. Recommendation: replace with template version after verifying output parity. |

### mkdocs.yml Configuration Pattern

**Decision: Hybrid mkdocs.yml -- project-local with submodule hook references.**

The "pure" gendoc-template pattern (no host-level mkdocs.yml) cannot work because the documentation project requires the `rewrite_gitbook_paths.py` hook. The template's mkdocs.yml hardcodes three hooks; there is no extension mechanism to inject additional hooks via `gendoc.yml`.

The project-local mkdocs.yml must:

1. Reference **template hooks** via submodule-relative paths
2. Reference the **project-specific hook** (`rewrite_gitbook_paths.py`)
3. Use **template-provided assets** for CSS and JS (since `copy-assets.py` copies them to the site)
4. Keep project-specific `extra.css` in the host's `stylesheets/` for GitBook overrides

```yaml
# mkdocs.yml -- Project-local configuration for docs.gnus.ai
# This project uses gendoc-template as a submodule for shared
# infrastructure, but keeps project-specific hooks and config
# that the template does not provide.

site_name: GNUS.ai Docs        # Overridden by load-gendoc-config.py from gendoc.yml
docs_dir: docs                  # Overridden by load-gendoc-config.py from gendoc.yml
site_dir: site                  # Overridden by load-gendoc-config.py from gendoc.yml
use_directory_urls: true

hooks:
  # gendoc-template hooks (submodule paths)
  - gendoc-template/scripts/load-gendoc-config.py   # Reads gendoc.yml, injects site_name/docs_dir/site_dir
  - gendoc-template/scripts/clean-nav.py             # Fixes nav rendering for clickable section titles
  - gendoc-template/scripts/copy-assets.py           # Copies template javascripts/ + stylesheets/ into site
  # Project-specific hook (NOT in gendoc-template)
  - scripts/rewrite_gitbook_paths.py                 # Converts GitBook syntax to standard Markdown

watch:
  - javascripts
  - stylesheets

theme:
  name: material
  features:
    - navigation.indexes
    - navigation.sections
    - navigation.top
    - navigation.footer
    - navigation.instant
    - navigation.tracking
    - navigation.path
    - search.suggest
    - search.highlight
    - content.tabs
    - content.code.copy
    - toc.integrate

  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - literate-nav:
      nav_file: SUMMARY_EXT.md
  - redirects:
      redirect_maps:

validation:
  links:
    absolute_links: ignore
    unrecognized_links: ignore
    not_found: ignore
  nav:
    omitted_files: ignore
    not_found: ignore

markdown_extensions:
  - toc:
      permalink: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.details
  - pymdownx.emoji
  - pymdownx.arithmatex:
      generic: true
  - admonition
  - attr_list
  - md_in_html

extra_css:
  # theme.css comes from gendoc-template (copied by copy-assets.py)
  - /stylesheets/theme.css
  # extra.css is project-specific GitBook overrides (kept in host stylesheets/)
  - /stylesheets/extra.css

extra_javascript:
  # External CDN scripts
  - https://unpkg.com/mermaid@10/dist/mermaid.min.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
  # Template-provided scripts (copied by copy-assets.py)
  - /javascripts/mermaid.js
  - /javascripts/external-links.js
  - /javascripts/mathjax.js
  - /javascripts/nav-state.js
  - /javascripts/breadcrumbs.js
  # Ask AI widget (from gendoc-template, copied by copy-assets.py)
  - path: /javascripts/ask/main.js
    type: module
```

### The `gendoc.yml` Configuration

Created at the host project root. This file is read by `load-gendoc-config.py` at build time.

```yaml
# gendoc.yml — docs.gnus.ai documentation configuration

project:
  name: "GNUS.ai Docs"
  number: ""               # No version number for docs site
  brief: "The GNUS.AI Operating System — official documentation"
  generator: false          # Hide "Made with Material for MkDocs" footer
  logo: "docs/favicon.ico"  # Path relative to host project root

paths:
  handwritten_docs: "docs"  # Points to the gitbook submodule directory

mkdocs:
  site_dir: "site"
  use_directory_urls: true
  strict: false

# No source_references — this project uses its own Doxygen pipeline
# via scripts/cf-build.sh, not gendoc-template's build-source-reference.sh.

# No navigation.generate_index — the gitbook submodule provides SUMMARY_EXT.md.

llms:
  enabled: true
  site_url: "https://docs.gnus.ai"
  corpus_cache: "llms-corpus"
  meta_file: "llms-meta.json"

  audiences:
    llms-technical.txt:
      title: "Architecture & Developer Reference"
      categories: [technical, architecture, api, nodes]

  related_catalogs:
    - url: "https://gcs.gnus.ai/llms.txt"
      title: "Genius Cognitive System"
      description: "Distributed cognitive platform documentation"
      audiences: [llms-technical.txt]

  ask:
    enabled: true
    endpoint: "https://ask.gnus.ai/api/ask"
    allowed_origins:
      - "https://docs.gnus.ai"
      - "https://gcs.gnus.ai"
    providers: "openrouter,gemini"
    gemini_model: "gemini-2.5-flash"
    openrouter_models: "nvidia/nemotron-3-super-120b-a12b:free,nvidia/nemotron-3-ultra-550b-a55b:free,nvidia/nemotron-3-nano-30b-a3b:free"
```

### .gitmodules Update

Add the gendoc-template submodule alongside existing submodules:

```
[submodule "gitbook"]
	path = docs
	url = ../gitbook
[submodule "sg-docs"]
	path = sg-docs
	url = ../sg-docs
[submodule "gendoc-template"]
	path = gendoc-template
	url = ../gendoc-template.git
```

### Build Script Changes

The `cf-build.sh` and `cf-build.bat` scripts are the Cloudflare Pages entry points. They must be updated to:

1. **Init submodules** -- already done; add `gendoc-template` to the recursive pull
2. **SuperGenius API pipeline** -- unchanged (Doxygen + doxybook2 + build_navigation.py)
3. **Python venv** -- install from `gendoc-template/requirements.txt` instead of `requirements.txt`
4. **MkDocs build** -- run from project root (uses project-local `mkdocs.yml` which references submodule hooks)
5. **LLM catalog generation** -- use gendoc-template's `build-llms.py` for consistency

Key change to `cf-build.sh`:

```bash
# Old: pip install -r requirements.txt
# New: pip install -r gendoc-template/requirements.txt

# Old: python3 "$SCRIPT_DIR/build_llms.py" "$@"
# New: python3 gendoc-template/scripts/build-llms.py "$@" --config gendoc.yml
```

Everything else stays the same: the Doxygen pipeline, venv setup, and `mkdocs build` command (because mkdocs.yml remains at project root).

### How Asset Copying Works (Cross-Reference)

The `copy-assets.py` hook (from gendoc-template) copies `javascripts/` and `stylesheets/` from the **template root** to the site directory on every build. This means:

- **5 shared JS files** (breadcrumbs, external-links, mathjax, mermaid, nav-state) come from the template
- **Ask AI widget** (`javascripts/ask/`) comes from the template
- **`theme.css`** (brand colors + Ask AI drawer styles) comes from the template

The host project's `stylesheets/extra.css` is picked up by mkdocs because the `docs/` submodule has a symlink `stylesheets -> ../stylesheets/`. This symlink must be preserved.

### Dependencies (pip)

**No `requirements.txt` at project root after refactoring.** The single source of truth is `gendoc-template/requirements.txt`:

```
mkdocs==1.6.1
mkdocs-material==9.5.27
pymdown-extensions>=10.14
mkdocs-literate-nav==0.6.1
pyyaml>=6.0
```

Note: The host's current `requirements.txt` includes `mkdocs-redirects`, `mkdocs-section-index`, `mkdocs-exclude`, and `mkdocs-git-revision-date-localized-plugin`. These are not in gendoc-template's requirements. `mkdocs-redirects` IS used (redirects plugin in mkdocs.yml). The others are present in the host's old requirements but not referenced in mkdocs.yml. This needs verification during Phase 2 implementation.

### Final Host Project Directory Layout

```
documentation/                          (host project root)
├── gendoc.yml                          (NEW: project configuration)
├── mkdocs.yml                          (MODIFIED: hybrid config)
├── .gitmodules                         (MODIFIED: add gendoc-template)
├── gendoc-template/                    (NEW: git submodule, read-only)
│   ├── mkdocs.yml                      (template reference -- not used directly)
│   ├── requirements.txt                (used by venv)
│   ├── scripts/                        (template hooks + build infra)
│   │   ├── load-gendoc-config.py       (MkDocs hook)
│   │   ├── clean-nav.py                (MkDocs hook)
│   │   ├── copy-assets.py              (MkDocs hook)
│   │   ├── build.sh                    (reference build script)
│   │   ├── build-widget.sh             (Ask AI widget builder)
│   │   ├── build-llms.py               (LLM catalog generator)
│   │   ├── setup.sh                    (Cloudflare setup)
│   │   ├── deploy.sh                   (Cloudflare deploy)
│   │   ├── deploy-ask.sh               (Ask AI worker deploy)
│   │   └── ...
│   ├── javascripts/                    (template JS + Ask AI widget)
│   │   ├── breadcrumbs.js
│   │   ├── external-links.js
│   │   ├── mathjax.js
│   │   ├── mermaid.js
│   │   ├── nav-state.js
│   │   └── ask/                        (Ask AI widget)
│   └── stylesheets/
│       └── theme.css                   (brand colors + Ask AI drawer)
├── docs/                               (KEPT: gitbook submodule, content)
│   ├── SUMMARY_EXT.md                  (nav structure)
│   ├── about-gnus.ai/
│   ├── technical-information/
│   ├── SuperGenius/                    (generated API reference)
│   ├── assets/
│   ├── javascripts -> ../javascripts/  (MAY NEED UPDATE: points to now-empty host dir)
│   └── stylesheets -> ../stylesheets/  (KEPT: picks up extra.css)
├── sg-docs/                            (KEPT: SuperGenius doxygen configs)
├── scripts/                            (SHRUNK: project-specific only)
│   ├── rewrite_gitbook_paths.py        (KEPT: unique hook)
│   ├── build_navigation.py             (KEPT: SuperGenius nav builder)
│   ├── doxybook.json                   (KEPT: doxybook2 config)
│   ├── cf-build.sh                     (MODIFIED: updated paths)
│   └── cf-build.bat                    (MODIFIED: updated paths)
└── stylesheets/
    └── extra.css                       (KEPT: GitBook-specific overrides only)
```

### REMOVED from host project after refactoring:
```
javascripts/breadcrumbs.js              (from gendoc-template)
javascripts/external-links.js           (from gendoc-template)
javascripts/mathjax.js                  (from gendoc-template)
javascripts/mermaid.js                  (from gendoc-template)
javascripts/nav-state.js                (from gendoc-template, newer version)
requirements.txt                        (from gendoc-template)
scripts/build_llms.py                   (replaced by gendoc-template version)
```

## The docs/ Submodule Symlink Issue

**Critical detail:** The `docs/` gitbook submodule contains symlinks:

```
docs/javascripts -> ../javascripts/
docs/stylesheets -> ../stylesheets/
```

These symlinks exist so mkdocs can find JS/CSS files when `docs_dir: docs`. After refactoring:

- `javascripts/` at host level is REMOVED (JS comes from gendoc-template via copy-assets.py)
- The symlink `docs/javascripts -> ../javascripts/` would point to an empty/non-existent directory
- `stylesheets/` at host level is KEPT (for extra.css only)
- The symlink `docs/stylesheets -> ../stylesheets/` still works for extra.css

**Options for the javascripts symlink:**

1. **Delete it** -- copy-assets.py handles copying template JS to the site dir. The symlink is no longer needed since mkdocs resolves `extra_javascript` against the site root, not `docs_dir`.
2. **Repoint it** -- `docs/javascripts -> ../gendoc-template/javascripts/` would let mkdocs find the template's JS during `mkdocs serve`. But this creates a dependency on the submodule path.
3. **Leave it broken** -- harmless if copy-assets.py runs. But `mkdocs serve` would fail to find the JS files until a build runs.

**Recommendation: Delete the symlink.** The `extra_javascript` entries in mkdocs.yml reference absolute paths (`/javascripts/...`) which mkdocs resolves relative to the site directory. The copy-assets.py hook populates these files in the site directory during build. The symlink is a vestige of the pre-template era when JS files lived in the host's `javascripts/` directory and mkdocs needed to find them relative to `docs_dir`.

For development (`mkdocs serve`), the copy-assets.py hook also runs. Files will be served correctly.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| mkdocs.yml location | Project-local hybrid | Pure submodule (no host mkdocs.yml) | Cannot inject `rewrite_gitbook_paths.py` hook into template's mkdocs.yml |
| build_llms.py | gendoc-template version | Keep host version | Template version is newer superset (445 lines vs 306). Host version is pre-extraction. |
| requirements.txt | gendoc-template version | Keep host version | Template adds pyyaml (needed). Host version lists unused plugins. |
| nav-state.js | gendoc-template version | Keep host version | Template version is newer (14233 vs 11390 bytes), same file with improvements. |

## Sources

- [gendoc-template README.md](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/README.md) -- HIGH confidence: official template documentation
- [gendoc-template gendoc.yml.example](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/gendoc.yml.example) -- HIGH confidence: full schema reference
- [GeniusCogntiveSystem gendoc.yml](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc.yml) -- HIGH confidence: reference implementation
- [gendoc-template scripts](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/scripts/) -- HIGH confidence: hook implementations analyzed
- [Documentation project .gitmodules](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/.gitmodules) -- HIGH confidence: existing submodule structure
- [Documentation project cf-build.sh](file:///Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/scripts/cf-build.sh) -- HIGH confidence: current build pipeline
- File size comparisons between host and template JS/CSS -- HIGH confidence: byte-for-byte verification of duplicates
