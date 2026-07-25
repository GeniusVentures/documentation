# Requirements: GNUS.AI Documentation Refactoring

## v1 Requirements

### Submodule & Configuration (SUBMOD)

- [ ] **SUBMOD-01**: Add `gendoc-template` as a git submodule pinned to the same commit as GeniusCogntiveSystem (`fc99df9e`)
- [ ] **SUBMOD-02**: Create `gendoc.yml` at project root with project metadata (name: "GNUS.AI Docs", number, logo, brief), paths (handwritten_docs: "docs"), mkdocs settings, and navigation sections
- [ ] **SUBMOD-03**: Update project `mkdocs.yml` to use gendoc-template hooks (`gendoc-template/scripts/load-gendoc-config.py`, `gendoc-template/scripts/clean-nav.py`, `gendoc-template/scripts/copy-assets.py`) while preserving the host-specific `scripts/rewrite_gitbook_paths.py` hook
- [ ] **SUBMOD-04**: Set `source_references: []` in gendoc.yml (this is a docs-only site with pre-generated API reference)

### Asset Migration (ASSET)

- [ ] **ASSET-01**: Delete host `javascripts/` directory (all 5 JS files confirmed identical or superseded by submodule versions)
- [ ] **ASSET-02**: Replace `stylesheets/extra.css` reference with `gendoc-template/stylesheets/theme.css` in mkdocs.yml (theme.css is a strict superset — same GNUS.AI brand palette plus Ask AI drawer styles)
- [ ] **ASSET-03**: Update `requirements.txt` to defer to `gendoc-template/requirements.txt` (submodule version is the superset adding `pyyaml>=6.0`)
- [ ] **ASSET-04**: Remove vestigial `docs/javascripts → ../javascripts/` symlink (copy-assets.py populates site dir at build time)
- [ ] **ASSET-05**: Verify `mkdocs-redirects` dependency is added to build pipeline (present in current requirements.txt, not in submodule's)

### Build Scripts (BUILD)

- [ ] **BUILD-01**: Update `cf-build.sh` to install dependencies from `gendoc-template/requirements.txt` and use submodule-relative paths
- [ ] **BUILD-02**: Update `cf-build.bat` with equivalent Windows changes
- [ ] **BUILD-03**: Preserve the custom SuperGenius Doxygen + doxybook2 pipeline in build scripts (gendoc-template's `build.sh` cannot replace `cf-build.sh` — fundamentally different pipeline)
- [ ] **BUILD-04**: Replace host `scripts/build_llms.py` with `gendoc-template/scripts/build_llms.py` (template version is a 139-line superset)
- [ ] **BUILD-05**: Create `llms-meta.json` for editorial metadata (required by the llms.txt generation pipeline)

### Ask AI Widget (ASKAI)

- [ ] **ASKAI-01**: Enable `llms.ask` in `gendoc.yml` — set `enabled: true`, `endpoint: "https://ask.gnus.ai/api/ask"` (shared worker with GeniusCogntiveSystem)
- [ ] **ASKAI-02**: Add `allowed_origins: ["https://docs.gnus.ai"]` to ask config
- [ ] **ASKAI-03**: Add `gendoc-template/javascripts/ask/main.js` (type: module) to `extra_javascript` in mkdocs.yml
- [ ] **ASKAI-04**: Verify `ask-config.json` is generated correctly during build

### Verification (VERIFY)

- [ ] **VERIFY-01**: Site builds successfully with zero errors from `mkdocs build`
- [ ] **VERIFY-02**: All existing page URLs are unchanged (no broken links, no redirect regressions)
- [ ] **VERIFY-03**: GitBook-syntax pages render correctly (`{% embed %}`, `{% hint %}`, cover page meta, GitBook math syntax)
- [ ] **VERIFY-04**: Mermaid diagrams, MathJax equations, breadcrumbs, external links, and nav state all function identically
- [ ] **VERIFY-05**: Ask AI widget (floating "Ask" button + chat drawer) appears and functions on all pages
- [ ] **VERIFY-06**: Site appearance is visually identical to pre-refactoring build (brand colors, typography, spacing)
- [ ] **VERIFY-07**: Mobile responsive layout is unchanged
- [ ] **VERIFY-08**: Update `DOCUMENTATION_CHANGES.md` with refactoring summary

### Cloudflare Pages Deploy Fix (DEPLOY)

- [x] **DEPLOY-01**: Uniform `.json.gz` for all JSON files — permanently, no restore. All `.json` files in the site directory are gzipped to `.json.gz` and the raw `.json` is deleted before `wrangler pages deploy`. No in-place gzip, no `_headers` file, no post-deploy restore.
- [x] **DEPLOY-02**: Shared `fetch-gzip.js` wrapper intercepts ALL `.json` fetches → `.json.gz` with transparent magic-byte + `DecompressionStream` decompression. Conditionally injected by `load-gendoc-config.py` when `gzip_json: true`.
- [x] **DEPLOY-03**: `deploy.cloudflare.gzip_json` toggle in `gendoc.yml` controls deploy.sh gzip behavior. `deploy.cloudflare.branch` configures the wrangler deploy branch. Both keys under the existing `deploy.cloudflare` block.
- [x] **DEPLOY-04**: `gendoc.yml.example` and host `gendoc.yml` document `branch` and `gzip_json` fields in the `deploy.cloudflare` section.

### LLM Document Graph (LLMGRAPH)

- [ ] **LLMGRAPH-01**: Implement three-layer metadata system in gendoc-template with strict separation: deterministic fields (file type, path, hash, dates, headings, tags) extracted by software, computed fields (BM25, embeddings, similarity, graph centrality) derived algorithmically, and LLM-generated fields (summaries, questions-answered, topics, relationships) produced via semantic analysis. No layer may be confused with another.
- [ ] **LLMGRAPH-02**: Implement `MetadataOrigin` enum (`SourceDeclared`, `ParserExtracted`, `AlgorithmDerived`, `ModelInferred`, `HumanReviewed`, `HumanAuthored`) and `MetadataValue` struct with value, origin, confidence, model_id, prompt_version, evidence spans, and source_hash. Every inferred value carries provenance.
- [ ] **LLMGRAPH-03**: Implement section-level-first LLM analysis pipeline: extract sections, analyze each for entities/claims/dependencies, merge section metadata, then analyze whole-document role and relationships with the corpus.
- [ ] **LLMGRAPH-04**: Implement two-pass LLM strategy: Pass 1 (evidence extraction) extracts only facts with evidence offsets; Pass 2 (interpretation) infers questions-answered, roles, and relationships from extracted facts. Prevents hallucinated relationships.
- [ ] **LLMGRAPH-05**: Implement composite relevance scoring formula `R(d,q) = w_l*L(d,q) + w_s*S(d,q) + w_m*M(d,q) + w_g*G(d,q) + w_a*A(d) - w_r*D(d,S)` with configurable weights. LLM metadata improves M (metadata-question match), G (graph support), and A (authority/freshness) components. Must not replace lexical or semantic retrieval.
- [ ] **LLMGRAPH-06**: Implement document role classification (overview, normative_standard, architecture_specification, implementation_reference, tutorial, FAQ, historical_design, roadmap, marketing_comparison, generated_api_reference, test_evidence, deprecated) with authority scores and conflict resolution precedence (normative standard > tutorial, current source > old architecture note, architecture spec > marketing copy).
- [ ] **LLMGRAPH-07**: Implement `questions_answered` field generation as the primary retrieval enrichment mechanism. User queries match against natural-language questions rather than only titles or raw text. This field receives priority in the LLM analysis pipeline.
- [ ] **LLMGRAPH-08**: Implement incremental reanalysis tied to content hashes. Unchanged sections reuse existing metadata. Changed sections trigger targeted reanalysis with only affected graph edges revisited. Full corpus reanalysis must never be triggered by a single change.
- [ ] **LLMGRAPH-09**: Define and implement document graph node schema with id, title, role, authority, freshness, topics[], questions_answered[], entities[], aliases[], and weighted relations[] (type: depends_on/followed_by/related_to/supersedes/possible_conflicts, target, weight, confidence). Graph metadata drives search expansion, graph traversal, candidate ranking, conflict resolution, context ordering, source explanations, and incremental updates.
- [ ] **LLMGRAPH-10**: Generate initial LLM-produced fields (summary, questions_answered, topics, aliases, document_role, authority_reason, entities, explicit_claims, depends_on, followed_by, related_to, supersedes, possible_conflicts) on the existing documentation corpus. Every value carries confidence, evidence spans, source content hash, model identifier, prompt version, analysis date, and review status.

## v2 Requirements (Deferred)

(None — this is a targeted refactoring. All scope is v1.)

## Out of Scope

- Content changes to documentation pages — content stays exactly as-is
- Changing the theme or visual design of the site
- Adding new documentation sections or pages
- Changing the deployment pipeline (Cloudflare Pages)
- Refactoring the API reference generation (Doxygen → doxybook2 pipeline for SuperGenius)
- Modifying the gendoc-template submodule itself
- Changing the docs (gitbook) or sg-docs submodules
- Adding new Cloudflare Worker — uses existing shared worker at `ask.gnus.ai`
- Any C++ code changes in sibling projects

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| SUBMOD-01 | Phase 1 | Pending |
| SUBMOD-02 | Phase 1 | Pending |
| SUBMOD-03 | Phase 1 | Pending |
| SUBMOD-04 | Phase 1 | Pending |
| ASSET-01 | Phase 2 | Pending |
| ASSET-02 | Phase 2 | Pending |
| ASSET-03 | Phase 2 | Pending |
| ASSET-04 | Phase 2 | Pending |
| ASSET-05 | Phase 2 | Pending |
| BUILD-01 | Phase 3 | Pending |
| BUILD-02 | Phase 3 | Pending |
| BUILD-03 | Phase 3 | Pending |
| BUILD-04 | Phase 3 | Pending |
| BUILD-05 | Phase 3 | Pending |
| ASKAI-01 | Phase 4 | Pending |
| ASKAI-02 | Phase 4 | Pending |
| ASKAI-03 | Phase 4 | Pending |
| ASKAI-04 | Phase 4 | Pending |
| VERIFY-01 | Phase 5 | Pending |
| VERIFY-02 | Phase 5 | Pending |
| VERIFY-03 | Phase 5 | Pending |
| VERIFY-04 | Phase 5 | Pending |
| VERIFY-05 | Phase 5 | Pending |
| VERIFY-06 | Phase 5 | Pending |
| VERIFY-07 | Phase 5 | Pending |
| VERIFY-08 | Phase 5 | Pending |
| DEPLOY-01 | Phase 7 | Complete |
| DEPLOY-02 | Phase 7 | Complete |
| DEPLOY-03 | Phase 7 | Complete |
| DEPLOY-04 | Phase 7 | Complete |
| LLMGRAPH-01 | Phase 8 | Pending |
| LLMGRAPH-02 | Phase 8 | Pending |
| LLMGRAPH-03 | Phase 8 | Pending |
| LLMGRAPH-04 | Phase 8 | Pending |
| LLMGRAPH-05 | Phase 8 | Pending |
| LLMGRAPH-06 | Phase 8 | Pending |
| LLMGRAPH-07 | Phase 8 | Pending |
| LLMGRAPH-08 | Phase 8 | Pending |
| LLMGRAPH-09 | Phase 8 | Pending |
| LLMGRAPH-10 | Phase 8 | Pending |

## Definition of Done

1. `gendoc-template` is a tracked git submodule
2. `gendoc.yml` exists at project root and is valid
3. `mkdocs.yml` references submodule hooks + host-specific `rewrite_gitbook_paths.py`
4. No duplicate JS/CSS assets in host project
5. `cf-build.sh` and `cf-build.bat` produce a successful build
6. Ask AI widget appears on all pages
7. Site is visually and functionally identical to pre-refactoring build
8. All verification checks pass

---
*Last updated: 2026-07-24 — added LLM Document Graph requirements (LLMGRAPH-01 through LLMGRAPH-10)*
