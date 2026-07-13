---
phase: 07-cloudflare-pages-deploy-fix
verified: 2026-07-13T23:45:00Z
status: human_needed
score: 13/13 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Open a browser page built with gendoc-template and gzip_json: true. Open DevTools Network tab. Trigger a .json fetch (MkDocs search, Ask AI widget). Verify the network request targets .json.gz (not .json) and the response is transparently decompressed — the calling code receives parsed JSON, not raw gzip bytes."
    expected: "Network tab shows fetch to /search_index.json.gz (or /ask-config.json.gz). Response Content-Type is application/json. The calling code works without modification."
    why_human: "fetch-gzip.js intercepts window.fetch at runtime — grep cannot verify DOM-level interception or DecompressionStream decompression in a browser context."
  - test: "Run `gendoc-template/scripts/deploy.sh` in a project with Cloudflare Pages configured and gzip_json: true. Verify: (a) all .json files are gzipped and raw .json deleted before upload, (b) wrangler pages deploy --branch reads the correct branch from gendoc.yml, (c) no _headers file is created, (d) no .json files remain in site/ after deploy."
    expected: "Deploy completes successfully. Site directory contains .json.gz files only (no raw .json). Cloudflare Pages dashboard shows deployed files under the configured branch."
    why_human: "Full end-to-end deploy requires Cloudflare credentials and an actual Pages project — cannot verify in a sandboxed environment."
  - test: "Run `mkdocs build` on a host project with gzip_json: true. Inspect the generated site HTML. Verify fetch-gzip.js appears in extra_javascript (first script loaded) and the wrapper IIFE is present in the page source."
    expected: "Generated HTML includes `<script src=\"/javascripts/fetch-gzip.js\"></script>` before any other extra_javascript scripts. Running `mkdocs build` with gzip_json: false does NOT include the script tag."
    why_human: "MkDocs hook injection depends on runtime YAML parsing and config mutation — grep can verify the Python code but not the build output."
---

# Phase 07: Cloudflare Pages Deploy Fix — Verification Report

**Phase Goal:** The gendoc-template deployment pipeline handles Cloudflare Pages' 25 MiB per-file upload limit with a uniform gzip strategy. All .json files become .json.gz, raw .json deleted pre-upload. Every consumer — frontend widget, worker, AND MkDocs search — handles .json.gz with transparent decompression. Deploy branch is configurable via gendoc.yml. All changes scoped to gendoc-template submodule (gendoc workstream).
**Verified:** 2026-07-13T23:45:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

#### Plan 07-01: Uniform JSON Gzip in deploy.sh

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All .json files in site/ are gzipped to .json.gz and raw .json permanently deleted pre-deploy — no special cases, no _headers file | VERIFIED | deploy.sh lines 71-85: uniform `find $SITE_DIR -name "*.json" ! -name "*.json.gz"` loop with gzip+rm, no `-path` exclusion. No _headers write. Zero grep matches for `_headers`, `raw.bak`, `search_index.json`, `gunzip`, `Restoring files`. |
| 2 | No in-place gzip of search_index.json — it follows the same uniform .json -> .json.gz pattern as every other file | VERIFIED | Zero grep matches for `search_index.json` in deploy.sh. All .json handled by identical find+gzip+rm path. |
| 3 | No post-deploy restore — .json.gz is the artifact. Local dev uses gzip_json: false or a fresh mkdocs build | VERIFIED | No gunzip or restore section. deploy_ok check (lines 96-104) follows wrangler directly — nothing between deploy and exit. |
| 4 | fetch-gzip.js wrapper is NOT copied here — copy-assets.py handles javascripts/ -> site/ automatically | VERIFIED | No fetch-gzip.js or search-gzip-sw in deploy.sh. copy-assets.py ASSET_DIRS includes `"javascripts"` (line 15). Single reference to fetch-gzip.js is a code comment on line 73. |

#### Plan 07-02: Shared fetch-gzip.js Wrapper

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A shared fetch-gzip.js intercepts ALL .json fetches on the main thread and rewrites them to .json.gz with transparent gzip decompression | VERIFIED | fetch-gzip.js line 29: `window.fetch = function(url, options)`. Line 26: `endsWith(".json")` matching. Line 36: `String(url) + ".gz"` rewrite. Lines 46-62: magic-byte detection + DecompressionStream. |
| 2 | load-gendoc-config.py injects fetch-gzip.js into extra_javascript ONLY when deploy.cloudflare.gzip_json is true — build-time decision, zero runtime overhead when off | VERIFIED | load-gendoc-config.py lines 148-153: `gzip_json = cfg.get("deploy", {}).get("cloudflare", {}).get("gzip_json", True)`, then `config["extra_javascript"].insert(0, "/javascripts/fetch-gzip.js")` when true, info log when false. |
| 3 | The wrapper has NO .json fallback — it rewrites and commits. If .json.gz doesn't exist, something is misconfigured. | VERIFIED | fetch-gzip.js: only fetches `gzUrl` (line 38), no `.json` retry. Non-ok responses propagate via `Promise.reject(res)` (line 42). |
| 4 | config.ts drops its inline gzip logic — just fetch('/ask-config.json') and let the wrapper handle it | VERIFIED | config.ts line 16: `CONFIG_URL = "/ask-config.json"` (no `.gz`). Line 27: `fetch(CONFIG_URL, { cache: "no-cache" })`. No `CONFIG_URL_FALLBACK`, no `0x1f` magic bytes, no `DecompressionStream`. Direct `JSON.parse(new TextDecoder().decode(body))` at line 31. |
| 5 | Service Worker approach is REJECTED — SWs require HTTPS, breaking mkdocs serve on localhost:8000 | VERIFIED | No Service Worker registration, no `navigator.serviceWorker`, no `sw.js` file anywhere. Implementation uses IIFE-pattern main-thread fetch interception. |
| 6 | The gzip magic-byte detection + DecompressionStream pattern matches config.ts lines 35-41 exactly | VERIFIED | fetch-gzip.js lines 46-62: Uint8Array view, `0x1f`/`0x8b` magic bytes, `new DecompressionStream("gzip")`, writer pattern — identical to the original config.ts approach. |

#### Plan 07-03: Deploy Config Schema Update

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | gendoc-template/gendoc.yml.example documents deploy.cloudflare.branch and deploy.cloudflare.gzip_json with inline comments explaining their purpose | VERIFIED | gendoc.yml.example line 90: `branch: "main"` with comment `# Branch alias for wrangler pages deploy`. Line 91: `gzip_json: true` with comment `# Gzip .json files before deploy (Cloudflare Pages 25 MiB per-file limit). Set false if not using Cloudflare Pages.` |
| 2 | Host gendoc.yml includes deploy.cloudflare.branch field set to 'main' | VERIFIED | gendoc.yml line 91: `branch: "main"` in deploy.cloudflare section. YAML parse confirms `cfg['deploy']['cloudflare']['branch'] == 'main'`. |
| 3 | Existing deploy.cloudflare fields (pages_project_name, production_branch, compatibility_date, custom_domain) are preserved unchanged | VERIFIED | Both gendoc.yml and gendoc.yml.example retain all four existing fields with original values and positions. |

**Score:** 13/13 PLAN must-have truths verified

---

### Roadmap Success Criteria Cross-Reference

| SC | Description | Status | Evidence |
|----|-------------|--------|----------|
| SC-1 | All .json uniformly gzipped to .json.gz, raw .json permanently deleted pre-upload — no in-place gzip, no _headers, no post-deploy restore, no special cases | VERIFIED | deploy.sh: uniform find+gzip+rm loop, zero special cases, no _headers, no restore |
| SC-2 | Shared fetch-gzip.js wrapper intercepts ALL .json fetches -> .json.gz with magic-byte + DecompressionStream decompression. config.ts drops inline gzip logic. | VERIFIED | fetch-gzip.js: window.fetch interception, magic-byte + DecompressionStream. config.ts: plain fetch('/ask-config.json') with no gzip logic. |
| SC-3 | Frontend config.ts fetches /ask-config.json.gz with gzip magic-byte detection and DecompressionStream fallback; falls back to /ask-config.json for local dev | SUPERSEDED | This SC was written before planning decision D-04. config.ts now does a plain `fetch('/ask-config.json')` — the shared wrapper handles the .gz rewrite. SC-2 correctly states config.ts drops inline gzip logic. SC-3 and SC-2 are internally contradictory in the ROADMAP; D-04 + SC-2 take precedence. |
| SC-4 | Worker fetches .json.gz with .json fallback (catalog.ts, normalizer.ts) — already implemented | VERIFIED (pre-existing) | catalog.ts lines 151-158: `/content-map.json.gz` first, fallback to `/content-map.json`. normalizer.ts lines 72-77: `/data/search-vocab.json.gz` first, fallback to `.json`. No changes needed or made. |
| SC-5 | deploy.sh permanently deletes raw .json files after gzip — no restore | VERIFIED | deploy.sh lines 75-81: gzip -fk then rm. No gunzip, no restore section, no .raw.bak. |
| SC-6 | Deploy branch read from gendoc.yml (deploy.cloudflare.branch, default "main") — not hardcoded | VERIFIED | deploy.sh lines 53-58: `DEPLOY_BRANCH` from `cfg.get('deploy', {}).get('cloudflare', {}).get('branch', 'main')`. Line 91: `wrangler pages deploy --branch "$DEPLOY_BRANCH"`. |
| SC-7 | gzip_json toggle controls deploy.sh gzip behavior only | VERIFIED | deploy.sh lines 71-85: gzip loop enclosed in `if [ "$GZIP_JSON" = "True" ]`. Workers have .json.gz-first fallback (pre-existing). fetch-gzip.js has no .json fallback — intentional per D-04 (wrapper rewrites and commits). |

**Note on SC-3:** The ROADMAP contains an internal contradiction between SC-2 ("config.ts drops its inline gzip logic") and SC-3 ("config.ts fetches .json.gz with fallback"). Planning decision D-04 resolved this by choosing the wrapper-based approach documented in SC-2. SC-3 is effectively outdated and should be revised to reflect the implemented approach.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `gendoc-template/scripts/deploy.sh` | Uniform gzip + YAML-driven config | VERIFIED | 105 lines. Uniform gzip loop (lines 71-85) wrapped in gzip_json toggle. DEPLOY_BRANCH + GZIP_JSON from gendoc.yml (lines 53-65). --branch wired (line 91). No _headers, no restore, no special cases. |
| `gendoc-template/javascripts/fetch-gzip.js` | Shared fetch wrapper (min 35 lines) | VERIFIED | 73 lines. IIFE-wrapped. window.fetch interception with endsWith('.json') matching. .json -> .json.gz rewrite. Magic-byte + DecompressionStream decompression. No fallback. Plain JS, no modules. |
| `gendoc-template/scripts/load-gendoc-config.py` | Conditional injection of fetch-gzip.js | VERIFIED | Lines 141-153: gzip_json config read + insert(0, "/javascripts/fetch-gzip.js"). Placed between navigation_sections and external_docs blocks. Existing functionality unchanged. |
| `gendoc-template/ask-ai/widget-src/config.ts` | Simplified config — plain fetch | VERIFIED | CONFIG_URL = "/ask-config.json" (no .gz). No CONFIG_URL_FALLBACK. No 0x1f/DecompressionStream. Direct JSON parse. LIMITS, STORAGE_KEY, loadAskConfig all preserved. |
| `gendoc-template/gendoc.yml.example` | Schema with branch + gzip_json | VERIFIED | branch: "main" + gzip_json: true with descriptive comments. All 4 existing fields preserved. Field order correct. |
| `gendoc.yml` (host) | deploy.cloudflare.branch field | VERIFIED | branch: "main" at line 91. YAML parse confirms. gzip_json intentionally omitted — host inherits default true from deploy.sh. |

---

### Key Link Verification

| From | To | Via | Status | Evidence |
|------|----|-----|--------|----------|
| deploy.sh | gendoc.yml deploy.cloudflare.branch | python3 yaml.safe_load | WIRED | deploy.sh lines 53-58: `cfg.get('deploy', {}).get('cloudflare', {}).get('branch', 'main')` |
| deploy.sh | gendoc.yml deploy.cloudflare.gzip_json | python3 yaml.safe_load | WIRED | deploy.sh lines 60-65: `cfg.get('deploy', {}).get('cloudflare', {}).get('gzip_json', True)` |
| deploy.sh | wrangler pages deploy | --branch "$DEPLOY_BRANCH" | WIRED | deploy.sh line 91: `wrangler pages deploy --branch "$DEPLOY_BRANCH"` |
| fetch-gzip.js | all .json fetch() calls | window.fetch interception | WIRED | fetch-gzip.js lines 29-72: replaces window.fetch, matches endsWith('.json'), rewrites to .gz |
| load-gendoc-config.py | gendoc.yml gzip_json | python3 yaml get | WIRED | load-gendoc-config.py lines 148-153: nested dict access + conditional insert |
| mkdocs.yml | fetch-gzip.js | load-gendoc-config.py injection | WIRED | mkdocs.yml line 7: hooks -> `scripts/load-gendoc-config.py`. Injection via `extra_javascript.insert(0, ...)`. |
| copy-assets.py | fetch-gzip.js | ASSET_DIRS "javascripts" | WIRED | copy-assets.py line 15: `ASSET_DIRS = ("javascripts", "stylesheets", "themes")`. fetch-gzip.js placed in `gendoc-template/javascripts/` automatically mirrors to site. |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| fetch-gzip.js | `window.fetch` return value | `_fetch(gzUrl, options)` -> response.arrayBuffer() -> DecompressionStream -> new Response | Yes (chain is complete from fetch through decompression to Response) | FLOWING |
| config.ts | `loadAskConfig()` return | `fetch(CONFIG_URL)` -> arrayBuffer() -> TextDecoder.decode() -> JSON.parse() | Yes (full fetch-through-parse chain, falls through to catch returning null on errors) | FLOWING |
| load-gendoc-config.py | `config["extra_javascript"]` | `insert(0, "/javascripts/fetch-gzip.js")` | Yes (conditional on gzip_json, but insert modifies real MkDocs config dict) | FLOWING |
| deploy.sh | `$DEPLOY_BRANCH` | python3 yaml.safe_load from gendoc.yml | Yes (reads deploy.cloudflare.branch, defaults to "main") | FLOWING |
| deploy.sh | `$GZIP_JSON` | python3 yaml.safe_load from gendoc.yml | Yes (reads deploy.cloudflare.gzip_json, defaults to True) | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| deploy.sh syntax | `bash -n gendoc-template/scripts/deploy.sh` | "deploy.sh syntax OK" (exit 0) | PASS |
| fetch-gzip.js syntax | `node -e "new Function(require('fs').readFileSync('gendoc-template/javascripts/fetch-gzip.js','utf8'))"` | "fetch-gzip.js syntax OK" (exit 0) | PASS |
| load-gendoc-config.py syntax | `python3 -c "import ast; ast.parse(open('gendoc-template/scripts/load-gendoc-config.py').read())"` | "load-gendoc-config.py syntax OK" (exit 0) | PASS |
| gendoc.yml YAML parse | `python3 -c "import yaml; ... cfg['deploy']['cloudflare']['branch']"` | "gendoc.yml: branch OK: main" (exit 0) | PASS |
| gendoc.yml.example deploy.cloudflare section | `python3 -c "import yaml; ... dc['branch']=='main'; dc['gzip_json']==True"` | Config values correct, but full-file parse fails at line 121 (pre-existing unrelated indentation bug in llms.related_catalogs block — documented in SUMM-03) | PASS (sectionally correct) |

---

### Probe Execution

No probe scripts found (`find scripts -path '*/tests/probe-*.sh'` returned empty). No probes declared in any PLAN file. **Step 7c: SKIPPED** (no probes to run).

---

### Requirements Coverage

No central `REQUIREMENTS.md` file exists in `.planning/workstreams/gendoc/`. Requirement IDs are declared in PLAN frontmatter only:

| Requirement | Source Plan | Description | Status | Evidence |
|------------|-------------|-------------|--------|----------|
| DEPLOY-01 | 07-01-PLAN | deploy.sh reads deploy.cloudflare.branch from gendoc.yml | SATISFIED | deploy.sh lines 53-58: DEPLOY_BRANCH YAML read + --branch wiring |
| DEPLOY-02 | 07-01-PLAN | deploy.sh gzip_json toggle controls gzip/delete cycle | SATISFIED | deploy.sh lines 60-65, 71-85: GZIP_JSON YAML read + conditional gzip loop |
| DEPLOY-03 | 07-02-PLAN | Shared fetch-gzip.js + load-gendoc-config.py injection | SATISFIED | fetch-gzip.js: complete wrapper. load-gendoc-config.py: conditional injection. config.ts: simplified. |
| DEPLOY-04 | 07-03-PLAN | gendoc.yml and gendoc.yml.example schema update | SATISFIED | Both files have branch field. gendoc.yml.example has gzip_json. All existing fields preserved. |

**Coverage:** 4/4 requirement IDs accounted for. No orphaned requirements (no REQUIREMENTS.md phase mapping exists to cross-reference).

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| gendoc-template/ask-ai/widget-src/config.ts | 19-21 | Stale JSDoc comment | WARNING | JSDoc describes old behavior: "Load /ask-config.json.gz, falling back to /ask-config.json" and "Handles gzip decompression". Actual code does a plain fetch('/ask-config.json') and direct JSON parse. Non-functional — the code is correct but the comment is misleading. |

**Debt marker scan:** Zero TBD, FIXME, XXX, TODO, HACK, PLACEHOLDER, or "coming soon/not yet implemented/placeholder" markers found in any file modified by this phase. (The `placeholder` match in config.ts line 39 is widget UI text, not a debt marker. The `placeholder` match in gendoc.yml.example line 137 is a commented-out config example, not a debt marker.)

---

### Human Verification Required

#### 1. fetch-gzip.js Runtime Interception

**Test:** Open a browser page built with gendoc-template and `gzip_json: true`. Open DevTools Network tab. Trigger a .json fetch (MkDocs search, Ask AI widget). Verify the network request targets .json.gz (not .json) and the response is transparently decompressed — the calling code receives parsed JSON, not raw gzip bytes.

**Expected:** Network tab shows fetch to `/search_index.json.gz` (or `/ask-config.json.gz`). Response Content-Type is `application/json`. The calling code works without modification.

**Why human:** fetch-gzip.js intercepts `window.fetch` at runtime — grep cannot verify DOM-level interception or DecompressionStream decompression in a browser context.

#### 2. deploy.sh End-to-End

**Test:** Run `gendoc-template/scripts/deploy.sh` in a project with Cloudflare Pages configured and `gzip_json: true`. Verify: (a) all .json files are gzipped and raw .json deleted before upload, (b) `wrangler pages deploy --branch` reads the correct branch from gendoc.yml, (c) no `_headers` file is created, (d) no .json files remain in `site/` after deploy.

**Expected:** Deploy completes successfully. Site directory contains `.json.gz` files only (no raw .json). Cloudflare Pages dashboard shows deployed files under the configured branch.

**Why human:** Full end-to-end deploy requires Cloudflare credentials and an actual Pages project — cannot verify in a sandboxed environment.

#### 3. Build-Time fetch-gzip.js Injection

**Test:** Run `mkdocs build` on a host project with `gzip_json: true`. Inspect the generated site HTML. Verify fetch-gzip.js appears in `extra_javascript` (first script loaded) and the wrapper IIFE is present in the page source. Repeat with `gzip_json: false` — the script tag must be absent.

**Expected:** Generated HTML includes `<script src="/javascripts/fetch-gzip.js"></script>` before any other `extra_javascript` scripts. Running `mkdocs build` with `gzip_json: false` does NOT include the script tag.

**Why human:** MkDocs hook injection depends on runtime YAML parsing and config dictionary mutation — grep can verify the Python code logic but not the build output.

---

### Gaps Summary

No blocking gaps found. All 13 PLAN must-have truths verified. All 6 artifacts pass existence, substantive, and wiring checks. All 7 key links wired. Data-flow traces show complete chains from source to output.

**Minor findings requiring attention (not blockers):**

1. **Stale JSDoc in config.ts** (lines 19-21): The function-level JSDoc still describes the old .json.gz + fallback + DecompressionStream approach. Code is correct but documentation is misleading. Should be updated to reflect the wrapper-based design: "Load /ask-config.json. When gzip_json is enabled, fetch-gzip.js transparently handles .json.gz rewriting and decompression."

2. **ROADMAP SC-3 is outdated:** The ROADMAP describes config.ts doing inline gzip with fallback, but planning decision D-04 resolved to use the shared wrapper approach. SC-3 should be revised for consistency.

3. **ROADMAP SC-7 partial inaccuracy:** "consumers always try .json.gz with .json fallback" — fetch-gzip.js intentionally has no fallback (D-04). Workers do have fallback (pre-existing). The statement is not universally true.

---

_Verified: 2026-07-13T23:45:00Z_
_Verifier: Claude (gsd-verifier)_
