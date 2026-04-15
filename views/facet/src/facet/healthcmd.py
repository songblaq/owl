"""``facet health`` — coverage check: sources/ vs shard entries.

Scans sources/ for all files, then checks whether any shard entry references
each source. Reports sources with no corresponding entry as coverage gaps.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from facet.entry import iter_all_entries
from facet.vault import discover_vault


def run_health(vault_arg: Optional[str] = None, json_out: bool = False) -> int:
    import json as json_mod

    vault = discover_vault(vault_arg)
    if not vault.exists():
        print(f"error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    sources_dir = vault / "sources"
    if not sources_dir.exists():
        print(f"note: no sources/ directory in vault {vault}")
        return 0

    source_files = sorted(
        p for p in sources_dir.rglob("*") if p.is_file()
    )
    source_names = {p.name for p in source_files}
    source_stems = {p.stem for p in source_files}

    # Collect all source references from entries
    all_entries = iter_all_entries(vault, include_superseded=False)
    referenced: set = set()
    for e in all_entries:
        if e.source:
            # source field may be a filename or a path fragment
            ref = Path(e.source).name
            referenced.add(ref)
            referenced.add(Path(e.source).stem)

    missing: list = []
    for sf in source_files:
        if sf.name not in referenced and sf.stem not in referenced:
            missing.append(str(sf.relative_to(vault)))

    if json_out:
        payload = {
            "vault": str(vault),
            "total_sources": len(source_files),
            "total_entries": len(all_entries),
            "uncovered_sources": missing,
            "coverage_pct": round(
                100 * (len(source_files) - len(missing)) / max(len(source_files), 1), 1
            ),
        }
        print(json_mod.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("facet health")
    print("============")
    print(f"  vault:        {vault}")
    print(f"  sources:      {len(source_files)}")
    print(f"  entries:      {len(all_entries)}")
    coverage = 100 * (len(source_files) - len(missing)) / max(len(source_files), 1)
    print(f"  coverage:     {coverage:.1f}%")
    print()

    if not missing:
        print("All sources have at least one entry referencing them.")
        return 0

    print(f"Uncovered sources ({len(missing)}):")
    for src in missing:
        print(f"  - {src}")
    print()
    print("Next steps:")
    print("  - Create entries in the appropriate shard referencing these sources")
    print("  - Set `source: <filename>` in frontmatter to establish coverage")
    return 0
