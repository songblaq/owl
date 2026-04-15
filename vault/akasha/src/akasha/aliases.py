"""ALIASES.tsv loader for akasha.

ALIASES.tsv maps surface forms to canonical topic names:

    surface_form\\ttopic_name
    orbit r4\\torbit
    dispatch score\\torbit

Lines starting with '#' are comments. Empty lines are ignored.
Copied from facet with topic-based semantics instead of shard-based.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


def load_aliases(vault: Path) -> Dict[str, str]:
    """Load ALIASES.tsv → {surface_form_lower: topic_name}."""
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
        surface, topic = parts[0].strip(), parts[1].strip()
        if surface and topic:
            mapping[surface.casefold()] = topic
    return mapping


def resolve_topic(query: str, aliases: Dict[str, str]) -> Optional[str]:
    """Return canonical topic name if query matches an alias."""
    q = query.strip().casefold()
    if q in aliases:
        return aliases[q]
    return None
