# Phase 8: LLM Document Graph - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-24
**Phase:** 08-llm-document-graph
**Areas discussed:** LLM provider, Metadata storage, Incremental reanalysis, Graph edge scope, Worker integration

---

## LLM Provider & Prompt Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| OpenAI only | Single provider, simpler setup | |
| Anthropic only | Single provider, prompt caching for large docs | |
| Both | Provider-agnostic, detect from available key | ✓ |

**User's choice:** Both OpenAI and Anthropic — "simple enough." Provider-agnostic with prompts inline in the Python script.
**Notes:** Prompts are simple enough for inline — no external template files needed.

---

## Metadata Storage Format

| Option | Description | Selected |
|--------|-------------|----------|
| New `llms-graph.json` | Separate file, clean schema | |
| Extend `llms-meta.json` | Add graph fields to existing schema | ✓ |

**User's choice:** Extend `llms-meta.json` — single source of truth, backward-compatible.
**Notes:** Graph node fields (topics, questions_answered, entities, relations, provenance) added alongside existing per-entry fields.

---

## Incremental Reanalysis

| Option | Description | Selected |
|--------|-------------|----------|
| Separate hash manifest | `content-hashes.json` alongside metadata | |
| Alongside metadata | Hashes in `llms-meta.json` per section | ✓ |
| No incrementality | Full reanalysis every build | |

**User's choice:** Content hashes stored alongside metadata in `llms-meta.json` — single file to check for staleness.

---

## Graph Edge Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Start with 2 types | `depends_on` + `related_to` only, add others later | |
| All 5 types | `depends_on`, `followed_by`, `related_to`, `supersedes`, `possible_conflicts` | ✓ |

**User's choice:** Build all five relation types in Phase 8.

---

## Worker-Side Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Extend CatalogEntry | Add graph fields to existing type | ✓ |
| Parallel fetch | Separate graph fetch alongside catalog | |
| New module | Dedicated graph module in worker | |

**User's choice:** `CatalogEntry` gets the `llms-meta.json` — worker fetches enriched metadata alongside the catalog.
**Notes:** `scoreEntries` and context ordering consume the new fields directly.

---

## Prior Decisions (Assumptions Discussion)

These were decided before the formal discuss-phase session:

| Area | Decision |
|------|----------|
| Script entry point | `scripts/build-graph.py`, invoked from `build.sh` after `build-llms.py` |
| API key gating | Detects from `.env`/env var, skips silently if absent |
| IDE integration | `update-catalogs.md` command picks up graph automatically when key present |
| CI/CD pattern | Reusable workflow pattern — parent passes secret through existing deploy.yml |

## Claude's Discretion

- Implementation language: Python for build-time, TypeScript for worker types
- Section boundary detection for Markdown + GitBook syntax
- Prompt engineering for Pass 1 (extraction) and Pass 2 (interpretation)

## Deferred Ideas

None — discussion stayed within phase scope.
