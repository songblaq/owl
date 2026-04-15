"""``akasha status`` — at-a-glance vault report."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from akasha import __version__
from akasha.vault import MARKER_FILE, discover_vault, discovery_source
from akasha.entry import iter_entries
from akasha.graph import count_graph_edges


def show_status(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    source = discovery_source(vault_arg)

    info: dict = {
        "version": __version__,
        "vault": str(vault),
        "discovery": source,
        "vault_exists": vault.exists(),
        "marker_present": (vault / MARKER_FILE).exists() if vault.exists() else False,
        "index_present": (vault / "INDEX.md").exists() if vault.exists() else False,
        "graph_present": (vault / "GRAPH.tsv").exists() if vault.exists() else False,
        "aliases_present": (vault / "ALIASES.tsv").exists() if vault.exists() else False,
        "compiled_present": (vault / "compiled").exists() if vault.exists() else False,
        "counts": {},
    }

    if vault.exists():
        all_entries = iter_entries(vault, include_superseded=False)
        active = [e for e in all_entries if not e.deprecated]
        graph_edges = count_graph_edges(vault)
        compiled_dir = vault / "compiled"
        compiled_count = sum(1 for f in compiled_dir.glob("*.md") if f.is_file()) if compiled_dir.exists() else 0

        info["counts"] = {
            "entries": len(active),
            "graph_edges": graph_edges,
            "compiled_docs": compiled_count,
        }

    if json_out:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    print("akasha status")
    print("=============")
    print(f"  version:        {info['version']}")
    print(f"  vault:          {info['vault']}")
    print(f"    discovered via: {info['discovery']}")

    if not info["vault_exists"]:
        print(f"\n  vault does not exist: {vault}")
        print(f"    Run: akasha init {vault}")
        return 1

    print()
    print("Vault state:")
    print(f"  marker ({MARKER_FILE}):  {'yes' if info['marker_present'] else 'missing  (run `akasha init`)'}")
    print(f"  INDEX.md:                {'yes' if info['index_present'] else 'missing  (run `akasha index`)'}")
    print(f"  GRAPH.tsv:               {'yes' if info['graph_present'] else 'missing  (run `akasha index`)'}")
    print(f"  ALIASES.tsv:             {'yes' if info['aliases_present'] else 'missing  (optional)'}")
    print(f"  compiled/:               {'yes' if info['compiled_present'] else 'missing  (run `akasha compile`)'}")
    print()
    print("Counts:")
    for k, v in info.get("counts", {}).items():
        print(f"  {k:20s} {v}")

    next_steps = []
    if not info["marker_present"]:
        next_steps.append("Vault not initialized — run `akasha init`")
    elif not info["index_present"]:
        next_steps.append("No INDEX.md — run `akasha index` to build the entry catalog")
    elif info["counts"].get("entries", 0) == 0:
        next_steps.append("No entries yet. Populate with: python scripts/populate_from_facet_lattice.py")
    elif not info["compiled_present"]:
        next_steps.append("No compiled docs — run `akasha compile --dry-run` first, then `akasha compile`")
    if next_steps:
        print()
        print("Next steps:")
        for s in next_steps:
            print(f"  - {s}")

    return 0
