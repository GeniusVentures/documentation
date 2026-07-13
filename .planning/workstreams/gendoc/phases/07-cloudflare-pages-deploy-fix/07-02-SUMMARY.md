---
phase: 07-cloudflare-pages-deploy-fix
plan: 02
subsystem: gendoc-template
tags:
  - gzip
  - cloudflare
  - fetch-interception
  - mkdocs
  - javascript
  - build-config
dependency_graph:
  requires: []
  provides:
    - DEPLOY-03
  affects:
    - gendoc-template/javascripts/fetch-gzip.js
    - gendoc-template/scripts/load-gendoc-config.py
    - gendoc-template/ask-ai/widget-src/config.ts
tech-stack:
  added:
    - Plain JavaScript (IIFE-pattern fetch interception)
    - DecompressionStream API (browser-native gzip)
  patterns:
    - Build-time feature gating via gendoc.yml
    - Transparent fetch interception (no caller changes needed)
    - Magic-byte gzip detection (server Content-Encoding agnostic)
key-files:
  created:
    - gendoc-template/javascripts/fetch-gzip.js
  modified:
    - gendoc-template/scripts/load-gendoc-config.py
    - gendoc-template/ask-ai/widget-src/config.ts
decisions:
  - "D-04: Shared fetch-gzip.js wrapper intercepts all .json fetches, rewrites to .json.gz with transparent decompression"
  - "D-03: load-gendoc-config.py injects wrapper only when deploy.cloudflare.gzip_json is true — build-time zero-cost toggle"
  - "config.ts simplified to plain fetch('/ask-config.json') — wrapper handles gzip transparently"
metrics:
  duration: 653
  completed_date: "2026-07-13T23:03:20Z"
---

# Phase 07 Plan 02: Shared fetch-gzip.js Wrapper for All .json Fetches

Shared fetch wrapper intercepts all window.fetch calls, rewrites .json URLs to .json.gz, and transparently decompresses gzip responses. Injected at build time only when `deploy.cloudflare.gzip_json` is true. config.ts simplified to a plain fetch with no inline gzip logic.

## Task Completion

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create fetch-gzip.js — shared fetch wrapper | `657753a` | `gendoc-template/javascripts/fetch-gzip.js` (new) |
| 2 | Update load-gendoc-config.py — inject fetch-gzip.js | `8fe06a6` | `gendoc-template/scripts/load-gendoc-config.py` (modified) |
| 3 | Simplify config.ts — drop inline gzip logic | `760627e` | `gendoc-template/ask-ai/widget-src/config.ts` (modified) |

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

### Task 1: fetch-gzip.js

- JS syntax check via `node -e "new Function(...)"` — PASSED
- `endsWith('.json')` URL matching — 1 occurrence
- Magic byte check `0x1f` + `0x8b` — 2 occurrences each
- `DecompressionStream("gzip")` — exactly 1 occurrence
- `Content-Type: application/json` response header — 2 occurrences
- `window.fetch =` interception — 1 occurrence
- IIFE wrapping (`(function() { ... })()` pattern) — confirmed
- No `import`/`export`/TypeScript/Node.js — confirmed (plain JS)
- No `.json` fallback — confirmed (error propagates naturally)

### Task 2: load-gendoc-config.py

- Python syntax via `ast.parse` — PASSED
- `fetch-gzip` references — 5 occurrences
- `gzip_json` references — 7 occurrences
- `insert(0, "/javascripts/fetch-gzip.js")` — present at correct position
- Block placed after `navigation_sections`, before `external_docs` — confirmed
- Existing functionality (`navigation_sections`, `external_docs`) untouched — confirmed

### Task 3: config.ts

- `CONFIG_URL = "/ask-config.json"` (no `.gz` suffix) — confirmed
- `CONFIG_URL_FALLBACK` — removed (0 occurrences)
- `0x1f` magic byte — removed (0 occurrences)
- `DecompressionStream` — removed (0 occurrences)
- `loadAskConfig` function — preserved
- `LIMITS` constant — preserved
- `STORAGE_KEY` constant — preserved
- Config validation (`cfg.enabled`, return shape) — unchanged

## Threat Model Compliance

| Threat ID | Mitigation | Status |
|-----------|-----------|--------|
| T-07-03 (Spoofing) | Only intercepts URLs ending in `.json` — no wildcard | Implemented |
| T-07-04 (DoS) | DecompressionStream is browser-native, no amplification | Accepted |
| T-07-05 (Elevation) | IIFE-scoped, build-time gating, original fetch preserved | Implemented |
| T-07-SC (Tampering) | No new packages installed | Accepted |

## Known Stubs

None — all data paths are fully wired.

## Threat Flags

None — no security-relevant surface beyond what was planned.
