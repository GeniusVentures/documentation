Yes. **Good metadata is the main asset**, and some of the most useful fields need semantic analysis rather than simple parsing.

The key is to make the LLM an **analyst that proposes metadata**, not the final authority on what the document says.

## Three layers of metadata

### 1. Deterministic metadata

Software can extract this without an LLM:

```text
File type
Path and canonical URL
Content hash
Created and modified dates
Title and headings
Author, when present
Page and section boundaries
Explicit links and citations
Tags and front matter
Code symbols
Word and token counts
Language
```

This metadata should carry high confidence because it comes directly from the source.

### 2. Computed metadata

Search and graph code can calculate this:

```text
BM25 terms and weights
Document frequency
Keyword positions
Embedding vector
Semantic neighbors
Inbound and outbound link counts
Graph centrality
Duplicate-content score
Document and section similarity
Freshness score
```

This is derived, but still reproducible.

### 3. LLM-generated metadata

This is where the useful meaning appears:

```text
One-sentence summary
Detailed abstract
Questions this document answers
Main concepts
Named entities
Claims and conclusions
Required prerequisites
Related documents
Depends-on relationships
Process order
Authority and document role
Whether the document is normative or descriptive
Potential contradictions
Staleness indicators
Audience and difficulty
Suggested search terms and aliases
```

That third layer is what makes the graph useful rather than merely connected.

## The most valuable field may be “questions answered”

For retrieval, this:

```json
{
  "description": "Explains how bridge validators collect and aggregate signatures."
}
```

is useful.

But this is much better:

```json
{
  "questions_answered": [
    "How are bridge validator signatures collected?",
    "How is the aggregation threshold determined?",
    "What happens when a validator does not respond?",
    "How is the aggregate signature verified?"
  ]
}
```

A user query often resembles one of those questions more closely than it resembles the document’s title or raw text.

This is already close to what your `llms-meta.json` descriptions are doing, but it could become much richer.

## Evidence-backed LLM metadata

Every inferred field should point back to source evidence.

Instead of:

```json
{
  "depends_on": [
    "node-verification"
  ]
}
```

store:

```json
{
  "depends_on": [
    {
      "target": "node-verification",
      "confidence": 0.91,
      "evidence": [
        {
          "section": "Signature Collection",
          "start_char": 1842,
          "end_char": 2037,
          "quote_hash": "94ac72..."
        }
      ],
      "generated_by": {
        "model": "model-id",
        "prompt_version": "relation-extraction-v3",
        "timestamp": "2026-07-24T00:00:00Z"
      }
    }
  ]
}
```

This lets you:

* Recheck an edge when the source changes.
* Show why the relationship exists.
* Separate author-written facts from model inference.
* Reprocess only stale metadata.
* Compare model versions.
* Remove an inferred edge safely.

## Provenance matters as much as confidence

I would give every metadata value a provenance class:

```cpp
enum class MetadataOrigin {
    SourceDeclared,
    ParserExtracted,
    AlgorithmDerived,
    ModelInferred,
    HumanReviewed,
    HumanAuthored
};
```

And store:

```cpp
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

A manually declared `depends_on` edge should usually outweigh an LLM-inferred one.

A sensible trust order is:

```text
Human-authored metadata
Source-declared metadata
Human-reviewed model metadata
Parser-extracted metadata
Algorithm-derived metadata
Model-inferred metadata
```

That order can vary by field. For example, embeddings are excellent for similarity, but poor evidence that one component truly depends on another.

## Separate description from authority

A model may correctly summarize a document but misunderstand its role.

You want fields such as:

```json
{
  "document_role": "normative_standard",
  "authority": 0.95,
  "freshness": 0.82,
  "status": "current",
  "applies_to": [
    "C++17",
    "SuperGenius"
  ]
}
```

Useful roles might include:

```text
Overview
Normative standard
Architecture specification
Implementation reference
Tutorial
FAQ
Historical design
Roadmap
Marketing comparison
Generated API reference
Test evidence
Deprecated documentation
```

This helps resolve conflicts.

For example:

```text
Coding standard beats tutorial
Current source reference beats old architecture note for implementation state
Architecture specification beats marketing copy for intended design
```

## The LLM should analyze sections, then documents

Sending a 100-page PDF to one metadata prompt will often produce vague metadata.

A better pipeline is:

```text
Document
  ↓
Extract sections
  ↓
Analyze each section
  ↓
Merge section metadata
  ↓
Analyze whole-document role
  ↓
Compare with related documents
  ↓
Propose graph edges
```

Section-level analysis can produce:

```text
Summary
Questions answered
Entities
Claims
Definitions
Inputs and outputs
Dependencies
References
```

Then a document-level pass can decide:

```text
Overall purpose
Authority
Audience
Primary topics
Canonical questions
Relation to the rest of the corpus
```

## Use two LLM passes

I would keep extraction and interpretation separate.

### Pass 1: evidence extraction

Ask for only facts present in the document:

```text
Entities
Definitions
Claims
Procedures
References
Explicit dependencies
Version statements
Dates
```

Require evidence offsets.

### Pass 2: interpretation

Using the extracted facts, infer:

```text
Questions answered
Document role
Topics
Aliases
Related documents
Possible contradictions
Retrieval description
```

This reduces the chance that the model invents a relationship while reading a large document.

## Metadata for graph construction

A document node could hold:

```json
{
  "id": "bridge-signature-aggregation",
  "title": "Signature Collection and Aggregation",
  "role": "architecture_specification",
  "authority": 0.9,
  "freshness": 0.85,

  "topics": [
    "cross-chain bridging",
    "validator signatures",
    "threshold aggregation"
  ],

  "questions_answered": [
    "How are bridge signatures aggregated?",
    "How many validators must sign?",
    "How is the aggregate verified?"
  ],

  "entities": [
    "validator",
    "bridge message",
    "destination chain"
  ],

  "aliases": [
    "signature collection",
    "threshold signatures",
    "bridge quorum"
  ],

  "relations": [
    {
      "type": "depends_on",
      "target": "node-verification-voting",
      "weight": 0.92,
      "confidence": 0.88
    },
    {
      "type": "followed_by",
      "target": "destination-chain-validation",
      "weight": 0.86,
      "confidence": 0.9
    }
  ]
}
```

That metadata can drive several systems at once:

```text
Search expansion
Graph traversal
Candidate ranking
Conflict resolution
Context ordering
Source explanations
Incremental updates
```

## Do not ask the LLM to assign one global relevance score

A document does not have one fixed relevance score.

It can have static attributes:

```text
Authority
Freshness
Specificity
Quality
Graph relationships
```

But relevance depends on the query:

```text
query → document relevance
```

The final score should combine static metadata and query-time evidence:

[
R(d,q)=
w_lL(d,q)
+w_sS(d,q)
+w_mM(d,q)
+w_gG(d,q)
+w_aA(d)
-w_rD(d,S)
]

Where:

* (L): lexical relevance
* (S): semantic similarity
* (M): metadata-question match
* (G): graph support
* (A): authority and freshness
* (D): redundancy with already selected evidence

The LLM-generated metadata improves (M), (G), and (A). It should not replace lexical or semantic retrieval.

## Incremental reanalysis

Tie all inferred metadata to the source content hash:

```text
Source unchanged:
    reuse metadata

One section changed:
    reanalyze that section
    rebuild affected document summary
    revisit only connected graph edges

Whole document replaced:
    invalidate all inferred metadata
```

This is important for GCS because source code and technical documents will change often. Reanalyzing the whole corpus after each commit would waste time and money.

## Recommended first schema

I would start with these LLM-produced fields:

```text
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

And require these fields on every inferred value:

```text
confidence
evidence spans
source content hash
model identifier
prompt version
analysis date
review status
```

That is enough to build a strong retrieval graph without trying to solve all knowledge representation at once.

So yes: **the metadata layer should include LLM analysis**. The important design choice is to keep raw source facts, computed search data, and model inferences separate. Then the graph can use all three without confusing an LLM’s interpretation with an established fact.
