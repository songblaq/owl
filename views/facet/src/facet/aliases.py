"""ALIASES.tsv loader for facet.

ALIASES.tsv maps surface forms to canonical shard names:

    surface_form\\tshard_name
    orbit r4\\torbit
    dispatch score\\torbit

Lines starting with '#' are comments. Empty lines are ignored.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


def load_aliases(vault: Path) -> Dict[str, str]:
    """Load ALIASES.tsv → {surface_form_lower: shard_name}."""
    aliases_path = vault / "ALIASES.tsv"
    mapping: Dict[str, str] = {}
    if not aliases_path.exists():
        return mapping
    for line in aliases_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        surface, shard = parts[0].strip(), parts[1].strip()
        if surface and shard:
            mapping[surface.casefold()] = shard
    return mapping


def resolve_shard(query: str, aliases: Dict[str, str]) -> Optional[str]:
    """Return canonical shard name if query (or any prefix) matches an alias."""
    q = query.strip().casefold()
    if q in aliases:
        return aliases[q]
    # also try individual tokens as fallback prefix match
    for surface, shard in aliases.items():
        if q == surface:
            return shard
    return None
