---
workstream: gendoc
created: 2026-07-11
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-08)

**Core value:** The documentation site must continue to build and deploy identically (same URLs, same appearance, same content) after refactoring to use the `gendoc-template` submodule, PLUS gain the Ask AI widget on all pages.
**Current focus:** Phase 6 — Theme Loader (complete)

## Current Position
**Status:** Complete
**Current Phase:** 6 - Theme Loader
**Last Activity:** 2026-07-12
**Last Activity Description:** Merged phase/06-theme-loader to main, branch deleted. Fixed Ask AI stopword filtering bug in gendoc-template.

## Progress
**Phases Complete:** 6/6
**Current Plan:** Phase 6 — Theme Loader (implemented, UAT 15/15 PASS, shipped)

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Hybrid mkdocs.yml pattern — host keeps its own mkdocs.yml for `rewrite_gitbook_paths.py` hook, shared assets come from submodule
- [Init]: gendoc-template submodule pinned to commit `fc99df9e` (same as GeniusCogntiveSystem)
- [Init]: `source_references: []` — docs-only site with pre-generated API reference, no inline Doxygen pipeline needed
- [Init]: Shared Ask AI worker at `https://ask.gnus.ai/api/ask` — no new Cloudflare Worker deployment required
- [Phase 6]: Theme Loader — load-theme.py hook with default/protocol presets + BYO custom theme support

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260709-e4k | Make ask worker origin-aware with per-origin caches, reference wrangler-ask.toml from parent repo | 2026-07-09 | 31128b0 | [260709-e4k-make-ask-worker-origin-aware-with-per-or](./quick/260709-e4k-make-ask-worker-origin-aware-with-per-or/) |

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-07-12
Stopped at: Phase 6 complete — merged to main, branch deleted. Fixed Ask AI stopword bug.
Resume file: None
