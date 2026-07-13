---
phase: 07-cloudflare-pages-deploy-fix
reviewed: 2026-07-13T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - gendoc-template/scripts/deploy.sh
  - gendoc-template/javascripts/fetch-gzip.js
  - gendoc-template/scripts/load-gendoc-config.py
  - gendoc-template/ask-ai/widget-src/config.ts
  - gendoc-template/gendoc.yml.example
  - gendoc.yml
findings:
  critical: 2
  warning: 3
  info: 2
  total: 7
status: issues_found
---

# Phase 07: Cloudflare Pages Deploy Fix — Code Review Report

**Reviewed:** 2026-07-13
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Reviewed six files spanning the gendoc-template deploy pipeline. Two BLOCKER issues were found. CR-01 (silent data loss) was fixed in a follow-up commit. CR-02 (whitespace-corrupted YAML key) is pre-existing, not caused by this phase.

## Critical Issues

### CR-01: Silent data loss when gzip fails during deploy ✅ FIXED

**File:** `gendoc-template/scripts/deploy.sh:75-78`
**Status:** Fixed in commit `a721577`
**Issue:** The gzip command suppressed all errors (`2>/dev/null || true`), then unconditionally deleted the original `.json`. If `gzip -fk` fails (disk full, permission error), the original file is silently lost.
**Fix:** Guard the `rm` so the original is only deleted when gzip succeeds. Emit warning to stderr on failure.

### CR-02: Leading whitespace corrupts YAML key in example template

**File:** `gendoc-template/gendoc.yml.example:121`
**Status:** Pre-existing — NOT introduced by Phase 7
**Issue:** The key ` related_catalogs:` has a leading space, making the parsed key `" related_catalogs"` instead of `"related_catalogs"`. Consumers looking up `cfg.get("related_catalogs")` won't find it.

## Warnings

### WR-01: Unhandled promise rejection in DecompressionStream write

**File:** `gendoc-template/javascripts/fetch-gzip.js:53-56`
**Issue:** `writer.write(body)` returns a Promise never awaited before `writer.close()`. While the Streams spec states `close()` waits for pending writes, if `write()` rejects the error is lost. Low practical risk for in-memory DecompressionStream.

### WR-02: Dict-form external_docs sources lose label key

**File:** `gendoc-template/scripts/load-gendoc-config.py:164-170`
**Issue:** When external_docs sources use the dict form with `label`/`paths`, only `paths` is forwarded to the MkDocs plugin config — the `label` key is silently dropped.

### WR-03: Triple YAML parse of the same file

**File:** `gendoc-template/scripts/deploy.sh:43-65`
**Issue:** Three separate inline `python3 -c "import yaml..."` invocations parse the same `gendoc.yml` file independently. Functional but adds startup latency and creates drift risk if the YAML read pattern diverges.

## Info

### IN-01: Misleading JSDoc in config.ts

**File:** `gendoc-template/ask-ai/widget-src/config.ts:18-22`
**Issue:** JSDoc describes a local `.json` fallback that this function no longer implements (removed in Phase 7).

### IN-02: Redundant host_project_root reassignment

**File:** `gendoc-template/scripts/load-gendoc-config.py:69`
**Issue:** `host_project_root` is assigned identically on line 38 and again on line 69. The second assignment is redundant.
