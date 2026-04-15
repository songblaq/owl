#!/usr/bin/env python3
"""Migrate non-empty edges from rehalf-vault → facet-vault.

For each entry in ~/rehalf-vault/shards/**/*.md that has non-empty edges:
1. Find matching entry in ~/facet-vault/shards/ by relative path (same shard + filename)
2. Add edges: field to the facet entry's YAML frontmatter
3. Report what was migrated

Slug matching: rehalf and facet share identical shard structure and filenames
(rehalf was copied from facet), so relative path matching is exact.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REHALF_VAULT = Path.home() / "rehalf-vault"
FACET_VAULT = Path.home() / "facet-vault"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def extract_edges_block(content: str) -> Optional[List[str]]:
    """Extract raw edge lines from YAML frontmatter. Returns None if no non-empty edges."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None

    front_raw = m.group(1)
    lines = front_raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.strip() == "edges:":
            # Block list
            edge_items: List[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  - ") or lines[i].startswith("\t- ")):
                edge_items.append(lines[i].rstrip())
                i += 1
            return edge_items if edge_items else None
        elif line.strip().startswith("edges:") and not line.strip().endswith(":"):
            inner_part = line.split(":", 1)[1].strip()
            if inner_part and inner_part != "[]":
                # Inline edges list
                return [inner_part]
            return None
        i += 1
    return None


def inject_edges(content: str, edge_lines: List[str]) -> str:
    """Inject or replace edges block in YAML frontmatter."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return content

    front_raw = m.group(1)
    body = m.group(2)
    front_lines = front_raw.splitlines()

    new_front: List[str] = []
    edges_injected = False
    i = 0
    while i < len(front_lines):
        line = front_lines[i].rstrip()
        if line.strip() == "edges:":
            # Replace block
            new_front.append("edges:")
            new_front.extend(edge_lines)
            edges_injected = True
            i += 1
            # Skip old edge items
            while i < len(front_lines) and (
                front_lines[i].startswith("  - ") or front_lines[i].startswith("\t- ")
            ):
                i += 1
            continue
        elif line.strip().startswith("edges:") and not line.strip().endswith(":"):
            # Replace inline
            new_front.append("edges:")
            new_front.extend(edge_lines)
            edges_injected = True
            i += 1
            continue
        new_front.append(line)
        i += 1

    if not edges_injected:
        # Insert before 'created:' if present, else append
        result: List[str] = []
        inserted = False
        for line in new_front:
            if not inserted and line.strip().startswith("created:"):
                result.append("edges:")
                result.extend(edge_lines)
                inserted = True
            result.append(line)
        if not inserted:
            result.append("edges:")
            result.extend(edge_lines)
        new_front = result

    new_front_str = "\n".join(new_front)
    return f"---\n{new_front_str}\n---\n{body}"


def main() -> int:
    print("migrate_edges_from_rehalf: rehalf-vault → facet-vault")
    print("=" * 55)
    print(f"  source:      {REHALF_VAULT}")
    print(f"  destination: {FACET_VAULT}")
    print()

    if not REHALF_VAULT.exists():
        print(f"error: rehalf-vault not found: {REHALF_VAULT}", file=sys.stderr)
        return 1
    if not FACET_VAULT.exists():
        print(f"error: facet-vault not found: {FACET_VAULT}", file=sys.stderr)
        return 1

    rehalf_shards = REHALF_VAULT / "shards"
    facet_shards = FACET_VAULT / "shards"

    if not rehalf_shards.exists():
        print(f"error: {rehalf_shards} not found", file=sys.stderr)
        return 1

    migrated = 0
    skipped_no_match = 0
    skipped_no_edges = 0

    for rehalf_file in sorted(rehalf_shards.rglob("*.md")):
        if not rehalf_file.is_file() or rehalf_file.name == "_index.md":
            continue

        try:
            rehalf_content = rehalf_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        edge_lines = extract_edges_block(rehalf_content)
        if not edge_lines:
            skipped_no_edges += 1
            continue

        # Find matching facet entry by relative path from shards/
        rel = rehalf_file.relative_to(rehalf_shards)
        facet_file = facet_shards / rel

        if not facet_file.exists():
            print(f"  WARNING: no facet match for {rel}")
            skipped_no_match += 1
            continue

        try:
            facet_content = facet_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            print(f"  WARNING: could not read {facet_file}")
            skipped_no_match += 1
            continue

        new_content = inject_edges(facet_content, edge_lines)
        if new_content == facet_content:
            print(f"  unchanged (already has identical edges): {rel}")
            continue

        facet_file.write_text(new_content, encoding="utf-8")
        print(f"  migrated edges: {rel} ({len(edge_lines)} edge(s))")
        migrated += 1

    print()
    print("Migration summary:")
    print(f"  edges migrated:     {migrated}")
    print(f"  skipped (no edges): {skipped_no_edges}")
    print(f"  skipped (no match): {skipped_no_match}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
