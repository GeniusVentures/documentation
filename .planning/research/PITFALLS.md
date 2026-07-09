# Domain Pitfalls

**Domain:** Documentation project refactoring — embedded build infrastructure to gendoc-template submodule
**Researched:** 2026-07-08

## Critical Pitfalls

Mistakes that cause rewrites, broken builds, or production regressions.

### Pitfall 1: Losing the `rewrite_gitbook_paths.py` Hook During mkdocs.yml Migration

**What goes wrong:** The documentation project's content was originally migrated from GitBook. The `scripts/rewrite_gitbook_paths.py` hook (registered in the current `mkdocs.yml` hooks list) converts GitBook-specific syntax that still exists in the hand-written docs: `{% embed %}`, `{% hint %}`, `{% file %}`, `{% content-ref %}`, GitBook inline/block math (`$$...$$`), cover page meta injection, description subtitle injection, `.gitbook/assets/` path rewriting, and raw Doxygen tag stripping. The gendoc-template does NOT include this hook. If mkdocs.yml is replaced or simplified without carrying this hook over, dozens of pages will render with broken, raw GitBook syntax visible to users.

**Why it happens:** The gendoc-template's mkdocs.yml only lists three hooks (`load-gendoc-config.py`, `clean-nav.py`, `copy-assets.py`). A naive copy-paste of the template's hook list will drop `rewrite_gitbook_paths.py`. GeniusCogntiveSystem never had this hook because its content was never GitBook-origin, so its transition provides no warning about this loss.

**Consequences:** Visible raw `{% embed url="..." %}`, `{% hint style="info" %}` blocks, broken `$$math$$` rendering, broken `.gitbook/assets/` image links, raw Doxygen `\brief`, `\author`, `\file` tags appearing on SuperGenius API pages. Site appears broken to all users.

**Prevention:** The new `mkdocs.yml` must include ALL of these hooks:
```yaml
hooks:
  - scripts/load-gendoc-config.py       # from gendoc-template
  - scripts/clean-nav.py                # from gendoc-template
  - scripts/copy-assets.py              # from gendoc-template
  - scripts/rewrite_gitbook_paths.py    # PROJECT-SPECIFIC — MUST NOT BE DROPPED
```

**Detection:** After any build, spot-check pages known to contain GitBook syntax (the "GNUS.AI Network vs Centralized" comparison page, any page with `cover` frontmatter, SuperGenius API pages with Doxygen tags). If raw `{% %}` tags or `\brief` strings appear in rendered HTML, the hook was dropped.

---

### Pitfall 2: Asset File Collision — Duplicate JavaScript Between Project and Submodule

**What goes wrong:** The documentation project has five JavaScript files in `javascripts/` at the project root: `breadcrumbs.js`, `external-links.js`, `mathjax.js`, `mermaid.js`, `nav-state.js`. The gendoc-template provides identical copies of all five in `gendoc-template/javascripts/`. Both are registered via `extra_javascript` in mkdocs.yml using absolute paths like `/javascripts/nav-state.js`. When MkDocs resolves these paths, the `watch` directive and `copy-assets.py` hook can cause conflicts or double-loading depending on which directory is served.

**Why it happens:** These JS files were the ORIGIN of gendoc-template's copies (the template was extracted from this codebase). They have likely diverged slightly since extraction. If both the project-local `javascripts/` AND the submodule's `javascripts/` are present on disk, MkDocs may serve the wrong version, or the `copy-assets.py` hook may overwrite project-local files with submodule versions (or vice versa).

**Consequences:** Silent behavioral regressions — a newer version from gendoc-template might lack a local fix, or an older local copy might lack template improvements. The `nav-state.js` in particular has complex sidebar persistence and resize logic where a version mismatch would produce visible layout bugs.

**Prevention (GeniusCogntiveSystem's pattern):** GeniusCogntiveSystem has NO local `javascripts/` or `stylesheets/` directories. All assets come exclusively from `gendoc-template/javascripts/` and `gendoc-template/stylesheets/` via the `copy-assets.py` hook. The documentation project should follow this exact pattern:
1. Verify each of the five JS files matches between project and submodule
2. Delete `javascripts/` and `stylesheets/` from the project root
3. Update `mkdocs.yml` to reference the submodule paths (already identical — no path changes needed)
4. The `copy-assets.py` hook copies `gendoc-template/javascripts/` and `gendoc-template/stylesheets/` into `site/` at build time

**Detection:** After deleting project-local assets, run a diff of the rendered HTML's `<script>` and `<link>` tags against a pre-refactoring build. All JS/CSS paths should resolve identically. Use browser dev tools to confirm exactly one copy of each JS file loads (no 404s, no duplicate network requests).

---

### Pitfall 3: `extra.css` vs `theme.css` — Losing Brand Styling or Gaining Duplicate Styles

**What goes wrong:** The documentation project's `stylesheets/extra.css` was the original source from which gendoc-template's `stylesheets/theme.css` was extracted. The two files are structurally identical for the core styles (brand colors, sidebar sizing, GitBook image alignment). However, `theme.css` has ADDITIONAL styles the submodule added after extraction:
- Ask AI Drawer theme variables (`--ask-accent`, `--ask-drawer-bg`, etc.)
- `.md-nav__item--nested > .md-nav > .md-nav__title { display: none; }` (suppresses duplicate nav labels)
- `.md-content__inner { padding-bottom: 4rem; }` (content bottom spacing)
- `.md-logo img { filter: brightness(.5) saturate(20); }` (logo treatment)

If the project keeps referencing `extra.css` instead of switching to `theme.css`, the Ask AI widget won't have CSS variables for theming, duplicate nav title labels will appear, and the logo won't be styled. If the project deletes `extra.css` and switches to `theme.css` but `theme.css` is missing something only in `extra.css`, styling regresses.

**Why it happens:** The files originated from the same source but have diverged because gendoc-template continued evolving after extraction.

**Consequences:** Missing Ask AI widget styling (invisible or unstyled drawer), duplicate nav labels, improperly styled logo, or missing GitBook compatibility.

**Prevention:** 
1. Diff `extra.css` against `theme.css` to confirm NO project-specific styles exist only in `extra.css` (from the analysis above, `theme.css` is a strict superset)
2. Change `extra_css` in mkdocs.yml from `- /stylesheets/extra.css` to `- /stylesheets/theme.css`
3. Delete `stylesheets/extra.css` from the project root (the entire `stylesheets/` directory goes away)

**Detection:** Side-by-side visual comparison of the old and new builds. Check every page type: light mode, dark mode, mobile, API reference pages, pages with GitBook figures, pages with the Ask AI widget.

---

### Pitfall 4: Build Script Incompatibility — Project's Custom Doxygen Pipeline vs Template's `build.sh`

**What goes wrong:** The documentation project's `scripts/cf-build.sh` and `scripts/cf-build.bat` have a heavily customized build pipeline that the gendoc-template's `build.sh` does not replicate:
- **SuperGenius-specific Doxygen pipeline**: Uses a custom `sg-docs/Doxyfile`, creates a `.cf-doxygen.Doxyfile` override on-the-fly with `FULL_PATH_NAMES = NO`, runs Doxygen from the `$SUPERGENIUS_ROOT` directory (not from the project root)
- **Custom `build_navigation.py`**: Project-specific script that parses doxybook2 index files and generates `SUMMARY_EXT.md` with category navigation (Classes, Files, Namespaces, etc.) — entirely different from the template's `build-navigation.py` which merges source-reference sets
- **`doxybook.json` config**: Project uses `scripts/doxybook.json` (different from template's)
- **Python venv location**: Project creates `.venv` in project root; template expects `.venv` inside `gendoc-template/`
- **`requirements.txt` divergence**: Project has extra packages (redirects, section-index, exclude, git-revision-date-localized)
- **Site directory placement**: Project outputs to `documentation/site/`; template outputs to `gendoc-template/site/`
- **llms.txt generation**: Project calls `scripts/build_llms.py` (staged); template calls `scripts/build-llms.py` (hyphenated, different implementation)

Simply switching to `gendoc-template/scripts/build.sh` will break the SuperGenius API reference entirely and may produce a site at the wrong path.

**Why it happens:** The documentation project predates gendoc-template and has three years of accumulated build logic that was never ported into the template's more generic abstraction.

**Consequences:** SuperGenius API reference pages vanish from the site, doxybook2 fails with wrong config, site builds in wrong directory confusing deploy scripts, missing Python packages cause MkDocs plugin errors.

**Prevention:** Do NOT replace `cf-build.sh` wholesale. Instead, refactor it in layers:
1. Keep the SuperGenius Doxygen + doxybook2 pipeline (Steps 1-2 of current `cf-build.sh`)
2. Keep the project's `build_navigation.py` call (not the template's)
3. Add a step to run `gendoc-template/scripts/build-source-reference.sh` ONLY if additional source reference sets are configured in `gendoc.yml` (initially none)
4. Use the template's venv location or reconcile venv paths
5. Either merge project requirements into a local override or install template + project requirements separately
6. Ensure `site_dir` matches what deploy scripts expect

**Detection:** Full comparison build — run old `cf-build.sh`, save `site/`, run new `cf-build.sh`, diff the two `site/` directories. Missing SuperGenius pages will be immediately obvious.

---

### Pitfall 5: The `docs` Submodule Namespace Collision

**What goes wrong:** The documentation project's `.gitmodules` already has `[submodule "gitbook"] path = docs`. This means `docs/` is a git submodule checkpoint that gets populated by `git submodule update --init`. The gendoc-template's `load-gendoc-config.py` will read `paths.handwritten_docs` from `gendoc.yml` and set MkDocs' `docs_dir` to that resolved absolute path. If `gendoc.yml` sets `paths.handwritten_docs: "docs"`, this resolves to `documentation/docs/` — which is the gitbook submodule checkout. This IS currently where all hand-written content lives, so it SHOULD work, but:

- The submodule must be initialized BEFORE `load-gendoc-config.py` runs (it's a MkDocs startup hook)
- If the submodule isn't checked out, MkDocs starts with an empty docs_dir and produces an empty site
- The `gendoc.yml` paths config must reference this correctly

**Why it happens:** The `docs` directory is simultaneously a git submodule path AND the hand-written docs root. This is unconventional — most gendoc-template consumers have `docs/` as a regular directory in their repo.

**Consequences:** Empty site build if submodule isn't initialized. Confusion about which files live where after adding `gendoc-template` as a third submodule (alongside `docs` and `sg-docs`).

**Prevention:**
1. Ensure `cf-build.sh`'s existing `git submodule sync --recursive && git submodule update --init --recursive` runs BEFORE any MkDocs invocation (already the case)
2. Set `paths.handwritten_docs: "docs"` in `gendoc.yml` (matches current `docs_dir: docs` in mkdocs.yml)
3. Verify the resolved absolute path in a test build

**Detection:** Build without submodule init and confirm the error is clear. Build WITH submodule init and confirm content appears.

---

### Pitfall 6: Lost `mkdocs.yml` Configuration — Redirects, Validation, Watch Directories

**What goes wrong:** The current `mkdocs.yml` has several configuration sections that the gendoc-template's `mkdocs.yml` does NOT include:
- `plugins.redirects` with `redirect_maps` (empty currently, but the plugin is installed)
- `plugins.section-index` (installed but not explicitly configured — implicit)
- `plugins.exclude` (installed in requirements.txt)
- `plugins.git-revision-date-localized` (installed in requirements.txt)
- `validation` section (links and nav warnings suppressed)
- `watch` directive (`javascripts` and `stylesheets` for dev server reload)

If these are silently dropped during the mkdocs.yml migration, the site may still build (most are non-fatal plugins), but:
- Redirect mappings won't work
- Validation warnings that were intentionally suppressed will flood build output
- Dev server won't auto-reload on asset changes

The gendoc-template's `mkdocs.yml` uses `load-gendoc-config.py` to inject site_name, docs_dir, site_dir, logo, and generator from `gendoc.yml`. Everything else in the template's mkdocs.yml is considered shared infrastructure. The documentation project must ensure its mkdocs.yml is a merge of: template shared config + project-specific config.

**Why it happens:** The documentation project's mkdocs.yml predates the template and accumulated configuration over time. A naive replacement with the template's mkdocs.yml drops everything project-specific.

**Consequences:** Broken redirects (if any are added later), noisy build output from validation warnings, slower dev iteration.

**Prevention:** Create the new `mkdocs.yml` by:
1. Starting with the gendoc-template's `mkdocs.yml` as the base
2. Adding the `rewrite_gitbook_paths.py` hook (preserving it alongside the template's three hooks)
3. Adding the `redirects` plugin configuration (the plugin is in requirements.txt)
4. Adding the `validation` section with all `ignore` directives
5. Setting `site_name` to `"GNUS.ai Docs"` (not relying on `load-gendoc-config.py` to override it — or setting it in `gendoc.yml`)
6. Adding `watch: [javascripts, stylesheets]` if keeping local asset directories (but per Pitfall 2, these should be deleted)
7. Adding `extra_javascript` entries for the Ask AI widget (`/javascripts/ask/main.js` with `type: module`)

**Detection:** Diff the old and new mkdocs.yml files. Every non-template plugin and configuration setting must have a documented reason for removal or must be present in the new file.

---

## Moderate Pitfalls

### Pitfall 7: `extra_javascript` Loading Order Breakage

**What goes wrong:** The current `extra_javascript` order in the documentation project is:
1. `mermaid.min.js` (CDN)
2. `mermaid.js` (local init)
3. `external-links.js`
4. `mathjax.js` (must load before MathJax CDN)
5. `mathjax CDN` (MathJax itself)
6. `nav-state.js`
7. `breadcrumbs.js`

MathJax configuration (`mathjax.js`) MUST load before the MathJax CDN script because it sets `window.MathJax` which the CDN script reads on load. If the order changes, MathJax won't render equations. The gendoc-template's mkdocs.yml preserves this same order, but if the documentation project manually edits the list and reorders it, math rendering breaks silently.

**Prevention:** Copy the `extra_javascript` list from GeniusCogntiveSystem's mkdocs.yml (which has the verified, identical order) and add the Ask AI widget entry at the end.

**Detection:** Visit a page with LaTeX math equations (e.g., SuperGenius technical pages with `$$...$$` blocks). Raw LaTeX source instead of rendered equations = order broken.

---

### Pitfall 8: Submodule Pin Drift — Template Updates Breaking the Build

**What goes wrong:** The gendoc-template submodule is versioned independently. GeniusCogntiveSystem pins `fc99df9e1817bbe297403bbf636d15bf8725aef6`. If the documentation project points to a different commit (e.g., `main` branch HEAD), future template changes could introduce breaking changes: new required `gendoc.yml` fields, changed script interfaces, or updated Python dependencies that conflict with the project's pinned versions.

**Why it happens:** Submodules default to tracking a branch, but best practice is pinning a specific commit. If the project uses `git submodule add` without specifying a commit, it gets whatever HEAD is at that moment.

**Consequences:** Builds suddenly break when someone runs `git submodule update --remote` and pulls a breaking template change. Hard to diagnose because the submodule update looks unrelated to any project change.

**Prevention:**
1. After adding the submodule, immediately pin it to a specific commit (preferably the same one GeniusCogntiveSystem uses, assuming compatibility)
2. NEVER use `git submodule update --remote` in build scripts — use `git submodule update --init` (checks out pinned commit)
3. Document the pinned commit in `DOCUMENTATION_CHANGES.md`
4. When updating the submodule intentionally, treat it as a full build verification step

**Detection:** The `cf-build.sh` scripts already use `git submodule update --init --recursive` (no `--remote`) — this is correct. Verify this isn't changed during refactoring.

---

### Pitfall 9: `gendoc.yml` Requires Fields the Project Doesn't Need

**What goes wrong:** The `gendoc.yml` schema has several required fields designed for projects with C++ source code (Doxygen pipeline): `source_references` (at least one set), `doxygen.output_dir`, `deploy.cloudflare.pages_project_name`, `deploy.cloudflare.compatibility_date`. The documentation project does NOT have inline C++ source to document — its SuperGenius API reference is generated by a separate Doxygen pipeline that predates the template. Forcing unused source_references entries could cause build errors or unnecessary Doxygen runs.

**Why it happens:** The template was designed for code projects (like GeniusCogntiveSystem with its C++ swarm code). The documentation project is purely a documentation site with hand-written content and pre-generated API reference.

**Consequences:** `build.sh` tries to run Doxygen on non-existent source directories and fails. Build pipeline errors out on a step the project doesn't need.

**Prevention:** 
1. Set `source_references: []` (empty list) — the template's `build-source-reference.sh` should skip when there are no sets
2. Verify `build.sh` handles an empty source_references gracefully, OR
3. Keep using `cf-build.sh` directly (not the template's `build.sh`) since the documentation project's build is fundamentally different
4. The `gendoc.yml` should focus on: `project` metadata, `paths.handwritten_docs`, `mkdocs` settings, `llms` configuration, and optionally `deploy.cloudflare`
5. Test: does `gendoc-template/scripts/build.sh` work with empty `source_references`? If not, do not use it — keep `cf-build.sh` as the primary build entry point

**Detection:** Run the template's `build.sh` on the project. If it fails at "Step 1: Building source reference", the empty-set handling doesn't work. Fall back to keeping `cf-build.sh` as the primary build script and document this decision.

---

### Pitfall 10: `build_llms.py` Version Mismatch

**What goes wrong:** The documentation project has a staged `scripts/build_llms.py` that was written independently. The gendoc-template has `scripts/build-llms.py` (note the hyphen) with a different implementation that reads `gendoc.yml`, generates `llms-meta.json`, and produces audience-specific catalogs. The `cf-build.sh` currently calls `python3 "$SCRIPT_DIR/build_llms.py"` (project-local version). After refactoring, this must switch to the template's version, which expects to be run from the host project root and reads `gendoc.yml` for configuration.

**Why it happens:** Two parallel implementations were created. The staged `build_llms.py` was being added before the gendoc-template refactoring was conceived.

**Consequences:** If the wrong script is called, `llms.txt` files may be generated with different format/content, or the call may fail because it can't find `gendoc.yml` or the `llms:` config section.

**Prevention:**
1. Use `gendoc-template/scripts/build-llms.py` (the template version) exclusively
2. Remove the staged `scripts/build_llms.py` from the project
3. Update `cf-build.sh` to call `python3 gendoc-template/scripts/build-llms.py "$@"` instead of `python3 "$SCRIPT_DIR/build_llms.py" "$@"`
4. Configure `llms:` section in `gendoc.yml` with `site_url`, `enabled: true`, and audience category mappings

**Detection:** After build, verify `site/llms.txt` and `site/llms-full.txt` are generated correctly. Compare format against GeniusCogntiveSystem's output as reference.

---

## Minor Pitfalls

### Pitfall 11: `watch` Directive Points to Deleted Directories

**What goes wrong:** The current `mkdocs.yml` has `watch: [javascripts, stylesheets]` for dev server auto-reload. After deleting these directories (per Pitfall 2), the `watch` directive will reference non-existent paths. MkDocs may log warnings or fail silently.

**Prevention:** Remove the `watch` directive if local `javascripts/` and `stylesheets/` are deleted. The `copy-assets.py` hook handles copying at build time; dev server reload for those assets is handled by the template differently.

---

### Pitfall 12: `.venv` Leftover Conflicts

**What goes wrong:** After refactoring, both `documentation/.venv/` and `gendoc-template/.venv/` may exist. Build scripts might activate the wrong one, leading to missing packages or version mismatches.

**Prevention:** 
1. Decide on ONE venv location (recommend: keep using `documentation/.venv/` since `cf-build.sh` is the primary build entry point)
2. Ensure `gendoc-template/.venv/` is in the project's `.gitignore` or explicitly not created
3. Update any scripts that reference the template's venv to use the project's venv

---

### Pitfall 13: `requirements.txt` Package Drift

**What goes wrong:** The documentation project's `requirements.txt` has packages not in gendoc-template's `requirements.txt`:
- `mkdocs-redirects==1.2.1`
- `mkdocs-section-index==0.3.9`
- `mkdocs-exclude`
- `mkdocs-git-revision-date-localized-plugin`

If the build switches to installing ONLY from `gendoc-template/requirements.txt`, these plugins will be missing and their mkdocs.yml configuration will cause errors or silent failures.

**Prevention:**
1. Keep `documentation/requirements.txt` as the authoritative dependency list
2. After installing template requirements, also install project requirements: `pip install -r gendoc-template/requirements.txt && pip install -r requirements.txt`
3. OR merge the extra packages into a single `requirements.txt` and update `cf-build.sh` accordingly

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Adding submodule | Submodule pin drift (Pitfall 8) | Pin to same commit as GeniusCogntiveSystem: `fc99df9e` |
| Creating gendoc.yml | Required fields for unused Doxygen pipeline (Pitfall 9) | Use empty `source_references: []`, verify template handles it |
| Creating gendoc.yml | `llms` section incomplete | Copy GeniusCogntiveSystem's `llms:` block, update `site_url` to `https://docs.gnus.ai` |
| Updating mkdocs.yml | Dropping `rewrite_gitbook_paths.py` hook (Pitfall 1) | Keep it alongside template hooks; test GitBook-syntax pages |
| Updating mkdocs.yml | Lost redirects/validation/watch config (Pitfall 6) | Merge all project-specific config into new mkdocs.yml |
| Updating mkdocs.yml | Wrong `extra_css` reference (Pitfall 3) | Change to `/stylesheets/theme.css` |
| Removing duplicate assets | JS file divergence (Pitfall 2) | Diff all five JS files; delete local copies; confirm no regressions |
| Removing duplicate assets | `extra_css` → `theme.css` switch (Pitfall 3) | Visual comparison of old vs new build |
| Updating build scripts | Doxygen pipeline incompatibility (Pitfall 4) | Keep SuperGenius pipeline in cf-build.sh; don't switch to template's build.sh |
| Updating build scripts | `build_llms.py` version mismatch (Pitfall 10) | Switch to template's `build-llms.py`; update cf-build.sh call |
| Enabling Ask AI widget | Missing Ask AI JS module entry (Pitfall 7) | Add `{ path: /javascripts/ask/main.js, type: module }` to extra_javascript |
| Verifying build | Submodule not initialized (Pitfall 5) | Ensure `git submodule update --init` runs before any MkDocs step |
| Verifying build | MathJax loading order (Pitfall 7) | Verify mathjax.js loads before MathJax CDN in extra_javascript list |

---

## GeniusCogntiveSystem Transition Notes

These are documented observations from GeniusCogntiveSystem's successful transition that the documentation project should replicate or learn from:

1. **GeniusCogntiveSystem has NO local `javascripts/` or `stylesheets/` at the host project root.** All five JS files and the `theme.css` come exclusively from the submodule. The documentation project should aim for this same clean state.

2. **GeniusCogntiveSystem's `mkdocs.yml` is the template's `mkdocs.yml` with minimal additions** — only added the Ask AI widget JS module entry. The documentation project needs more additions (rewrite_gitbook_paths hook, redirects, validation), but the principle holds: start from the template, add only what's project-specific.

3. **GeniusCogntiveSystem has NO build scripts in its project root.** Everything runs from `gendoc-template/scripts/`. The documentation project cannot fully replicate this because of its SuperGenius Doxygen pipeline, but `cf-build.sh` should be simplified to call template scripts where possible.

4. **GeniusCogntiveSystem's `gendoc.yml` has `generator: false`** — this hides the "Made with Material for MkDocs" footer. The documentation project should do the same.

5. **The `llms.ask.allowed_origins` in GeniusCogntiveSystem's `gendoc.yml` includes `https://docs.gnus.ai`** — this is the shared Ask AI worker pattern. The documentation project should add its own origin here AND ensure GeniusCogntiveSystem's `gendoc.yml` is updated if docs.gnus.ai isn't already in its allowed_origins.

## Sources

- Context7: not applicable (project-specific analysis)
- Project files analyzed directly:
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/mkdocs.yml` (current config)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/scripts/cf-build.sh` (current build)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/javascripts/` (all five JS files)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/stylesheets/extra.css` (current theme)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/scripts/rewrite_gitbook_paths.py` (GitBook compat hook)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/scripts/build_navigation.py` (SuperGenius nav)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/requirements.txt`
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc.yml` (reference working config)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/mkdocs.yml` (reference working mkdocs config)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/scripts/copy-assets.py` (asset copy hook)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/scripts/load-gendoc-config.py` (config injection hook)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/scripts/build.sh` (template build script)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/stylesheets/theme.css` (template theme)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/GeniusCogntiveSystem/gendoc-template/README.md` (template documentation)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/.gitmodules` (existing submodules)
  - `/Users/Shared/SSDevelopment/Development/GeniusVentures/GeniusNetwork/documentation/.planning/PROJECT.md` (project context)
