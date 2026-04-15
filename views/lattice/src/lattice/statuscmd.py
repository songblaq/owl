"""``lattice status`` — at-a-glance vault report."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from lattice import __version__
from lattice.vault import MARKER_FILE, discover_vault, discovery_source
from lattice.entry import iter_entries


def _count_tsv_lines(path: Path) -> int:
    """Count non-comment, non-empty lines in a TSV file."""
    if not path.exists():
        return 0
    return sum(
        1 for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )


def show_status(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    source = discovery_source(vault_arg)

    manifold_path = vault / "MANIFOLD.tsv"
    bloom_path = vault / "BLOOM.txt"
    graph_path = vault / "GRAPH.tsv"
    map_path = vault / "MAP.md"

    info: dict = {
        "version": __version__,
        "vault": str(vault),
        "discovery": source,
        "vault_exists": vault.exists(),
        "marker_present": (vault / MARKER_FILE).exists() if vault.exists() else False,
        "manifold_present": manifold_path.exists() if vault.exists() else False,
        "bloom_present": bloom_path.exists() if vault.exists() else False,
        "graph_present": graph_path.exists() if vault.exists() else False,
        "map_present": map_path.exists() if vault.exists() else False,
        "counts": {},
    }

    if vault.exists():
        entries = iter_entries(vault, include_superseded=False)
        active_entries = [e for e in entries if not e.deprecated]
        manifold_size = _count_tsv_lines(manifold_path)
        graph_edges = _count_tsv_lines(graph_path)
        bloom_tokens = sum(
            1 for line in bloom_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ) if bloom_path.exists() else 0
        sources_dir = vault / "sources"
        sources_count = sum(1 for p in sources_dir.rglob("*") if p.is_file()) if sources_dir.exists() else 0

        info["counts"] = {
            "entries": len(active_entries),
            "manifold_ngrams": manifold_size,
            "bloom_tokens": bloom_tokens,
            "graph_edges": graph_edges,
            "sources": sources_count,
        }

    if json_out:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    print("lattice status")
    print("==============")
    print(f"  version:        {info['version']}")
    print(f"  vault:          {info['vault']}")
    print(f"    discovered via: {info['discovery']}")

    if not info["vault_exists"]:
        print(f"\n  vault does not exist: {vault}")
        print(f"    Run: lattice init {vault}")
        return 1

    print()
    print("Vault state:")
    print(f"  marker ({MARKER_FILE}):  {'yes' if info['marker_present'] else 'missing  (run `lattice init`)'}")
    print(f"  MANIFOLD.tsv:            {'yes' if info['manifold_present'] else 'missing  (run `lattice index`)'}")
    print(f"  BLOOM.txt:               {'yes' if info['bloom_present'] else 'missing  (run `lattice index`)'}")
    print(f"  GRAPH.tsv:               {'yes' if info['graph_present'] else 'missing  (run `lattice index`)'}")
    print(f"  MAP.md:                  {'yes' if info['map_present'] else 'missing  (run `lattice index`)'}")
    print()
    print("Counts:")
    for k, v in info.get("counts", {}).items():
        print(f"  {k:20s} {v}")

    next_steps = []
    if not info["marker_present"]:
        next_steps.append("Vault not initialized — run `lattice init`")
    elif not info["manifold_present"]:
        next_steps.append("No MANIFOLD.tsv — run `lattice index` to build the search index")
    elif info["counts"].get("entries", 0) == 0:
        next_steps.append("No entries yet. Add atomic claims to entries/")
    if next_steps:
        print()
        print("Next steps:")
        for s in next_steps:
            print(f"  - {s}")

    return 0
