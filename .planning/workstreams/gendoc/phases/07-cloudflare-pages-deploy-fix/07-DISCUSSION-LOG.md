# Phase 07: Cloudflare Pages Deploy Fix — Discussion Log

**Date:** 2026-07-13
**Mode:** Advisor (minimal_decisive calibration)
**User decisions:** 3 areas, 3 picks

## Area 1: JSON Gzip Strategy

**Question:** Uniform `.json.gz` for all files, or mixed approach (in-place gzip for search_index.json + .json.gz for others)?

| Option | Description |
|--------|-------------|
| A) Uniform `.json.gz` | Gzip everything to .json.gz, delete all raw .json. Frontend + worker handle it. MkDocs search breaks (needs fix). |
| B) Mixed (current) | In-place gzip for search_index.json (_headers + Cloudflare transparent), .json.gz for everything else. Two approaches, fragile. |

**Selected:** A — Uniform `.json.gz`

**Rationale:** Consistency. Every file follows the same pattern. The `_headers` approach was fragile and inconsistent with how every other file works. MkDocs search breakage is fixed by Area 2.

## Area 2: search_index.json Handling

**Question:** MkDocs search widget fetches `search_index.json` — can't request `.json.gz`. How to handle?

| Option | Description |
|--------|-------------|
| A) Accept broken search | Site search 404s on deploy. Not viable. |
| B) Keep _headers for this one file | Only special case, but fragile and inconsistent. |
| C) Override MkDocs search JS | Patch the search worker to request .json.gz with decompression fallback, same pattern as config.ts. |

**Selected:** C — Override MkDocs search JS

**Rationale:** Consistent with the uniform strategy (Area 1). Same gzip magic-byte + DecompressionStream pattern already proven in config.ts. Eliminates the need for special cases entirely.

## Area 3: Deploy Branch

**Question:** Hardcoded `--branch main` in deploy.sh, or configurable from gendoc.yml?

| Option | Description |
|--------|-------------|
| A) Hardcode `--branch main` | Simple, no config surface. Can't deploy to preview. |
| B) Configurable from gendoc.yml | `deploy.cloudflare.branch`, default "main". Enables preview deploys. |

**Selected:** B — Configurable from gendoc.yml

**Rationale:** One extra YAML key enables preview deploys for testing. Safe default ("main") means no action needed for production deploys. Pays for itself next time someone tests a deploy.

## Claude's Discretion

- Exact MkDocs search JS override mechanism (fetch interception shim, extra_javascript injection, or post-build patch)
- gendoc.yml key placement under existing `deploy.cloudflare` block

## Deferred Ideas

None.

---

*Discussion completed: 2026-07-13*
