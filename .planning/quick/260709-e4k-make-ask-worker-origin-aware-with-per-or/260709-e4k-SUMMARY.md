---
phase: quick-260709-e4k
plan: 01
subsystem: ask-worker
tags: [ask-worker, cloudflare, caching, multi-site]
requires:
  - gendoc-template ask-ai worker
provides:
  - origin-aware ask worker serving multiple doc sites from one deployment
affects:
  - gendoc-template/ask-ai/worker/ask.js
  - gendoc-template/scripts/setup.sh
  - wrangler-ask.toml
tech-stack:
  added: []
  patterns:
    - "Per-origin cache namespacing via Map<origin, ...>"
    - "Relative-URL resolution against validated request Origin at runtime"
key-files:
  created: []
  modified:
    - gendoc-template/ask-ai/worker/ask.js
    - gendoc-template/scripts/setup.sh
    - wrangler-ask.toml
decisions:
  - "Caches keyed by validated Origin string (not LLMS_URL) — Origin is the trust boundary already enforced by corsHeaders"
  - "LLMS_URL resolved against Origin only when relative (startsWith '/'); absolute URLs pass through unchanged for backward compat"
  - "setup.sh writes generated wrangler-ask.toml to host root ($HOST_ROOT) instead of inside the submodule"
metrics:
  duration: 186s
  completed: 2026-07-09
  tasks: 2
  files: 3
---

# Phase quick-260709-e4k Plan 01: Make ask worker origin-aware with per-origin caches Summary

Made the ask Cloudflare Worker origin-aware so a single shared deployment serves multiple documentation sites (`docs.gnus.ai`, `gcs.gnus.ai`) with isolated per-origin caches, resolving a relative `/llms.txt` against the validated request Origin at runtime.

## What Changed

### Task 1 — ask.js: origin-aware caches and relative LLMS_URL resolution
- Replaced the three singleton module-scope caches with `Map<origin, ...>` instances:
  - `catalogCache` — `Map<origin, { entries, ts }>`
  - `normalizerCache` — `Map<origin, MkDocsSearchNormalizer>`
  - `contentMapCache` — `Map<origin, object>`
- Extracted the validated Origin (`cors['Access-Control-Allow-Origin']`) in `fetch()` after the 403 gate and threaded it through `loadCatalog`, `getNormalizer`, `loadContentMap`, `fetchDoc`, and `extractTerms`.
- `loadCatalog` now resolves a relative `LLMS_URL` (`/llms.txt`) against `origin` via `new URL(llmsUrl, origin)`; absolute URLs pass through unchanged. Sub-catalog resolution derives from the resolved LLMS_URL origin (`catalogOrigin`) preserving backward compatibility.
- `getNormalizer` and `loadContentMap` build their URLs directly from `origin` (no longer from `new URL(env.LLMS_URL).origin`).
- `fetchDoc` falls back to `env.SITE_URL || origin` for relative doc URLs — the `http://localhost:8000` fallback was removed.
- Cache debug logs now include the origin prefix for clarity (e.g. `[ask] [https://docs.gnus.ai] normalizer loaded: ...`).
- `corsHeaders` and the search-normalizer import are unchanged.

### Task 2 — setup.sh and wrangler-ask.toml: relative LLMS_URL
- `gendoc-template/scripts/setup.sh`:
  - `ASK_OUT` changed from `$TEMPLATE_ROOT/ask-ai/wrangler-ask.toml` to `$HOST_ROOT/wrangler-ask.toml` so the generated worker config lands in the parent repo where wrangler deploys from.
  - `{{LLMS_URL}}` token value changed from `sys.argv[4] + '/llms.txt'` (absolute) to `'/llms.txt'` (relative); the worker resolves it against Origin at runtime.
- `wrangler-ask.toml` (project root): `LLMS_URL` changed from `"https://docs.gnus.ai/llms.txt"` to `"/llms.txt"`. `SITE_URL` left as `"https://docs.gnus.ai"` (now serves as a secondary fallback after Origin).
- `wrangler-ask.toml.template`: no changes — already used the `{{LLMS_URL}}` token pass-through.

## Threat Model — Mitigations Applied

- **T-quick-01 (Spoofing, Origin as cache key):** Only origins validated by `corsHeaders` against `ALLOWED_ORIGINS` ever reach the cache layer — the 403 gate on `!cors['Access-Control-Allow-Origin']` runs before any cache access. Unverified origins never get a cache slot.
- **T-quick-02 (Information Disclosure, per-origin caches):** Each origin's cache lives in its own `Map` entry keyed by the validated origin string. `docs.gnus.ai` requests cannot read `gcs.gnus.ai`'s catalog/normalizer/content-map — `Map.get(otherOrigin)` is the only access path and callers only ever pass the current request's own origin.

## Verification Results

- `node --check gendoc-template/ask-ai/worker/ask.js` — passes, no syntax errors.
- `grep -c "= new Map()" ask.js` — 3 matches (catalogCache, normalizerCache, contentMapCache).
- `origin` parameter present in all five helper signatures and all call sites (11 references).
- `wrangler-ask.toml` at root has `LLMS_URL = "/llms.txt"`.
- `localhost:8000` fallback removed (0 occurrences).
- All four Task 2 grep verifications return 1.

## Deviations from Plan

None — plan executed exactly as written. No rules triggered.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, or trust-boundary surface introduced beyond what the threat model already covers. The Origin-as-cache-key surface is explicitly mitigated (T-quick-01, T-quick-02).

## Commits

| Task | Repo | Hash | Message |
|------|------|------|---------|
| 1 | gendoc-template (submodule) | `0ec71d7` | feat(ask-worker): make caches origin-aware with per-origin maps |
| 2 | gendoc-template (submodule) | `6a9dfb7` | chore(setup): write wrangler-ask.toml to host root with relative LLMS_URL |
| 2 | parent (docs) | `31128b0` | chore(ask-worker): switch root wrangler-ask.toml to relative LLMS_URL |

## Self-Check: PASSED

All four target files exist. All three commit hashes verified present in their respective repos (`git log` confirms `0ec71d7` and `6a9dfb7` in submodule, `31128b0` in parent).
