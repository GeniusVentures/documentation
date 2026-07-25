# Phase 8: LLM Document Graph - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning

## Phase Boundary

This phase adds an LLM-powered document graph capability to gendoc-template that enriches the Ask AI worker's RAG retrieval pipeline. Documents are analyzed at build time through a three-layer metadata system (deterministic, computed, LLM-generated) with evidence-backed provenance tracking. The script gates on an API key from `.env`/environment and skips silently when absent — same behavior in IDE and CI/CD. All scope is contained within the gendoc-template submodule.

## Implementation Decisions

### LLM Provider Strategy
- **D-01:** Support both OpenAI and Anthropic. Design is provider-agnostic — detected from whichever API key is available (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). Both providers can be used in the same pipeline if configured.
- **D-02:** Prompts (Pass 1 extraction, Pass 2 interpretation) live inline in the Python script, not external template files. Simple enough for a single-script pipeline.

### Metadata Storage
- **D-03:** Extend the existing `llms-meta.json` schema rather than creating `llms-graph.json` or any separate file. Add graph nodes (with `topics`, `questions_answered`, `entities`, `aliases`, `document_role`, `authority`), weighted `relations`, and `provenance` fields to the current per-entry structure. Backward-compatible — existing fields unchanged.

### Incremental Reanalysis
- **D-04:** Content hashes stored alongside metadata within `llms-meta.json` per section. A single file check (compare stored hash vs current content hash) determines staleness. No separate manifest or hash file.

### Graph Edge Scope
- **D-05:** All five relation types from the SPEC in this phase: `depends_on`, `followed_by`, `related_to`, `supersedes`, `possible_conflicts`. No phased rollout — build them all.

### Worker-Side Integration
- **D-06:** The worker's `CatalogEntry` type consumes `llms-meta.json`. Worker fetches and parses the enriched metadata alongside the catalog (`llms.txt`). The `scoreEntries` function and context ordering pipeline use the new fields (questions_answered, topics, authority, graph relations) for enhanced ranking.

### Build & CI/CD Integration
- **D-07:** Script (`scripts/build-graph.py`) gates on API key from environment or parent project `.env`. Skips silently with a log message when no key is present.
- **D-08:** Invoked from `build.sh` alongside `build-llms.py`, after it. The existing `update-catalogs.md` Claude command picks up the graph automatically when an API key is configured.
- **D-09:** CI/CD follows the existing reusable workflow pattern — parent project passes `OPENAI_API_KEY` (and/or `ANTHROPIC_API_KEY`) as a GitHub secret through the reusable `gendoc-template/.github/workflows/deploy.yml` workflow. The `build.yml` (PR checks) also runs it when the key is present. No new workflow files needed — just a new step in the existing ones.

### Claude's Discretion
- Implementation language: Python (build-time script follows `build-llms.py` pattern)
- TypeScript types for worker-side `CatalogEntry` extension
- Section boundary detection logic for Markdown + GitBook syntax
- Prompt wording for Pass 1 (extraction) and Pass 2 (interpretation)

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### SPEC & Requirements
- `.planning/workstreams/gendoc/llm-doc-graph.md` — Full SPEC: three-layer metadata, MetadataOrigin/MetadataValue schema, two-pass LLM pipeline, composite scoring formula, incremental reanalysis strategy
- `.planning/workstreams/gendoc/ROADMAP.md` §Phase 8 — Phase scope, 10 success criteria, dependency on Phase 4
- `.planning/REQUIREMENTS.md` §LLMGRAPH-01 through LLMGRAPH-10 — Traceable requirements

### Existing Build Pipeline
- `gendoc-template/scripts/build-llms.py` — Catalog generation pattern to follow/extend
- `gendoc-template/scripts/build.sh` — Build orchestration where graph step is invoked
- `gendoc-template/.github/workflows/deploy.yml` — Reusable CI/CD workflow to extend with graph step
- `gendoc-template/.github/workflows/build.yml` — PR check workflow to extend

### Worker Integration
- `gendoc-template/ask-ai/worker/src/catalog.ts` — `loadCatalog`, `scoreEntries`, `fetchDoc` — consumer of enriched metadata
- `gendoc-template/ask-ai/worker/src/index.ts` — Context ordering pipeline that benefits from enriched ranking
- `gendoc-template/ask-ai/worker/src/types.ts` — `CatalogEntry`, `Env` types to extend

## Existing Code Insights

### Reusable Assets
- `build-llms.py` — Proven pattern: reads Markdown sources, produces `llms-meta.json` + `llms.txt`. New script follows same structure.
- `gendoc-template/.github/workflows/deploy.yml` — Reusable workflow with `workflow_call` inputs and secrets. New graph step fits into the existing steps array.
- `update-catalogs.md` command — IDE workflow that runs `build.sh` and validates output. Graph step is transparent to this command.

### Established Patterns
- Python scripts in `scripts/` invoked from `build.sh` with environment-controlled behavior
- Reusable GitHub Actions workflows with `workflow_call` + `secrets` passthrough
- Worker TypeScript types in `types.ts` consumed by `catalog.ts` and `index.ts`
- `llms-meta.json` as the single metadata source of truth

### Integration Points
- `build.sh` → add `build-graph.py` invocation after `build-llms.py`
- `deploy.yml` → add graph build step, guarded by API key presence
- `build.yml` → add graph build step (PR checks), guarded by API key presence
- `catalog.ts` → extend `CatalogEntry` with optional graph fields from `llms-meta.json`
- `index.ts` → enhanced `scoreEntries` using questions_answered, authority, graph relations

## Specific Ideas

- API key detection from parent project `.env` file for local/IDE use; from GitHub secrets in CI/CD
- Same script works both environments — no branching, just environment variable detection
- The `update-catalogs.md` Claude command automatically benefits from graph when a key is set — no command changes needed
- Graph metadata enriches the `R(d,q)` composite scoring and the U-shaped context ordering discussed separately

## Deferred Ideas

None — discussion stayed within phase scope. The context ordering improvements (relevance tiers + U-shaped interleave) are a separate concern in the worker runtime, not this build-time metadata phase.

---

*Phase: 08-LLM Document Graph*
*Context gathered: 2026-07-24*
