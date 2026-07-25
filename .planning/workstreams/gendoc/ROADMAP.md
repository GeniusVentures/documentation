# Roadmap: gendoc Workstream

## Overview

The gendoc-template workstream for GNUS.AI Documentation. Phase 8 adds an LLM-powered document graph capability that enriches the RAG retrieval pipeline with three-layer metadata (deterministic, computed, LLM-generated), evidence-backed provenance tracking, and graph-based document relationships.

## Phases

- [x] **Phase 7: Cloudflare Pages Deploy Fix** — [gendoc, gendoc-template] Gzip JSON assets for 25 MiB limit, frontend .json.gz handling with decompression fallback, production branch deploys
- [ ] **Phase 8: LLM Document Graph** — [gendoc-template] Three-layer metadata system for RAG retrieval enrichment, evidence-backed LLM analysis pipeline, graph-based document relationships, incremental reanalysis

### Phase 8: LLM Document Graph
**Goal**: The gendoc-template gains an LLM-powered document graph capability that enriches the RAG retrieval pipeline powering the Ask AI widget. Documents are analyzed through a three-layer metadata system (deterministic/software-extracted, computed/algorithm-derived, LLM-generated/semantic) with evidence-backed provenance tracking. The system produces structured metadata — summaries, questions-answered, topics, entities, document roles, authority scores, and graph relationships — that improves search relevance, candidate ranking, and context ordering without replacing existing lexical or semantic retrieval.
**Depends on**: Phase 4 (Ask AI widget must be enabled; the graph enriches its retrieval pipeline)
**Scope**: gendoc-template submodule, gendoc workstream
**Requirements**: LLMGRAPH-01, LLMGRAPH-02, LLMGRAPH-03, LLMGRAPH-04, LLMGRAPH-05, LLMGRAPH-06, LLMGRAPH-07, LLMGRAPH-08, LLMGRAPH-09, LLMGRAPH-10
**Success Criteria** (what must be TRUE):
  1. Three-layer metadata system is implemented with strict separation: deterministic fields (file type, path, hash, dates, headings, tags, etc.) are extracted by software; computed fields (BM25, embeddings, similarity, graph centrality) are derived algorithmically; LLM-generated fields (summaries, questions-answered, topics, relationships) are produced via semantic analysis — no layer is confused with another
  2. `MetadataOrigin` enum and `MetadataValue` struct are implemented in the gendoc-template codebase, with every inferred value carrying provenance (origin, confidence, model_id, prompt_version, evidence spans, source_hash)
  3. LLM analysis pipeline follows section-level-first architecture: extract sections, analyze each section for entities/claims/dependencies, merge section metadata, then analyze whole-document role and relationships
  4. Two-pass LLM strategy is implemented: Pass 1 extracts only facts with evidence offsets; Pass 2 interprets (questions-answered, roles, relationships) using extracted facts — preventing hallucinated relationships
  5. Composite relevance scoring formula `R(d,q)` is implemented, combining lexical relevance, semantic similarity, metadata-question match, graph support, authority/freshness, and redundancy penalty — LLM metadata improves the metadata, graph, and authority components without replacing lexical/semantic retrieval
  6. Document role classification is implemented (overview, normative_standard, architecture_specification, tutorial, FAQ, etc.) with authority scores and conflict resolution precedence (coding standard > tutorial, current source > old architecture note, architecture spec > marketing copy)
  7. `questions_answered` field receives priority as the primary retrieval enrichment field — user queries match against natural-language questions rather than just titles or raw text
  8. Incremental reanalysis is tied to content hashes: unchanged sections reuse metadata, changed sections trigger targeted reanalysis, only affected graph edges are revisited — full corpus reanalysis is never triggered by a single change
  9. Document graph node schema is defined with id, title, role, authority, freshness, topics, questions_answered, entities, aliases, and weighted relations (depends_on, followed_by, related_to, supersedes, possible_conflicts)
  10. Initial LLM-produced fields (summary, questions_answered, topics, aliases, document_role, authority_reason, entities, explicit_claims, depends_on, followed_by, related_to, supersedes, possible_conflicts) are generated on the existing corpus and stored with confidence, evidence spans, source content hash, model identifier, prompt version, analysis date, and review status on every value
**Plans**: 3 plans

Plans:
- [ ] 08-01-PLAN.md — build-graph.py: two-pass LLM pipeline, section-level analysis, incremental reanalysis, provider-agnostic API key detection
- [ ] 08-02-PLAN.md — Worker TypeScript integration: CatalogEntry graph types, llms-meta.json loading, graph-enhanced scoreEntries
- [ ] 08-03-PLAN.md — Build pipeline integration: build.sh Step 9, deploy.yml secrets, build.yml graph step
**UI hint**: no

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 7. Cloudflare Pages Deploy Fix | 3/3 | Complete | 2026-07-13 |
| 8. LLM Document Graph | 0/3 | Not started | - |
