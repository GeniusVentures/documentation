# Phase 07: Cloudflare Pages Deploy Fix - Context

**Gathered:** 2026-07-13
**Status:** Ready for planning

<domain>
## Phase Boundary

The gendoc-template deployment pipeline handles Cloudflare Pages' 25 MiB per-file upload limit with a uniform gzip strategy: all `.json` files are gzipped to `.json.gz` and raw `.json` deleted pre-upload. Every consumer — frontend widget, worker, AND MkDocs search — handles `.json.gz` requests with transparent decompression fallback. The deploy branch is configurable via `gendoc.yml` rather than hardcoded. All changes are scoped to the gendoc-template submodule (gendoc workstream).

</domain>

<decisions>
## Implementation Decisions

### JSON Gzip Strategy
- **D-01: Uniform `.json.gz` for all JSON files.** All `.json` files in the site directory are gzipped to `.json.gz` and the raw `.json` is deleted before `wrangler pages deploy`. No in-place gzip, no `_headers` file. Every file follows the same pattern.
- **D-02: Revert in-place gzip + `_headers` for `search_index.json`.** The current deploy.sh gzip-replaces `search_index.json` content in-place and writes a `_headers` file for Cloudflare transparent serving. This is removed — `search_index.json` is handled identically to every other `.json` file.
- **D-03: `deploy.cloudflare.gzip_json` toggle in gendoc.yml — deploy.sh only.** A boolean (default `true`) that controls whether `deploy.sh` gzips+deletes raw `.json` before upload. When `false`, deploy.sh skips the entire gzip/delete/restore cycle. Consumers (frontend, worker, MkDocs search) do NOT read this flag — they always try `.json.gz` first with magic-byte detection + `.json` fallback. The toggle exists purely for teams that don't use Cloudflare Pages and don't want the gzip overhead.

### MkDocs Search
- **D-04: Override MkDocs Material search to fetch `.json.gz`.** The MkDocs Material theme's search worker fetches `search_index.json` from a hardcoded URL. A JS shim intercepts this and redirects to `search_index.json.gz`, with the same gzip magic-byte detection + `DecompressionStream` decompression pattern used by `config.ts`. The override must load before the MkDocs search JS initializes.

### Deploy Configuration (gendoc.yml)
- **D-05: Deploy branch configurable via gendoc.yml.** `deploy.cloudflare.branch` in `gendoc.yml` (default: `"main"`). `deploy.sh` reads this value and passes it to `wrangler pages deploy --branch <value>`. Replaces hardcoded `--branch main`.
- **D-03 (see above): `deploy.cloudflare.gzip_json`** — deploy.sh-only toggle. Both keys under the existing `deploy.cloudflare` block.

### Claude's Discretion
- Exact implementation of the MkDocs search JS override — fetch interception shim, `extra_javascript` injection, or post-build template patch. Planner picks the most maintainable approach consistent with the existing `config.ts` pattern.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Code (current state to modify)
- `gendoc-template/scripts/deploy.sh` — Current deploy script with in-place gzip + `_headers` + `--branch main`. MUST be read to understand what's being changed.
- `gendoc-template/ask-ai/widget-src/config.ts` — Frontend `.json.gz` handling pattern (magic bytes + `DecompressionStream`). Reference implementation for the MkDocs search override.
- `gendoc-template/ask-ai/worker/src/catalog.ts` — Worker `.json.gz` → `.json` fallback pattern.
- `gendoc-template/ask-ai/worker/src/normalizer.ts` — Worker `.json.gz` → `.json` fallback pattern.
- `gendoc-template/scripts/copy-assets.py` — How `javascripts/` gets into the site. Any new JS file must be placed correctly for this hook.
- `gendoc-template/mkdocs.yml` — `extra_javascript` and `hooks` configuration. Entry point for search JS override.

### Config
- `gendoc.yml` (host root) — `deploy.cloudflare` section, existing fields.
- `gendoc-template/gendoc.yml.example` — Template schema to update.

### MkDocs Material Search
- MkDocs Material theme JS bundle — `assets/javascripts/bundle/*.min.js` and `assets/javascripts/worker/search/*.min.js` in the built site. Planner should inspect how the search worker resolves `search_index.json` to design the override.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`config.ts` gzip decompression pattern**: Magic bytes `0x1f 0x8b` → `DecompressionStream("gzip")` → `new Response(ds.readable)`. Reuse this exact pattern in the MkDocs search override.
- **`copy-assets.py`**: Already mirrors `javascripts/` into the site post-build. Any new JS file placed in `gendoc-template/javascripts/` is automatically deployed.

### Established Patterns
- **Progressive enhancement**: Worker and frontend both try `.json.gz` first, fall back to `.json`. The MkDocs search override should follow the same "try .gz, decompress if needed" pattern.
- **`deploy.sh` gzip/restore cycle**: Gzip before deploy, gunzip after. This pattern stays — just simplified to be uniform (no in-place special case).
- **YAML config reading**: `deploy.sh` already reads `gendoc.yml` values via `python3 -c "import yaml..."`. Branch config follows the same pattern.

### Integration Points
- **MkDocs search initialization**: The theme's `bundle.js` initializes search on `DOMContentLoaded`. Override must register before this event.
- **Cloudflare Pages**: 25 MiB per-file upload limit. All `.json.gz` files must be under this limit (should be fine — `search_index.json` gzips to ~3-5 MiB).
- **Local dev**: `deploy.sh` restores all `.json` from `.json.gz` after deploy. `wrangler pages dev` serves `.gz` with `Content-Encoding: gzip` (same as production). Non-wrangler local servers (Python `http.server`) need the `.json` fallback.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly wants all `.json` handling to be uniform — no special cases. The `_headers` approach was "fragile and inconsistent."
- The MkDocs search override should mirror `config.ts` as closely as possible for maintainability.
- Branch default is `"main"` — safe production default. Teams that need preview deploys set `deploy.cloudflare.branch: "develop"` in their gendoc.yml.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-cloudflare-pages-deploy-fix*
*Context gathered: 2026-07-13*
