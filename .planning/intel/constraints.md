# Constraints: gendoc SPECs

## LLM Document Graph Architecture

**Source:** `.planning/workstreams/gendoc/llm-doc-graph.md`
**Type:** SPEC (medium confidence)
**Scope:** gendoc-template metadata system, LLM analysis pipeline, documentation graph

### Constraint LLMGRAPH-ARCH-01: Three-Layer Metadata Separation

The metadata system must maintain three distinct layers:

1. **Deterministic** (software-extracted without LLM): file type, path, canonical URL, content hash, dates, title/headings, author, page/section boundaries, explicit links/citations, tags/frontmatter, code symbols, word/token counts, language. Carries high confidence.
2. **Computed** (algorithm-derived without LLM): BM25 terms/weights, document frequency, keyword positions, embedding vector, semantic neighbors, link counts, graph centrality, duplicate-content score, document/section similarity, freshness score. Reproducible.
3. **LLM-generated** (semantic analysis): one-sentence summary, detailed abstract, questions-answered, main concepts, named entities, claims/conclusions, prerequisites, related documents, depends-on relationships, process order, authority/document role, normative vs descriptive classification, potential contradictions, staleness indicators, audience/difficulty, suggested search terms/aliases.

These layers must not be confused — a model inference must never be treated as an established fact.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, sections "Three layers of metadata"

### Constraint LLMGRAPH-ARCH-02: Evidence-Backed Provenance Tracking

Every inferred metadata field must point back to source evidence. The system must implement:

```cpp
enum class MetadataOrigin {
    SourceDeclared,
    ParserExtracted,
    AlgorithmDerived,
    ModelInferred,
    HumanReviewed,
    HumanAuthored
};

struct MetadataValue {
    std::string value;
    MetadataOrigin origin;
    float confidence;
    std::string model_id;
    std::string prompt_version;
    std::vector<EvidenceSpan> evidence;
    std::uint64_t source_hash;
};
```

Trust ordering (may vary by field):
1. Human-authored metadata
2. Source-declared metadata
3. Human-reviewed model metadata
4. Parser-extracted metadata
5. Algorithm-derived metadata
6. Model-inferred metadata

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, sections "Evidence-backed LLM metadata" and "Provenance matters as much as confidence"

### Constraint LLMGRAPH-ARCH-03: Section-Level Then Document-Level Pipeline

The LLM analysis pipeline must follow this order:

```
Document → Extract sections → Analyze each section → Merge section metadata
→ Analyze whole-document role → Compare with related documents → Propose graph edges
```

Section-level analysis produces: summary, questions answered, entities, claims, definitions, inputs/outputs, dependencies, references.
Document-level pass decides: overall purpose, authority, audience, primary topics, canonical questions, relation to corpus.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "The LLM should analyze sections, then documents"

### Constraint LLMGRAPH-ARCH-04: Two-Pass LLM Strategy

LLM analysis must use two separate passes:

**Pass 1 (Evidence Extraction):** Extract only facts present in the document — entities, definitions, claims, procedures, references, explicit dependencies, version statements, dates. Must require evidence offsets.

**Pass 2 (Interpretation):** Using extracted facts, infer — questions answered, document role, topics, aliases, related documents, possible contradictions, retrieval description.

This prevents the model from inventing relationships while reading a large document.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Use two LLM passes"

### Constraint LLMGRAPH-ARCH-05: Composite Relevance Scoring

Do not ask the LLM to assign a single global relevance score. Relevance depends on the query. The final score combines static metadata and query-time evidence:

```
R(d,q) = w_l*L(d,q) + w_s*S(d,q) + w_m*M(d,q) + w_g*G(d,q) + w_a*A(d) - w_r*D(d,S)
```

Where:
- L: lexical relevance
- S: semantic similarity
- M: metadata-question match
- G: graph support
- A: authority and freshness
- D: redundancy with already selected evidence

LLM-generated metadata improves M, G, and A — it must not replace lexical or semantic retrieval.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Do not ask the LLM to assign one global relevance score"

### Constraint LLMGRAPH-ARCH-06: Incremental Reanalysis via Content Hashes

All inferred metadata must be tied to source content hashes with this strategy:

- Source unchanged: reuse metadata
- One section changed: reanalyze that section, rebuild affected document summary, revisit only connected graph edges
- Whole document replaced: invalidate all inferred metadata

This is critical for cost efficiency — reanalyzing the entire corpus after each commit wastes time and money.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Incremental reanalysis"

### Constraint LLMGRAPH-ARCH-07: Document Role and Authority Classification

The system must classify documents by role and authority, separate from content description. Useful roles:

- Overview
- Normative standard
- Architecture specification
- Implementation reference
- Tutorial
- FAQ
- Historical design
- Roadmap
- Marketing comparison
- Generated API reference
- Test evidence
- Deprecated documentation

Conflict resolution precedence: coding standard beats tutorial, current source reference beats old architecture note, architecture specification beats marketing copy.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Separate description from authority"

### Constraint LLMGRAPH-ARCH-08: Initial LLM-Produced Schema

First implementation should produce these LLM fields:

```
summary
questions_answered
topics
aliases
document_role
authority_reason
entities
explicit_claims
depends_on
followed_by
related_to
supersedes
possible_conflicts
```

Every inferred value must carry: confidence, evidence spans, source content hash, model identifier, prompt version, analysis date, review status.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Recommended first schema"

### Constraint LLMGRAPH-ARCH-09: Questions-Answered as Primary Retrieval Field

The `questions_answered` field is identified as the most valuable metadata field for retrieval because user queries more closely resemble natural questions than document titles or raw text. This field should receive priority in the LLM analysis pipeline.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "The most valuable field may be 'questions answered'"

### Constraint LLMGRAPH-ARCH-10: Document Graph Node Schema

Document graph nodes must support a schema including: id, title, role, authority, freshness, topics[], questions_answered[], entities[], aliases[], and relations[] (with type, target, weight, confidence). This metadata drives search expansion, graph traversal, candidate ranking, conflict resolution, context ordering, source explanations, and incremental updates.

Source: `.planning/workstreams/gendoc/llm-doc-graph.md`, section "Metadata for graph construction"
