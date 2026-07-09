# Requirements: GNUS.AI Documentation Refactoring

## v1 Requirements

### Submodule & Configuration (SUBMOD)

- [ ] **SUBMOD-01**: Add `gendoc-template` as a git submodule pinned to the same commit as GeniusCogntiveSystem (`fc99df9e`)
- [ ] **SUBMOD-02**: Create `gendoc.yml` at project root with project metadata (name: "GNUS.AI Docs", number, logo, brief), paths (handwritten_docs: "docs"), mkdocs settings, and navigation sections
- [ ] **SUBMOD-03**: Update project `mkdocs.yml` to use gendoc-template hooks (`gendoc-template/scripts/load-gendoc-config.py`, `gendoc-template/scripts/clean-nav.py`, `gendoc-template/scripts/copy-assets.py`) while preserving the host-specific `scripts/rewrite_gitbook_paths.py` hook
- [ ] **SUBMOD-04**: Set `source_references: []` in gendoc.yml (this is a docs-only site with pre-generated API reference)

### Asset Migration (ASSET)

- [ ] **ASSET-01**: Delete host `javascripts/` directory (all 5 JS files confirmed identical or superseded by submodule versions)
- [ ] **ASSET-02**: Replace `stylesheets/extra.css` reference with `gendoc-template/stylesheets/theme.css` in mkdocs.yml (theme.css is a strict superset — same GNUS.AI brand palette plus Ask AI drawer styles)
- [ ] **ASSET-03**: Update `requirements.txt` to defer to `gendoc-template/requirements.txt` (submodule version is the superset adding `pyyaml>=6.0`)
- [ ] **ASSET-04**: Remove vestigial `docs/javascripts → ../javascripts/` symlink (copy-assets.py populates site dir at build time)
- [ ] **ASSET-05**: Verify `mkdocs-redirects` dependency is added to build pipeline (present in current requirements.txt, not in submodule's)

### Build Scripts (BUILD)

- [ ] **BUILD-01**: Update `cf-build.sh` to install dependencies from `gendoc-template/requirements.txt` and use submodule-relative paths
- [ ] **BUILD-02**: Update `cf-build.bat` with equivalent Windows changes
- [ ] **BUILD-03**: Preserve the custom SuperGenius Doxygen + doxybook2 pipeline in build scripts (gendoc-template's `build.sh` cannot replace `cf-build.sh` — fundamentally different pipeline)
- [ ] **BUILD-04**: Replace host `scripts/build_llms.py` with `gendoc-template/scripts/build_llms.py` (template version is a 139-line superset)
- [ ] **BUILD-05**: Create `llms-meta.json` for editorial metadata (required by the llms.txt generation pipeline)

### Ask AI Widget (ASKAI)

- [ ] **ASKAI-01**: Enable `llms.ask` in `gendoc.yml` — set `enabled: true`, `endpoint: "https://ask.gnus.ai/api/ask"` (shared worker with GeniusCogntiveSystem)
- [ ] **ASKAI-02**: Add `allowed_origins: ["https://docs.gnus.ai"]` to ask config
- [ ] **ASKAI-03**: Add `gendoc-template/javascripts/ask/main.js` (type: module) to `extra_javascript` in mkdocs.yml
- [ ] **ASKAI-04**: Verify `ask-config.json` is generated correctly during build

### Verification (VERIFY)

- [ ] **VERIFY-01**: Site builds successfully with zero errors from `mkdocs build`
- [ ] **VERIFY-02**: All existing page URLs are unchanged (no broken links, no redirect regressions)
- [ ] **VERIFY-03**: GitBook-syntax pages render correctly (`{% embed %}`, `{% hint %}`, cover page meta, GitBook math syntax)
- [ ] **VERIFY-04**: Mermaid diagrams, MathJax equations, breadcrumbs, external links, and nav state all function identically
- [ ] **VERIFY-05**: Ask AI widget (floating "Ask" button + chat drawer) appears and functions on all pages
- [ ] **VERIFY-06**: Site appearance is visually identical to pre-refactoring build (brand colors, typography, spacing)
- [ ] **VERIFY-07**: Mobile responsive layout is unchanged
- [ ] **VERIFY-08**: Update `DOCUMENTATION_CHANGES.md` with refactoring summary

## v2 Requirements (Deferred)

(None — this is a targeted refactoring. All scope is v1.)

## Out of Scope

- Content changes to documentation pages — content stays exactly as-is
- Changing the theme or visual design of the site
- Adding new documentation sections or pages
- Changing the deployment pipeline (Cloudflare Pages)
- Refactoring the API reference generation (Doxygen → doxybook2 pipeline for SuperGenius)
- Modifying the gendoc-template submodule itself
- Changing the docs (gitbook) or sg-docs submodules
- Adding new Cloudflare Worker — uses existing shared worker at `ask.gnus.ai`
- Any C++ code changes in sibling projects

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| SUBMOD-01 through SUBMOD-04 | Phase 1 | — Pending |
| ASSET-01 through ASSET-05 | Phase 2 | — Pending |
| BUILD-01 through BUILD-05 | Phase 3 | — Pending |
| ASKAI-01 through ASKAI-04 | Phase 4 | — Pending |
| VERIFY-01 through VERIFY-08 | Phase 5 | — Pending |

## Definition of Done

1. `gendoc-template` is a tracked git submodule
2. `gendoc.yml` exists at project root and is valid
3. `mkdocs.yml` references submodule hooks + host-specific `rewrite_gitbook_paths.py`
4. No duplicate JS/CSS assets in host project
5. `cf-build.sh` and `cf-build.bat` produce a successful build
6. Ask AI widget appears on all pages
7. Site is visually and functionally identical to pre-refactoring build
8. All verification checks pass

---
*Last updated: 2026-07-08 — auto-generated from research synthesis*
