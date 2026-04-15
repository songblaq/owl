"""``facet status`` — at-a-glance vault report with per-shard breakdown."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from facet import __version__
from facet.vault import MARKER_FILE, discover_vault, discovery_source, iter_shards
from facet.entry import iter_shard_entries


def show_status(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    source = discovery_source(vault_arg)

    info: dict = {
        "version": __version__,
        "vault": str(vault),
        "discovery": source,
        "vault_exists": vault.exists(),
        "marker_present": (vault / MARKER_FILE).exists() if vault.exists() else False,
        "manifest_present": (vault / "MANIFEST.md").exists() if vault.exists() else False,
        "aliases_present": (vault / "ALIASES.tsv").exists() if vault.exists() else False,
        "shards": {},
        "total_entries": 0,
        "sources": 0,
    }

    if vault.exists():
        total = 0
        for shard_name, shard_path in iter_shards(vault):
            entries = iter_shard_entries(shard_path, shard_name)
            count = len([e for e in entries if not e.deprecated])
            info["shards"][shard_name] = count
            total += count
        info["total_entries"] = total
        sources_dir = vault / "sources"
        if sources_dir.exists():
            info["sources"] = sum(1 for p in sources_dir.rglob("*") if p.is_file())

    if json_out:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    print("facet status")
    print("============")
    print(f"  version:        {info['version']}")
    print(f"  vault:          {info['vault']}")
    print(f"    discovered via: {info['discovery']}")

    if not info["vault_exists"]:
        print(f"\n  vault does not exist: {vault}")
        print(f"    Run: facet init {vault}")
        return 1

    print()
    print("Vault state:")
    print(f"  marker ({MARKER_FILE}):  {'yes' if info['marker_present'] else 'missing  (run `facet init`)'}")
    print(f"  MANIFEST.md:             {'yes' if info['manifest_present'] else 'missing  (run `facet index`)'}")
    print(f"  ALIASES.tsv:             {'yes' if info['aliases_present'] else 'missing  (optional)'}")
    print()
    print(f"Shards ({len(info['shards'])} total, {info['total_entries']} entries):")
    if info["shards"]:
        for shard_name, count in sorted(info["shards"].items()):
            print(f"  {shard_name:24s} {count} entries")
    else:
        print("  (no shards yet)")
    print()
    print(f"Sources: {info['sources']}")

    next_steps = []
    if not info["marker_present"]:
        next_steps.append("Vault not initialized — run `facet init`")
    elif not info["manifest_present"]:
        next_steps.append("No MANIFEST.md — run `facet index` to build the table of contents")
    elif info["total_entries"] == 0:
        next_steps.append("No entries yet. Create shards/ subdirs and add atomic claims.")
    if next_steps:
        print("Next steps:")
        for s in next_steps:
            print(f"  - {s}")

    return 0
