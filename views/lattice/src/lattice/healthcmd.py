"""``lattice health`` — coverage check: sources/ vs entries.

Writes coverage.tsv to vault root listing each source file and whether
it has at least one entry referencing it.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from lattice.entry import iter_entries
from lattice.vault import discover_vault


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

    source_files = sorted(p for p in sources_dir.rglob("*") if p.is_file())

    all_entries = iter_entries(vault, include_superseded=False)
    referenced: set = set()
    for e in all_entries:
        if e.source:
            ref = Path(e.source).name
            referenced.add(ref)
            referenced.add(Path(e.source).stem)

    rows = []
    for sf in source_files:
        covered = sf.name in referenced or sf.stem in referenced
        rows.append((str(sf.relative_to(vault)), "covered" if covered else "missing"))

    # Write coverage.tsv
    coverage_path = vault / "coverage.tsv"
    lines = ["# source_path\tstatus"]
    for path_str, status in rows:
        lines.append(f"{path_str}\t{status}")
    coverage_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    missing = [r for r in rows if r[1] == "missing"]

    if json_out:
        payload = {
            "vault": str(vault),
            "total_sources": len(source_files),
            "total_entries": len(all_entries),
            "covered": len(source_files) - len(missing),
            "uncovered": [r[0] for r in missing],
            "coverage_pct": round(
                100 * (len(source_files) - len(missing)) / max(len(source_files), 1), 1
            ),
            "coverage_tsv": str(coverage_path),
        }
        print(json_mod.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("lattice health")
    print("==============")
    print(f"  vault:          {vault}")
    print(f"  sources:        {len(source_files)}")
    print(f"  entries:        {len(all_entries)}")
    coverage = 100 * (len(source_files) - len(missing)) / max(len(source_files), 1)
    print(f"  coverage:       {coverage:.1f}%")
    print(f"  coverage.tsv:   {coverage_path}")
    print()

    if not missing:
        print("All sources have at least one entry referencing them.")
        return 0

    print(f"Uncovered sources ({len(missing)}):")
    for path_str, _ in missing:
        print(f"  - {path_str}")
    print()
    print("Next steps:")
    print("  - Create entries in entries/ referencing these sources")
    print("  - Set `source: <filename>` in frontmatter to establish coverage")
    return 0
