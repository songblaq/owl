"""``cairn status`` — at-a-glance vault report."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from cairn import __version__
from cairn.entry import Entry, iter_entries
from cairn.vault import MARKER_FILE, discover_vault, discovery_source


def _count_files(directory: Path, pattern: str = "*") -> int:
    if not directory.exists():
        return 0
    return sum(1 for p in directory.rglob(pattern) if p.is_file())


def show_status(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    vault = discover_vault(vault_arg)
    source = discovery_source(vault_arg)

    info = {
        "version": __version__,
        "vault": str(vault),
        "discovery": source,
        "vault_exists": vault.exists(),
        "marker_present": (vault / MARKER_FILE).exists() if vault.exists() else False,
        "index_present": (vault / "INDEX.md").exists() if vault.exists() else False,
        "counts": {},
        "types": {},
    }

    if vault.exists():
        info["counts"] = {
            "entries": _count_files(vault / "entries", "*.md"),
            "sources": _count_files(vault / "sources", "*.md"),
            "superseded": _count_files(vault / "superseded", "*.md"),
        }
        # Breakdown by type
        entries = iter_entries(vault, include_superseded=False)
        type_counter: Counter = Counter()
        for e in entries:
            type_counter[e.type or "(untyped)"] += 1
        info["types"] = dict(type_counter)

    if json_out:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    # Human-readable
    print("cairn status")
    print("============")
    print(f"  version:        {info['version']}")
    print(f"  vault:          {info['vault']}")
    print(f"    discovered via: {info['discovery']}")

    if not info["vault_exists"]:
        print(f"\n  ✗ vault does not exist: {vault}")
        print(f"    Run: cairn init {vault}")
        return 1

    print()
    print("Vault state:")
    print(f"  marker ({MARKER_FILE}):   {'✓' if info['marker_present'] else '✗  (run `cairn init`)'}")
    print(f"  INDEX.md:                 {'✓' if info['index_present'] else '✗  (run `cairn index`)'}")
    print()
    print("Counts:")
    for k, v in info["counts"].items():
        print(f"  {k:12s} {v}")

    if info["types"]:
        print()
        print("By type:")
        for t, n in sorted(info["types"].items(), key=lambda x: -x[1]):
            print(f"  {t:20s} {n}")

    # Next-step hints
    next_steps = []
    if not info["marker_present"]:
        next_steps.append("Vault not initialized — run `cairn init`")
    elif not info["index_present"]:
        next_steps.append("No INDEX.md — run `cairn index` to build the brain's TOC")
    elif info["counts"].get("entries", 0) == 0:
        next_steps.append("No entries yet. Start writing atomic claims into entries/")
    if next_steps:
        print()
        print("Next steps:")
        for s in next_steps:
            print(f"  - {s}")

    return 0
