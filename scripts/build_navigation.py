#!/usr/bin/env python3
"""
Build navigation structure from index_*.md files.
Parses markdown lists and links to generate SUMMARY_EXT.md files in each category directory.
"""

import glob
import os
import re
import sys


def _is_up_to_date(target_path, source_path, extra_sources=None):
    """
    Return True if target_path exists and is newer than all source paths.
    """
    if not os.path.exists(target_path):
        return False
    target_mtime = os.path.getmtime(target_path)
    source_paths = [source_path]
    if extra_sources:
        source_paths.extend(extra_sources)
    for source in source_paths:
        if os.path.exists(source) and os.path.getmtime(source) > target_mtime:
            return False
    return True


def parse_markdown_links(md_content):
    """
    Parse markdown list items with links into a hierarchical structure.
    Returns list of tuples: (indent_level, link_text, link_url)
    Indent is based on consecutive asterisks and/or leading spaces.
    """
    items = []

    for line in md_content.split('\n'):
        # Skip empty lines and non-list items
        if not line.strip() or not line.lstrip().startswith('*'):
            continue

        # Count leading spaces to determine nesting level
        # Each level of nesting is typically 4 spaces
        leading_spaces = len(line) - len(line.lstrip())
        indent = leading_spaces // 4

        # Extract link: [text](url)
        match = re.search(r'\[([^\]]+)\]\(([^)#]+)', line)
        if match:
            text = match.group(1)
            url = match.group(2)
            items.append((indent, text, url))

    return items


def _has_linked_descendant(items, parent_index):
    """
    Return True if any item after parent_index with a deeper indent has a URL.
    Stops as soon as the indent returns to or below the parent's indent.
    """
    parent_indent = items[parent_index][0]
    for j in range(parent_index + 1, len(items)):
        if items[j][0] <= parent_indent:
            break
        if items[j][2]:  # has a URL
            return True
    return False


def _prune_empty_labels(items):
    """
    Remove label-only items (url=None) whose entire subtree contains no
    linked items.  Iterates repeatedly until no more pruning is possible,
    handling chains of empty parents (e.g. ipfs_lite -> ipfs -> <nothing>).
    """
    changed = True
    while changed:
        changed = False
        pruned = []
        for i, item in enumerate(items):
            indent, text, url = item
            if not url and not _has_linked_descendant(items, i):
                changed = True  # drop this item, loop again
            else:
                pruned.append(item)
        items = pruned
    return items


def build_literate_nav(items):
    """
    Convert list of (indent, text, url) tuples into a Markdown list.
    Uses 4 spaces per indent level to match SUMMARY.md formatting.

    Dir entries have a dir_*.md url — section-index plugin makes those
    clickable section headers that also show the dir page in the right pane.
    """
    items = _prune_empty_labels(items)
    lines = []
    for indent, text, url in items:
        indent_str = "    " * indent
        if url:
            lines.append(f"{indent_str}- [{text}]({url})")
        else:
            lines.append(f"{indent_str}- {text}")
    return "<!--nav-->\n\n" + "\n".join(lines) + "\n"


def parse_index_file(filepath):
    """
    Parse a single index_*.md file and return list of navigation entries.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    items = parse_markdown_links(content)
    return items


def _write_root_summary(supergenius_dir, categories):
    """
    Write SuperGenius/SUMMARY_EXT.md with links to category subdirectories.
    """
    summary_path = os.path.join(supergenius_dir, "SUMMARY_EXT.md")
    lines = ["<!--nav-->", ""]
    for category in categories:
        lines.append(f"- [{category}]({category}/)")
    content = "\n".join(lines) + "\n"
    with open(summary_path, 'w') as f:
        f.write(content)


def write_readme(supergenius_dir, categories):
    """
    Write SuperGenius/README.md as the landing page for the SuperGenius nav entry.
    """
    readme_path = os.path.join(supergenius_dir, "README.md")
    lines = [
        "# SuperGenius Code\n",
        "Browse the SuperGenius C++ source code documentation generated from Doxygen.\n",
    ]
    for cat in categories:
        lines.append(f"- [{cat}]({cat}/)")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")


def write_root_nav(docs_dir, supergenius_rel="SuperGenius"):
    """
    Merge docs/SUMMARY.md with the SuperGenius Code nav entry and write
    docs/SUMMARY_EXT.md for literate-nav to consume.

    literate-nav only reads the **last** ``<ul>`` in the nav file, so the
    entire nav must be one unbroken list — ``##`` headings must not be used
    because they split the document into multiple ``<ul>`` blocks.

    GitBook ``## Section`` headings are converted to plain unlinked list items
    at indent 0.  Their children (originally 2-space indented) are shifted to
    4-space indent so literate-nav recognises them as nested children of the
    section label.  Deeper levels are shifted left by 2 spaces uniformly.

    The ``# Table of contents`` title is dropped (not valid in a list).

    The SuperGenius Code entry is appended as a matching plain unlinked list
    item with each category as a 4-space-indented child.
    """
    summary_file     = os.path.join(docs_dir, "SUMMARY.md")
    summary_ext_file = os.path.join(docs_dir, "SUMMARY_EXT.md")
    supergenius_dir  = os.path.join(docs_dir, supergenius_rel)

    if not os.path.exists(summary_file):
        raise FileNotFoundError(f"SUMMARY.md not found at {summary_file}")

    with open(summary_file, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    # Drop the ``# Title`` line — not valid in a literate-nav list.
    # Convert ``## Section`` headings to plain unlinked list items so the
    # entire nav is one unbroken <ul> (literate-nav only reads the last <ul>
    # in the document; multiple ## headings produce multiple <ul> blocks and
    # only the final one is used).
    # Strip the 2-space GitBook indent so items nest correctly under their
    # section label.  Check longest patterns first to avoid partial matches.
    converted_lines = []
    for line in raw_lines:
        stripped = line.rstrip('\n')
        if re.match(r'^# ', stripped) and not re.match(r'^## ', stripped):
            # Drop level-1 title only.
            pass
        elif re.match(r'^## ', stripped):
            # Section divider → unlinked top-level list item.
            label = stripped[3:].strip()
            converted_lines.append(f"- {label}\n")
        elif re.match(r'^\s*- ', stripped):
            # All list items shift down one level (+4 spaces) because the
            # ## section heading is now a level-0 list item and all content
            # must be nested under it.
            converted_lines.append("    " + line)
        else:
            converted_lines.append(line)

    content = "".join(converted_lines)

    # Build the category children lines (4-space indent = children of the section label).
    category_lines = []
    for entry in sorted(os.scandir(supergenius_dir), key=lambda e: e.name):
        if entry.is_dir() and os.path.exists(os.path.join(entry.path, "SUMMARY_EXT.md")):
            category_lines.append(f"    - [{entry.name}]({supergenius_rel}/{entry.name}/)")

    # Plain unlinked list item — same pattern as the other section labels.
    sg_block = "\n- ⌨️ SuperGenius Code\n"
    if category_lines:
        sg_block += "\n".join(category_lines) + "\n"

    extended = content.rstrip() + sg_block

    with open(summary_ext_file, 'w', encoding='utf-8') as f:
        f.write(extended)


def _normalize_url(url, category_dir, category_path, link_text):
    """
    Normalize a link target to be relative to the category directory.

    Doxybook generates absolute paths like /SuperGenius/Files/d5/df0/foo/
    literate-nav treats any absolute path as an external resource, so we
    must strip the leading /SuperGenius/<category>/ prefix to produce a
    plain relative path like d5/df0/foo/ that literate-nav resolves
    correctly within the category's SUMMARY_EXT.md.

    Dir index entries (dir_*/ or dir_*.md) are kept as links — their pages
    list the files in that directory and are useful content.
    """
    if not url:
        return None

    normalized = url.replace("\\", "/").lstrip("/")

    # Strip leading SuperGenius/ prefix (with or without leading slash).
    if normalized.startswith("SuperGenius/"):
        normalized = normalized[len("SuperGenius/"):]

    # Drop cross-category links.  Doxybook's index_classes.md can reference
    # entries in Namespaces/, Files/, etc.  Those paths don't exist under the
    # current category directory, so literate-nav resolves them wrongly.
    # Each category's own SUMMARY_EXT.md handles its own entries.
    known_categories = {"Classes", "Files", "Namespaces", "Modules", "Pages", "Examples"}
    first_segment = normalized.split("/")[0]
    if first_segment in known_categories and first_segment != category_dir:
        return None

    # Strip leading category prefix e.g. "Files/".
    category_prefix = f"{category_dir}/"
    if normalized.startswith(category_prefix):
        normalized = normalized[len(category_prefix):]

    # Strip trailing slash from dir_* entries and add .md so literate-nav
    # treats them as a direct page link (section index) rather than a
    # directory cross-link that recurses looking for a child SUMMARY_EXT.md.
    bare = normalized.rstrip("/").split("#")[0]
    if os.path.basename(bare).startswith("dir_"):
        normalized = bare + ".md"

    # Resolve doxybook hash-suffixed files.  Doxybook sometimes appends a
    # hash to the filename (e.g. namespacesgns_1_1scale_1_1_0d176...md) but
    # the index links to the unhashed stem with a trailing slash.  If the
    # normalized path ends with / and no real directory exists at that path,
    # look for a .md file whose name starts with the same stem.
    if normalized.endswith("/"):
        stem = os.path.basename(normalized.rstrip("/"))
        parent_rel = os.path.dirname(normalized.rstrip("/"))
        parent_abs = os.path.join(category_path, parent_rel)
        candidate_dir = os.path.join(category_path, normalized.rstrip("/"))
        if not os.path.isdir(candidate_dir):
            matches = glob.glob(os.path.join(parent_abs, stem + "*.md"))
            if len(matches) == 1:
                # Use the relative path to the matched file from category_path.
                normalized = os.path.relpath(matches[0], category_path).replace("\\", "/")
            elif len(matches) > 1:
                # Multiple matches — pick the shortest name (closest to original).
                matches.sort(key=lambda p: len(os.path.basename(p)))
                normalized = os.path.relpath(matches[0], category_path).replace("\\", "/")

    return normalized or None


def _needs_nav_marker_regen(summary_path):
    """
    Return True if the summary file is missing the nav marker.
    """
    if not os.path.exists(summary_path):
        return True
    with open(summary_path, 'r', encoding='utf-8') as handle:
        first_line = handle.readline().strip()
    return first_line != "<!--nav-->"



def generate_category_pages(supergenius_dir, force=False):
    """
    Generate SUMMARY_EXT.md files in each category directory.
    Maps index_*.md to category directories.
    """
    index_to_category = {
        'index_classes.md':    'Classes',
        'index_examples.md':   'Examples',
        'index_files.md':      'Files',
        'index_groups.md':     'Modules',
        'index_namespaces.md': 'Namespaces',
        'index_pages.md':      'Pages',
    }

    generated   = []
    categories  = []
    any_updated = False
    script_path = os.path.abspath(__file__)

    for index_filename, category_dir in index_to_category.items():
        index_filepath = os.path.join(supergenius_dir, index_filename)
        category_path  = os.path.join(supergenius_dir, category_dir)

        if not os.path.exists(index_filepath) or not os.path.isdir(category_path):
            continue

        summary_file = os.path.join(category_path, "SUMMARY_EXT.md")

        # Skip all expensive work if nothing has changed.
        if not force and _is_up_to_date(summary_file, index_filepath, [script_path]):
            if not _needs_nav_marker_regen(summary_file):
                categories.append(category_dir)
                continue

        items = parse_index_file(index_filepath)
        if not items:
            continue

        normalized_items = [
            (indent, text, _normalize_url(url, category_dir, category_path, text))
            for indent, text, url in items
        ]
        if not normalized_items:
            continue

        # Prepend README.md as first nav entry so section-index makes the
        # category header a clickable link to the index page.
        nav_lines = build_literate_nav(normalized_items)
        nav_lines = "<!--nav-->\n\n- [" + category_dir + "](README.md)\n" + nav_lines[len("<!--nav-->\n\n"):]

        with open(summary_file, 'w') as f:
            f.write(nav_lines)

        # Symlink index_*.md as README.md in the category dir so the section
        # header has a landing page without duplicating content.
        # Use a relative target so the symlink is portable.
        readme_path = os.path.join(category_path, "README.md")
        if os.path.islink(readme_path) or os.path.exists(readme_path):
            os.remove(readme_path)
        rel_target = os.path.relpath(index_filepath, category_path)
        os.symlink(rel_target, readme_path)

        any_updated = True
        categories.append(category_dir)
        generated.append((summary_file, len(items)))
        print(f"Generated {summary_file} ({len(items)} entries)")

    if categories:
        root_summary = os.path.join(supergenius_dir, "SUMMARY_EXT.md")
        if force or any_updated or not os.path.exists(root_summary):
            _write_root_summary(supergenius_dir, categories)
        write_root_nav(os.path.dirname(supergenius_dir))

    return generated



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build SUMMARY_EXT.md navigation files.")
    parser.add_argument("supergenius_dir", help="Path to docs/SuperGenius directory")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if up to date")
    args = parser.parse_args()

    if not os.path.isdir(args.supergenius_dir):
        print(f"Error: Directory not found: {args.supergenius_dir}", file=sys.stderr)
        sys.exit(1)

    generated = generate_category_pages(args.supergenius_dir, force=args.force)

    if generated:
        print(f"\nSuccessfully generated {len(generated)} SUMMARY_EXT.md files")
        sys.exit(0)
    else:
        print("Error: No SUMMARY_EXT.md files were generated", file=sys.stderr)
        sys.exit(1)

