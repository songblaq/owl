#!/usr/bin/env python3
"""Populate ~/akasha-vault from facet and lattice vaults.

Steps:
1. Copy ~/facet-vault/shards/**/*.md -> ~/akasha-vault/entries/ (flatten, prefix with shard)
2. Copy ~/lattice-vault/entries/*.md -> ~/akasha-vault/entries/ (merge, slug dedup)
3. Copy ~/facet-vault/ALIASES.tsv -> ~/akasha-vault/ALIASES.tsv
4. Run `akasha index` (builds INDEX.md + GRAPH.tsv)
5. Run `akasha compile --dry-run` (show topics, no LLM call)

Note: LLM compile is NOT run automatically. Cost is non-zero.
After reviewing the dry-run output, run: akasha compile
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


FACET_VAULT = Path.home() / "facet-vault"
LATTICE_VAULT = Path.home() / "lattice-vault"
AKASHA_VAULT = Path.home() / "akasha-vault"


def _copy_facet_entries(dst_entries: Path) -> int:
    """Flatten facet shards/**/*.md -> akasha entries/ with shard prefix."""
    facet_shards = FACET_VAULT / "shards"
    if not facet_shards.exists():
        print(f"  [skip] facet shards not found: {facet_shards}")
        return 0

    count = 0
    collisions = 0
    for shard_dir in sorted(facet_shards.iterdir()):
        if not shard_dir.is_dir():
            continue
        shard_name = shard_dir.name
        for md_file in sorted(shard_dir.rglob("*.md")):
            if md_file.is_file() and md_file.name != "_index.md":
                # Prefix with shard name to avoid collisions
                dest_name = f"{shard_name}--{md_file.stem}.md"
                dest = dst_entries / dest_name
                if dest.exists():
                    collisions += 1
                    print(f"  [skip collision] {dest_name}")
                    continue
                shutil.copy2(md_file, dest)
                count += 1

    print(f"  Copied {count} facet entries ({collisions} collisions skipped)")
    return count


def _copy_lattice_entries(dst_entries: Path) -> int:
    """Copy lattice entries/*.md -> akasha entries/ with lattice-- prefix."""
    lattice_entries = LATTICE_VAULT / "entries"
    if not lattice_entries.exists():
        print(f"  [skip] lattice entries not found: {lattice_entries}")
        return 0

    count = 0
    collisions = 0
    for md_file in sorted(lattice_entries.rglob("*.md")):
        if not md_file.is_file():
            continue
        dest_name = f"lattice--{md_file.stem}.md"
        dest = dst_entries / dest_name
        if dest.exists():
            collisions += 1
            print(f"  [skip collision] {dest_name}")
            continue
        shutil.copy2(md_file, dest)
        count += 1

    print(f"  Copied {count} lattice entries ({collisions} collisions skipped)")
    return count


def _copy_aliases() -> bool:
    """Copy ALIASES.tsv from facet vault."""
    src = FACET_VAULT / "ALIASES.tsv"
    dst = AKASHA_VAULT / "ALIASES.tsv"
    if not src.exists():
        print(f"  [skip] ALIASES.tsv not found: {src}")
        return False
    shutil.copy2(src, dst)
    print(f"  Copied ALIASES.tsv ({src.stat().st_size} bytes)")
    return True


def _run_cmd(cmd: list) -> int:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> int:
    print("akasha populate — from facet + lattice vaults")
    print("=" * 50)

    # Ensure akasha vault is initialized
    if not AKASHA_VAULT.exists():
        print(f"\nInitializing vault: {AKASHA_VAULT}")
        rc = _run_cmd(["akasha", "init"])
        if rc != 0:
            print("error: akasha init failed", file=sys.stderr)
            return rc
    else:
        print(f"\nUsing existing vault: {AKASHA_VAULT}")
        # Ensure entries/ subdir exists
        (AKASHA_VAULT / "entries").mkdir(exist_ok=True)

    print()
    print("Step 1: Copy facet entries")
    facet_count = _copy_facet_entries(AKASHA_VAULT / "entries")

    print()
    print("Step 2: Copy lattice entries")
    lattice_count = _copy_lattice_entries(AKASHA_VAULT / "entries")

    total = facet_count + lattice_count
    print(f"\n  Total: {total} entries copied to {AKASHA_VAULT / 'entries'}")

    print()
    print("Step 3: Copy ALIASES.tsv")
    _copy_aliases()

    print()
    print("Step 4: Build index (INDEX.md + GRAPH.tsv)")
    rc = _run_cmd(["akasha", "index"])
    if rc != 0:
        print("warning: akasha index failed (non-fatal)", file=sys.stderr)

    print()
    print("Step 5: Dry-run compile (topic list preview)")
    _run_cmd(["akasha", "compile", "--dry-run"])

    print()
    print("=" * 50)
    print("Populate complete.")
    print()
    print("Next steps:")
    print("  akasha status                 # verify counts")
    print("  akasha search 'aria'          # test search (no LLM needed)")
    print("  akasha compile                # generate narrative docs (LLM call)")
    print("  akasha compile --topic aria   # compile one topic only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
