# Architecture Patterns

**Domain:** MkDocs documentation site with submodule-based build framework
**Researched:** 2026-07-08
**Confidence:** HIGH (current codebase analyzed + reference implementation inspected)

## Recommended Architecture

The refactored architecture separates concerns into three layers: **content** (host project), **framework** (gendoc-template submodule), and **build orchestration** (host project build scripts).

```
HOST PROJECT (documentation/)              SUBMODULE (gendoc-template/)
===================================        ===================================
gendoc.yml           (config)      ──►     scripts/load-gendoc-config.py
docs/                (content)     ──►     mkdocs.yml
scripts/
  cf-build.sh        (orchestrate) ──►     scripts/build.sh (or parts thereof)
  cf-build.bat
  rewrite_gitbook_paths.py (hook)          scripts/clean-nav.py
  build_navigation.py (nav gen)            scripts/copy-assets.py
  build_llms.py      (llms gen)     ──►    scripts/build-llms.py
  doxybook.json
SUMMARY_EXT.md       (nav structure)       SUMMARY_EXT.md (template default)
stylesheets/                              stylesheets/theme.css
  (DELETED — template provides)           javascripts/
javascripts/                               ├── breadcrumbs.js
  (DELETED — template provides)           ├── external-links.js
  EXCEPT possibly nav-state.js            ├── mathjax.js
                                           ├── mermaid.js
                                           ├── nav-state.js (superset)
                                           └── ask/
                                               ├── main.js
                                               ├── config.js
                                               ├── drawer.js
                                               ├── transport.js
                                               ├── session.js
                                               └── ...
```

### Component Boundaries

| Component | Ownership | Responsibility | Communicates With |
|-----------|-----------|---------------|-------------------|
| `gendoc.yml` | Host | Project-specific configuration (name, paths, llms, ask, deploy) | `load-gendoc-config.py`, `build.sh`, `build-widget.sh`, `build-llms.py` |
| `gendoc-template/mkdocs.yml` | Submodule | MkDocs build configuration (theme, plugins, hooks, markdown extensions, JS/CSS references) | All MkDocs hooks |
| `gendoc-template/scripts/load-gendoc-config.py` | Submodule | Reads host's `gendoc.yml` at startup, injects site_name/docs_dir/site_dir/logo into MkDocs config | `gendoc.yml` (host root) |
| `gendoc-template/scripts/clean-nav.py` | Submodule | Rewrites .md link URLs to directory URLs; promotes section indexes for clickable nav | MkDocs nav structure |
| `gendoc-template/scripts/copy-assets.py` | Submodule | Copies javascripts/ and stylesheets/ from submodule into built site directory at post_build | Site output directory |
| `gendoc-template/scripts/build.sh` | Submodule | Full build pipeline: source ref, index gen, widget build, mkdocs build, llms generation | `gendoc.yml`, `build-source-reference.sh`, `build-widget.sh`, `build-llms.py` |
| `gendoc-template/scripts/build-widget.sh` | Submodule | Compiles TypeScript widget, generates ask-config.json | `gendoc.yml`, `ask-ai/widget-src/` |
| `gendoc-template/scripts/build-llms.py` | Submodule | Generates llms.txt agent catalogs from content + metadata | `gendoc.yml`, `llms-meta.json` |
| `gendoc-template/javascripts/` | Submodule | Client-side JS: breadcrumbs, external-links, mermaid, mathjax, nav-state, ask widget | Built HTML pages |
| `gendoc-template/stylesheets/theme.css` | Submodule | Brand colors, MkDocs overrides, Ask AI drawer styles | Built HTML pages |
| `scripts/cf-build.sh` | Host | Orchestrates the full Cloudflare Pages build (submodule init, Doxygen, doxybook2, mkdocs, llms) | Submodule scripts, `gendoc-template/.venv` |
| `scripts/rewrite_gitbook_paths.py` | Host | Gitbook-specific URL rewriting hook (the only host-specific hook) | MkDocs config |
| `scripts/build_navigation.py` | Host | Generates SUMMARY_EXT.md section for SuperGenius API reference docs | `docs/SuperGenius/` |
| `docs/` (gitbook submodule) | Host (submodule) | Hand-written documentation content in Gitbook format | MkDocs docs_dir |
| `sg-docs/` (submodule) | Host (submodule) | Doxygen config for SuperGenius API reference | Doxygen, doxybook2 pipeline |
| `SUMMARY_EXT.md` | Host | Root navigation structure for literate-nav plugin | MkDocs literate-nav plugin |

### Data Flow

The full build pipeline from configuration to deployed site:

```
gendoc.yml ──────────────────────────────────────────────────────────────────────
    │
    ├──► load-gendoc-config.py (on_config hook)
    │    │  Reads: project.name, project.logo, paths.handwritten_docs, mkdocs.site_dir
    │    │  Injects into MkDocs config: site_name, docs_dir, site_dir, theme.logo
    │    │
    ├──► build.sh (main build orchestrator — from submodule)
    │    │  Step 1: build-source-reference.sh → Doxygen → doxybook2 → build-navigation.py
    │    │  Step 2: generate-index.sh (if navigation.generate_index: true)
    │    │  Step 3: build-widget.sh → TypeScript compile → ask-config.json
    │    │  Step 4: mkdocs build -f gendoc-template/mkdocs.yml
    │    │  Step 5: build-llms.py → llms.txt agent catalogs
    │    │
    ├──► build-widget.sh
    │    │  Reads: llms.ask (enabled, endpoint, title, site_url, providers)
    │    │  Outputs: javascripts/ask/*.js (compiled), site/ask-config.json
    │    │
    └──► build-llms.py
         Reads: llms (site_url, audiences, related_catalogs, meta_file)
         Outputs: llms.txt, llms-full.txt, llms-technical.txt, etc.

mkdocs build flow:
    gendoc-template/mkdocs.yml
         │
         ├── hooks: load-gendoc-config.py   (on_config — injects gendoc.yml values)
         ├── hooks: clean-nav.py             (on_nav — rewrites URLs, promotes indexes)
         ├── hooks: [rewrite_gitbook_paths.py] (host-specific, on_page_content)
         ├── hooks: copy-assets.py           (on_post_build — mirrors JS/CSS into site/)
         │
         ├── plugins: literate-nav           (reads SUMMARY_EXT.md)
         ├── plugins: search
         ├── plugins: redirects
         │
         └── Output: site/ directory
              ├── index.html
              ├── (all doc pages)
              ├── javascripts/   ← copied by copy-assets.py from submodule
              ├── stylesheets/   ← copied by copy-assets.py from submodule
              └── ask-config.json ← generated by build-widget.sh
```

### Host-Project mkdocs.yml Strategy

Unlike the reference implementation (GeniusCogntiveSystem) which uses the submodule's mkdocs.yml directly (no host mkdocs.yml), the documentation project needs its own mkdocs.yml because it requires a host-specific hook (`rewrite_gitbook_paths.py`).

**Strategy:** The host project maintains an `mkdocs.yml` at its root that is functionally equivalent to the submodule's mkdocs.yml but references submodule scripts via `gendoc-template/scripts/` paths and adds the host hook.

**Key difference from reference implementation:** GeniusCogntiveSystem runs `mkdocs build -f gendoc-template/mkdocs.yml` (no host mkdocs.yml). The documentation project runs `mkdocs build -f mkdocs.yml` (host mkdocs.yml that mirrors the template's).

**Host mkdocs.yml structure:**

| Section | Source | Notes |
|---------|--------|-------|
| site_name | load-gendoc-config override | Template default "Project Docs" replaced by gendoc.yml project.name |
| docs_dir | load-gendoc-config override | Set to host project's docs/ via gendoc.yml paths.handwritten_docs |
| site_dir | "site" | Same as template |
| use_directory_urls | true | Same as template |
| hooks | gendoc-template/scripts/* + host scripts/* | All template hooks plus rewrite_gitbook_paths.py |
| watch | javascripts, stylesheets | Same as template (paths resolve relative to mkdocs.yml) |
| theme | Same as template | Material theme, palette, features |
| plugins | Same as template | search, literate-nav, redirects |
| markdown_extensions | Same as template | toc, superfences, highlight, mathjax, etc. |
| extra_css | /stylesheets/theme.css | Provided by copy-assets.py from submodule |
| extra_javascript | Template JS list + Ask AI module | /javascripts/ask/main.js loaded as module |

The host project's `cf-build.sh` and `cf-build.bat` remain the build entry points (Cloudflare Pages invokes them). They are modified to run `mkdocs build -f mkdocs.yml` using the host's mkdocs.yml rather than the submodule's.

## Patterns to Follow

### Pattern 1: Submodule Script Paths in Host Config

**What:** When the host project maintains its own mkdocs.yml, hook paths to submodule scripts use `gendoc-template/scripts/` prefix.

**When:** Any host project that needs custom hooks beyond what the template provides.

**Why:** MkDocs resolves hook paths relative to the config file location. Since the host's mkdocs.yml is at project root, `gendoc-template/scripts/load-gendoc-config.py` correctly resolves into the submodule.

### Pattern 2: Asset Copy at Build Time

**What:** The `copy-assets.py` hook mirrors submodule javascripts/ and stylesheets/ into the built site/ directory at post_build.

**When:** Every build. The submodule's assets live outside the docs_dir (which is the host's content directory), so MkDocs does not automatically copy them.

**Why:** MkDocs only copies files under docs_dir. The submodule's assets (javascripts/, stylesheets/) live at the template root. copy-assets.py bridges this gap so `/javascripts/nav-state.js` and `/stylesheets/theme.css` resolve correctly in the built site.

### Pattern 3: Configuration Injection at Startup

**What:** `load-gendoc-config.py` reads the host's `gendoc.yml` during MkDocs config loading (on_config hook) and overrides site_name, docs_dir, site_dir, and logo.

**When:** Every MkDocs build or serve invocation. Runs before any other hook.

**Why:** Keeps the submodule's mkdocs.yml project-agnostic. The template never hardcodes a project name or content path. All project-specific values flow from gendoc.yml.

### Pattern 4: Custom Hook Registration

**What:** Host-specific hooks (like `rewrite_gitbook_paths.py`) are listed in the host's mkdocs.yml hooks array, placed between clean-nav (on_nav) and copy-assets (on_post_build).

**When:** When a project has content transformations the template does not cover.

**Recommended hook ordering:**
```yaml
hooks:
  - gendoc-template/scripts/load-gendoc-config.py   # on_config — inject settings
  - gendoc-template/scripts/clean-nav.py              # on_nav — fix .md URLs
  - scripts/rewrite_gitbook_paths.py                  # on_page_content — gitbook URLs
  - gendoc-template/scripts/copy-assets.py            # on_post_build — mirror assets
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Modifying the Submodule

**What:** Editing files inside gendoc-template/ to add project-specific behavior.

**Why bad:** Submodule changes are per-repo, not shared. Updates to the template (git pull in submodule) would conflict. The submodule is designed to be read-only from the host's perspective.

**Instead:** Put all project-specific configuration in gendoc.yml. Put project-specific hooks in host scripts/. If a hook is needed, add it to the host's mkdocs.yml hooks list.

### Anti-Pattern 2: Keeping Duplicate Assets

**What:** Leaving javascripts/ or stylesheets/ in the host project after gendoc-template already provides them.

**Why bad:** Divergence — the host's copy becomes stale while the template's copy receives bug fixes and feature additions (e.g., nav-state.js in the template has scroll persistence and active-link highlighting that the documentation project's copy lacks).

**Instead:** Delete host javascripts/ and stylesheets/ entirely. The template provides them. The template's nav-state.js is a superset of the documentation project's (69 additional lines: scroll persistence, active-link highlighting, expand/collapse persistence).

### Anti-Pattern 3: Skipping the Host mkdocs.yml

**What:** Attempting to use gendoc-template/mkdocs.yml directly (like GeniusCogntiveSystem does) without accounting for the host's custom hooks.

**Why bad:** The `rewrite_gitbook_paths.py` hook would not execute. Gitbook-style URLs in content would not be rewritten, breaking internal links throughout the documentation.

**Instead:** Create and maintain a host mkdocs.yml that includes all template hooks (via gendoc-template/scripts/ paths) plus the host's custom hooks.

### Anti-Pattern 4: Running mkdocs from the Submodule Directory

**What:** `cd gendoc-template && mkdocs build`

**Why bad:** Docs resolve relative paths differently. The docs_dir would point to the wrong location. Hooks that resolve host_root (like load-gendoc-config.py) compute it as `../..` from the script, which works correctly regardless — but `gendoc.yml` would not be found at the expected location.

**Instead:** Always run mkdocs from the host project root: `mkdocs build -f mkdocs.yml`. The build scripts (cf-build.sh, cf-build.bat) ensure this.

## Migration Path: Current to Target Architecture

### What Gets Deleted

| File/Directory | Reason |
|---------------|--------|
| `javascripts/breadcrumbs.js` | Identical to gendoc-template's copy |
| `javascripts/external-links.js` | Identical to gendoc-template's copy |
| `javascripts/mathjax.js` | Identical to gendoc-template's copy |
| `javascripts/mermaid.js` | Identical to gendoc-template's copy |
| `javascripts/nav-state.js` | gendoc-template's version is a superset (+69 lines) |
| `stylesheets/extra.css` | Replaced by gendoc-template's theme.css (includes Ask AI styles) |
| Entire `javascripts/` directory | All files provided by gendoc-template + new ask/ directory |
| Entire `stylesheets/` directory | Provided by gendoc-template |
| `mkdocs.yml` (old) | Replaced by new host mkdocs.yml referencing submodule scripts |

### What Gets Created

| File | Content |
|------|---------|
| `gendoc.yml` | Copied from gendoc-template/gendoc.yml.example, customized for docs.gnus.ai |
| `mkdocs.yml` (new) | Template-equivalent mkdocs.yml with gendoc-template/script paths + host hook |
| `.gitmodules` entry | `[submodule "gendoc-template"]` pointing at the gendoc-template repo |

### What Gets Modified

| File | Change |
|------|--------|
| `scripts/cf-build.sh` | Run mkdocs with `-f mkdocs.yml` (host config); venv in `gendoc-template/.venv`; build-llms.py from submodule; rely on submodule for init/update |
| `scripts/cf-build.bat` | Same changes as cf-build.sh |
| `scripts/build_llms.py` | May be replaced by gendoc-template/scripts/build-llms.py if the template version is a superset; otherwise kept |
| `requirements.txt` | Align with gendoc-template/requirements.txt (remove mkdocs-redirects, mkdocs-section-index, mkdocs-exclude if not needed; add pyyaml) |

### What Stays (Unchanged)

| File/Directory | Reason |
|---------------|--------|
| `docs/` (gitbook submodule) | Content — out of scope for refactoring |
| `sg-docs/` (submodule) | SuperGenius Doxygen config — unchanged |
| `SUMMARY_EXT.md` | Nav structure — unchanged |
| `scripts/rewrite_gitbook_paths.py` | Host-specific hook — kept |
| `scripts/build_navigation.py` | Host-specific nav generation — kept |
| `scripts/doxybook.json` | Host-specific doxybook2 config — kept |
| `scripts/cf-build-deploy.sh` | Deployment script — unchanged |
| `scripts/cf-build-deploy.bat` | Deployment script — unchanged |

## Scalability Considerations

| Concern | Current | Target |
|---------|---------|--------|
| Template updates | Manual copy of changes between projects | git pull in submodule, update host mkdocs.yml if hooks changed |
| Adding new projects | Clone and customize entire build infrastructure | Add submodule, copy gendoc.yml, customize |
| Custom hooks | Trivial (add to mkdocs.yml hooks list) | Trivial (add to host mkdocs.yml hooks list + gendoc-template/ prefix for template hooks) |
| CSS changes | Edit project's extra.css | Edit gendoc-template's theme.css (shared) or add project-specific CSS file |
| JS changes | Edit project's copy | Edit gendoc-template's copy (shared); template nav-state.js already has more features |
| Ask AI widget | Not present | Enabled via gendoc.yml llms.ask; widget JS compiled from submodule TypeScript |

## Build Order (Dependencies Between Refactoring Steps)

```
Step 1: Add gendoc-template submodule
    │
    │  (Prerequisite for all subsequent steps)
    │
    ├──► Step 2: Create gendoc.yml
    │       │
    │       │  (Needed by load-gendoc-config.py hook)
    │       │
    │       ├──► Step 3: Create new host mkdocs.yml
    │       │       │
    │       │       │  (References gendoc-template scripts; needs gendoc.yml for load-gendoc-config)
    │       │       │
    │       │       ├──► Step 4: Delete host javascripts/ and stylesheets/
    │       │       │       │
    │       │       │       │  (Safe once mkdocs.yml references template-provided assets)
    │       │       │       │
    │       │       │       └──► Step 5: Update cf-build.sh and cf-build.bat
    │       │       │               │
    │       │       │               │  (Depends on mkdocs.yml being in place)
    │       │       │               │
    │       │       │               └──► Step 6: Enable Ask AI widget
    │       │       │                       │
    │       │       │                       │  (Requires build scripts working with submodule)
    │       │       │                       │
    │       │       │                       └──► Step 7: Verify build produces identical output
    │       │       │
    │       │       └──► [Can run in parallel with Step 5]
    │       │
    │       └──► [Can run in parallel with Step 3]
    │
    └──► [Must complete before all other steps]
```

**Critical dependency chain:** Step 1 (submodule) is the hard prerequisite. Steps 2 and 3 can partially overlap (gendoc.yml values inform mkdocs.yml). Steps 4, 5, and 6 SHOULD be sequential to isolate failures — each is independently verifiable.

**Verification gates:**
- After Step 3: `mkdocs build -f mkdocs.yml` succeeds (ignore missing JS/CSS)
- After Step 4: `mkdocs build -f mkdocs.yml` succeeds with correct JS/CSS from template
- After Step 5: `scripts/cf-build.sh` succeeds full pipeline
- After Step 6: Ask AI widget appears on built pages
- After Step 7: Diff old site/ vs new site/ — content identical (CSS/JS may differ due to template additions)

## Sources

- `documentation/mkdocs.yml` — Current build configuration (read directly)
- `documentation/scripts/cf-build.sh` — Current build script (read directly)
- `documentation/scripts/cf-build.bat` — Current Windows build script (read directly)
- `documentation/.gitmodules` — Current submodule configuration (read directly)
- `documentation/requirements.txt` — Current Python dependencies (read directly)
- `GeniusCogntiveSystem/gendoc-template/mkdocs.yml` — Template mkdocs configuration (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/gendoc.yml.example` — Full configuration schema reference (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/load-gendoc-config.py` — Config injection hook (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/clean-nav.py` — Nav URL rewriting hook (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/copy-assets.py` — Asset mirroring hook (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/build.sh` — Full build pipeline (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/build-widget.sh` — Ask widget compilation (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc-template/scripts/setup.sh` — Project initialization (read directly) — HIGH confidence
- `GeniusCogntiveSystem/gendoc.yml` — Reference gendoc.yml (read directly) — HIGH confidence
- File comparison (md5): breadcrumbs.js, external-links.js, mathjax.js, mermaid.js confirmed identical between host and template — HIGH confidence
- File diff: nav-state.js — template is a superset (+69 lines: scroll persistence, active-link highlighting) — HIGH confidence
- File comparison: extra.css vs theme.css — shared GNUS brand palette, template adds Ask AI drawer styles — HIGH confidence
