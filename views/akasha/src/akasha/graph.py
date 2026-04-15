"""GRAPH.tsv builder and 1-hop lookup for akasha.

GRAPH.tsv format: entry_id<TAB>neighbor_id1,neighbor_id2,...

Built from entries' edges field (facet-style dict edges with 'to' key).
Read by search for 1-hop graph expansion.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set


def build_graph(entries: list) -> Dict[str, List[str]]:
    """Build adjacency list from entry edges.

    Args:
        entries: List of Entry objects with edges field (List[Dict[str, str]]).

    Returns:
        Dict mapping entry_id -> [neighbor_id, ...]
    """
    graph: Dict[str, List[str]] = {}
    for e in entries:
        if e.edges:
            neighbors: List[str] = []
            for edge in e.edges:
                to = edge.get("to", "")
                if to:
                    neighbors.append(to)
            if neighbors:
                graph[e.id] = neighbors
    return graph


def write_graph(vault: Path, graph: Dict[str, List[str]]) -> None:
    """Write GRAPH.tsv to vault root."""
    graph_path = vault / "GRAPH.tsv"
    lines = ["# entry_id\tneighbor_id1,neighbor_id2,..."]
    for src in sorted(graph.keys()):
        neighbors_str = ",".join(graph[src])
        lines.append(f"{src}\t{neighbors_str}")
    graph_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def count_graph_edges(vault: Path) -> int:
    """Count non-comment lines in GRAPH.tsv (nodes with edges)."""
    graph_path = vault / "GRAPH.tsv"
    if not graph_path.exists():
        return 0
    return sum(
        1 for line in graph_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )
