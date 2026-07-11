# Classification: gendoc-theme-loader/MIGRATION.md

**Type:** DOC
**Confidence:** HIGH
**Reasoning:** Step-by-step implementation guide — specifies exact file operations (copy, replace, delete, edit) with file paths and YAML snippets. No decisions to make, no alternatives evaluated, no formal spec structure.

**Title:** Theme Loader Migration
**Scope:** Add a `load-theme.py` hook to gendoc-template that selects theme CSS dynamically at build time. Includes two built-in presets (default/protocol), BYO custom theme support, and cleanup of the old hardcoded `stylesheets/theme.css`.

**Cross-references:** None (new feature, no dependency on existing phases beyond general template stability)
