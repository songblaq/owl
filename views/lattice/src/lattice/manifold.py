"""MANIFOLD.tsv and BLOOM.txt I/O for lattice.

MANIFOLD.tsv: ngram<TAB>entry_id1,entry_id2,...
BLOOM.txt: sorted unique token list (one per line)

These are rebuilt by `lattice index` and read by `lattice search`.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


def load_manifold(vault: Path) -> Dict[str, List[str]]:
    """Load MANIFOLD.tsv → {ngram: [entry_id, ...]}."""
    manifold_path = vault / "MANIFOLD.tsv"
    mapping: Dict[str, List[str]] = {}
    if not manifold_path.exists():
        return mapping
    for line in manifold_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        ngram, ids_str = parts[0].strip(), parts[1].strip()
        if ngram and ids_str:
            mapping[ngram] = [x.strip() for x in ids_str.split(",") if x.strip()]
    return mapping


def bloom_has_token(vault: Path, token: str) -> bool:
    """Check if a token exists in BLOOM.txt using binary-search-friendly sorted list."""
    bloom_path = vault / "BLOOM.txt"
    if not bloom_path.exists():
        return False
    target = token.casefold()
    # Simple linear scan (BLOOM.txt is small enough; binary search is overkill without bisect on lines)
    for line in bloom_path.read_text(encoding="utf-8").splitlines():
        if line.strip() == target:
            return True
    return False


def query_manifold(
    manifold: Dict[str, List[str]], tokens: List[str]
) -> List[str]:
    """Return ordered list of candidate entry IDs matching any token in manifold."""
    seen: Set[str] = set()
    candidates: List[str] = []
    for token in tokens:
        token_lower = token.casefold()
        if token_lower in manifold:
            for entry_id in manifold[token_lower]:
                if entry_id not in seen:
                    seen.add(entry_id)
                    candidates.append(entry_id)
    return candidates


def load_graph(vault: Path) -> Dict[str, List[str]]:
    """Load GRAPH.tsv → {entry_id: [neighbor_id, ...]}."""
    graph_path = vault / "GRAPH.tsv"
    graph: Dict[str, List[str]] = {}
    if not graph_path.exists():
        return graph
    for line in graph_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        src, neighbors_str = parts[0].strip(), parts[1].strip()
        if src and neighbors_str:
            graph[src] = [x.strip() for x in neighbors_str.split(",") if x.strip()]
    return graph


def expand_one_hop(
    candidate_ids: List[str], graph: Dict[str, List[str]]
) -> List[str]:
    """Expand candidates by 1 hop in the graph. Returns deduplicated list."""
    seen: Set[str] = set(candidate_ids)
    expanded: List[str] = list(candidate_ids)
    for entry_id in candidate_ids:
        for neighbor in graph.get(entry_id, []):
            if neighbor not in seen:
                seen.add(neighbor)
                expanded.append(neighbor)
    return expanded
