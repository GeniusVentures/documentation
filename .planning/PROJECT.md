# Project: GNUS.AI Documentation

## What This Is

The official documentation site for the GNUS.AI ecosystem (`docs.gnus.ai`), built with MkDocs + Material theme. This project currently has embedded build infrastructure (scripts, javascripts, stylesheets, mkdocs config) that was the origin of the `gendoc-template` — a reusable documentation template now used as a git submodule by sibling projects (GeniusCogntiveSystem).

## What This Is Not

- Not a code SDK or library
- Not a new documentation site from scratch
- Not a content rewrite — content stays as-is

## Core Value

**ONE thing that must work:** The documentation site must continue to build and deploy identically (same URLs, same appearance, same content) after refactoring to use the `gendoc-template` submodule, PLUS gain the Ask AI widget on all pages.

## Context

### Current State
- MkDocs 1.6.1 + Material theme 9.5.27
- Custom `javascripts/` (breadcrumbs, external-links, mathjax, mermaid, nav-state)
- Custom `stylesheets/extra.css`
- Build scripts: `scripts/cf-build.sh`, `scripts/cf-build.bat`
- Doxygen + doxybook2 pipeline for SuperGenius API reference
- Hand-written docs in `docs/` (about-gnus.ai, technical-information)
- `.gitmodules` already has submodules: `docs` (gitbook), `sg-docs`
- Deployed to Cloudflare Pages

### Target State (after refactoring)
- `gendoc-template` added as a git submodule (same pattern as GeniusCogntiveSystem)
- `gendoc.yml` configuration file at project root (like GeniusCogntiveSystem's)
- `mkdocs.yml` simplified to use gendoc-template hooks (`load-gendoc-config.py`, `clean-nav.py`, `copy-assets.py`)
- Duplicate assets (javascripts, stylesheets, scripts) removed where gendoc-template provides them
- Ask AI widget enabled on all pages via `gendoc.yml` → `llms.ask` config
- Build scripts updated to work with submodule-based layout

## Requirements

### Validated

(None yet — existing site is the baseline)

### Active

- [ ] **REFACTOR-01**: Add `gendoc-template` as a git submodule
- [ ] **REFACTOR-02**: Create `gendoc.yml` config replacing embedded mkdocs settings
- [ ] **REFACTOR-03**: Update `mkdocs.yml` to use gendoc-template hooks and inherit from submodule
- [ ] **REFACTOR-04**: Remove duplicate assets now provided by gendoc-template (javascripts, stylesheets, scripts)
- [ ] **REFACTOR-05**: Enable Ask AI widget in `gendoc.yml` llms.ask configuration
- [ ] **REFACTOR-06**: Update build scripts (`cf-build.sh`, `cf-build.bat`) for submodule layout
- [ ] **REFACTOR-07**: Verify site builds identically (same content, URLs, appearance)
- [ ] **REFACTOR-08**: Verify Ask AI widget appears and functions on all pages
- [ ] **REFACTOR-09**: Update `DOCUMENTATION_CHANGES.md` with refactoring summary

### Out of Scope

- Content changes to documentation pages — content stays exactly as-is
- Changing the theme or visual design of the site
- Adding new documentation sections
- Changing the deployment pipeline (Cloudflare Pages)
- Refactoring the API reference generation (Doxygen → doxybook2 pipeline)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use gendoc-template submodule | Already extracted from this code, proven in GeniusCogntiveSystem | Pending |
| Sequential execution | Dependent steps (submodule → config → build) | Pending |
| Coarse granularity | Well-understood refactoring, few distinct phases | Pending |
| Keep content unchanged | Risk mitigation — refactor infrastructure only | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-08 after initialization*
