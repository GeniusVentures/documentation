---
phase: 07-cloudflare-pages-deploy-fix
plan: 03
subsystem: gendoc-template-config
tags: [config, deploy, cloudflare, yaml, schema]
requires:
  - 07-01 (deploy.sh reads branch + gzip_json from gendoc.yml)
provides:
  - branch + gzip_json schema documentation in gendoc.yml.example
  - branch field in host gendoc.yml for deploy.sh consumption
affects:
  - gendoc-template/gendoc.yml.example
  - gendoc.yml
tech-stack:
  added: []
  patterns: [yaml-config, inline-comment-documentation]
key-files:
  created: []
  modified:
    - gendoc-template/gendoc.yml.example (added branch, gzip_json to deploy.cloudflare schema)
    - gendoc.yml (added branch to deploy.cloudflare section)
decisions:
  - D-03: gzip_json field in template schema documents the deploy.sh toggle; host inherits default true
  - D-05: branch field added to both template and host configs; deploy.sh reads via existing YAML pattern
metrics:
  duration: 6m24s
  completed_date: 2026-07-13
  task_count: 2
  file_count: 2
---

# Phase 07 Plan 03: Deploy Config Schema Update Summary

Added `branch` and `gzip_json` fields to the deploy.cloudflare YAML schema documentation (gendoc.yml.example) and the `branch` field to the host production config (gendoc.yml), enabling deploy.sh's new YAML-driven branch and gzip controls to be documented and configured.

## Tasks Completed

| # | Name | Type | Commit | Files |
|---|------|------|--------|-------|
| 1 | Update gendoc-template/gendoc.yml.example with branch and gzip_json fields | auto | `97fec0a` (submodule) | gendoc-template/gendoc.yml.example |
| 2 | Update host gendoc.yml with deploy.cloudflare.branch | auto | `d180e46` (parent) | gendoc.yml, gendoc-template (submodule pointer) |

## What Changed

### Task 1: Template Schema (gendoc.yml.example)

Two new fields inserted between `production_branch` and `custom_domain` in the `deploy.cloudflare` block:

- **`branch: "main"`** — Branch alias passed to `wrangler pages deploy --branch`. Documented with comment: `# Branch alias for wrangler pages deploy (default "main")`. Separate from `production_branch` which configures the Cloudflare Pages CI trigger in `wrangler.toml`.
- **`gzip_json: true`** — Controls whether deploy.sh gzips `.json` files before upload. Documented with comment: `# Gzip .json files before deploy (Cloudflare Pages 25 MiB per-file limit). Set false if not using Cloudflare Pages.`

All six existing fields (`pages_project_name`, `production_branch`, `custom_domain`, `compatibility_date`, and the `# Authenticate` comment) remain unchanged. Field order verified: pages_project_name, production_branch, branch, gzip_json, custom_domain, compatibility_date.

### Task 2: Host Config (gendoc.yml)

Added `branch: "main"` between `production_branch: "main"` and `custom_domain: "docs.gnus.ai"` in the host `gendoc.yml` deploy.cloudflare section. Matches the host's minimal YAML style (no inline comments, bare key-value pairs). All existing fields preserved unchanged.

`gzip_json` was intentionally NOT added to the host config — deploy.sh defaults to `true` when the field is absent, and the host doesn't need to override that default.

## Deviations from Plan

### Out-of-Scope Findings

**1. Pre-existing YAML parse error in gendoc.yml.example (line 121)**
- **Found during:** Task 1 verification
- **Issue:** `related_catalogs:` inside the `llms:` block has an extra leading space, causing YAML parser error at line 121 column 2. This is a pre-existing indentation bug — confirmed by reverting to the pre-change state which produces the identical error.
- **Not fixed:** Out of scope per deviation rules — not caused by current task changes. The error is in the `llms.related_catalogs` section, completely unrelated to the `deploy.cloudflare` block modified in this plan.
- **Impact:** Full-file YAML parsing fails, but the deploy.cloudflare section (lines 86-95) is syntactically correct and can be extracted independently. deploy.sh reads specific keys via `python3 -c "import yaml; print(cfg['deploy']['cloudflare']['branch'])"` which targets the correct block.

No other deviations — plan executed as written.

## Known Stubs

None. All fields have concrete values appropriate for production use.

## Threat Flags

None. Changes are YAML configuration field additions only — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. Plan threat model entries T-07-06 and T-07-SC remain accepted as documented.

## Verification

- [x] `gendoc.yml` YAML parses correctly with all fields present
- [x] `gendoc.yml.example` deploy.cloudflare section has `branch` and `gzip_json` with correct values
- [x] Both files have `branch: "main"` in the deploy.cloudflare section
- [x] Field order matches specification in both files
- [x] All pre-existing fields preserved unchanged in both files
- [x] gendoc.yml.example pre-existing YAML parse error at line 121 is unrelated and documented

## Self-Check: PASSED

- SUMMARY.md: exists at .planning/workstreams/gendoc/phases/07-cloudflare-pages-deploy-fix/07-03-SUMMARY.md
- Task 1 commit 97fec0a: verified in gendoc-template submodule
- Task 2 commit d180e46: verified in parent repository
- gendoc-template/gendoc.yml.example: exists, modified with branch + gzip_json
- gendoc.yml: exists, modified with branch field
