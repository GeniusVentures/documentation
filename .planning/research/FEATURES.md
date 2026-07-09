# Feature Landscape: Documentation Site Refactoring with gendoc-template

**Domain:** MkDocs + Material documentation site with existing custom assets and GitBook history
**Researched:** 2026-07-08
**Confidence:** HIGH (all findings verified by direct file comparison against both codebases)

---

## Table Stakes

Features that must continue working identically post-refactoring. Missing = site is broken.

| Feature | Why Expected | Provided By Submodule? | Complexity | Notes |
|---------|--------------|------------------------|------------|-------|
| Mermaid diagram rendering | 50+ diagrams across architecture/SuperGenius docs | YES -- `javascripts/mermaid.js` | Low | MD5-identical files. Remove local copy. |
| MathJax equation rendering | Math content in technical docs | YES -- `javascripts/mathjax.js` | Low | MD5-identical files. Remove local copy. |
| External link handling | Opens external links in new tab with indicator | YES -- `javascripts/external-links.js` | Low | MD5-identical files. Remove local copy. |
| Breadcrumb navigation | Path breadcrumbs in nav header | YES -- `javascripts/breadcrumbs.js` | Low | MD5-identical files. Remove local copy. |
| Navigation state persistence | Sidebar expansion state survives page loads with animation | YES -- `javascripts/nav-state.js` (enhanced) | Low | Submodule version is a **superset**: adds scroll position persistence, active-link highlighting for anchor navigation, and hashchange handling. Migration is an upgrade. |
| GNUS.AI brand colors | Cyan-blue palette (`#0096c7` ramp) in light/dark modes | YES -- `stylesheets/theme.css` | Low | Submodule's `theme.css` is a **superset** of the site's `extra.css`. Same brand variables, plus Ask AI drawer CSS variables and duplicate-nav-title suppression. Remove local `extra.css`. |
| Search (Material) | Full-text search with suggestions/highlight | YES -- Material theme + `literate-nav` plugin | Low | Submodule's `mkdocs.yml` enables same search features. No config change needed. |
| Mermaid + superfences | Mermaid fenced code blocks via `pymdownx.superfences` | YES -- submodule `mkdocs.yml` | Low | Identical `markdown_extensions` config. |
| MathJax via arithmatex | `pymdownx.arithmatex` with `generic: true` | YES -- submodule `mkdocs.yml` + `mathjax.js` | Low | Identical config. CDN MathJax loaded via `extra_javascript`. |
| Light/dark palette toggle | Auto-detect + manual switch with custom scheme colors | YES -- submodule `mkdocs.yml` + `theme.css` | Low | Identical palette config (`default`/`slate`, `primary: custom`, `accent: custom`). |
| GitBook content migration hooks | Rewrite GitBook syntax (`{% embed %}`, `{% file %}`, `{% hint %}`, `$$...$$` math, cover images) | **NO** -- `scripts/rewrite_gitbook_paths.py` is site-specific | **Medium** | This hook is unique to the documentation site's GitBook migration history. Must be preserved as a custom hook in the new `mkdocs.yml`. |
| Gzip search shim injection | Injects client-side decompression for gzipped search index | **NO** -- part of `rewrite_gitbook_paths.py` `on_post_build` | Low | The `_SEARCH_GZIP_SHIM` injected into HTML pages. Must be preserved; it lives in the existing `rewrite_gitbook_paths.py`. |
| DealCard/DocCard custom components | Custom styled cards in documentation pages | N/A -- handled by inline HTML/CSS in content | None | These are in the markdown content itself, not in build infrastructure. No migration risk. |
| Literate-nav with SUMMARY_EXT.md | Sidebar navigation built from curated SUMMARY_EXT.md | YES -- submodule `mkdocs.yml` enables `literate-nav` + `build-navigation.py` generates it | **Medium** | The site currently has a hand-maintained `SUMMARY_EXT.md`. The submodule generates it from `gendoc.yml` `navigation.sections`. Content parity must be verified. |
| Directory URLs | Clean URLs without `.html` extension | YES -- `use_directory_urls: true` in `gendoc.yml` > `mkdocs.use_directory_urls` | Low | Identical config. |

---

## Differentiators

New capabilities gained through migration. Not expected by current users, but valuable.

| Feature | Value Proposition | Provided By | Complexity | Notes |
|---------|-------------------|-------------|------------|-------|
| **Ask AI widget** | Floating "Ask" button + chat drawer that answers questions from documentation content using RAG | Submodule: `javascripts/ask/` + Cloudflare Worker + `ask-config.json` | **Medium** | Core motivation for refactoring. Requires: (1) `llms.ask.enabled: true` in gendoc.yml, (2) shared endpoint `https://ask.gnus.ai/api/ask` (already deployed for GeniusCogntiveSystem), (3) `ask-config.json` generated into site output, (4) `ask/main.js` loaded as ES module in `extra_javascript`. |
| **llms.txt generation** | Standardized agent catalog at `/llms.txt` + audience-specific catalogs + `/llms-full.txt` full corpus | Submodule: `scripts/build-llms.py` | **Low-Medium** | Post-build step produces llms.txt, llms-technical.txt, llms-full.txt from SUMMARY.md docs. The site already has `scripts/build_llms.py` but the submodule version is more mature with `llms-meta.json` editorial workflow, Google Docs fetching, and source-reference integration. Existing llms.txt setup should be migrated to submodule version. |
| **Audience-specific catalogs** | Separate llms-*.txt files per audience (technical, sales, investors) for targeted AI consumption | Submodule: `llms.audiences` config in gendoc.yml | Low | Configured entirely in gendoc.yml. Each catalog filters docs by category tags from `llms-meta.json`. |
| **Scroll position persistence** | Sidebar scroll position saved and restored across page loads | Submodule: enhanced `nav-state.js` (`bindScrollPersist`) | None | Comes free with submodule's enhanced nav-state.js. Session storage; no config needed. |
| **Anchor-aware active link highlighting** | Same-page anchor clicks highlight the active nav item without full page reload | Submodule: enhanced `nav-state.js` (`updateActiveLink` + `hashchange` listener) | None | Comes free with submodule's enhanced nav-state.js. |
| **Related catalogs** | Cross-reference other GNUS.AI documentation sites from llms.txt | Submodule: `llms.related_catalogs` in gendoc.yml | Low | Can link to `https://gcs.gnus.ai/llms.txt` for GeniusCogntiveSystem docs. |
| **Google Docs into corpus** | Fetch public Google Docs as markdown and include in llms.txt | Submodule: `llms.google_docs` in gendoc.yml | Low | Optional. Useful for architecture overviews, business docs. |

---

## Anti-Features

Features to explicitly NOT change during this refactoring.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Content changes | Risk of broken links, SEO impact, user confusion | All markdown in `docs/` stays exactly as-is. Content is in git submodules (`docs`, `sg-docs`) and is not part of this refactoring. |
| URL structure changes | Existing bookmarks, search engine indexing, cross-references from GCS docs | Keep `use_directory_urls: true`, same `docs_dir`, same page paths. Any MkDocs config change that would alter URL generation must be tested. |
| Theme/visual design changes | Users familiar with current appearance | Same Material theme, same palette, same features. The submodule's `theme.css` has identical brand colors (verified: GNUS.AI cyan-blue palette). |
| Doxygen/doxybook2 pipeline | Existing API reference generation for SuperGenius | This pipeline (in `scripts/`) continues to work independently. The submodule's `build-source-reference.sh` is for C++ projects using the template; the docs site has its own Doxygen setup for documenting the SDK. |
| Cloudflare Pages deployment | Existing CI/CD pipeline | The submodule provides `deploy.sh` and `wrangler.toml` templates, but the site's existing `cf-build.sh`/`cf-build.bat` scripts can be updated rather than replaced. |
| GitBook `rewrite_gitbook_paths.py` hook | Essential for content correctness -- GitBook syntax still present in many pages | Preserve as a custom MkDocs hook. Register it alongside the submodule hooks in `mkdocs.yml`. |
| Gzip search shim | Local preview and non-Cloudflare deployments fail search without it | The `_SEARCH_GZIP_SHIM` injection in `on_post_build` must continue running. It currently lives in `rewrite_gitbook_paths.py` and should remain there. |

---

## Feature Dependencies

```
Ask AI Widget
├── llms.enabled: true (in gendoc.yml)
├── llms.site_url (in gendoc.yml)
├── llms.ask.enabled: true (in gendoc.yml)
├── llms.ask.endpoint (shared worker: https://ask.gnus.ai/api/ask)
├── ask-config.json generated by build-widget.sh (in site_dir)
├── ask/main.js loaded as ES module in extra_javascript
├── theme.css (Ask AI drawer CSS variables)
└── Cloudflare Worker already deployed (setup.sh; shared endpoint, no new worker needed)

llms.txt generation
├── llms.enabled: true (in gendoc.yml)
├── llms.site_url (in gendoc.yml)
├── llms.audiences (catalog definitions in gendoc.yml)
├── llms-meta.json (editorial metadata at project root)
├── SUMMARY.md or SUMMARY_EXT.md (source of truth for doc list)
└── build-llms.py runs post-build

Navigation (clean-nav.py)
├── navigation.indexes feature (in mkdocs.yml)
└── navigation.sections feature (in mkdocs.yml)

Navigation (build-navigation.py)
├── gendoc.yml navigation.sections config
├── index.md with link lists
└── No source_references (docs-only site)

copy-assets.py
├── Submodule javascripts/ and stylesheets/ exist
└── extra_javascript/extra_css in mkdocs.yml reference /javascripts/* and /stylesheets/*
```

---

## Migration Requirements Summary

### What the submodule provides (remove from site)

| Local Asset | Action | Reason |
|-------------|--------|--------|
| `javascripts/mermaid.js` | Remove | MD5-identical; submodule provides via copy-assets.py |
| `javascripts/mathjax.js` | Remove | MD5-identical; submodule provides via copy-assets.py |
| `javascripts/external-links.js` | Remove | MD5-identical; submodule provides via copy-assets.py |
| `javascripts/breadcrumbs.js` | Remove | MD5-identical; submodule provides via copy-assets.py |
| `javascripts/nav-state.js` | Remove | Submodule has enhanced version (superset -- scroll persistence, active-link highlighting) |
| `stylesheets/extra.css` | Remove | Submodule's `theme.css` is a superset (adds Ask AI drawer variables, duplicate-nav suppression) |
| `scripts/build_llms.py` | Remove (after migration) | Submodule provides enhanced version; migrate llms-meta.json setup |

### What the site must keep (not in submodule)

| Local Asset | Action | Reason |
|-------------|--------|--------|
| `scripts/rewrite_gitbook_paths.py` | **Preserve** as custom MkDocs hook | GitBook content migration -- unique to docs site. Contains: GitBook embed/tag/hint/file conversion, math delimiter rewriting, cover image injection, gzip search shim, nav filtering |
| `scripts/cf-build.sh` / `scripts/cf-build.bat` | **Update** (not remove) | Cloudflare Pages build orchestration. Update to use gendoc-template submodule paths rather than local scripts. |
| `scripts/doxybook.json` | Preserve | SuperGenius API reference Doxygen config |
| `docs/` (content) | Preserve as-is | All hand-written documentation |
| `.gitmodules` (existing submodules) | Preserve | `docs` (gitbook) and `sg-docs` submodules |
| `SUMMARY_EXT.md` | Keep during transition; may be replaced by build-navigation.py generation | Currently hand-maintained navigation list. Can be generated from gendoc.yml `navigation.sections` config. |

### What must be newly configured

| Item | Location | Purpose |
|------|----------|---------|
| `gendoc.yml` | Project root | Host project configuration (see gendoc.yml section below) |
| `mkdocs.yml` (updated) | Project root | Simplified to use submodule hooks + preserve custom hooks |
| `llms-meta.json` | Project root | Editorial metadata for llms.txt generation (descriptions, categories) |
| `gendoc-template` submodule | `.gitmodules` + `git submodule add` | The template submodule itself |

---

## gendoc.yml Configuration for docs.gnus.ai

This is a **docs-only site** (no source code to document), so many gendoc.yml sections are omitted or disabled.

```yaml
# gendoc.yml -- docs.gnus.ai documentation configuration
# docs-only site: no source_references, no doxygen pipeline

# ── Project identification ──────────────────────────────────────
project:
  name: "GNUS.AI Docs"
  number: "1.0"
  logo: "docs/gnus-ai-logo.png"
  brief: "The GNUS.AI Operating System -- technical documentation, architecture, and API reference"
  generator: false

# ── Paths (relative to project root) ───────────────────────────
paths:
  handwritten_docs: "docs"

# ── MkDocs configuration ────────────────────────────────────────
mkdocs:
  site_dir: "site"
  use_directory_urls: true
  strict: false

# ── Navigation ───────────────────────────────────────────────────
# docs-only: no source_references appended. navigation.sections
# determines what build-navigation.py writes into SUMMARY_EXT.md.
navigation:
  sections:
    - label: "About GNUS.AI"
      source_file: "index.md"
      extract_heading: "About GNUS.AI"

# ── Deploy (Cloudflare Pages) ───────────────────────────────────
deploy:
  cloudflare:
    pages_project_name: "gnus-ai-docs"
    compatibility_date: "2024-01-01"
    production_branch: "main"
    custom_domain: "docs.gnus.ai"

# ── LLMs / Ask AI ────────────────────────────────────────────────
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
      description: "Distributed cognitive platform -- ELM inference, swarm orchestration, verification, memory, and agent framework"
      audiences: [llms-technical.txt]

  # Ask AI: shares the existing ask.gnus.ai worker (no new deployment)
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

### Configuration notes:

1. **No `source_references`** -- docs.gnus.ai documents itself + the SDK (via existing Doxygen pipeline). It is not a C++/Python project being documented by the gendoc pipeline.

2. **No `doxygen` block** -- no code references to generate. The existing SuperGenius API reference continues via its own Doxygen + doxybook2 scripts.

3. **Ask AI shares the existing worker** (`https://ask.gnus.ai/api/ask`). No new Cloudflare Worker deployment needed. Just set the endpoint and the widget configures itself.

4. **`allowed_origins` must include `docs.gnus.ai`**. This is already configured in the GCS gendoc.yml and the worker already accepts both origins. No change needed on the worker side.

5. **`navigation.sections`** needs careful mapping of existing hand-written content structure. The `extract_heading` mechanism scopes link extraction to specific sections of index.md.

---

## Migration Risks by Feature

| Feature | Risk Level | Risk Description | Mitigation |
|---------|------------|------------------|------------|
| GitBook content hooks | **HIGH** | `rewrite_gitbook_paths.py` is complex (323 lines). It must continue working after being registered alongside submodule hooks. MkDocs hook ordering matters. | Register as the **first** `on_page_markdown` hook so it transforms content before other hooks process it. Test with a full site build. |
| SUMMARY_EXT.md generation | **MEDIUM** | The site currently has a hand-curated `SUMMARY_EXT.md`. The submodule's `build-navigation.py` generates one from `gendoc.yml` `navigation.sections`. If the generation misses entries, pages disappear from the sidebar. | Run a diff between generated and current SUMMARY_EXT.md. Add missing `navigation.sections` entries. |
| Nav-state.js upgrade | **MEDIUM** | The submodule's version has new code paths (scroll persistence, active-link highlighting). Potential interaction with existing nav behavior. | Manual testing: sidebar expansion persistence, anchor navigation, scroll position across page loads. The old version is battle-tested; the new version must match. |
| Ask AI worker CORS | **MEDIUM** | The shared worker must allow `docs.gnus.ai` as an origin. | Already configured in GCS's gendoc.yml (`allowed_origins` includes both domains). No worker-side change needed. |
| llms-meta.json migration | **MEDIUM** | The site has an existing `scripts/build_llms.py` with its own metadata format. Transitioning to the submodule version requires creating `llms-meta.json`. | Run the submodule's `build-llms.py` -- it auto-populates `llms-meta.json` with discovered entries. Then run `/update-catalogs` for editorial pass. |
| `extra_javascript` / `extra_css` paths | **LOW** | The submodule's `mkdocs.yml` references `theme.css` not `extra.css`, and adds `ask/main.js`. The site's `mkdocs.yml` must adopt these paths. | Update `extra_css` to `/stylesheets/theme.css` and add `ask/main.js` as ES module. Remove old `extra.css` reference. |
| Build script updates | **LOW** | `cf-build.sh` references local script paths. Must be updated for submodule paths. | Mechanical update: change `scripts/` to `gendoc-template/scripts/` where the submodule provides equivalents. Or call `gendoc-template/scripts/build.sh` directly (which orchestrates everything). |
| Doxybook pipeline | **LOW** | Existing `scripts/doxybook.json` and Doxygen workflow for SuperGenius API reference must continue working. Not affected by gendoc-template. | The submodule's `build-source-reference.sh` is not used for this site. Existing pipeline is separate. |

---

## Feature Parity Verification Checklist

Post-migration, verify each of these renders identically to the current site:

- [ ] Mermaid diagrams render in both light and dark modes
- [ ] MathJax equations render correctly (inline $$...$$ and block)
- [ ] External links open in new tabs with indicator icon
- [ ] Breadcrumb path shows correctly on all page depths
- [ ] Sidebar expansion state persists across page loads
- [ ] Light/dark mode toggle works and brand colors match
- [ ] Search returns expected results
- [ ] GitBook-imported content renders correctly (embed tags, hint blocks, file blocks, cover images)
- [ ] All URLs match current production (directory URLs, no `.html`)
- [ ] Sidebar navigation matches current structure
- [ ] Gzip search shim is injected into HTML pages (search works in local preview)

---

## Sources

- Direct file comparison (MD5 hashing) of all javascripts between `/documentation/javascripts/` and `GeniusCogntiveSystem/gendoc-template/javascripts/` -- HIGH confidence
- Direct file comparison of stylesheets (`extra.css` vs `theme.css`) -- HIGH confidence
- `gendoc-template/mkdocs.yml` -- submodule's MkDocs configuration -- HIGH confidence
- `gendoc-template/scripts/` -- all submodule scripts read and analyzed -- HIGH confidence
- `gendoc-template/javascripts/ask/` -- Ask AI widget source code -- HIGH confidence
- `gendoc-template/gendoc.yml.example` -- full configuration schema -- HIGH confidence
- `GeniusCogntiveSystem/gendoc.yml` -- reference implementation with Ask AI enabled -- HIGH confidence
- `documentation/mkdocs.yml` -- current site configuration -- HIGH confidence
- `documentation/scripts/rewrite_gitbook_paths.py` -- custom GitBook migration hook -- HIGH confidence
- `.planning/PROJECT.md` -- project scope and requirements -- HIGH confidence
