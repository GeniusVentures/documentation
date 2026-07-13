# Roadmap: GNUS.AI Documentation Refactoring

## Overview

The documentation site (`docs.gnus.ai`) transitions from embedded build infrastructure to a consumer of the `gendoc-template` git submodule — completing the circle after the template was originally extracted from this codebase. This is a hybrid pattern: the host keeps its own `mkdocs.yml` for the GitBook content hook (`rewrite_gitbook_paths.py`), while shared assets (JS, CSS, Python deps) come from the submodule. The primary motivation is enabling the Ask AI widget on all pages. Five sequential phases move from structural foundation through asset cleanup, build script modernization, widget enablement, and end with full parity verification.

## Phases

- [ ] **Phase 1: Template Integration** — Add submodule, create gendoc.yml, update mkdocs.yml to reference template hooks
- [ ] **Phase 2: Asset Cleanup** — Delete duplicate JS/CSS, switch to submodule-provided assets and dependencies
- [ ] **Phase 3: Build Script Refactoring** — Update cf-build.sh/.bat for submodule paths while preserving Doxygen pipeline
- [ ] **Phase 4: Ask AI Widget Enablement** — Enable llms.ask in gendoc.yml, add widget JS module, verify ask-config.json
- [ ] **Phase 5: Full Verification** — Parity check against pre-refactoring build, verify all 8 VERIFY criteria
- [ ] **Phase 6: Theme Loader** — Add load-theme.py hook for dynamic theme CSS selection, two built-in presets, BYO custom theme support
- [ ] **Phase 7: Cloudflare Pages Deploy Fix** — [gendoc, gendoc-template] Gzip JSON assets for 25 MiB limit, frontend .json.gz handling with decompression fallback, production branch deploys (INSERTED)

## Phase Details

### Phase 1: Template Integration
**Goal**: The project is structurally integrated with gendoc-template — submodule is tracked, gendoc.yml exists, and mkdocs.yml references template hooks alongside the host-specific GitBook hook.
**Depends on**: Nothing (first phase)
**Requirements**: SUBMOD-01, SUBMOD-02, SUBMOD-03, SUBMOD-04
**Success Criteria** (what must be TRUE):
  1. `gendoc-template/` directory exists at project root as a tracked git submodule, pinned to commit `fc99df9e`
  2. `gendoc.yml` exists at project root with valid project metadata (name, number, logo, brief), paths (`handwritten_docs: "docs"`), mkdocs settings, and llms configuration including ask AI settings
  3. `mkdocs.yml` references gendoc-template hooks (`load-gendoc-config.py`, `clean-nav.py`, `copy-assets.py`) alongside the host-specific `rewrite_gitbook_paths.py` hook
  4. Running `mkdocs build -f mkdocs.yml` completes without errors (content may render with raw GitBook syntax at this stage — assets are not yet migrated)
**Plans**: 3 plans

### Phase 2: Asset Cleanup
**Goal**: All duplicate assets removed from host project. Site builds and renders using template-provided JavaScript, CSS, and Python dependencies exclusively.
**Depends on**: Phase 1
**Requirements**: ASSET-01, ASSET-02, ASSET-03, ASSET-04, ASSET-05
**Success Criteria** (what must be TRUE):
  1. `javascripts/` directory no longer exists at project root — all five JS files (breadcrumbs, external-links, mathjax, mermaid, nav-state) are served from gendoc-template via `copy-assets.py`
  2. Site renders with correct GNUS.AI brand colors, typography, and spacing using `theme.css` from the submodule — no visual regression compared to pre-refactoring build
  3. Mermaid diagrams, MathJax equations, breadcrumbs, external links, and nav state all function using template-provided JavaScript
  4. Python dependencies resolve correctly — `pyyaml>=6.0` is available from `gendoc-template/requirements.txt`, `mkdocs-redirects` is preserved for the redirects plugin
**Plans**: 3 plans
**UI hint**: yes

### Phase 3: Build Script Refactoring
**Goal**: `cf-build.sh` and `cf-build.bat` produce a complete, successful build using submodule-relative paths while preserving the custom SuperGenius Doxygen + doxybook2 pipeline.
**Depends on**: Phase 2
**Requirements**: BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05
**Success Criteria** (what must be TRUE):
  1. Running `scripts/cf-build.sh` produces a complete `site/` directory with all documentation pages and the SuperGenius API reference
  2. The SuperGenius Doxygen + doxybook2 pipeline runs successfully within the build script, generating API reference pages with correct category navigation (Classes, Files, Namespaces)
  3. `llms.txt` and audience-specific catalogs are generated in the site directory using the template's `build-llms.py`
  4. `llms-meta.json` exists at project root and is consumed by the llms generation pipeline
  5. Running `scripts/cf-build.bat` produces equivalent output on Windows
**Plans**: 3 plans

### Phase 4: Ask AI Widget Enablement
**Goal**: The Ask AI floating button and chat drawer appear and function on every documentation page, powered by the shared `ask.gnus.ai` worker.
**Depends on**: Phase 3
**Requirements**: ASKAI-01, ASKAI-02, ASKAI-03, ASKAI-04
**Success Criteria** (what must be TRUE):
  1. Every documentation page loads the Ask AI widget — a floating "Ask" button is visible in the bottom-right corner
  2. Clicking "Ask" opens a chat drawer where users can type questions and receive AI-generated responses powered by documentation content
  3. `ask-config.json` is generated in the site directory during build with correct endpoint (`https://ask.gnus.ai/api/ask`), allowed origins, and provider configuration
  4. The Ask AI widget functions correctly on both light and dark mode, desktop and mobile viewports
**Plans**: 3 plans
**UI hint**: yes

### Phase 5: Full Verification
**Goal**: Confirm the refactored site is functionally and visually identical to the pre-refactoring build, Ask AI widget functions on all pages, and the migration is documented.
**Depends on**: Phase 4
**Requirements**: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04, VERIFY-05, VERIFY-06, VERIFY-07, VERIFY-08
**Success Criteria** (what must be TRUE):
  1. All existing page URLs are unchanged — no broken links, no redirect regressions, directory URLs preserved
  2. GitBook-syntax pages render correctly — embed tags, hint blocks, cover page meta, and GitBook math syntax all convert to valid HTML
  3. Site appearance is visually identical to pre-refactoring build in both light and dark modes, on desktop and mobile — same brand colors, typography, spacing
  4. Mermaid diagrams, MathJax equations, breadcrumbs, external links, and nav state all function identically to pre-refactoring build
  5. `DOCUMENTATION_CHANGES.md` contains a summary of the refactoring including what was added (submodule, gendoc.yml, Ask AI widget), removed (duplicate JS/CSS, old build files), and modified (mkdocs.yml, build scripts)
**Plans**: 3 plans
**UI hint**: yes

### Phase 6: Theme Loader
**Goal**: The gendoc-template supports dynamic theme CSS selection via a `load-theme.py` MkDocs hook. Two built-in presets (default/protocol) are included, the old hardcoded `stylesheets/theme.css` is removed, and host projects can supply a custom theme via `gendoc.yml` without modifying the submodule.
**Depends on**: Phase 5 (verified baseline)
**Requirements**: THEME-01, THEME-02, THEME-03, THEME-04, THEME-05, THEME-06
**Success Criteria** (what must be TRUE):
  1. `scripts/load-theme.py` is registered as a MkDocs hook in `mkdocs.yml` and selects the correct CSS at build time based on `gendoc.yml` `theme.name`
  2. Two built-in presets exist: `default` (original cyan look, zero-change fallback) and `protocol` (new design)
  3. `stylesheets/theme.css` is deleted — `load-theme.py` dynamically sets `extra_css` instead
  4. `stylesheets/base.css` provides shared foundation styles; `themes/default.css` and `themes/protocol.css` provide the preset overrides
  5. `scripts/copy-assets.py` is updated to include `themes/` in its `ASSET_DIRS` tuple
  6. Host projects can set `theme.name: "custom"` + `theme.custom_css: "my-theme.css"` in `gendoc.yml` to load a project-specific theme — `load-theme.py` copies the file into `themes/custom.css` at build time
  7. `gendoc.yml.example` and host `gendoc.yml` document the `theme:` block with `name` (default/protocol/custom) and optional `custom_css`
  8. `themes/custom.css` is listed in `gendoc-template/.gitignore` to prevent accidental commits
**Plans**: 3 plans
**UI hint**: yes

### Phase 7: Cloudflare Pages Deploy Fix
**Goal**: The gendoc-template deployment pipeline handles Cloudflare Pages' 25 MiB per-file upload limit with a uniform gzip strategy: all `.json` files become `.json.gz`, raw `.json` deleted pre-upload. Every consumer — frontend widget, worker, AND MkDocs search — handles `.json.gz` with transparent decompression fallback. Deploy branch is configurable via `gendoc.yml`. All changes scoped to gendoc-template submodule (gendoc workstream).
**Depends on**: Phase 6 (deployment infrastructure from Phase 4-6)
**Scope**: gendoc-template submodule, gendoc workstream only
**Requirements**: DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04
**Success Criteria** (what must be TRUE):
  1. All `.json` files in the site directory are uniformly gzipped to `.json.gz` and raw `.json` deleted pre-upload — no in-place gzip, no `_headers` hack, no special cases
  2. MkDocs search is overridden via pre-bundle `extra_javascript` fetch interception (NOT Service Worker — SW requires HTTPS, breaks local `mkdocs serve`). Redirects `search_index.json` → `search_index.json.gz` with magic-byte + `DecompressionStream`, same pattern as `config.ts`
  3. Frontend `config.ts` fetches `/ask-config.json.gz` with gzip magic-byte detection and `DecompressionStream` fallback; falls back to `/ask-config.json` for local dev
  4. Worker fetches `.json.gz` with `.json` fallback (`catalog.ts`, `normalizer.ts`) — already implemented, no changes needed
  5. `deploy.sh` restores all raw `.json` files after deploy for local development compatibility
  6. Deploy branch is read from `gendoc.yml` (`deploy.cloudflare.branch`, default `"main"`) — not hardcoded
  7. `deploy.cloudflare.gzip_json` toggle (default `true`) controls deploy.sh gzip behavior only — consumers always try `.json.gz` with magic-byte detection + `.json` fallback regardless of config
**Plans**: 3 plans

Plans:
- [ ] 07-01-PLAN.md — Uniform JSON gzip in deploy.sh, remove _headers and in-place gzip, add gendoc.yml-driven branch and gzip_json config
- [ ] 07-02-PLAN.md — Service Worker override for MkDocs Material search fetching search_index.json.gz with gzip decompression
- [ ] 07-03-PLAN.md — Update gendoc.yml.example and host gendoc.yml with deploy.cloudflare.branch and gzip_json fields

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Template Integration | 0/TBD | Not started | - |
| 2. Asset Cleanup | 0/TBD | Not started | - |
| 3. Build Script Refactoring | 0/TBD | Not started | - |
| 4. Ask AI Widget Enablement | 0/TBD | Not started | - |
| 5. Full Verification | 0/TBD | Not started | - |
| 6. Theme Loader | 0/TBD | Not started | - |
| 7. Cloudflare Pages Deploy Fix | 0/TBD | Not started | - |
