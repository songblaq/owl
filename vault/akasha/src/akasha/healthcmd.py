"""``akasha health`` — vault coverage check.

Reports:
- entries vs sources coverage
- compiled docs vs topics coverage
- graph connectivity stats
"""
from __future__ import annotations

import json as json_mod
import sys
from pathlib import Path
from typing import Optional

from akasha.entry import iter_entries
from akasha.graph import load_graph
from akasha.vault import discover_vault


def run_health(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    all_entries = iter_entries(vault, include_superseded=False)
    active = [e for e in all_entries if not e.deprecated]

    # Source coverage
    sources_dir = vault / "sources"
    source_files = sorted(p for p in sources_dir.rglob("*") if p.is_file()) if sources_dir.exists() else []
    referenced: set = set()
    for e in active:
        if e.source:
            referenced.add(Path(e.source).name)
            referenced.add(Path(e.source).stem)
    uncovered_sources = [
        str(sf.relative_to(vault)) for sf in source_files
        if sf.name not in referenced and sf.stem not in referenced
    ]

    # Topic coverage (entries with at least one topic)
    no_topic = [e for e in active if not e.topics]

    # Graph stats
    graph = load_graph(vault)
    entries_with_edges = len(graph)
    total_edges = sum(len(v) for v in graph.values())

    # Compiled docs
    compiled_dir = vault / "compiled"
    compiled_count = sum(1 for f in compiled_dir.glob("*.md") if f.is_file()) if compiled_dir.exists() else 0

    source_coverage = round(
        100 * (len(source_files) - len(uncovered_sources)) / max(len(source_files), 1), 1
    )
    topic_coverage = round(100 * (len(active) - len(no_topic)) / max(len(active), 1), 1)

    if json_out:
        payload = {
            "vault": str(vault),
            "total_entries": len(active),
            "total_sources": len(source_files),
            "source_coverage_pct": source_coverage,
            "uncovered_sources": uncovered_sources,
            "entries_without_topic": [e.id for e in no_topic],
            "topic_coverage_pct": topic_coverage,
            "graph_nodes": entries_with_edges,
            "graph_total_edges": total_edges,
            "compiled_docs": compiled_count,
        }
        print(json_mod.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("akasha health")
    print("=============")
    print(f"  vault:          {vault}")
    print(f"  entries:        {len(active)}")
    print(f"  sources:        {len(source_files)}")
    print(f"  source coverage:{source_coverage:.1f}%")
    print(f"  topic coverage: {topic_coverage:.1f}% ({len(no_topic)} entries without topic)")
    print(f"  graph nodes:    {entries_with_edges} (of {len(active)} entries have edges)")
    print(f"  graph edges:    {total_edges} total")
    print(f"  compiled docs:  {compiled_count}")
    print()

    issues = []
    if uncovered_sources:
        print(f"Uncovered sources ({len(uncovered_sources)}):")
        for s in uncovered_sources[:10]:
            print(f"  - {s}")
        if len(uncovered_sources) > 10:
            print(f"  ... and {len(uncovered_sources) - 10} more")
        print()
        issues.append("Some sources have no entries referencing them")

    if no_topic:
        print(f"Entries without topic ({len(no_topic)}):")
        for e in no_topic[:10]:
            print(f"  - {e.id}")
        if len(no_topic) > 10:
            print(f"  ... and {len(no_topic) - 10} more")
        print()
        issues.append("Some entries have no topics — add topics: [...] to frontmatter")

    if not issues:
        print("Vault looks healthy.")
        return 0

    print("Next steps:")
    for issue in issues:
        print(f"  - {issue}")
    return 0
